#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""

import sys


if __name__ == "__main__":
    # Checking if the user is using the correct version of Python
    # Reference:
    #  If Python version is 3.6.5
    #               major --^
    #               minor ----^
    #               micro ------^
    major = sys.version_info[0]
    minor = sys.version_info[1]

    python_version = str(sys.version_info[0])+"."+str(sys.version_info[1])+"."+str(sys.version_info[2])

    if major != 3 or major == 3 and minor < 6:
        print("Sherlock requires Python 3.6+\nYou are using Python %s, which is not supported by Sherlock" % (python_version))
        sys.exit(1)

    import sherlock
    sherlock.main()
