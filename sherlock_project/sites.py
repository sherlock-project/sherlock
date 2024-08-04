"""Sherlock Sites Information Module

This module supports storing information about websites.
This is the raw data that will be used to search for usernames.
"""
import json
import requests
import secrets

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

        if not data_file_path:
            # The default data file is the live data.json which is in the GitHub repo. The reason why we are using
            # this instead of the local one is so that the user has the most up-to-date data. This prevents
            # users from creating issue about false positives which has already been fixed or having outdated data
            data_file_path = "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.json"

        # Ensure that specified data file has correct extension.
        if not data_file_path.lower().endswith(".json"):
            raise FileNotFoundError(f"Incorrect JSON file extension for data file '{data_file_path}'.")

        # if "http://"  == data_file_path[:7].lower() or "https://" == data_file_path[:8].lower():
        if data_file_path.lower().startswith("http"):
            # Reference is to a URL.
            try:
                response = requests.get(url=data_file_path)
            except Exception as error:
                raise FileNotFoundError(
                    f"Problem while attempting to access data file URL '{data_file_path}':  {error}"
                )

            if response.status_code != 200:
                raise FileNotFoundError(f"Bad response while accessing "
                                        f"data file URL '{data_file_path}'."
                                        )
            try:
                site_data = response.json()
            except Exception as error:
                raise ValueError(
                    f"Problem parsing json contents at '{data_file_path}':  {error}."
                )

        else:
            # Reference is to a file.
            try:
                with open(data_file_path, "r", encoding="utf-8") as file:
                    try:
                        site_data = json.load(file)
                    except Exception as error:
                        raise ValueError(
                            f"Problem parsing json contents at '{data_file_path}':  {error}."
                        )

            except FileNotFoundError:
                raise FileNotFoundError(f"Problem while attempting to access "
                                        f"data file '{data_file_path}'."
                                        )
        
        site_data.pop('$schema', None)

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
            except TypeError:
                print(f"Encountered TypeError parsing json contents for target '{site_name}' at {data_file_path}\nSkipping target.\n")

        return

    def remove_nsfw_sites(self, do_not_remove: list = []):
        """
        Remove NSFW sites from the sites, if isNSFW flag is true for site

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        None
        """
        sites = {}
        do_not_remove = [site.casefold() for site in do_not_remove]
        for site in self.sites:
            if self.sites[site].is_nsfw and site.casefold() not in do_not_remove:
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
