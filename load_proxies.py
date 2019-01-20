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