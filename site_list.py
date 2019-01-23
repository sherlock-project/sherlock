"""Sherlock: Supported Site Listing

This module generates the listing of supported sites.
"""
import json
from collections import OrderedDict

with open("data.json", "r", encoding="utf-8") as data_file:
    data = json.load(data_file)

sorted_json_data = json.dumps(data, indent=2, sort_keys=True)

with open("data.json", "w") as data_file:
    data_file.write(sorted_json_data)

with open("sites.md", "w") as site_file:
    site_file.write(f'## List Of Supported Sites ({len(data)} Sites In Total!)\n')

    index = 1
    for social_network in OrderedDict(sorted(data.items())): 
        url_main = data.get(social_network).get("urlMain")
        site_file.write(f'{index}. [{social_network}]({url_main})\n')
        index = index + 1

print("Finished updating supported site listing!")
