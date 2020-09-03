"""Sherlock Sites Information Module

This module supports storing information about web sites.
This is the raw data that will be used to search for usernames.
"""
import os
import json
import operator
import requests
import sys


class SiteInformation():
    def __init__(self, name, url_home, url_username_format, username_claimed,
                 username_unclaimed, information):
        """Create Site Information Object.

        Contains information about a specific web site.

        Keyword Arguments:
        self                   -- This object.
        name                   -- String which identifies site.
        url_home               -- String containing URL for home of site.
        url_username_format    -- String containing URL for Username format
                                  on site.
                                  NOTE:  The string should contain the
                                         token "{}" where the username should
                                         be substituted.  For example, a string
                                         of "https://somesite.com/users/{}"
                                         indicates that the individual
                                         usernames would show up under the
                                         "https://somesite.com/users/" area of
                                         the web site.
        username_claimed       -- String containing username which is known
                                  to be claimed on web site.
        username_unclaimed     -- String containing username which is known
                                  to be unclaimed on web site.
        information            -- Dictionary containing all known information
                                  about web site.
                                  NOTE:  Custom information about how to
                                         actually detect the existence of the
                                         username will be included in this
                                         dictionary.  This information will
                                         be needed by the detection method,
                                         but it is only recorded in this
                                         object for future use.

        Return Value:
        Nothing.
        """

        self.name                = name
        self.url_home            = url_home
        self.url_username_format = url_username_format

        self.username_claimed    = username_claimed
        self.username_unclaimed  = username_unclaimed
        self.information         = information

        return

    def __str__(self):
        """Convert Object To String.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nicely formatted string to get information about this object.
        """

        return f"{self.name} ({self.url_home})"


class SitesInformation():
    def __init__(self, data_file_path=None):
        """Create Sites Information Object.

        Contains information about all supported web sites.

        Keyword Arguments:
        self                   -- This object.
        data_file_path         -- String which indicates path to data file.
                                  The file name must end in ".json".

                                  There are 3 possible formats:
                                   * Absolute File Format
                                     For example, "c:/stuff/data.json".
                                   * Relative File Format
                                     The current working directory is used
                                     as the context.
                                     For example, "data.json".
                                   * URL Format
                                     For example,
                                     "https://example.com/data.json", or
                                     "http://example.com/data.json".

                                  An exception will be thrown if the path
                                  to the data file is not in the expected
                                  format, or if there was any problem loading
                                  the file.

                                  If this option is not specified, then a
                                  default site list will be used.

        Return Value:
        Nothing.
        """

        if data_file_path is None:
            # The default data file is the live data.json which is in the GitHub repo. The reason why we are using
            # this instead of the local one is so that the user has the most up to date data. This prevents
            # users from creating issue about false positives which has already been fixed or having outdated data
            data_file_path = "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock/resources/data.json"

        # Ensure that specified data file has correct extension.
        if not data_file_path.lower().endswith(".json"):
            raise FileNotFoundError(f"Incorrect JSON file extension for "
                                    f"data file '{data_file_path}'."
                                   )

        if "http://"  == data_file_path[:7].lower() or "https://" == data_file_path[:8].lower():
            # Reference is to a URL.
            try:
                response = requests.get(url=data_file_path)
            except Exception as error:
                raise FileNotFoundError(f"Problem while attempting to access "
                                        f"data file URL '{data_file_path}':  "
                                        f"{str(error)}"
                                       )
            if response.status_code == 200:
                try:
                    site_data = response.json()
                except Exception as error:
                    raise ValueError(f"Problem parsing json contents at "
                                     f"'{data_file_path}':  {str(error)}."
                                    )
            else:
                raise FileNotFoundError(f"Bad response while accessing "
                                        f"data file URL '{data_file_path}'."
                                       )
        else:
            #Reference is to a file.
            try:
                with open(data_file_path, "r", encoding="utf-8") as file:
                    try:
                        site_data = json.load(file)
                    except Exception as error:
                        raise ValueError(f"Problem parsing json contents at "
                                         f"'{data_file_path}':  {str(error)}."
                                        )
            except FileNotFoundError as error:
                raise FileNotFoundError(f"Problem while attempting to access "
                                        f"data file '{data_file_path}'."
                                       )

        self.sites = {}

        #Add all of site information from the json file to internal site list.
        for site_name in site_data:
            try:

                self.sites[site_name] = \
                    SiteInformation(site_name,
                                    site_data[site_name]["urlMain"],
                                    site_data[site_name]["url"],
                                    site_data[site_name]["username_claimed"],
                                    site_data[site_name]["username_unclaimed"],
                                    site_data[site_name]
                                   )
            except KeyError as error:
                raise ValueError(f"Problem parsing json contents at "
                                 f"'{data_file_path}':  "
                                 f"Missing attribute {str(error)}."
                                )

        return

    def site_name_list(self):
        """Get Site Name List.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        List of strings containing names of sites.
        """

        site_names = sorted([site.name for site in self], key=str.lower)

        return site_names

    def __iter__(self):
        """Iterator For Object.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Iterator for sites object.
        """

        for site_name in self.sites:
            yield self.sites[site_name]

    def __len__(self):
        """Length For Object.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Length of sites object.
        """
        return len(self.sites)
