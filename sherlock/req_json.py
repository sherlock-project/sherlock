import os

from sherlock.notify import QueryNotifyPrint
from sherlock.result import QueryStatus
from sherlock.sherlock import sherlock
from sherlock.sites import SitesInformation


def req_json(username):
    # Load list of sites to look in
    sites = SitesInformation(os.path.join(
        os.path.dirname(__file__), "resources/data.json"))
    site_data = {site.name: site.information for site in sites}

    # Query notify (not really needed but just to feed the sherlock function enough args
    query_notify = QueryNotifyPrint(result=None,
                                    verbose=False,
                                    print_all=False,
                                    browse=False)

    # Load search results
    results = sherlock(username,
                       site_data,
                       query_notify,
                       tor=False,
                       unique_tor=False,
                       proxy=None,
                       timeout=60)
    json_data = {
        "username": username,
        "sites": jsonify_sites(results),
    }
    print(json_data)
    return json_data


def jsonify_sites(results):
    sites = []

    for site in results:
        if results[site]["status"].status != QueryStatus.CLAIMED:
            continue
        response_time_s = results[site]["status"].query_time
        if response_time_s is None:
            response_time_s = ""
        sites.append({
            "site": site,
            "urlMain": results[site]["url_main"],
            "urlUser": results[site]["url_user"],
            "status": str(results[site]["status"].status),
            "httpStatus": results[site]["http_status"],
            "responseTime": response_time_s
        })

    return sites
