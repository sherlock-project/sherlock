#! /usr/bin/env python3
"""
Sherlock Test: Test Finding Of Usernames Across Social Networks Module

This module contains test code to ensure that the finding logic works.
"""
import csv
import json
import os
import platform
import logging
import requests
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from colorama import Back, Fore, Style, init
import sherlock

module_name = "Sherlock Test: Test Finding Of Usernames Across Social Networks"
__version__ = "0.1.0"



def sherlock_test(username_exist_list, username_unknown_list, site_data_all, verbose=False, tor=False, unique_tor=False):
    """Run Test On Sherlock Analysis.

    Tests checks for existence of username on various social media sites.

    Keyword Arguments:
    username_exist_list    -- List of strings indicating usernames that should
                              exist in all of the specified sites.
    username_unknown_list  -- List of strings indicating usernames that should
                              not exist in all of the specified sites.
    site_data_all          -- Dictionary containing all of the site data.
    verbose                -- Boolean indicating whether to give verbose output.
    tor                    -- Boolean indicating whether to use a tor circuit for the requests.
    unique_tor             -- Boolean indicating whether to use a new tor circuit for each request.

    Return Value:
    Boolean indicating if tests succeeded.
    """

    tests_succeeded = True

    #Run test to ensure that usernames which exist are detected to exist.
    for username in username_exist_list:
        results = sherlock.sherlock(username,
                                    site_data_all,
                                    verbose=verbose,
                                    tor=tor,
                                    unique_tor=unique_tor
                                   )
        for social_network, result in results.items():
            if result['exists'] == "yes":
                 logging.info(f"Username '{username}' detected "
                              f"on {social_network}."
                             )
            else:
                 #At least one test failed.
                 tests_succeeded = False
                 logging.error(f"Username '{username}' not detected "
                               f"on {social_network}."
                              )

    #Run test to ensure that usernames which do not exist are detected to
    #not exist.
    for username in username_unknown_list:
        results = sherlock.sherlock(username,
                                    site_data_all,
                                    verbose=verbose,
                                    tor=tor,
                                    unique_tor=unique_tor
                                   )
        for social_network, result in results.items():
            if result['exists'] == "no":
                 logging.info(f"Username '{username}' not detected "
                              f"on {social_network}."
                             )
            else:
                 #At least one test failed.
                 tests_succeeded = False
                 logging.error(f"Username '{username}' detected "
                               f"on {social_network}."
                              )

    return tests_succeeded


def main():
    # Colorama module's initialization.
    init(autoreset=True)

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
                        help="Make requests over TOR; increases runtime; requires TOR to be installed and in system path.")
    parser.add_argument("--unique-tor", "-u",
                        action="store_true", dest="unique_tor", default=False,
                        help="Make requests over TOR with new TOR circuit after each request; increases runtime; requires TOR to be installed and in system path.")

    args = parser.parse_args()

    # Load the data
    data_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.json")
    with open(data_file_path, "r", encoding="utf-8") as raw:
        site_data_all = json.load(raw)


    #Setup logging to show informational messages.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    result_summary = []
    site_data = {site: site_data_all[site]
                       for site in ['Twitter', 'eBay'] if site in site_data_all
                }
    result_summary.append(sherlock_test(['hoadlck'],
                                        ['hoadlckblah'],
                                        site_data,
                                        args.verbose,
                                        args.tor,
                                        args.unique_tor
                                       )
                         )

    if all(result_summary):
        logging.info(f"All tests succeeded!")
    else:
        logging.error(f"One of more tests failed!")

    return


if __name__ == "__main__":
    main()
