"""Sherlock Base Tests

This module contains various utilities for running tests.
"""
import os
import os.path
import unittest
import sherlock
from result import QueryStatus
from result import QueryResult
from notify import QueryNotify
from sites  import SitesInformation
import warnings


class SherlockBaseTest(unittest.TestCase):
    def setUp(self):
        """Sherlock Base Test Setup.

        Does common setup tasks for base Sherlock tests.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        N/A.
        """

        #This ignores the ResourceWarning from an unclosed SSLSocket.
        #TODO: Figure out how to fix the code so this is not needed.
        warnings.simplefilter("ignore", ResourceWarning)

        #Create object with all information about sites we are aware of.
        sites = SitesInformation()

        #Create original dictionary from SitesInformation() object.
        #Eventually, the rest of the code will be updated to use the new object
        #directly, but this will glue the two pieces together.
        site_data_all = {}
        for site in sites:
            site_data_all[site.name] = site.information
        self.site_data_all = site_data_all

        # Load excluded sites list, if any
        excluded_sites_path = os.path.join(os.path.dirname(os.path.realpath(sherlock.__file__)), "tests/.excluded_sites")
        try:
          with open(excluded_sites_path, "r", encoding="utf-8") as excluded_sites_file:
            self.excluded_sites = excluded_sites_file.read().splitlines()
        except FileNotFoundError:
          self.excluded_sites = []

        #Create notify object for query results.
        self.query_notify = QueryNotify()

        self.tor=False
        self.unique_tor=False
        self.timeout=None
        self.skip_error_sites=True

        return

    def site_data_filter(self, site_list):
        """Filter Site Data.

        Keyword Arguments:
        self                   -- This object.
        site_list              -- List of strings corresponding to sites which
                                  should be filtered.

        Return Value:
        Dictionary containing sub-set of site data specified by 'site_list'.
        """

        # Create new dictionary that has filtered site data based on input.
        # Note that any site specified which is not understood will generate
        # an error.
        site_data = {}
        for site in site_list:
            with self.subTest(f"Checking test vector Site '{site}' "
                              f"exists in total site data."
                             ):
                site_data[site] = self.site_data_all[site]

        return site_data

    def username_check(self, username_list, site_list, exist_check=True):
        """Username Exist Check.

        Keyword Arguments:
        self                   -- This object.
        username_list          -- List of strings corresponding to usernames
                                  which should exist on *all* of the sites.
        site_list              -- List of strings corresponding to sites which
                                  should be filtered.
        exist_check            -- Boolean which indicates if this should be
                                  a check for Username existence,
                                  or non-existence.

        Return Value:
        N/A.
        Will trigger an assert if Username does not have the expected
        existence state.
        """

        #Filter all site data down to just what is needed for this test.
        site_data = self.site_data_filter(site_list)

        if exist_check:
            check_type_text = "claimed"
            exist_result_desired = QueryStatus.CLAIMED
        else:
            check_type_text = "available"
            exist_result_desired = QueryStatus.AVAILABLE

        for username in username_list:
            results = sherlock.sherlock(username,
                                        site_data,
                                        self.query_notify,
                                        tor=self.tor,
                                        unique_tor=self.unique_tor,
                                        timeout=self.timeout
                                       )
            for site, result in results.items():
                with self.subTest(f"Checking Username '{username}' "
                                  f"{check_type_text} on Site '{site}'"
                                 ):
                    if (
                         (self.skip_error_sites == True) and
                         (result['status'].status == QueryStatus.UNKNOWN)
                       ):
                        #Some error connecting to site.
                        self.skipTest(f"Skipping Username '{username}' "
                                      f"{check_type_text} on Site '{site}':  "
                                      f"Site returned error status."
                                     )

                    self.assertEqual(exist_result_desired,
                                     result['status'].status)

        return

    def detect_type_check(self, detect_type, exist_check=True):
        """Username Exist Check.

        Keyword Arguments:
        self                   -- This object.
        detect_type            -- String corresponding to detection algorithm
                                  which is desired to be tested.
                                  Note that only sites which have documented
                                  usernames which exist and do not exist
                                  will be tested.
        exist_check            -- Boolean which indicates if this should be
                                  a check for Username existence,
                                  or non-existence.

        Return Value:
        N/A.
        Runs tests on all sites using the indicated detection algorithm
        and which also has test vectors specified.
        Will trigger an assert if Username does not have the expected
        existence state.
        """

        #Dictionary of sites that should be tested for having a username.
        #This will allow us to test sites with a common username in parallel.
        sites_by_username = {}

        for site, site_data in self.site_data_all.items():
            if (
                 (site in self.excluded_sites)                 or
                 (site_data["errorType"] != detect_type)       or
                 (site_data.get("username_claimed")   is None) or
                 (site_data.get("username_unclaimed") is None)
               ):
                # This is either not a site we are interested in, or the
                # site does not contain the required information to do
                # the tests.
                pass
            else:
                # We should run a test on this site.

                # Figure out which type of user
                if exist_check:
                     username = site_data.get("username_claimed")
                else:
                     username = site_data.get("username_unclaimed")

                # Add this site to the list of sites corresponding to this
                # username.
                if username in sites_by_username:
                    sites_by_username[username].append(site)
                else:
                    sites_by_username[username] = [site]

        # Check on the username availability against all of the sites.
        for username, site_list in sites_by_username.items():
            self.username_check([username],
                                site_list,
                                exist_check=exist_check
                               )

        return

    def coverage_total_check(self):
        """Total Coverage Check.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        N/A.
        Counts up all Sites with full test data available.
        Will trigger an assert if any Site does not have test coverage.
        """

        site_no_tests_list = []

        for site, site_data in self.site_data_all.items():
            if (
                 (site_data.get("username_claimed")   is None) or
                 (site_data.get("username_unclaimed") is None)
               ):
                # Test information not available on this site.
                site_no_tests_list.append(site)

        self.assertEqual("", ", ".join(site_no_tests_list))

        return
