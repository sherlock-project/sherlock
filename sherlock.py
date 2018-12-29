#!/usr/bin/env python3.6
"""Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""
import requests
import json
import os
import sys
import re
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import platform


module_name = "Sherlock: Find Usernames Across Social Networks"
__version__ = "0.1.0"


# TODO: fix tumblr

def write_to_file(url, fname):
    with open(fname, "a") as f:
        f.write(url+"\n")


def print_error(err, errstr, var, debug = False):
    if debug:
        print(f"\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m {errstr}\033[93;1m {err}")
    else:
        print(f"\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m {errstr}\033[93;1m {var}")


def make_request(url, headers, error_type, social_network, verbose=False):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code:
            return r
    except requests.exceptions.HTTPError as errh:
        print_error(errh, "HTTP Error:", social_network, verbose)
    except requests.exceptions.ConnectionError as errc:
        print_error(errc, "Error Connecting:", social_network, verbose)
    except requests.exceptions.Timeout as errt:
        print_error(errt, "Timeout Error:", social_network, verbose)
    except requests.exceptions.RequestException as err:
        print_error(err, "Unknown error:", social_network, verbose)
    return None


def get_social_network_result(username, headers, social_network, info, verbose =
        False):
    _result = {}
    _result["username"] = username
    _result["social_network"] = social_network
    _result["success"] = False
    _result["url"] = info["url"].format(username)
    error_type = info["errorType"]

    if "regexCheck" in info:
        if re.search(info["regexCheck"], username) is None:
            # No need to do the check at the site: this user name is not allowed.
            _result["success"] = False
            _result["url"] = "Illegal Username Format For This Site!"
            return _result

    r = make_request(_result["url"], headers, error_type, social_network, verbose)

    if error_type == "message" and r:
        error = info["errorMsg"]
        # Checks if the error message is in the HTML
        if not error in r.text:
            _result["success"] = True
        else:
            _result["success"] = False
            _result["url"] = ""
    elif error_type == "status_code" and r:
        # Checks if the status code of the repsonse is 404
        if not r.status_code == 404:
            _result["success"] = True
        else:
            _result["success"] = False
            _result["url"] = ""
    elif error_type == "response_url" and r:
        error = info["errorUrl"]
        # Checks if the redirect url is the same as the one defined in data.json
        if not error in r.url:
            _result["success"] = True
        else:
            _result["success"] = False
            _result["url"] = ""
    elif not r:
        _result["success"] = False
        _result["url"] = "Error"

    return _result


def get_username_results(username, verbose = False):
    with open("data.json", "r", encoding="utf-8") as raw:
        data = json.load(raw)

    # User agent is needed because some sites does not
    # return the correct information because it thinks that
    # we are bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
    }

    for social_network, info in data.items():
        yield get_social_network_result(username, headers, social_network, info, verbose)


def sherlock(username, verbose=False):
    fname = username+".txt"

    if os.path.isfile(fname):
        os.remove(fname)
        print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Removing previous file:\033[1;37m {}\033[0m".format(fname))

    print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Checking username\033[0m\033[1;37m {}\033[0m\033[1;92m on: \033[0m".format(username))

    for result in get_username_results(username, verbose):
        if result["success"]:
            print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".
                  format(result["social_network"]), result["url"])
            write_to_file(result["url"], fname)
        elif not "http" in result["url"]:
            print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".
                  format(result["social_network"]), result["url"])
        else:
            print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".
                  format(result["social_network"]))

    print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Saved: \033[37;1m{}\033[0m".format(username+".txt"))

    return


def main():
    version_string = f"%(prog)s {__version__}\n" +  \
                     f"{requests.__description__}:  {requests.__version__}\n" + \
                     f"Python:  {platform.python_version()}"

    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=f"{module_name} (Version {__version__})"
                           )
    parser.add_argument("--version",
                        action="version",  version=version_string,
                        help="Display version information and dependencies."
                       )
    parser.add_argument("--verbose", "-v", "-d", "--debug",
                        action="store_true",  dest="verbose", default=False,
                        help="Display extra debugging information."
                       )
    parser.add_argument("--quiet", "-q",
                        action="store_false", dest="verbose",
                        help="Disable debugging information (Default Option)."
                       )
    parser.add_argument("--input", "-i",
                        action="store", dest="input", default="",
                        help="Input CSV file with one or more usernames to check with social networks."
                       )
    parser.add_argument("--output", "-o",
                        action="store", dest="output", default="",
                        help="Output CSV file with one or more usernames to check with social networks."
                       )
    parser.add_argument("username",
                        nargs='+', metavar='USERNAMES',
                        action="store",
                        help="One or more usernames to check with social networks."
                       )

    args = parser.parse_args()

    # Banner
    print(
"""\033[37;1m                                              .\"\"\"-.
\033[37;1m                                             /      \\
\033[37;1m ____  _               _            _        |  _..--'-.
\033[37;1m/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`
\033[37;1m\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\
\033[37;1m ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.
\033[37;1m|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.
\033[37;1m                                           .'`-._ `.\    | J /
\033[37;1m                                          /      `--.|   \__/\033[0m""")

    # Run report on all specified users.
    for username in args.username:
        print()
        sherlock(username, verbose=args.verbose)



if __name__ == "__main__":
    main()
