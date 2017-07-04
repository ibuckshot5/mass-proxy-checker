# mass-proxy-checker
Mass proxy checker for RocketMap and Monocle

# Install
```
git clone https://github.com/ibuckshot5/mass-proxy-checker
cd mass-proxy-checker
pip install -r requirements.txt
```

# Running
Examples

* Running the checker from the proxy file `proxies.txt`: `python proxychecker.py -pf proxies.txt`

--> The results will be printed to files `good.txt`, `banned.txt` and `error.txt`

* Running with customized good, banned and error files: `python proxychecker.py -pf proxies.txt -gf goodproxies.txt -bf bannedproxies.txt -ef errorproxies.txt`

--> If the files are not found, it will create them.

* Running with verbose logging: `python proxychecker.py -pf proxies.txt -v`

--> This will allow you to see the details of what's going on behind the scenes.
