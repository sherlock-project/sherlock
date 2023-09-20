#!/usr/bin/env python
# This module generates the listing of supported sites which can be found in
# sites.md. It also organizes all the sites in alphanumeric order
import json

# Read the data.json file
with open("sherlock/resources/data.json", "r", encoding="utf-8") as data_file:
    data = json.load(data_file)

# Sort the social networks in alphanumeric order
social_networks = sorted(data.items())

# Write the list of supported sites to sites.md
with open("sites.md", "w") as site_file:
    site_file.write(f"## List Of Supported Sites ({len(social_networks)} Sites In Total!)\n")
    for social_network, info in social_networks:
        url_main = info["urlMain"]
        is_nsfw = "**(NSFW)**" if info.get("isNSFW") else ""
        site_file.write(f"1. ![](https://www.google.com/s2/favicons?domain={url_main}) [{social_network}]({url_main}) {is_nsfw}\n")

# Overwrite the data.json file with sorted data
with open("sherlock/resources/data.json", "w") as data_file:
    sorted_data = json.dumps(data, indent=2, sort_keys=True)
    data_file.write(sorted_data)
    data_file.write("\n")

print("Finished updating supported site listing!")
