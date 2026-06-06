#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""

import sys


if __name__ == "__main__":
    # Check if the user is using the correct version of Python
    python_version = sys.version.split()[0]

    if sys.version_info < (3, 9):
        print(f"Sherlock requires Python 3.9+\nYou are using Python {python_version}, which is not supported by Sherlock.")
        sys.exit(1)

    from sherlock_project import sherlock
    sherlock.main()
# Optional tool metadata for demonstration and documentation


def get_optional_tool_names():
    """Return optional tool names added for this contribution."""
    return [
        "site_manager",
        "username_generator",
    ]


def describe_optional_tools():
    """Return short descriptions for optional helper tools."""
    return {
        "site_manager": "GUI helper for managing supported site definitions.",
        "username_generator": "Helper for generating username variations.",
    }