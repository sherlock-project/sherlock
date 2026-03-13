#! /usr/bin/env python3

"""
Sherlock: Site data loading and filtering utilities
"""

import os
import sys
from json import loads as json_loads

import requests

from ..sites import SitesInformation


def load_and_filter_sites(args):
    """Load and filter site data based on command-line arguments."""
    try:
        if args.local:
            sites = SitesInformation(os.path.join(
                os.path.dirname(__file__),
                "../resources/data.json"
            ))
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
        return site_data_all
    
    site_data = {}
    # Create a mapping from lowercase site name to original site name
    lower_to_original_site_map = {s.lower(): s for s in site_data_all}

    site_missing = []

    for site_name in args.site_list:
        lower_site_name = site_name.lower()
        if lower_site_name in lower_to_original_site_map:
            original_site_name = lower_to_original_site_map[lower_site_name]
            site_data[original_site_name] = site_data_all[original_site_name]
        else:
            site_missing.append(site_name)

    if site_missing:
        print(f"Error: Desired sites not found: {', '.join(site_missing)}.")

    if not site_data:
        sys.exit(1)

    return site_data
