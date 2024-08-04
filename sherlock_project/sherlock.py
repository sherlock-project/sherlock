#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""

import sys

try:
    from sherlock_project.__init__ import import_error_test_var # noqa: F401
except ImportError:
    print("Did you run Sherlock with `python3 sherlock/sherlock.py ...`?")
    print("This is an outdated method. Please see https://sherlockproject.xyz/installation for up to date instructions.")
    sys.exit(1)

import csv
import signal
import pandas as pd
import os
import re
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from json import loads as json_loads
from time import monotonic

import requests
from requests_futures.sessions import FuturesSession

from sherlock_project.__init__ import (
    __longname__,
    __shortname__,
    __version__,
    forge_api_latest_release,
)

from sherlock_project.result import QueryStatus
from sherlock_project.result import QueryResult
from sherlock_project.notify import QueryNotify
from sherlock_project.notify import QueryNotifyPrint
from sherlock_project.sites import SitesInformation
from colorama import init
from argparse import ArgumentTypeError


class SherlockFuturesSession(FuturesSession):
    def request(self, method, url, hooks=None, *args, **kwargs):
        """Request URL.

        This extends the FuturesSession request method to calculate a response
        time metric to each request.

        It is taken (almost) directly from the following Stack Overflow answer:
        https://github.com/ross/requests-futures#working-in-the-background

        Keyword Arguments:
        self                   -- This object.
        method                 -- String containing method desired for request.
        url                    -- String containing URL for request.
        hooks                  -- Dictionary containing hooks to execute after
                                  request finishes.
        args                   -- Arguments.
        kwargs                 -- Keyword arguments.

        Return Value:
        Request object.
        """
        # Record the start time for the request.
        if hooks is None:
            hooks = {}
        start = monotonic()

        def response_time(resp, *args, **kwargs):
            """Response Time Hook.

            Keyword Arguments:
            resp                   -- Response object.
            args                   -- Arguments.
            kwargs                 -- Keyword arguments.

            Return Value:
            Nothing.
            """
            resp.elapsed = monotonic() - start

            return

        # Install hook to execute when response completes.
        # Make sure that the time measurement hook is first, so we will not
        # track any later hook's execution time.
        try:
            if isinstance(hooks["response"], list):
                hooks["response"].insert(0, response_time)
            elif isinstance(hooks["response"], tuple):
                # Convert tuple to list and insert time measurement hook first.
                hooks["response"] = list(hooks["response"])
                hooks["response"].insert(0, response_time)
            else:
                # Must have previously contained a single hook function,
                # so convert to list.
                hooks["response"] = [response_time, hooks["response"]]
        except KeyError:
            # No response hook was already defined, so install it ourselves.
            hooks["response"] = [response_time]

        return super(SherlockFuturesSession, self).request(
            method, url, hooks=hooks, *args, **kwargs
        )


def get_response(request_future, error_type, social_network):
    # Default for Response object if some failure occurs.
    response = None

    error_context = "General Unknown Error"
    exception_text = None
    try:
        response = request_future.result()
        if response.status_code:
            # Status code exists in response object
            error_context = None
    except requests.exceptions.HTTPError as errh:
        error_context = "HTTP Error"
        exception_text = str(errh)
    except requests.exceptions.ProxyError as errp:
        error_context = "Proxy Error"
        exception_text = str(errp)
    except requests.exceptions.ConnectionError as errc:
        error_context = "Error Connecting"
        exception_text = str(errc)
    except requests.exceptions.Timeout as errt:
        error_context = "Timeout Error"
        exception_text = str(errt)
    except requests.exceptions.RequestException as err:
        error_context = "Unknown Error"
        exception_text = str(err)

    return response, error_context, exception_text


def interpolate_string(input_object, username):
    if isinstance(input_object, str):
        return input_object.replace("{}", username)
    elif isinstance(input_object, dict):
        return {k: interpolate_string(v, username) for k, v in input_object.items()}
    elif isinstance(input_object, list):
        return [interpolate_string(i, username) for i in input_object]
    return input_object


def check_for_parameter(username):
    """checks if {?} exists in the username
    if exist it means that sherlock is looking for more multiple username"""
    return "{?}" in username


