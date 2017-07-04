import argparse
import requests

def main():
    global args
    args = None
    log('Booting up.')
    log('Mass Proxy Checker by ibuckshot5: v1.0.0')
    parser = argparse.ArgumentParser(description='Check some proxies')
    parser.add_argument('-pf', '--proxy-file', default='proxies.txt', help=('Proxy file to check.'))
    parser.add_argument('-bf', '--banned-file', default='banned.txt', help=('File to write banned proxies to (banned)'))
    parser.add_argument('-gf', '--good-file', default='good.txt', help=('File to write good proxies too (not banned)'))
    parser.add_argument('-ef', '--error-file', default='error.txt', help=('File to store errored out proxies'))
    parser.add_argument('-v', '--verbose', default=False, action='store_false', help=('Verbose logging'))
    # TODO:
    # parser.add_argument('-er', '--error-retry', default=False, action='store_false', help=('Retry on proxy error'))
    # parser.add_argument('-erl', '--error-retry-limit', default=3, help=('Number of times to retry the proxy before it is declared not working'))
    args = parser.parse_args()

    NIANTIC_URL = 'https://pgorelease.nianticlabs.com/plfe/version'
    PTC_URL = 'https://sso.pokemon.com/sso/login?locale=en&service=https://www.pokemon.com/us/pokemon-trainer-club/caslogin'
    # TODO: Make this better, reduce nesting on "with open"
    with open(args.proxy_file, 'r+') as f, open(args.banned_file, 'w+') as banned, open(args.good_file, 'w+') as good, open(args.error_file, 'w+') as error:
        proxies = f.readlines()
        for p in proxies:
            # TODO: Use multithreading to make it go ZOOM ZOOM
            log('Attempting to check proxy {}...'.format(p))
            pr = {
                'http': p,
                'https': p
            }
            try:
                verbose_log('Sending HTTP request to {}, watiting for response...'.format(NIANTIC_URL))
                r = requests.get(NIANTIC_URL, proxies=pr, timeout=5)
                verbose_log('Received response from {} : {}'.format(NIANTIC_URL, r.status_code))
                if r.status_code == 200:
                    nstatus = '{}, Niantic: 200 OK, proxy is not banned.'.format(p)
                if r.status_code == 403:
                    nstatus = '{}, Niantic: 403 Forbidden, proxy is banned.'.format(p)
            except requests.exceptions.Timeout:
                nstatus = '{}, Niantic: Timed out after 5 seconds.'.format(p)
            except requests.exceptions.RequestException as e:
                nstatus = '{pr}, Niantic: Unable to connect to the proxy {pr}, or timed out. Make sure to add https://, and the port.'.format(pr=p)
                log('requestsexception: ' + str(e), '!')

            log(nstatus)

            try:
                verbose_log('Sending HTTP request to {}, watiting for response...'.format(NIANTIC_URL))
                r = requests.get(PTC_URL,proxies=pr, timeout=5)
                verbose_log('Received response from {} : {}'.format(NIANTIC_URL, r.status_code))
                if r.status_code == 200:
                    pstatus = '{}, PTC: 200 OK, proxy is not banned.'.format(p)
                if r.status_code == 409:
                    pstatus = '{}, PTC: 409 Conflict, proxy is banned.'.format(p)
            except requests.exceptions.Timeout:
                pstatus = '{}, PTC: Timed out after 5 seconds.'.format(p)
            except requests.exceptions.RequestException as e:
                pstatus = '{pr}, PTC: Unable to connect to the proxy {pr}, or timed out. Make sure to add https://, and the port.'.format(pr=p)
                log('requestsexception: ' + str(e), '!')

            log(pstatus)

            # TODO: Implement a way to see "where proxies fucked up": IE, on Niantic, PTC or both
            if "200 OK, proxy is not banned." in nstatus and "200 OK, proxy is not banned." in pstatus:
                good.write('{}\n'.format(p))
            elif ('Timed out after 5 seconds.' in nstatus or 'Unable to connect to the proxy' in nstatus) or ('Timed out after 5 seconds.' in pstatus or 'Unable to connect to the proxy' in pstatus):
                error.write('{}\n'.format(p))
            else:
                banned.write('{}\n')

            log('Moving to next proxy...')

        f.close()
        good.close()
        banned.close()
        error.close()

    log('Done checking proxies. You can find them at {} for good ones, and {} for banned ones.'.format(args.good_file, args.banned_file))

def log(message, char='+'):
    print('[{}] {}'.format(char, message))

def verbose_log(message, char='+'):
    if args.verbose:
        print('--> [{}] {}'.format(char, message))

if __name__ == '__main__':
    main()
