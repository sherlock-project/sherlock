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
    def __init__(self, name, url_home, url_username_format, popularity_rank,
                 username_claimed, username_unclaimed,
                 information):
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
        popularity_rank        -- Integer indicating popularity of site.
                                  In general, smaller numbers mean more
                                  popular ("0" or None means ranking
                                  information not available).
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

        if (popularity_rank is None) or (popularity_rank == 0):
            #We do not know the popularity, so make site go to bottom of list.
            popularity_rank = sys.maxsize
        self.popularity_rank     = popularity_rank

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
            #Use internal default.
            data_file_path = \
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "resources/data.json"
                            )

        #Ensure that specified data file has correct extension.
        if ".json" != data_file_path[-5:].lower():
            raise FileNotFoundError(f"Incorrect JSON file extension for "
                                    f"data file '{data_file_path}'."
                                   )

        if ( ("http://"  == data_file_path[:7].lower()) or
             ("https://" == data_file_path[:8].lower())
           ):
            #Reference is to a URL.
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
                #If popularity unknown, make site be at bottom of list.
                popularity_rank = site_data[site_name].get("rank", sys.maxsize)

                self.sites[site_name] = \
                    SiteInformation(site_name,
                                    site_data[site_name]["urlMain"],
                                    site_data[site_name]["url"],
                                    popularity_rank,
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

    def site_name_list(self, popularity_rank=False):
        """Get Site Name List.

        Keyword Arguments:
        self                   -- This object.
        popularity_rank        -- Boolean indicating if list should be sorted
                                  by popularity rank.
                                  Default value is False.
                                  NOTE:  List is sorted in ascending
                                         alphabetical order is popularity rank
                                         is not requested.

        Return Value:
        List of strings containing names of sites.
        """

        if popularity_rank:
            #Sort in ascending popularity rank order.
            site_rank_name = \
                sorted([(site.popularity_rank,site.name) for site in self],
                       key=operator.itemgetter(0)
                      )
            site_names = [name for _,name in site_rank_name]
        else:
            #Sort in ascending alphabetical order.
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
