import json

raw = open("data.json", "r", encoding="utf-8")
data = json.load(raw)

site_file = open('sites.md', 'w')
site_file.write('## List of supported sites\n')

index = 1
for social_network in data:
    url_main = data.get(social_network).get("urlMain")
    site_file.write(f'{index}. [{social_network}]({url_main})\n')
    index = index + 1

site_file.close()