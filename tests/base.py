"""Sherlock Base Tests

This module contains various utilities for running tests.
"""
import json
import os
import os.path
import unittest
import sherlock
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

        # Load the data file with all site information.
        data_file_path = os.path.join(os.path.dirname(os.path.realpath(sherlock.__file__)), "data.json")
        with open(data_file_path, "r", encoding="utf-8") as raw:
            self.site_data_all = json.load(raw)

        self.verbose=False
        self.tor=False
        self.unique_tor=False

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
            check_type_text = "exists"
            exist_result_desired = "yes"
        else:
            check_type_text = "does not exist"
            exist_result_desired = "no"

        for username in username_list:
            results = sherlock.sherlock(username,
                                        site_data,
                                        verbose=self.verbose,
                                        tor=self.tor,
                                        unique_tor=self.unique_tor
                                       )
            for site, result in results.items():
                with self.subTest(f"Checking Username '{username}' "
                                  f"{check_type_text} on Site '{site}'"
                                 ):
                    self.assertEqual(result['exists'], exist_result_desired)

        return
