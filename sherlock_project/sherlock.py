#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social networks.
"""

import sys
import signal
import asyncio
from json import loads as json_loads
from concurrent.futures import as_completed

from colorama import init

# Local imports
from .utils.text import (
    check_for_parameter,
    multiple_usernames,
)
from .utils.cli import get_parser
from .utils.output import (
    write_text_file,
    write_csv_file,
    write_xlsx_file,
    get_output_file_path,
)
from .utils.version import check_for_updates
from .notify import QueryNotifyPrint
from .utils.sites import load_and_filter_sites
from .workers.search import search_username

# Check for proper import structure
try:
    from .__init__ import import_error_test_var  # noqa: F401
except ImportError:
    print("Did you run Sherlock with `python3 sherlock/sherlock.py ...`?")
    print("Please see https://sherlock-project.github.io/sherlock/ for installation instructions.")
    sys.exit(1)


def handler(signal_received, frame):
    """Handle Ctrl+C gracefully"""
    print("\nKeyboardInterrupt detected. Exiting...")
    sys.exit(0)


async def main():
    """Main entry point for the Sherlock CLI."""
    parser = get_parser()
    args = parser.parse_args()

    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handler)

    # Check for updates
    check_for_updates()

    # Validate arguments
    if args.tor and args.proxy:
        print("Error: Cannot use both Tor and proxy at the same time.")
        sys.exit(1)

    if args.output and len(args.username) > 1:
        print("Error: --output can only be used with a single username")
        sys.exit(1)

    # Initialize color output
    init(autoreset=True, strip=args.no_color)

    # Load and filter site data
    site_data = load_and_filter_sites(args)

    # Set up notification system
    query_notify = QueryNotifyPrint(
        result=None,
        verbose=args.verbose,
        print_all=args.print_all,
        browse=args.browse
    )

    # Process each username
    all_usernames = []
    for username in args.username:
        if check_for_parameter(username):
            all_usernames.extend(multiple_usernames(username))
        else:
            all_usernames.append(username)

    for username in all_usernames:
        results = await search_username(
            username=username,
            site_data=site_data,
            query_notify=query_notify,
            tor=args.tor,
            unique_tor=args.unique_tor,
            proxy=args.proxy,
            timeout=args.timeout
        )

        # Save results
        if not args.no_txt or args.csv or args.xlsx:
            output_path = get_output_file_path(username, args)
            
            if not args.no_txt:
                write_text_file(results, output_path)
            if args.csv:
                write_csv_file(username, results, output_path, args)
            if args.xlsx:
                write_xlsx_file(username, results, output_path, args)

    query_notify.finish()


if __name__ == "__main__":
    # Run Sherlock
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting... (Ctrl+C pressed)")
        sys.exit(0)