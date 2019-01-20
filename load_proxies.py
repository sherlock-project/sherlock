import csv
import requests
import time
from collections import namedtuple

"""
A function which loads proxies from a .csv file, to a list.

Inputs: path to .csv file which contains proxies, described by fields: 'ip', 'port', 'protocol'.

Outputs: list containing proxies stored in named tuples.
"""


def load_proxies_from_csv(path_to_list):
    Proxy = namedtuple('Proxy', ['ip', 'port', 'protocol'])

    with open(path_to_list, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        proxies = [Proxy(line['ip'],line['port'],line['protocol']) for line in csv_reader]

    return proxies


"""
A function which test the proxy by attempting 
to make a request to the designated website.

We use 'wikipedia.org' as a test, since we can test the proxy anonymity 
by check if the returning 'X-Client-IP' header matches the proxy ip.
"""


def check_proxy(proxy_ip, proxy_port, protocol):
    full_proxy = f'{protocol}://{proxy_ip}:{proxy_port}'
    proxies = {'http': full_proxy, 'https': full_proxy}
    try:
        r = requests.get('https://www.wikipedia.org',proxies=proxies, timeout=4)
        return_proxy = r.headers['X-Client-IP']
        if proxy_ip==return_proxy:
            return True
        else:
            return False
    except Exception:
        return False