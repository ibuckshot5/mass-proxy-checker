import argparse
import requests


def main():
    global args
    args = None
    log('Booting up.')
    log('Mass Proxy Checker by ibuckshot5: v1.0.0')
    parser = argparse.ArgumentParser(description='Check some proxies')
    parser.add_argument('-pf', '--proxy-file', default='proxies.txt', help='Proxy file to check.')
    parser.add_argument('-bf', '--banned-file', default='banned.txt', help='File to write banned proxies to (banned)')
    parser.add_argument('-gf', '--good-file', default='good.txt', help='File to write good proxies too (not banned)')
    parser.add_argument('-ef', '--error-file', default='error.txt', help='File to store errored out proxies')
    parser.add_argument('-t', '--timeout', default=5, help='Timeout for requests to Niantic and PTC servers.')
    parser.add_argument('-v', '--verbose', default=False, action='store_false', help='Verbose logging')
    parser.add_argument('-de', '--display-exceptions', default=False, action='store_false', help='Display errors on console')
    # TODO:
    # parser.add_argument('-er', '--error-retry', default=False, action='store_false', help='Retry on proxy error')
    # parser.add_argument('-erl', '--error-retry-limit', default=3, help='Number of times to retry the proxy before it is declared not working')
    args = parser.parse_args()

    niantic_url = 'https://pgorelease.nianticlabs.com/plfe/version'
    ptc_url = 'https://sso.pokemon.com/sso/login?locale=en&service=https://www.pokemon.com/us/pokemon-trainer-club/caslogin'

    niantic_headers = {'User-Agent': 'Niantic App'}
    ptc_headers = {'User-Agent': 'pokemongo/1 CFNetwork/811.4.18 Darwin/16.5.0', 'Host': 'sso.pokemon.com'}

    # TODO: Make this better, reduce nesting on "with open"
    with open(args.proxy_file, 'r+') as f, open(args.banned_file, 'w+') as banned, open(args.good_file, 'w+') as good, open(args.error_file, 'w+') as error:
        proxies = f.read().splitlines()
        for p in proxies:
            # TODO: Use multithreading to make it go ZOOM ZOOM
            log('Attempting to check proxy {}...'.format(p))
            pr = {
                'http': p,
                'https': p
            }
            try:
                verbose_log('Sending HTTP request to {}, watiting for response...'.format(niantic_url))
                r = requests.get(niantic_url, proxies=pr, timeout=float(args.timeout), headers=niantic_headers)
                verbose_log('Received response from {} : {}'.format(niantic_url, r.status_code))
                if r.status_code == 200:
                    nstatus = '{}, Niantic: 200 OK, proxy is not banned.'.format(p)
                if r.status_code == 403:
                    nstatus = '{}, Niantic: 403 Forbidden, proxy is banned.'.format(p)
            except requests.exceptions.Timeout:
                nstatus = '{}, Niantic: Timed out after {} seconds.'.format(p, args.timeout)
            except requests.exceptions.RequestException as e:
                nstatus = '{pr}, Niantic: Unable to connect to the proxy {pr}, or timed out. Make sure to add https://, and the port.'.format(pr=p)
                log_error('requestsexception: ' + str(e))

            log(nstatus)

            try:
                verbose_log('Sending HTTP request to {}, watiting for response...'.format(niantic_url))
                r = requests.get(ptc_url, proxies=pr, timeout=float(args.timeout), headers=ptc_headers)
                verbose_log('Received response from {} : {}'.format(niantic_url, r.status_code))
                if r.status_code == 200:
                    pstatus = '{}, PTC: 200 OK, proxy is not banned.'.format(p)
                if r.status_code == 409:
                    pstatus = '{}, PTC: 409 Conflict, proxy is banned.'.format(p)
            except requests.exceptions.Timeout:
                pstatus = '{}, PTC: Timed out after {} seconds.'.format(p, args.timeout)
            except requests.exceptions.RequestException as e:
                pstatus = '{pr}, PTC: Unable to connect to the proxy {pr}, or timed out. Make sure to add https://, and the port.'.format(pr=p)
                log_error('requestsexception: ' + str(e))

            log(pstatus)

            # TODO: Implement a way to see "where proxies fucked up": IE, on Niantic, PTC or both
            if "200 OK, proxy is not banned." in nstatus and "200 OK, proxy is not banned." in pstatus:
                good.write('{}\n'.format(p))
            elif ('Timed out after' in nstatus or 'Unable to connect to the proxy' in nstatus) or ('Timed out after' in pstatus or 'Unable to connect to the proxy' in pstatus):
                error.write('{}\n'.format(p))
            else:
                banned.write('{}\n'.format(p))

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

        
def log_error(message):
    if args.display_exceptions:
        log(message, '!')


if __name__ == '__main__':
    main()
