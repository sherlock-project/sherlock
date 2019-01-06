#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""
import csv
import platform
import requests
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from colorama import Fore, Style, init

from sherlock import Sherlock

__version__ = "0.1.9"
module_name = "Sherlock: Find Usernames Across Social Networks"


def main():
    # Colorama module's initialization.
    init(autoreset=True)

    version_string = f"%(prog)s {__version__}\n" + \
                     f"{requests.__description__}:  {requests.__version__}\n" + \
                     f"Python:  {platform.python_version()}"

    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=f"{module_name} (Version {__version__})"
                            )
    parser.add_argument("--version",
                        action="version", version=version_string,
                        help="Display version information and dependencies."
                        )
    parser.add_argument("--verbose", "-v", "-d", "--debug",
                        action="store_true", dest="verbose", default=False,
                        help="Display extra debugging information."
                        )
    parser.add_argument("--quiet", "-q",
                        action="store_false", dest="verbose",
                        help="Disable debugging information (Default Option)."
                        )
    parser.add_argument("--tor", "-t",
                        action="store_true", dest="tor", default=False,
                        help="Make requests over TOR; increases runtime; requires TOR to be installed and in system "
                             "path.")
    parser.add_argument("--unique-tor", "-u",
                        action="store_true", dest="unique_tor", default=False,
                        help="Make requests over TOR with new TOR circuit after each request; increases runtime; "
                             "requires TOR to be installed and in system path.")
    parser.add_argument("--csv",
                        action="store_true", dest="csv", default=False,
                        help="Create Comma-Separated Values (CSV) File."
                        )
    parser.add_argument("username",
                        nargs='+', metavar='USERNAMES',
                        action="store",
                        help="One or more usernames to check with social networks."
                        )

    args = parser.parse_args()

    # Banner
    print(Fore.WHITE + Style.BRIGHT +
          """                                              .\"\"\"-.
                                             /      \\
 ____  _               _            _        |  _..--'-.
/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`
\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\
 ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.
|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.
                                           .'`-._ `.\    | J /
                                          /      `--.|   \\__/""")

    if args.tor or args.unique_tor:
        print("Warning: some websites might refuse connecting over TOR, so note that using this option might increase "
              "connection errors.")

    # Run report on all specified users.
    for username in args.username:
        print()
        sherlock = Sherlock(username, args.verbose)
        results = sherlock.search(args.tor, args.unique_tor)

        if args.csv:
            with open(username + ".csv", "w", newline='') as csv_report:
                writer = csv.writer(csv_report)
                writer.writerow(['username',
                                 'name',
                                 'url_main',
                                 'url_user',
                                 'exists',
                                 'http_status'
                                 ]
                                )
                for site in results:
                    writer.writerow([username,
                                     site,
                                     results[site]['url_main'],
                                     results[site]['url_user'],
                                     results[site]['exists'],
                                     results[site]['http_status']
                                     ]
                                    )


if __name__ == "__main__":
    main()
