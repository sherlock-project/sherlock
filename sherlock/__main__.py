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
    if exception is requests.exceptions.HTTPError:git 
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

    # Create all the sherlock services.
    services = [
        SherlockService(
            username, config=data[key], logger=logger, on_recv=response
        ).grequest
        for key in data.keys()
    ]

    # Tell the user of the start
    logger.log("Finding username %s under %i different services" % (username, len(data.keys())))
    logger.log("Waiting for responses")

    # Process all requests
    grequests.map(
        services,
        exception_handler=lambda request, exception: response_error(
            request, exception, logger
        ),
    )


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
