"""Sherlock: Supported Site Listing
This module generates the listing of supported sites.
"""
import json
import sys
import requests
import threading
from bs4 import BeautifulSoup as bs
from datetime import datetime

pool = list()

def get_rank(domain_to_query, dest):
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
	dest = result

with open("sherlock/data.json", "r", encoding="utf-8") as data_file:
	data = json.load(data_file)

with open("sites.md", "w") as site_file:
	data_length = len(data)
	site_file.write(f'## List Of Supported Sites ({data_length} Sites In Total!)\n')

	for social_network in data:
		url_main = data.get(social_network).get("urlMain")
		th = threading.Thread(target=get_rank, args=(url_main, data.get(social_network)["rank"]))
		pool.append((url_main, th))
		th.start()

	index = 1
	for social_network, th in pool:
		th.join()
		site_file.write(f'{index}. [{social_network}]({url_main})\n')
		sys.stdout.write("\r{0}".format(f"Updated {index} out of {data_length} entries"))
		sys.stdout.flush()
		index = index + 1

	site_file.write(f'\nAlexa.com rank data fetched at ({datetime.utcnow()} UTC)\n')

sorted_json_data = json.dumps(data, indent=2, sort_keys=True)

with open("sherlock/data.json", "w") as data_file:
	data_file.write(sorted_json_data)

print("\nFinished updating supported site listing!")