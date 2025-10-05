import requests

claimed = 'blue'
unclaimed = 'noonewouldeverusethis7'
url_claimed = f'https://www.codementor.io/@{claimed}'
url_unclaimed = f'https://www.codementor.io/@{unclaimed}'

print('Codementor Claimed:', requests.get(url_claimed).status_code)
print('Codementor Unclaimed:', requests.get(url_unclaimed).status_code)