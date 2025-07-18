#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""

import sys
import os
import signal
import re
from json import loads as json_loads
from typing import Optional

try:
    from sherlock_project.__init__ import import_error_test_var  # noqa: F401
except ImportError:
    print("Did you run Sherlock with `python3 sherlock/sherlock.py ...`?")
    print("This is an outdated method. Please see https://sherlockproject.xyz/installation for up to date instructions.")
    sys.exit(1)

import requests
from sherlock_project.utils.http import SherlockFuturesSession, get_response
from sherlock_project.utils.text import (
    interpolate_string,
    check_for_parameter,
    multiple_usernames,
)
from sherlock_project.utils.cli import get_parser
from sherlock_project.utils.output import (
    write_text_file,
    write_csv_file,
    write_xlsx_file,
    get_output_file_path,
)
from sherlock_project.utils.version import check_for_updates

from sherlock_project.result import QueryStatus, QueryResult
from sherlock_project.notify import QueryNotify, QueryNotifyPrint
from sherlock_project.sites import SitesInformation
from colorama import init





def sherlock(
    username: str,
    site_data: dict,
    query_notify: QueryNotify,
    tor: bool = False,
    unique_tor: bool = False,
    dump_response: bool = False,
    proxy: Optional[str] = None,
    timeout: int = 60,
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
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
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
            r'.loading-spinner{visibility:hidden}body.no-js .challenge-running{display:none}body.dark{background-color:#222;color:#d9d9d9}body.dark a{color:#fff}body.dark a:hover{color:#ee730a;text-decoration:underline}body.dark .lds-ring div{border-color:#999 transparent transparent}body.dark .font-red{color:#b20f03}body.dark', # 2024-05-13 Cloudflare
            r'<span id="challenge-error-text">', # 2024-11-11 Cloudflare error page
            r'AwsWafIntegration.forceRefreshToken', # 2024-11-11 Cloudfront (AWS)
            r'{return l.onPageView}}),Object.defineProperty(r,"perimeterxIdentifiers",{enumerable:' # 2024-04-09 PerimeterX / Human Security
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


def handler(signal_received, frame):
    """Exit gracefully without throwing errors

    Source: https://www.devdungeon.com/content/python-catch-sigint-ctrl-c
    """
    sys.exit(0)


def main():
    """Main function for the Sherlock CLI."""
    parser = get_parser()
    args = parser.parse_args()

    # If the user presses CTRL-C, exit gracefully
    signal.signal(signal.SIGINT, handler)

    # Check for updates
    check_for_updates()

    # Argument validation
    if args.tor and (args.proxy is not None):
        raise Exception("Tor and Proxy cannot be set at the same time.")

    if args.output is not None and args.folderoutput is not None:
        print("You can only use one of the output methods.")
        sys.exit(1)

    if args.output is not None and len(args.username) > 1:
        print("You can only use --output with a single username")
        sys.exit(1)

    # Setup prompts and color
    if args.proxy:
        print(f"Using the proxy: {args.proxy}")
    if args.tor or args.unique_tor:
        print("Using Tor to make requests")
        print("Warning: some websites might refuse connecting over Tor...")

    init(autoreset=True, strip=args.no_color)

    # Load site data
    try:
        if args.local:
            sites = SitesInformation(os.path.join(os.path.dirname(__file__), "resources/data.json"))
        else:
            json_file_location = args.json_file
            if args.json_file and args.json_file.isnumeric():
                pull_url = f"https://api.github.com/repos/sherlock-project/sherlock/pulls/{args.json_file}"
                pull_request_raw = requests.get(pull_url).text
                pull_request_json = json_loads(pull_request_raw)
                if "message" in pull_request_json:
                    print(f"ERROR: Pull request #{args.json_file} not found.")
                    sys.exit(1)
                head_commit_sha = pull_request_json["head"]["sha"]
                json_file_location = f"https://raw.githubusercontent.com/sherlock-project/sherlock/{head_commit_sha}/sherlock_project/resources/data.json"
            sites = SitesInformation(json_file_location)
    except Exception as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    if not args.nsfw:
        sites.remove_nsfw_sites(do_not_remove=args.site_list)

    site_data_all = {site.name: site.information for site in sites}
    if not args.site_list:
        site_data = site_data_all
    else:
        site_data = {}
        site_missing = [s for s in args.site_list if s.lower() not in [e.lower() for e in site_data_all]]
        for site in args.site_list:
            if site.lower() in [e.lower() for e in site_data_all]:
                 for existing_site in site_data_all:
                    if site.lower() == existing_site.lower():
                        site_data[existing_site] = site_data_all[existing_site]
        if site_missing:
            print(f"Error: Desired sites not found: {', '.join(site_missing)}.")
        if not site_data:
            sys.exit(1)

    # Create notify object
    query_notify = QueryNotifyPrint(
        result=None, verbose=args.verbose, print_all=args.print_all, browse=args.browse
    )

    # Process usernames
    all_usernames = []
    for username in args.username:
        if check_for_parameter(username):
            all_usernames.extend(multiple_usernames(username))
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

        # Handle output
        file_path = get_output_file_path(username, args)
        if not args.no_txt:
            write_text_file(results, file_path)
        if args.csv:
            write_csv_file(username, results, file_path, args)
        if args.xlsx:
            write_xlsx_file(username, results, file_path, args)

        print()

    query_notify.finish()


if __name__ == "__main__":
    main()
