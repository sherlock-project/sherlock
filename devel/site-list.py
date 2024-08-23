#!/usr/bin/env python
# This module generates the listing of supported sites which can be found in
# sites.md. It also organizes all the sites in alphanumeric order
import json
import os


DATA_REL_URI: str = "sherlock_project/resources/data.json"

# Read the data.json file
with open(DATA_REL_URI, "r", encoding="utf-8") as data_file:
    data: dict = json.load(data_file)

# Removes schema-specific keywords for proper processing
social_networks: dict = dict(data)
social_networks.pop('$schema', None)

# Sort the social networks in alphanumeric order
social_networks: list = sorted(social_networks.items())

# Make output dir where the site list will be written
os.mkdir("output")

# Write the list of supported sites to sites.md
with open("output/sites.mdx", "w") as site_file:
    site_file.write("---\ntitle: 'List of supported sites'\nsidebarTitle: 'Supported sites'\nicon: 'globe'\ndescription: 'Sherlock currently supports **400+** sites'\n---\n\n")
    for social_network, info in social_networks:
        url_main = info["urlMain"]
        is_nsfw = "**(NSFW)**" if info.get("isNSFW") else ""
        site_file.write(f"1. [{social_network}]({url_main}) {is_nsfw}\n")

# Overwrite the data.json file with sorted data
with open(DATA_REL_URI, "w") as data_file:
    sorted_data = json.dumps(data, indent=2, sort_keys=True)
    data_file.write(sorted_data)
    data_file.write("\n")

print("Finished updating supported site listing!")

