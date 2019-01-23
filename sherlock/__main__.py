# ==================== Imports ==================== #
import os
import platform
import requests
import json
from time import time
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from colorama import init, Fore, Style

import constants
from sherlock import Sherlock


# ==================== Main ==================== #
if __name__ == "__main__":
    # Colorama module's initialization.
    init(autoreset=True)
    print(constants.__version__)

    version_string = f"%(prog)s {constants.__version__}\n" +  \
                     f"{requests.__description__}:  {requests.__version__}\n" + \
                     f"Python:  {platform.python_version()}"

    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=f"{__name__} (Version {constants.__version__})"
                            )
    parser.add_argument("--version",
                        action="version",  version=version_string,
                        help="Display version information and dependencies."
                        )
    parser.add_argument("--verbose", "-v", "-d", "--debug",
                        action="store_true",  dest="verbose", default=False,
                        help="Display extra debugging information and metrics."
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
    parser.add_argument("--csv",
                        action="store_true",  dest="csv", default=False,
                        help="Create Comma-Separated Values (CSV) File."
                        )
    parser.add_argument("--site",
                        action="append", metavar='SITE_NAME',
                        dest="site_list", default=None,
                        help="Limit analysis to just the listed sites.  Add multiple options to specify more than one site."
                        )
    parser.add_argument("--proxy", "-p", metavar='PROXY_URL',
                        action="store", dest="proxy", default=None,
                        help="Make requests over a proxy. e.g. socks5://127.0.0.1:1080"
                        )
    parser.add_argument("username",
                        nargs='+', metavar='USERNAMES',
                        action="store",
                        help="One or more usernames to check with social networks."
                        )

    args = parser.parse_args()

    print(Fore.WHITE + Style.BRIGHT + constants.__banner__)

    # Argument check
    # TODO regex check on args.proxy
    if args.tor and args.proxy != None:
        raise Exception("TOR and Proxy cannot be set in the meantime.")

    # Make prompts
    if args.proxy != None:
        print("Using the proxy: " + args.proxy)
    if args.tor or args.unique_tor:
        print("Using TOR to make requests")
        print("Warning: some websites might refuse connecting over TOR, so note that using this option might increase connection errors.")

    # Load the data
    data_file_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "data.json")
    with open(data_file_path, "r", encoding="utf-8") as raw:
        site_data_all = json.load(raw)

    if args.site_list is None:
        # Not desired to look at a sub-set of sites
        site_data = site_data_all
    else:
        # User desires to selectively run queries on a sub-set of the site list.

        # Make sure that the sites are supported & build up pruned site database.
        site_data = {}
        site_missing = []
        for site in args.site_list:
            for existing_site in site_data_all:
                if site.lower() == existing_site.lower():
                    site_data[existing_site] = site_data_all[existing_site]
            if not site_data:
                # Build up list of sites not supported for future error message.
                site_missing.append(f"'{site}'")

        if site_missing:
            print(
                f"Error: Desired sites not found: {', '.join(site_missing)}.")
            sys.exit(1)

    # Run report on all specified users.
    for username in args.username:
        print()
        results = {}
        sherlock = Sherlock()
        results = sherlock.run(username, site_data, verbose=args.verbose,
                           tor=args.tor, unique_tor=args.unique_tor, proxy=args.proxy)

        if args.csv == True:
            with open(username + ".csv", "w", newline='', encoding="utf-8") as csv_report:
                writer = csv.writer(csv_report)
                writer.writerow(['username',
                                 'name',
                                 'url_main',
                                 'url_user',
                                 'exists',
                                 'http_status',
                                 'response_time_ms'
                                 ]
                                )
                for site in results:
                    writer.writerow([username,
                                     site,
                                     results[site]['url_main'],
                                     results[site]['url_user'],
                                     results[site]['exists'],
                                     results[site]['http_status'],
                                     results[site]['response_time_ms']
                                     ]
                                    )
