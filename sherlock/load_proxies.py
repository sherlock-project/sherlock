import csv
import requests
import time
from collections import namedtuple
from colorama import Fore, Style


def load_proxies_from_csv(path_to_list):
    """
    A function which loads proxies from a .csv file, to a list.

    Inputs: path to .csv file which contains proxies, described by fields: 'ip', 'port', 'protocol'.

    Outputs: list containing proxies stored in named tuples.
    """
    Proxy = namedtuple('Proxy', ['ip', 'port', 'protocol'])

    with open(path_to_list, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        proxies = [Proxy(line['ip'],line['port'],line['protocol']) for line in csv_reader]

    return proxies


def check_proxy(proxy_ip, proxy_port, protocol):
    """
    A function which test the proxy by attempting
    to make a request to the designated website.

    We use 'wikipedia.org' as a test, since we can test the proxy anonymity
    by check if the returning 'X-Client-IP' header matches the proxy ip.
    """
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


def check_proxy_list(proxy_list, max_proxies=None):
    """
    A function which takes in one mandatory argument -> a proxy list in
    the format returned by the function 'load_proxies_from_csv'.

    It also takes an optional argument 'max_proxies', if the user wishes to
    cap the number of validated proxies.

    Each proxy is tested by the check_proxy function. Since each test is done on
    'wikipedia.org', in order to be considerate to Wikipedia servers, we are not using any async modules,
    but are sending successive requests each separated by at least 1 sec.

    Outputs: list containing proxies stored in named tuples.
    """
    print((Style.BRIGHT + Fore.GREEN + "[" +
           Fore.YELLOW + "*" +
           Fore.GREEN + "] Started checking proxies."))
    working_proxies = []

    # If the user has limited the number of proxies we need,
    # the function will stop when the working_proxies
    # loads the max number of requested proxies.
    if max_proxies != None:
        for proxy in proxy_list:
            if len(working_proxies) < max_proxies:
                time.sleep(1)
                if check_proxy(proxy.ip,proxy.port,proxy.protocol) == True:
                    working_proxies.append(proxy)
            else:
                break
    else:
        for proxy in proxy_list:
            time.sleep(1)
            if check_proxy(proxy.ip,proxy.port,proxy.protocol) == True:
                working_proxies.append(proxy)

    if len(working_proxies) > 0:
        print((Style.BRIGHT + Fore.GREEN + "[" +
               Fore.YELLOW + "*" +
               Fore.GREEN + "] Finished checking proxies."))
        return working_proxies

    else:
        raise Exception("Found no working proxies.")
