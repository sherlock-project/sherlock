"""Sherlock: Supported Site Listing

This module generates the listing of supported sites.
"""
import json
import sys
import requests
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from bs4 import BeautifulSoup as bs
from collections import OrderedDict

def get_rank(domain_to_query):
    result = -1
    url = "http://www.alexa.com/siteinfo/" + domain_to_query
    page = requests.get(url).text
    soup = bs(page, features="lxml")
    for span in soup.find_all('span'):
    	if span.has_attr("class"):
            if "globleRank" in span["class"]:
                for strong in span.find_all("strong"):
                    if strong.has_attr("class"):
                        if "metrics-data" in strong["class"]:
                            result = int(strong.text.strip().replace(',', ''))
    return result

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter
                        )
parser.add_argument("--rank","-r",
                    action="store_true",  dest="rank", default=False,
                    help="Update all website ranks (not recommended)."
                    )
args = parser.parse_args()

with open("data.json", "r", encoding="utf-8") as data_file:
    data = json.load(data_file)

with open("sites.md", "w") as site_file:
	data_length = len(data)
	site_file.write(f'## List Of Supported Sites ({data_length} Sites In Total!)\n')

	index = 1
	for social_network in data:
		url_main = data.get(social_network).get("urlMain")
		site_file.write(f'{index}. [{social_network}]({url_main})\n')
		if args.rank == True:
			data.get(social_network)["rank"] = get_rank(url_main)
			sys.stdout.write("\r{0}".format(f"Updated {index} out of {data_length} entries"))
			sys.stdout.flush()
		index = index + 1

sorted_json_data = json.dumps(data, indent=2, sort_keys=True)

with open("data.json", "w") as data_file:
    data_file.write(sorted_json_data)

sys.stdout.write("\r{0}".format(f"Finished updating supported site listing!\n"))
sys.stdout.flush()