checksymbols = ["_", "-", "."]


def multiple_usernames(username):
    """replace the parameter with with symbols and return a list of usernames"""
    allUsernames = []
    for i in checksymbols:
        allUsernames.append(username.replace("{?}", i))
    return allUsernames


def sherlock(
    username,
    site_data,
    query_notify: QueryNotify,
    tor: bool = False,
    unique_tor: bool = False,
    dump_response: bool = False,
    proxy=None,
    timeout=60,
):
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
    # Create session based on request methodology
    if tor or unique_tor:
        try:
            from torrequest import TorRequest  # noqa: E402
        except ImportError:
            print("Important!")
            print("> --tor and --unique-tor are now DEPRECATED, and may be removed in a future release of Sherlock.")
            print("> If you've installed Sherlock via pip, you can include the optional dependency via `pip install 'sherlock-project[tor]'`.")
            print("> Other packages should refer to their documentation, or install it separately with `pip install torrequest`.\n")
            sys.exit(query_notify.finish())

        print("Important!")
        print("> --tor and --unique-tor are now DEPRECATED, and may be removed in a future release of Sherlock.")

        # Requests using Tor obfuscation
        try:
            underlying_request = TorRequest()
        except OSError:
            print("Tor not found in system path. Unable to continue.\n")
            sys.exit(query_notify.finish())

        underlying_session = underlying_request.session
    else:
        # Normal requests
        underlying_session = requests.session()
        underlying_request = requests.Request()

    # Limit number of workers to 20.
    # This is probably vastly overkill.
    if len(site_data) >= 20:
        max_workers = 20
    else:
        max_workers = len(site_data)

    # Create multi-threaded session for all requests.
    session = SherlockFuturesSession(
        max_workers=max_workers, session=underlying_session
    )

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
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
        }

        if "headers" in net_info:
            # Override/append any extra headers required by a given site.
            headers.update(net_info["headers"])

        # URL of user on site (if it exists)
        url = interpolate_string(net_info["url"], username.replace(' ', '%20'))

        # Don't make request if username is invalid for the site
        regex_check = net_info.get("regexCheck")
        if regex_check and re.search(regex_check, username) is None:
            # No need to do the check at the site: this username is not allowed.
            results_site["status"] = QueryResult(
                username, social_network, url, QueryStatus.ILLEGAL
            )
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
                future = request(
                    url=url_probe,
                    headers=headers,
                    proxies=proxies,
                    allow_redirects=allow_redirects,
                    timeout=timeout,
                    json=request_payload,
                )
            else:
                future = request(
                    url=url_probe,
                    headers=headers,
                    allow_redirects=allow_redirects,
                    timeout=timeout,
                    json=request_payload,
                )

            # Store future in data for access later
            net_info["request_future"] = future

            # Reset identify for tor (if needed)
            if unique_tor:
                underlying_request.reset_identity()

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

        # Retrieve future and ensure it has finished
        future = net_info["request_future"]
        r, error_text, exception_text = get_response(
            request_future=future, error_type=error_type, social_network=social_network
        )

        # Get response time for response of our request.
        try:
            response_time = r.elapsed
        except AttributeError:
            response_time = None

        # Attempt to get request information
        try:
            http_status = r.status_code
        except Exception:
            http_status = "?"
        try:
            response_text = r.text.encode(r.encoding or "UTF-8")
        except Exception:
            response_text = ""

        query_status = QueryStatus.UNKNOWN
        error_context = None

        # As WAFs advance and evolve, they will occasionally block Sherlock and
        # lead to false positives and negatives. Fingerprints should be added
        # here to filter results that fail to bypass WAFs. Fingerprints should
        # be highly targetted. Comment at the end of each fingerprint to
        # indicate target and date fingerprinted.
        WAFHitMsgs = [
            '.loading-spinner{visibility:hidden}body.no-js .challenge-running{display:none}body.dark{background-color:#222;color:#d9d9d9}body.dark a{color:#fff}body.dark a:hover{color:#ee730a;text-decoration:underline}body.dark .lds-ring div{border-color:#999 transparent transparent}body.dark .font-red{color:#b20f03}body.dark', # 2024-05-13 Cloudflare
            '{return l.onPageView}}),Object.defineProperty(r,"perimeterxIdentifiers",{enumerable:' # 2024-04-09 PerimeterX / Human Security
        ]

        if error_text is not None:
            error_context = error_text

        elif any(hitMsg in r.text for hitMsg in WAFHitMsgs):
            query_status = QueryStatus.WAF

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
            error_codes = net_info.get("errorCode")
            query_status = QueryStatus.CLAIMED

            # Type consistency, allowing for both singlets and lists in manifest
            if isinstance(error_codes, int):
                error_codes = [error_codes]

            if error_codes is not None and r.status_code in error_codes:
                query_status = QueryStatus.AVAILABLE
            elif r.status_code >= 300 or r.status_code < 200:
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
            raise ValueError(
                f"Unknown Error Type '{error_type}' for " f"site '{social_network}'"
            )
        
        if dump_response:
            print("+++++++++++++++++++++")
            print(f"TARGET NAME   : {social_network}")
            print(f"USERNAME      : {username}")
            print(f"TARGET URL    : {url}")
            print(f"TEST METHOD   : {error_type}")
            try:
                print(f"STATUS CODES  : {net_info['errorCode']}")
            except KeyError:
                pass
            print("Results...")
            try:
                print(f"RESPONSE CODE : {r.status_code}")
            except Exception:
                pass
            try:
                print(f"ERROR TEXT    : {net_info['errorMsg']}")
            except KeyError:
                pass
            print(">>>>> BEGIN RESPONSE TEXT")
            try:
                print(r.text)
            except Exception:
                pass
            print("<<<<< END RESPONSE TEXT")
            print("VERDICT       : " + str(query_status))
            print("+++++++++++++++++++++")

        # Notify caller about results of query.
        result = QueryResult(
            username=username,
            site_name=social_network,
            site_url_user=url,
            status=query_status,
            query_time=response_time,
            context=error_context,
        )
        query_notify.update(result)

        # Save status of request
        results_site["status"] = result

        # Save results from request
        results_site["http_status"] = http_status
        results_site["response_text"] = response_text

        # Add this site's results into final dictionary with all of the other results.
        results_total[social_network] = results_site

    return results_total


