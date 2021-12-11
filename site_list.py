"""Sherlock: Supported Site Listing
This module generates the listing of supported sites
which can be found in sites.md
It also organizes all the sites in alphanumeric order
"""
import json

pool = list()

with open("sherlock/resources/data.json", "r", encoding="utf-8") as data_file:
    data = json.load(data_file)

with open("sites.md", "w") as site_file:
    data_length = len(data)
    site_file.write(f"## List Of Supported Sites ({data_length} Sites In Total!)\n")

    for social_network in data:
        url_main = data.get(social_network).get("urlMain")
        pool.append((social_network, url_main))

    for social_network, url_main in pool:
        site_file.write(f"1. [{social_network}]({url_main})\n")

sorted_json_data = json.dumps(data, indent=2, sort_keys=True)

with open("sherlock/resources/data.json", "w") as data_file:
    data_file.write(sorted_json_data)
    data_file.write("\n")

print("Finished updating supported site listing!")
