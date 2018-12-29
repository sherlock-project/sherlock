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
from torrequest import TorRequest

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


def make_request(url, headers, error_type, social_network, verbose=False, tor=False):
    r = TorRequest() if tor else requests
    try:
        r = r.get(url, headers=headers)
        if r.status_code:
            return r, error_type
    except requests.exceptions.HTTPError as errh:
        print_error(errh, "HTTP Error:", social_network, verbose)
    except requests.exceptions.ConnectionError as errc:
        print_error(errc, "Error Connecting:", social_network, verbose)
    except requests.exceptions.Timeout as errt:
        print_error(errt, "Timeout Error:", social_network, verbose)
    except requests.exceptions.RequestException as err:
        print_error(err, "Unknown error:", social_network, verbose)
    return None, ""


def sherlock(username, verbose=False, tor=False):
    fname = username+".txt"

    if os.path.isfile(fname):
    	os.remove(fname)
    	print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Removing previous file:\033[1;37m {}\033[0m".format(fname))

    print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Checking username\033[0m\033[1;37m {}\033[0m\033[1;92m on: \033[0m".format(username))
    raw = open("data.json", "r", encoding="utf-8")
    data = json.load(raw)

    # User agent is needed because some sites does not
    # return the correct information because it thinks that
    # we are bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
    }

    for social_network in data:
        url = data.get(social_network).get("url").format(username)
        error_type = data.get(social_network).get("errorType")
        regex_check = data.get(social_network).get("regexCheck")

        if regex_check and re.search(regex_check, username) is None:
            #No need to do the check at the site: this user name is not allowed.
            print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Illegal Username Format For This Site!".format(social_network))
            continue

        r, error_type = make_request(url=url, headers=headers, error_type=error_type, social_network=social_network, verbose=verbose, tor=tor)

        if error_type == "message":
            error = data.get(social_network).get("errorMsg")
            # Checks if the error message is in the HTML
            if not error in r.text:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)

            else:
            	print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

        elif error_type == "status_code":
            # Checks if the status code of the repsonse is 404
            if not r.status_code == 404:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)

            else:
            	print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

        elif error_type == "response_url":
            error = data.get(social_network).get("errorUrl")
            # Checks if the redirect url is the same as the one defined in data.json
            if not error in r.url:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)
            else:
            	print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

        elif error_type == "":
            print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Error!".format(social_network))

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
    parser.add_argument("--tor", "-t",
                        action="store_true", dest="tor", default=False,
                        help="Make requests over TOR; requires TOR to be installed and in system path.")
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

    if args.tor:
        print("Warning: some websites might refuse connecting over TOR, so note that using this option might increase connection errors.")

    # Run report on     all specified users.
    for username in args.username:
        print()
        sherlock(username, verbose=args.verbose, tor=args.tor)



if __name__ == "__main__":
    main()