def timeout_check(value):
    """Check Timeout Argument.

    Checks timeout for validity.

    Keyword Arguments:
    value                  -- Time in seconds to wait before timing out request.

    Return Value:
    Floating point number representing the time (in seconds) that should be
    used for the timeout.

    NOTE:  Will raise an exception if the timeout in invalid.
    """

    float_value = float(value)

    if float_value <= 0:
        raise ArgumentTypeError(
            f"Invalid timeout value: {value}. Timeout must be a positive number."
        )

    return float_value


def handler(signal_received, frame):
    """Exit gracefully without throwing errors

    Source: https://www.devdungeon.com/content/python-catch-sigint-ctrl-c
    """
    sys.exit(0)


def main():
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=f"{__longname__} (Version {__version__})",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{__shortname__} v{__version__}",
        help="Display version information and dependencies.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        "-d",
        "--debug",
        action="store_true",
        dest="verbose",
        default=False,
        help="Display extra debugging information and metrics.",
    )
    parser.add_argument(
        "--folderoutput",
        "-fo",
        dest="folderoutput",
        help="If using multiple usernames, the output of the results will be saved to this folder.",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        help="If using single username, the output of the result will be saved to this file.",
    )
    parser.add_argument(
        "--tor",
        "-t",
        action="store_true",
        dest="tor",
        default=False,
        help="Make requests over Tor; increases runtime; requires Tor to be installed and in system path.",
    )
    parser.add_argument(
        "--unique-tor",
        "-u",
        action="store_true",
        dest="unique_tor",
        default=False,
        help="Make requests over Tor with new Tor circuit after each request; increases runtime; requires Tor to be installed and in system path.",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        dest="csv",
        default=False,
        help="Create Comma-Separated Values (CSV) File.",
    )
    parser.add_argument(
        "--xlsx",
        action="store_true",
        dest="xlsx",
        default=False,
        help="Create the standard file for the modern Microsoft Excel spreadsheet (xlsx).",
    )
    parser.add_argument(
        "--site",
        action="append",
        metavar="SITE_NAME",
        dest="site_list",
        default=[],
        help="Limit analysis to just the listed sites. Add multiple options to specify more than one site.",
    )
    parser.add_argument(
        "--proxy",
        "-p",
        metavar="PROXY_URL",
        action="store",
        dest="proxy",
        default=None,
        help="Make requests over a proxy. e.g. socks5://127.0.0.1:1080",
    )
    parser.add_argument(
        "--dump-response",
        action="store_true",
        dest="dump_response",
        default=False,
        help="Dump the HTTP response to stdout for targeted debugging.",
    )
    parser.add_argument(
        "--json",
        "-j",
        metavar="JSON_FILE",
        dest="json_file",
        default=None,
        help="Load data from a JSON file or an online, valid, JSON file.",
    )
    parser.add_argument(
        "--timeout",
        action="store",
        metavar="TIMEOUT",
        dest="timeout",
        type=timeout_check,
        default=60,
        help="Time (in seconds) to wait for response to requests (Default: 60)",
    )
    parser.add_argument(
        "--print-all",
        action="store_true",
        dest="print_all",
        default=False,
        help="Output sites where the username was not found.",
    )
    parser.add_argument(
        "--print-found",
        action="store_true",
        dest="print_found",
        default=True,
        help="Output sites where the username was found (also if exported as file).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        dest="no_color",
        default=False,
        help="Don't color terminal output",
    )
    parser.add_argument(
        "username",
        nargs="+",
        metavar="USERNAMES",
        action="store",
        help="One or more usernames to check with social networks. Check similar usernames using {?} (replace to '_', '-', '.').",
    )
    parser.add_argument(
        "--browse",
        "-b",
        action="store_true",
        dest="browse",
        default=False,
        help="Browse to all results on default browser.",
    )

    parser.add_argument(
        "--local",
        "-l",
        action="store_true",
        default=False,
        help="Force the use of the local data.json file.",
    )

    parser.add_argument(
        "--nsfw",
        action="store_true",
        default=False,
        help="Include checking of NSFW sites from default list.",
    )

    args = parser.parse_args()

    # If the user presses CTRL-C, exit gracefully without throwing errors
    signal.signal(signal.SIGINT, handler)

    # Check for newer version of Sherlock. If it exists, let the user know about it
    try:
        latest_release_raw = requests.get(forge_api_latest_release).text
        latest_release_json = json_loads(latest_release_raw)
        latest_remote_tag = latest_release_json["tag_name"]

        if latest_remote_tag[1:] != __version__:
            print(
                f"Update available! {__version__} --> {latest_remote_tag[1:]}"
                f"\n{latest_release_json['html_url']}"
            )

    except Exception as error:
        print(f"A problem occurred while checking for an update: {error}")

    # Argument check
    # TODO regex check on args.proxy
    if args.tor and (args.proxy is not None):
        raise Exception("Tor and Proxy cannot be set at the same time.")

    # Make prompts
    if args.proxy is not None:
        print("Using the proxy: " + args.proxy)

    if args.tor or args.unique_tor:
        print("Using Tor to make requests")

        print(
            "Warning: some websites might refuse connecting over Tor, so note that using this option might increase connection errors."
        )

    if args.no_color:
        # Disable color output.
        init(strip=True, convert=False)
    else:
        # Enable color output.
        init(autoreset=True)

    # Check if both output methods are entered as input.
    if args.output is not None and args.folderoutput is not None:
        print("You can only use one of the output methods.")
        sys.exit(1)

    # Check validity for single username output.
    if args.output is not None and len(args.username) != 1:
        print("You can only use --output with a single username")
        sys.exit(1)

    # Create object with all information about sites we are aware of.
    try:
        if args.local:
            sites = SitesInformation(
                os.path.join(os.path.dirname(__file__), "resources/data.json")
            )
        else:
            sites = SitesInformation(args.json_file)
    except Exception as error:
        print(f"ERROR:  {error}")
        sys.exit(1)

    if not args.nsfw:
        sites.remove_nsfw_sites(do_not_remove=args.site_list)

    # Create original dictionary from SitesInformation() object.
    # Eventually, the rest of the code will be updated to use the new object
    # directly, but this will glue the two pieces together.
    site_data_all = {site.name: site.information for site in sites}
    if args.site_list == []:
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
            print(f"Error: Desired sites not found: {', '.join(site_missing)}.")

        if not site_data:
            sys.exit(1)

    # Create notify object for query results.
    query_notify = QueryNotifyPrint(
        result=None, verbose=args.verbose, print_all=args.print_all, browse=args.browse
    )

    # Run report on all specified users.
    all_usernames = []
    for username in args.username:
        if check_for_parameter(username):
            for name in multiple_usernames(username):
                all_usernames.append(name)
        else:
            all_usernames.append(username)
    for username in all_usernames:
        results = sherlock(
            username,
            site_data,
            query_notify,
            tor=args.tor,
            unique_tor=args.unique_tor,
            dump_response=args.dump_response,
            proxy=args.proxy,
            timeout=args.timeout,
        )

        if args.output:
            result_file = args.output
        elif args.folderoutput:
            # The usernames results should be stored in a targeted folder.
            # If the folder doesn't exist, create it first
            os.makedirs(args.folderoutput, exist_ok=True)
            result_file = os.path.join(args.folderoutput, f"{username}.txt")
        else:
            result_file = f"{username}.txt"

        with open(result_file, "w", encoding="utf-8") as file:
            exists_counter = 0
            for website_name in results:
                dictionary = results[website_name]
                if dictionary.get("status").status == QueryStatus.CLAIMED:
                    exists_counter += 1
                    file.write(dictionary["url_user"] + "\n")
            file.write(f"Total Websites Username Detected On : {exists_counter}\n")

        if args.csv:
            result_file = f"{username}.csv"
            if args.folderoutput:
                # The usernames results should be stored in a targeted folder.
                # If the folder doesn't exist, create it first
                os.makedirs(args.folderoutput, exist_ok=True)
                result_file = os.path.join(args.folderoutput, result_file)

            with open(result_file, "w", newline="", encoding="utf-8") as csv_report:
                writer = csv.writer(csv_report)
                writer.writerow(
                    [
                        "username",
                        "name",
                        "url_main",
                        "url_user",
                        "exists",
                        "http_status",
                        "response_time_s",
                    ]
                )
                for site in results:
                    if (
                        args.print_found
                        and not args.print_all
                        and results[site]["status"].status != QueryStatus.CLAIMED
                    ):
                        continue

                    response_time_s = results[site]["status"].query_time
                    if response_time_s is None:
                        response_time_s = ""
                    writer.writerow(
                        [
                            username,
                            site,
                            results[site]["url_main"],
                            results[site]["url_user"],
                            str(results[site]["status"].status),
                            results[site]["http_status"],
                            response_time_s,
                        ]
                    )
        if args.xlsx:
            usernames = []
            names = []
            url_main = []
            url_user = []
            exists = []
            http_status = []
            response_time_s = []

            for site in results:
                if (
                    args.print_found
                    and not args.print_all
                    and results[site]["status"].status != QueryStatus.CLAIMED
                ):
                    continue

                if response_time_s is None:
                    response_time_s.append("")
                else:
                    response_time_s.append(results[site]["status"].query_time)
                usernames.append(username)
                names.append(site)
                url_main.append(results[site]["url_main"])
                url_user.append(results[site]["url_user"])
                exists.append(str(results[site]["status"].status))
                http_status.append(results[site]["http_status"])

            DataFrame = pd.DataFrame(
                {
                    "username": usernames,
                    "name": names,
                    "url_main": url_main,
                    "url_user": url_user,
                    "exists": exists,
                    "http_status": http_status,
                    "response_time_s": response_time_s,
                }
            )
            DataFrame.to_excel(f"{username}.xlsx", sheet_name="sheet1", index=False)

        print()
    query_notify.finish()


if __name__ == "__main__":
    main()
