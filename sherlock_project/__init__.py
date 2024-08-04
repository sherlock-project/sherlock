""" Sherlock Module

This module contains the main logic to search for usernames at social
networks.

"""

# This variable is only used to check for ImportErrors induced by users running as script rather than as module or package
import_error_test_var = None

__shortname__   = "Sherlock"
__longname__    = "Sherlock: Find Usernames Across Social Networks"
__version__     = "0.15.0"

forge_api_latest_release = "https://api.github.com/repos/sherlock-project/sherlock/releases/latest"
