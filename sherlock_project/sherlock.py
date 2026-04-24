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
from typing import Optional

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


def sherlock(username, site_data, query_notify, dump_response=False, proxy=None, timeout=60):
    query_notify.start(username)

    session = create_session(site_data)
    results_total = {}

    
    for site, net_info in site_data.items():
        results_total[site] = prepare_request(
            site, net_info, username, session,
            query_notify, proxy, timeout
        )

    
    for site, net_info in site_data.items():
        results_total[site] = process_response(
            site, net_info, username,
            results_total[site], query_notify, dump_response
        )

    return results_total



def create_session(site_data):
    max_workers = min(len(site_data), 20)
    return SherlockFuturesSession(
        max_workers=max_workers,
        session=requests.session()
    )



def prepare_request(site, net_info, username, session, query_notify, proxy, timeout):
    result = {"url_main": net_info.get("urlMain")}

    url = interpolate_string(net_info["url"], username.replace(' ', '%20'))

    
    if is_illegal_username(net_info, username):
        result.update(build_illegal_result(username, site, url))
        query_notify.update(result["status"])
        return result

    headers = build_headers(net_info)
    request_func = resolve_request_method(net_info, session)
    url_probe = build_probe_url(net_info, username)
    payload = build_payload(net_info, username)

    future = send_request(
        request_func, url_probe, headers,
        payload, proxy, timeout, net_info
    )

    net_info["request_future"] = future
    result["url_user"] = url

    return result


def is_illegal_username(net_info, username):
    regex_check = net_info.get("regexCheck")
    return regex_check and re.search(regex_check, username) is None


def build_illegal_result(username, site, url):
    return {
        "status": QueryResult(username, site, url, QueryStatus.ILLEGAL),
        "url_user": "",
        "http_status": "",
        "response_text": "",
    }


def build_headers(net_info):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    if "headers" in net_info:
        headers.update(net_info["headers"])
    return headers


def resolve_request_method(net_info, session):
    method = net_info.get("request_method")

    mapping = {
        "GET": session.get,
        "HEAD": session.head,
        "POST": session.post,
        "PUT": session.put,
    }

    if method:
        return mapping.get(method)

    if net_info["errorType"] == "status_code":
        return session.head

    return session.get


def build_probe_url(net_info, username):
    if net_info.get("urlProbe"):
        return interpolate_string(net_info["urlProbe"], username)
    return interpolate_string(net_info["url"], username)


def build_payload(net_info, username):
    payload = net_info.get("request_payload")
    if payload:
        return interpolate_string(payload, username)
    return None


def send_request(request_func, url, headers, payload, proxy, timeout, net_info):
    allow_redirects = net_info.get("errorType") != "response_url"

    kwargs = {
        "url": url,
        "headers": headers,
        "allow_redirects": allow_redirects,
        "timeout": timeout,
        "json": payload,
    }

    if proxy:
        kwargs["proxies"] = {"http": proxy, "https": proxy}

    return request_func(**kwargs)



def process_response(site, net_info, username, result, query_notify, dump_response):
    if result.get("status"):
        return result

    future = net_info["request_future"]

    response, error_text, _ = get_response(
        future, net_info["errorType"], site
    )

    http_status, response_text, response_time = extract_response_data(response)

    status, context = determine_status(response, net_info, error_text)

    final_result = QueryResult(
        username=username,
        site_name=site,
        site_url_user=result["url_user"],
        status=status,
        query_time=response_time,
        context=context,
    )

    query_notify.update(final_result)

    result.update({
        "status": final_result,
        "http_status": http_status,
        "response_text": response_text,
    })

    if dump_response:
        debug_dump(site, username, result, net_info, response)

    return result


def extract_response_data(response):
    try:
        http_status = response.status_code
    except Exception:
        http_status = "?"

    try:
        response_text = response.text.encode(response.encoding or "UTF-8")
    except Exception:
        response_text = ""

    try:
        response_time = response.elapsed
    except Exception:
        response_time = None

    return http_status, response_text, response_time



def determine_status(response, net_info, error_text):
    if error_text:
        return QueryStatus.UNKNOWN, error_text

    if is_waf(response):
        return QueryStatus.WAF, None

    error_type = normalize_error_type(net_info["errorType"])

    if "message" in error_type:
        return check_message(response, net_info), None

    if "status_code" in error_type:
        return check_status_code(response, net_info), None

    if "response_url" in error_type:
        return check_response_url(response), None

    return QueryStatus.UNKNOWN, "Unknown error type"


