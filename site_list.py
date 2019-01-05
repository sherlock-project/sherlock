"""Sherlock: Supported Site Listing

This module generates the listing of supported sites.
"""
import json

with open("data.json", "r", encoding="utf-8") as data_file:
    data = json.load(data_file)

with open("sites.md", "w") as site_file:
    site_file.write(f'## List Of Supported Sites ({len(data)} Sites In Total!)\n')

    index = 1
    for social_network in data:
        url_main = data.get(social_network).get("urlMain")
        site_file.write(f'{index}. [{social_network}]({url_main})\n')
        index = index + 1

print("Finished updating supported site listing!")
