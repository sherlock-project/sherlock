#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
"""

import sys
# Append sherlock to path
# Considering that we're running the application from __main__
# we could face importing problem (relative import)
sys.path.insert(0, "../sherlock")


if __name__ == "__main__":
    # Check if the user is using the correct version of Python
    from sherlock import sherlock

    
    python_version = sys.version.split()[0]

    if sys.version_info < (3, 6):
        print("Sherlock requires Python 3.6+\nYou are using Python %s, which is not supported by Sherlock" % (python_version))
        sys.exit(1)

    sherlock.main()