def normalize_error_type(error_type):
    return error_type if isinstance(error_type, list) else [error_type]


def is_waf(response):
    waf_signatures = [
        "challenge-running",
        "challenge-error-text",
        "AwsWafIntegration",
        "perimeterxIdentifiers"
    ]
    return any(sig in response.text for sig in waf_signatures)


def check_message(response, net_info):
    errors = net_info.get("errorMsg", [])
    if isinstance(errors, str):
        errors = [errors]

    for err in errors:
        if err in response.text:
            return QueryStatus.AVAILABLE

    return QueryStatus.CLAIMED


def check_status_code(response, net_info):
    error_codes = net_info.get("errorCode", [])
    if isinstance(error_codes, int):
        error_codes = [error_codes]

    if response.status_code in error_codes:
        return QueryStatus.AVAILABLE

    if response.status_code < 200 or response.status_code >= 300:
        return QueryStatus.AVAILABLE

    return QueryStatus.CLAIMED


def check_response_url(response):
    if 200 <= response.status_code < 300:
        return QueryStatus.CLAIMED
    return QueryStatus.AVAILABLE



def debug_dump(site, username, result, net_info, response):
    print("+++++++++++++++++++++")
    print(f"TARGET: {site}")
    print(f"USER: {username}")
    print(f"URL: {result['url_user']}")
    print(f"STATUS: {result['status'].status}")
    print(f"HTTP: {response.status_code if response else 'N/A'}")
    print("+++++++++++++++++++++")


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
        help="Load data from a JSON file or an online, valid, JSON file. Upstream PR numbers also accepted.",
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

    parser.add_argument(
        "--txt",
        action="store_true",
        dest="output_txt",
        default=False,
        help="Enable creation of a txt file",
    )

    parser.add_argument(
        "--ignore-exclusions",
        action="store_true",
        dest="ignore_exclusions",
        default=False,
        help="Ignore upstream exclusions (may return more false positives)",
    )

    args = parser.parse_args()

    # If the user presses CTRL-C, exit gracefully without throwing errors
    signal.signal(signal.SIGINT, handler)

    # Check for newer version of Sherlock. If it exists, let the user know about it
    try:
        latest_release_raw = requests.get(forge_api_latest_release, timeout=10).text
        latest_release_json = json_loads(latest_release_raw)
        latest_remote_tag = latest_release_json["tag_name"]

        if latest_remote_tag[1:] != __version__:
            print(
                f"Update available! {__version__} --> {latest_remote_tag[1:]}"
                f"\n{latest_release_json['html_url']}"
            )

    except Exception as error:
        print(f"A problem occurred while checking for an update: {error}")

    # Make prompts
    if args.proxy is not None:
        print("Using the proxy: " + args.proxy)

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
                os.path.join(os.path.dirname(__file__), "resources/data.json"),
                honor_exclusions=False,
            )
        else:
            json_file_location = args.json_file
            if args.json_file:
                # If --json parameter is a number, interpret it as a pull request number
                if args.json_file.isnumeric():
                    pull_number = args.json_file
                    pull_url = f"https://api.github.com/repos/sherlock-project/sherlock/pulls/{pull_number}"
                    pull_request_raw = requests.get(pull_url, timeout=10).text
                    pull_request_json = json_loads(pull_request_raw)

                    # Check if it's a valid pull request
                    if "message" in pull_request_json:
                        print(f"ERROR: Pull request #{pull_number} not found.")
                        sys.exit(1)

                    head_commit_sha = pull_request_json["head"]["sha"]
                    json_file_location = f"https://raw.githubusercontent.com/sherlock-project/sherlock/{head_commit_sha}/sherlock_project/resources/data.json"

            sites = SitesInformation(
                data_file_path=json_file_location,
                honor_exclusions=not args.ignore_exclusions,
                do_not_exclude=args.site_list,
            )
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

        if args.output_txt:
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
                    "url_main": [f'=HYPERLINK(\"{u}\")' for u in url_main],
                    "url_user": [f'=HYPERLINK(\"{u}\")' for u in url_user],
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
