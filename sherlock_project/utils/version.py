#!/usr/bin/env python3

"""
Sherlock Version Utilities

This module contains version-related utility functions for the Sherlock project.
"""

import requests
from json import loads as json_loads
from sherlock_project.__init__ import __version__, forge_api_latest_release

def check_for_updates():
    """Check for a new version of Sherlock."""
    try:
        latest_release_raw = requests.get(forge_api_latest_release).text
        latest_release_json = json_loads(latest_release_raw)
        latest_remote_tag = latest_release_json["tag_name"]

        if latest_remote_tag[1:] != __version__:
            print(
                f"Update available! {__version__} --> {latest_remote_tag[1:]}"
                f"\n{latest_release_json['html_url']}"
            )

    except Exception as error:
        print(f"A problem occurred while checking for an update: {error}")
