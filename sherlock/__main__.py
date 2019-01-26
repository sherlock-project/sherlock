# ==================== Imports ==================== #
import platform
import requests
import json
import csv
from time import time
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from colorama import init, Fore, Style

import constants
from sherlock import Sherlock
import watson


# ==================== Main ==================== #
if __name__ == "__main__":
    # Colorama module's initialization.
    init(autoreset=True)

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
    parser.add_argument("--output", "-o", dest="output",
                        help="If using single username, the output of the result will be saved at this file."
                        )

    args = parser.parse_args()

    print(Fore.WHITE + Style.BRIGHT + constants.__banner__)

    if args.verbose:
        print(constants.__version__)

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

    # Run report on all specified users.
    for username in args.username:
        print()
        print((Style.BRIGHT + Fore.GREEN + "[" +
            Fore.YELLOW + "*" +
            Fore.GREEN + "] Checking username" +
            Fore.WHITE + " {}" +
            Fore.GREEN + " on sites {}").format(username, ' '.join(args.site_list) if args.site_list is not None else ''))

        loader = watson.Loader().start_loader()
        
        results = {}
        sherlock = Sherlock(username)
        results = sherlock.check(args.site_list, verbose=args.verbose,
                           tor=args.tor, unique_tor=args.unique_tor, proxy=args.proxy)

        loader.stop_loader()

        for social_network, result in results.items():
            if result['exists'] == 'yes':
                watson.print_found(social_network, result['url_user'], result['response_time_ms'], args.verbose)
            elif result['exists'] == 'no':
                watson.print_not_found(social_network, result['response_time_ms'], args.verbose)
            elif result['exists'] == 'error':
                print((Style.BRIGHT + Fore.WHITE + "[" +
                    Fore.RED + "-" +
                    Fore.WHITE + "]" +
                    Fore.GREEN + " {}:" +
                    Fore.YELLOW + " Error!").format(social_network))

        if args.output:
            file = open(args.output, "w", encoding="utf-8")
            exists_counter = 0
            for website_name in results:
                dictionary = results[website_name]
                if dictionary.get("exists") == "yes":
                    exists_counter += 1
                    file.write(dictionary["url_user"] + "\n")
            file.write("Total Websites : {}".format(exists_counter))
            file.close()

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
