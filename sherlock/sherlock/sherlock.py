#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""

import re
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import requests

from result import QueryStatus
from result import QueryResult
from notify import QueryNotifyDict
from sites import SitesInformation
from colorama import init

from sherlock import check_for_parameter, multiple_usernames, get_response, interpolate_string, SherlockFuturesSession, timeout_check, handler

module_name = "Sherlock: Find Usernames Across Social Networks"
__version__ = "0.14.3"


def sherlock(username, site_data, query_notify,
             proxy=None, timeout=60):
    """Run Sherlock Analysis.

    Checks for existence of username on various social media sites.

    Keyword Arguments:
    username               -- String indicating username that report
                              should be created against.
    site_data              -- Dictionary containing all of the site data.
    query_notify           -- Object with base type of QueryNotify().
                              This will be used to notify the caller about
                              query results.
    tor                    -- Boolean indicating whether to use a tor circuit for the requests.
    unique_tor             -- Boolean indicating whether to use a new tor circuit for each request.
    proxy                  -- String indicating the proxy URL
    timeout                -- Time in seconds to wait before timing out request.
                              Default is 60 seconds.

    Return Value:
    Dictionary containing results from report. Key of dictionary is the name
    of the social network site, and the value is another dictionary with
    the following keys:
        url_main:      URL of main site.
        url_user:      URL of user on site (if account exists).
        status:        QueryResult() object indicating results of test for
                       account existence.
        http_status:   HTTP status code of query which checked for existence on
                       site.
        response_text: Text that came back from request.  May be None if
                       there was an HTTP error when checking for existence.
    """

    # Notify caller that we are starting the query.
    query_notify.start(username)

        # Normal requests
    underlying_session = requests.session()

    # Limit number of workers to 20.
    # This is probably vastly overkill.
    if len(site_data) >= 20:
        max_workers = 20
    else:
        max_workers = len(site_data)

    # Create multi-threaded session for all requests.
    session = SherlockFuturesSession(max_workers=max_workers,
                                     session=underlying_session)

    # Results from analysis of all sites
    results_total = {}

    # First create futures for all requests. This allows for the requests to run in parallel
    for social_network, net_info in site_data.items():

        # Results from analysis of this specific site
        results_site = {"url_main": net_info.get("urlMain")}

        # Record URL of main site

        # A user agent is needed because some sites don't return the correct
        # information since they think that we are bots (Which we actually are...)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
        }

        if "headers" in net_info:
            # Override/append any extra headers required by a given site.
            headers.update(net_info["headers"])

        # URL of user on site (if it exists)
        url = interpolate_string(net_info["url"], username)

        # Don't make request if username is invalid for the site
        regex_check = net_info.get("regexCheck")
        if regex_check and re.search(regex_check, username) is None:
            # No need to do the check at the site: this username is not allowed.
            results_site["status"] = QueryResult(username,
                                                 social_network,
                                                 url,
                                                 QueryStatus.ILLEGAL)
            results_site["url_user"] = ""
            results_site["http_status"] = ""
            results_site["response_text"] = ""
            query_notify.update(results_site["status"])
        else:
            # URL of user on site (if it exists)
            results_site["url_user"] = url
            url_probe = net_info.get("urlProbe")
            request_method = net_info.get("request_method")
            request_payload = net_info.get("request_payload")
            request = None

            if request_method is not None:
                if request_method == "GET":
                    request = session.get
                elif request_method == "HEAD":
                    request = session.head
                elif request_method == "POST":
                    request = session.post
                elif request_method == "PUT":
                    request = session.put
                else:
                    raise RuntimeError(f"Unsupported request_method for {url}")

            if request_payload is not None:
                request_payload = interpolate_string(request_payload, username)

            if url_probe is None:
                # Probe URL is normal one seen by people out on the web.
                url_probe = url
            else:
                # There is a special URL for probing existence separate
                # from where the user profile normally can be found.
                url_probe = interpolate_string(url_probe, username)

            if request is None:
                if net_info["errorType"] == "status_code":
                    # In most cases when we are detecting by status code,
                    # it is not necessary to get the entire body:  we can
                    # detect fine with just the HEAD response.
                    request = session.head
                else:
                    # Either this detect method needs the content associated
                    # with the GET response, or this specific website will
                    # not respond properly unless we request the whole page.
                    request = session.get

            if net_info["errorType"] == "response_url":
                # Site forwards request to a different URL if username not
                # found.  Disallow the redirect so we can capture the
                # http status from the original URL request.
                allow_redirects = False
            else:
                # Allow whatever redirect that the site wants to do.
                # The final result of the request will be what is available.
                allow_redirects = True

            # This future starts running the request in a new thread, doesn't block the main thread
            if proxy is not None:
                proxies = {"http": proxy, "https": proxy}
                future = request(url=url_probe, headers=headers,
                                 proxies=proxies,
                                 allow_redirects=allow_redirects,
                                 timeout=timeout,
                                 json=request_payload
                                 )
            else:
                future = request(url=url_probe, headers=headers,
                                 allow_redirects=allow_redirects,
                                 timeout=timeout,
                                 json=request_payload
                                 )

            # Store future in data for access later
            net_info["request_future"] = future

        # Add this site's results into final dictionary with all the other results.
        results_total[social_network] = results_site

    # Open the file containing account links
    # Core logic: If tor requests, make them here. If multi-threaded requests, wait for responses
    for social_network, net_info in site_data.items():

        # Retrieve results again
        results_site = results_total.get(social_network)

        # Retrieve other site information again
        url = results_site.get("url_user")
        status = results_site.get("status")
        if status is not None:
            # We have already determined the user doesn't exist here
            continue

        # Get the expected error type
        error_type = net_info["errorType"]
        error_code = net_info.get("errorCode")

        # Retrieve future and ensure it has finished
        future = net_info["request_future"]
        r, error_text, exception_text = get_response(request_future=future,
                                                     error_type=error_type,
                                                     social_network=social_network)

        # Get response time for response of our request.
        try:
            response_time = r.elapsed
        except AttributeError:
            response_time = None

        # Attempt to get request information
        try:
            http_status = r.status_code
        except:
            http_status = "?"
        try:
            response_text = r.text.encode(r.encoding or "UTF-8")
        except:
            response_text = ""

        query_status = QueryStatus.UNKNOWN
        error_context = None

        if error_text is not None:
            error_context = error_text

        elif error_type == "message":
            # error_flag True denotes no error found in the HTML
            # error_flag False denotes error found in the HTML
            error_flag = True
            errors = net_info.get("errorMsg")
            # errors will hold the error message
            # it can be string or list
            # by isinstance method we can detect that
            # and handle the case for strings as normal procedure
            # and if its list we can iterate the errors
            if isinstance(errors, str):
                # Checks if the error message is in the HTML
                # if error is present we will set flag to False
                if errors in r.text:
                    error_flag = False
            else:
                # If it's list, it will iterate all the error message
                for error in errors:
                    if error in r.text:
                        error_flag = False
                        break
            if error_flag:
                query_status = QueryStatus.CLAIMED
            else:
                query_status = QueryStatus.AVAILABLE
        elif error_type == "status_code":
            # Checks if the Status Code is equal to the optional "errorCode" given in 'data.json'
            if error_code == r.status_code:
                query_status = QueryStatus.AVAILABLE
            # Checks if the status code of the response is 2XX
            elif not r.status_code >= 300 or r.status_code < 200:
                query_status = QueryStatus.CLAIMED
            else:
                query_status = QueryStatus.AVAILABLE
        elif error_type == "response_url":
            # For this detection method, we have turned off the redirect.
            # So, there is no need to check the response URL: it will always
            # match the request.  Instead, we will ensure that the response
            # code indicates that the request was successful (i.e. no 404, or
            # forward to some odd redirect).
            if 200 <= r.status_code < 300:
                query_status = QueryStatus.CLAIMED
            else:
                query_status = QueryStatus.AVAILABLE
        else:
            # It should be impossible to ever get here...
            raise ValueError(f"Unknown Error Type '{error_type}' for "
                             f"site '{social_network}'")

        # Notify caller about results of query.
        result = QueryResult(username=username,
                             site_name=social_network,
                             site_url_user=url,
                             status=query_status,
                             query_time=response_time,
                             context=error_context)
        query_notify.update(result)

        # Save status of request
        results_site["status"] = result

        # Save results from request
        results_site["http_status"] = http_status
        results_site["response_text"] = response_text

        # Add this site's results into final dictionary with all of the other results.
        results_total[social_network] = results_site

    return results_total


