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
    except UnicodeError as err:
        error_context = "Encoding Error"
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

def parse_arguments():
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=f"{__longname__} (Version {__version__})",
    )

    parser.add_argument("--version", action="version", version=f"{__shortname__} v{__version__}")
    parser.add_argument("--verbose", "-v", "-d", "--debug", action="store_true", dest="verbose", default=False)
    parser.add_argument("--folderoutput", "-fo", dest="folderoutput")
    parser.add_argument("--output", "-o", dest="output")
    parser.add_argument("--csv", action="store_true", dest="csv", default=False)
    parser.add_argument("--xlsx", action="store_true", dest="xlsx", default=False)
    parser.add_argument("--site", action="append", dest="site_list", default=[])
    parser.add_argument("--proxy", "-p", dest="proxy", default=None)
    parser.add_argument("--dump-response", action="store_true", dest="dump_response", default=False)
    parser.add_argument("--json", "-j", dest="json_file", default=None)
    parser.add_argument("--timeout", dest="timeout", type=timeout_check, default=60)
    parser.add_argument("--print-all", action="store_true", dest="print_all", default=False)
    parser.add_argument("--print-found", action="store_true", dest="print_found", default=True)
    parser.add_argument("--no-color", action="store_true", dest="no_color", default=False)
    parser.add_argument("--browse", "-b", action="store_true", dest="browse", default=False)
    parser.add_argument("--local", "-l", action="store_true", default=False)
    parser.add_argument("--nsfw", action="store_true", default=False)
    parser.add_argument("--txt", action="store_true", dest="output_txt", default=False)
    parser.add_argument("--ignore-exclusions", action="store_true", dest="ignore_exclusions", default=False)
    parser.add_argument("username", nargs="+", metavar="USERNAMES")

    return parser.parse_args()


def check_latest_version():
    try:
        latest_release_raw = requests.get(forge_api_latest_release, timeout=10).text
        latest_release_json = json_loads(latest_release_raw)
        latest_remote_tag = latest_release_json["tag_name"]

        if latest_remote_tag[1:] != __version__:
            print(
                f"Update available! {__version__} --> {latest_remote_tag[1:]}\n"
                f"{latest_release_json['html_url']}"
            )
    except Exception as error:
        print(f"A problem occurred while checking for an update: {error}")


def validate_output_options(args):
    if args.output and args.folderoutput:
        print("You can only use one of the output methods.")
        sys.exit(1)

    if args.output and len(args.username) != 1:
        print("You can only use --output with a single username")
        sys.exit(1)


def load_sites(args):
    try:
        if args.local:
            return SitesInformation(
                os.path.join(os.path.dirname(__file__), "resources/data.json"),
                honor_exclusions=False,
            )

        json_file_location = args.json_file

        if args.json_file and args.json_file.isnumeric():
            pull_url = f"https://api.github.com/repos/sherlock-project/sherlock/pulls/{args.json_file}"
            pull_request_json = json_loads(requests.get(pull_url, timeout=10).text)

            if "message" in pull_request_json:
                print(f"ERROR: Pull request #{args.json_file} not found.")
                sys.exit(1)

            sha = pull_request_json["head"]["sha"]
            json_file_location = f"https://raw.githubusercontent.com/sherlock-project/sherlock/{sha}/sherlock_project/resources/data.json"

        return SitesInformation(
            data_file_path=json_file_location,
            honor_exclusions=not args.ignore_exclusions,
            do_not_exclude=args.site_list,
        )

    except Exception as error:
        print(f"ERROR: {error}")
        sys.exit(1)


def filter_sites(sites, args):
    if not args.nsfw:
        sites.remove_nsfw_sites(do_not_remove=args.site_list)

    site_data_all = {site.name: site.information for site in sites}

    if not args.site_list:
        return site_data_all

    site_data = {}
    missing = []
    lower_map = {k.lower(): k for k in site_data_all}

    for site in args.site_list:
        key = lower_map.get(site.lower())
        if key:
            site_data[key] = site_data_all[key]
        else:
            missing.append(site)

    if missing:
        print(f"Error: Desired sites not found: {', '.join(missing)}")

    if not site_data:
        sys.exit(1)

    return site_data


def expand_usernames(usernames):
    result = []
    for username in usernames:
        if check_for_parameter(username):
            result.extend(multiple_usernames(username))
        else:
            result.append(username)
    return result


def write_txt(results, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        count = 0
        for site in results:
            status = results[site].get("status")
            if status and status.status == QueryStatus.CLAIMED:
                count += 1
                file.write(results[site]["url_user"] + "\n")
        file.write(f"Total Websites Username Detected On : {count}\n")


def write_csv(results, username, file_path, args):
    with open(file_path, "w", newline="", encoding="utf-8") as csv_report:
        writer = csv.writer(csv_report)
        writer.writerow(["username","name","url_main","url_user","exists","http_status","response_time_s"])

        for site in results:
            if args.print_found and not args.print_all and results[site]["status"].status != QueryStatus.CLAIMED:
                continue

            status = results[site]["status"]
            writer.writerow([
                username,
                site,
                results[site]["url_main"],
                results[site]["url_user"],
                str(status.status),
                results[site]["http_status"],
                status.query_time or ""
            ])


def write_xlsx(results, username, args):
    usernames, names, url_main, url_user, exists, http_status, response_time_s = [], [], [], [], [], [], []

    for site in results:
        if args.print_found and not args.print_all and results[site]["status"].status != QueryStatus.CLAIMED:
            continue

        status = results[site]["status"]

        usernames.append(username)
        names.append(site)
        url_main.append(results[site]["url_main"])
        url_user.append(results[site]["url_user"])
        exists.append(str(status.status))
        http_status.append(results[site]["http_status"])
        response_time_s.append(status.query_time or "")

    df = pd.DataFrame({
        "username": usernames,
        "name": names,
        "url_main": [f'=HYPERLINK("{u}")' for u in url_main],
        "url_user": [f'=HYPERLINK("{u}")' for u in url_user],
        "exists": exists,
        "http_status": http_status,
        "response_time_s": response_time_s,
    })

    df.to_excel(f"{username}.xlsx", index=False)


def main():
    args = parse_arguments()

    signal.signal(signal.SIGINT, handler)

    check_latest_version()
    validate_output_options(args)

    if args.proxy:
        print("Using the proxy: " + args.proxy)

    init(strip=True, convert=False) if args.no_color else init(autoreset=True)

    sites = load_sites(args)
    site_data = filter_sites(sites, args)

    query_notify = QueryNotifyPrint(
        result=None,
        verbose=args.verbose,
        print_all=args.print_all,
        browse=args.browse
    )

    usernames = expand_usernames(args.username)

    for username in usernames:
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
            os.makedirs(args.folderoutput, exist_ok=True)
            result_file = os.path.join(args.folderoutput, f"{username}.txt")
        else:
            result_file = f"{username}.txt"

        if args.output_txt:
            write_txt(results, result_file)

        if args.csv:
            csv_file = f"{username}.csv"
            if args.folderoutput:
                os.makedirs(args.folderoutput, exist_ok=True)
                csv_file = os.path.join(args.folderoutput, csv_file)
            write_csv(results, username, csv_file, args)

        if args.xlsx:
            write_xlsx(results, username, args)

        print()

    query_notify.finish()


if __name__ == "__main__":
    main()
