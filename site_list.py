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

def get_rank(domain_to_query, dest):

    #Retrieve ranking data via alexa API
    url = f"http://data.alexa.com/data?cli=10&url={domain_to_query}"
    xml_data = requests.get(url).text
    root = ET.fromstring(xml_data)
    try:
        #Get ranking for this site.
        dest['rank'] = int(root.find(".//REACH").attrib["RANK"])
    except:
        #We did not find the rank for some reason.
        print(f"Error retrieving rank information for '{domain_to_query}'")
        print(f"     Returned XML is |{xml_data}|")

    return

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter
                        )
parser.add_argument("--rank","-r",
                    action="store_true",  dest="rank", default=False,
                    help="Update all website ranks (not recommended)."
                    )
args = parser.parse_args()

with open("sherlock/resources/data.json", "r", encoding="utf-8") as data_file:
    data = json.load(data_file)

with open("sites.md", "w") as site_file:
    data_length = len(data)
    site_file.write(f'## List Of Supported Sites ({data_length} Sites In Total!)\n')

    for social_network in data:
        url_main = data.get(social_network).get("urlMain")
        data.get(social_network)["rank"] = 0
        if args.rank:
            th = threading.Thread(target=get_rank, args=(url_main, data.get(social_network)))
        else:
            th = None
        pool.append((social_network, url_main, th))
        if args.rank:
            th.start()

    index = 1
    for social_network, url_main, th in pool:
        if args.rank:
            th.join()
        site_file.write(f'{index}. [{social_network}]({url_main})\n')
        sys.stdout.write("\r{0}".format(f"Updated {index} out of {data_length} entries"))
        sys.stdout.flush()
        index = index + 1

    if args.rank:
        site_file.write(f'\nAlexa.com rank data fetched at ({datetime.utcnow()} UTC)\n')

sorted_json_data = json.dumps(data, indent=2, sort_keys=True)

with open("sherlock/resources/data.json", "w") as data_file:
    data_file.write(sorted_json_data)

print("\nFinished updating supported site listing!")
