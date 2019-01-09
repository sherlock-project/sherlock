# requests and grequests
import requests
import grequests
from argparse import ArgumentParser, RawDescriptionHelpFormatter

# Import all the services
from data import SherlockData
from log import SherlockLog
from service import SherlockService

# Response header and changes
def response(service, found, logger):

    if found:
        logger.error("%s User Not Found" % service.url)
    else:
        logger.info("%s User Found" % service.url)


# Response alteration
def response_error(req, exception, logger):
    logger.error("Request Failed %s" % req.url)
    if exception is requests.exceptions.HTTPError:
        logger.error(str(errh) + " HTTP Error")
    elif exception is requests.exceptions.ConnectionError:
        logger.error(str(errc) + " Error Connecting")
    elif exception is requests.exceptions.Timeout:
        logger.error(str(errt) + " Timeout Error")
    elif exception is requests.exceptions.RequestException:
        logger.error(str(err) + " Unknown error")


# Main function for the logger
def main(
    username: str, data: SherlockData, logger: SherlockLog = SherlockLog.getLogger()
):

    # Map requests
    requestmap = []

    # Create all the sherlock services.
    services = [
        SherlockService(
            username, config=data[key], logger=log, on_recv=response, mapper=requestmap
        )
        for key in data.keys()
    ]

    # Tell the user of the start
    log.log(
        "Finding username %s under %i different services" % (username, len(data.keys()))
    )

    # Scan thorugh each service and send an unset request
    for service in services:
        service.request()

    log.log("Waiting for responses")

    # Process all requests
    grequests.map(requestmap, exception_handler=response_error)


if __name__ == "__main__":

    print(
        """
                                              .\"\"\"-.
                                             /      \\
 ____  _               _            _        |  _..--'-.
/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`
\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\
 ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.
|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.
                                           .'`-._ `.\    | J /

"""
    )

    logger = SherlockLog.getLogger()
    main("penguin", SherlockData.fromFile(filename="data.json", t="json"), logger)
