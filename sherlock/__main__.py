import requests
import grequests

from sherlockdata import SherlockData
from sherlockfinder import SherlockFinder
from sherlocklog import SherlockLog
from sherlockservice import SherlockService

logger = None

# Reponse handler
def response(service, found):

    if found:
        logger.error("%s User Not Found" % service.url)
    else:
        logger.info("%s User Found" % service.url)

def response_error(req, exception):
    global logger

    logger.error("Request Failed %s" % req.url) 
    try:
        raise exception
    except requests.exceptions.HTTPError as errh:
        logger.error(str(errh) + " HTTP Error")
    except requests.exceptions.ConnectionError as errc:
        logger.error(str(errc) + " Error Connecting")
    except requests.exceptions.Timeout as errt:
        logger.error(str(errt) + " Timeout Error")
    except requests.exceptions.RequestException as err:
        logger.error(str(err) + " Unknown error" )

# Main function for the logger
def main(username: str, data: SherlockData):
    global logger
    
    log = logger
    
    # Map requests
    requestmap = []
    
    # Create all the sherlock services.
    services = [SherlockService(
        username, 
        config=data[key], 
        logger=log, 
        on_recv=response, 
        mapper=requestmap) for key in data.keys()]

    # Tell the user of the start
    log.log("Finding username %s under %i different services" % (username, len(data.keys())))

    # Scan thorugh each service and send an unset request
    for service in services:
        service.request()
    
    log.log("Waiting for responses")
    
    # Process all requests
    grequests.map(requestmap, exception_handler=response_error)

if __name__ == "__main__":
    
    print("""
                                              .\"\"\"-.
                                             /      \\
 ____  _               _            _        |  _..--'-.
/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`
\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\
 ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.
|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.
                                           .'`-._ `.\    | J /

""")
    
    logger = SherlockLog.getLogger()
    main(
        "penguin",
        SherlockData.fromFile(filename="../local/data.json",t="json"))
    
    
