"""Sherlock Sites Information Module

This module supports storing information about websites.
This is the raw data that will be used to search for usernames.
"""
import json
import secrets
import sys

import requests
from colorama import Fore, Style, init
from requests.exceptions import Timeout
from tqdm import tqdm


class SiteInformation:
    def __init__(self, name, url_home, url_username_format, username_claimed,
                information, is_nsfw, username_unclaimed=secrets.token_urlsafe(10)):
        """Create Site Information Object.

        Contains information about a specific website.

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
                                         the website.
        username_claimed       -- String containing username which is known
                                  to be claimed on website.
        username_unclaimed     -- String containing username which is known
                                  to be unclaimed on website.
        information            -- Dictionary containing all known information
                                  about website.
                                  NOTE:  Custom information about how to
                                         actually detect the existence of the
                                         username will be included in this
                                         dictionary.  This information will
                                         be needed by the detection method,
                                         but it is only recorded in this
                                         object for future use.
        is_nsfw                -- Boolean indicating if site is Not Safe For Work.

        Return Value:
        Nothing.
        """

        self.name = name
        self.url_home = url_home
        self.url_username_format = url_username_format

        self.username_claimed = username_claimed
        self.username_unclaimed = secrets.token_urlsafe(32)
        self.information = information
        self.is_nsfw  = is_nsfw

        return

    def __str__(self):
        """Convert Object To String.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nicely formatted string to get information about this object.
        """
        
        return f"{self.name} ({self.url_home})"


class SitesInformation:
    def __init__(self, data_file_path=None):
        """Create Sites Information Object.

        Contains information about all supported websites.

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
        init(autoreset=True)
        # sys.stdout.write("Loading...")
        # sys.stdout.flush() 
        data_file_url = data_file_path if data_file_path else "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock/resources/data.json"

        try:
            response = None

            # Attempt to fetch data from the specified URL
            if data_file_url.lower().startswith("http"):
                sys.stdout.write(Fore.YELLOW + "\rEstablishing connection to data file URL...")
                sys.stdout.flush()
                try:
                    response = requests.get(url=data_file_url, timeout=10)
                    response.raise_for_status()  # Raise an exception for non-200 responses
                except Timeout:
                    sys.stdout.write(Fore.RED + "\rConnection timed out. Please check your internet connection.")
                    sys.stdout.flush()
                except requests.exceptions.RequestException as error:
                    sys.stdout.write(Fore.RED + "\rAn error occurred while fetching data from URL: " + str(error))
                    sys.stdout.flush()

            if response and response.status_code == 200:
                site_data = response.json()
            else:
                sys.stdout.write(Fore.YELLOW + "\rFalling back to the local data file...")
                sys.stdout.flush()
                data_file_path = "sherlock/resources/data.json"
                with open(data_file_path, "r", encoding="utf-8") as file:
                    site_data = json.load(file)
        except Exception as error:
            sys.stdout.write(Fore.RED + "\rAn error occurred while loading data: " + str(error))
            sys.stdout.flush()
            site_data = None


        if not site_data:
            raise ValueError("Failed to load site data.")

        # Clear the previous message by overwriting it with spaces
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.flush()

        self.sites = {}
        # Add all site information from the json file to internal site list.
        for site_name in site_data:
            try:

                self.sites[site_name] = \
                    SiteInformation(site_name,
                                    site_data[site_name]["urlMain"],
                                    site_data[site_name]["url"],
                                    site_data[site_name]["username_claimed"],
                                    site_data[site_name],
                                    site_data[site_name].get("isNSFW",False)

                                    )
            except KeyError as error:
                raise ValueError(
                    f"Problem parsing json contents at '{data_file_path}':  Missing attribute {error}."
                )

        return

    def remove_nsfw_sites(self):
        """
        Remove NSFW sites from the sites, if isNSFW flag is true for site

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        None
        """
        sites = {}
        for site in self.sites:
            if self.sites[site].is_nsfw:
                continue
            sites[site] = self.sites[site]  
        self.sites =  sites

    def site_name_list(self):
        """Get Site Name List.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        List of strings containing names of sites.
        """

        return sorted([site.name for site in self], key=str.lower)

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