def run():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=f"{module_name} (Version {__version__})"
                            )
    parser.add_argument("--folderoutput", "-fo", dest="folderoutput",
                        help="If using multiple usernames, the output of the results will be saved to this folder."
                        )
    parser.add_argument("--output", "-o", dest="output",
                        help="If using single username, the output of the result will be saved to this file."
                        )
    parser.add_argument("--site",
                        action="append", metavar="SITE_NAME",
                        dest="site_list", default=None,
                        help="Limit analysis to just the listed sites. Add multiple options to specify more than one site."
                        )
    parser.add_argument("--proxy", "-p", metavar="PROXY_URL",
                        action="store", dest="proxy", default=None,
                        help="Make requests over a proxy. e.g. socks5://127.0.0.1:1080"
                        )
    parser.add_argument("--json", "-j", metavar="JSON_FILE",
                        dest="json_file", default=None,
                        help="Load data from a JSON file or an online, valid, JSON file.")
    parser.add_argument("--timeout",
                        action="store", metavar="TIMEOUT",
                        dest="timeout", type=timeout_check, default=60,
                        help="Time (in seconds) to wait for response to requests (Default: 60)"
                        )
    parser.add_argument("username",
                        nargs="+", metavar="USERNAMES",
                        action="store",
                        help="One or more usernames to check with social networks. Check similar usernames using {%%} (replace to '_', '-', '.')."
                        )
    parser.add_argument("--browse", "-b",
                        action="store_true", dest="browse", default=False,
                        help="Browse to all results on default browser.")

    args = parser.parse_args()



    # Check for newer version of Sherlock. If it exists, let the user know about it
    try:
        r = requests.get(
            "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock/sherlock.py")

        remote_version = str(re.findall('__version__ = "(.*)"', r.text)[0])
        local_version = __version__

        if remote_version != local_version:
            print("Update Available!\n" +
                  f"You are running version {local_version}. Version {remote_version} is available at https://github.com/sherlock-project/sherlock")

    except Exception as error:
        print(f"A problem occurred while checking for an update: {error}")

    try:
        sites = SitesInformation(args.json_file)
    except Exception as error:
        print(f"ERROR:  {error}")
        sys.exit(1)

    # Create original dictionary from SitesInformation() object.
    # Eventually, the rest of the code will be updated to use the new object
    # directly, but this will glue the two pieces together.
    site_data_all = {site.name: site.information for site in sites}
    if args.site_list is None:
        # Not desired to look at a sub-set of sites
        site_data = site_data_all
    else:
        # User desires to selectively run queries on a sub-set of the site list.
        # Make sure that the sites are supported & build up pruned site database.
        site_data = {}
        site_missing = []
        for site in args.site_list:
            counter = 0
            for existing_site in site_data_all:
                if site.lower() == existing_site.lower():
                    site_data[existing_site] = site_data_all[existing_site]
                    counter += 1
            if counter == 0:
                # Build up list of sites not supported for future error message.
                site_missing.append(f"'{site}'")

        if site_missing:
            print(
                f"Error: Desired sites not found: {', '.join(site_missing)}.")

        if not site_data:
            sys.exit(1)

    # Create notify object for query results.
    query_notify = QueryNotifyDict(result=None,
                                    print_all=args.print_all,
                                    browse=args.browse)

    # Run report on all specified users.
    all_usernames = []
    for username in args.username:
        if (check_for_parameter(username)):
            for name in multiple_usernames(username):
                all_usernames.append(name)
        else:
            all_usernames.append(username)
    for username in all_usernames:

        results = sherlock(username,
                           site_data,
                           query_notify,
                           proxy=args.proxy,
                           timeout=args.timeout)

    return query_notify.finish()