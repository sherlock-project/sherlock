"""Sherlock: Supported Site Listing
This module generates the listing of supported sites.
"""
import json
import sys
import requests
import threading
import xml.etree.ElementTree as ET
from datetime import datetime
from argparse import ArgumentParser, RawDescriptionHelpFormatter

pool = list()

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)

args = parser.parse_args()

with open("sherlock/resources/data.json", "r", encoding="utf-8") as data_file:
    data = json.load(data_file)

with open("sites.md", "w") as site_file:
    data_length = len(data)
    site_file.write(f'## List Of Supported Sites ({data_length} Sites In Total!)\n')

    index = 1
    for social_network, url_main, th in pool:

        site_file.write(f'{index}. [{social_network}]({url_main})\n')
        sys.stdout.write("\r{0}".format(f"Updated {index} out of {data_length} entries"))
        sys.stdout.flush()
        index = index + 1

sorted_json_data = json.dumps(data, indent=2, sort_keys=True)

with open("sherlock/resources/data.json", "w") as data_file:
    data_file.write(sorted_json_data)

print("\nFinished updating supported site listing!")
