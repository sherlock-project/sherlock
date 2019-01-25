# requests, grequests and platform
import requests
import grequests
import platform

# argparse and colorama
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from colorama import init as coloramainit

# Import all the services
from sherlock.core import Data
from sherlock.core import Log
from sherlock.core import Service

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
        logger.error(str(exception) + " HTTP Error")
    elif exception is requests.exceptions.ConnectionError:
        logger.error(str(exception) + " Error Connecting")
    elif exception is requests.exceptions.Timeout:
        logger.error(str(exception) + " Timeout Error")
    elif exception is Exception:
        logger.error(str(exception) + " Unknown error")


# Main function for the logger
def main(
    username: str,
    data_file="data.json",
    data_type="json",
    tor: bool = False,
    new_tor_circuit: bool = False
):

    # Create a logger and data object
    logger = Log.getLogger()
    data = Data(data_file, t="")

    # Tell the user of the start
    logger.log(
        "Finding username %s under %i different services" % (username, len(data.keys()))
    )


    logger.log("Waiting for responses")

    # Create all the sherlock services.
    services = [
        Service(
            username, config=data[key], logger=logger, recv=response
        )
        for key in data.keys()
    ]

    # Get service requests
    service_requests = [
       service.grequest for service in services
    ]

    # Send requests
    grequests.map(
        service_requests,
        exception_handler=lambda request, exception: response_error(
            request, exception, logger
        ),
    )
