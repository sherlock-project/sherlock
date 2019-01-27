#! /usr/bin/env python3

'''
Sherlock: Find Usernames Across Social Networks Module

This module contains the main logic to search for usernames at social
networks.
'''

# ==================== Imports ==================== #
import os
import sys
import json
import csv
import re
from concurrent.futures import ThreadPoolExecutor
import requests
from colorama import Fore, Style, init
from torrequest import TorRequest

from watson import *

# TODO: fix tumblr


# ==================== Main ==================== #
class Sherlock:
    def __init__(self, username, index_by_original_query=False, source=os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.json")):
        '''Create an instance of Sherlock that can be used to look up usernames on social media.

        Keyword Arguments:
        username                    -- The username to look up.
        index_by_original_query     -- Index the results by original query, if false, results are indexed by the actual name of the social media site.
        source                      -- The source of the site data JSON used by Sherlock, can be a URL.
        '''
        self.results = dict()
        self.username = username
        self.indexed_by_original_query = index_by_original_query
        if source is None:
            self.source = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.json")
        else:
            self.source = source

    def __prepare_site_data(self, sites, ranked=False):
        '''Prepares a site data dictionary of all the sites that Sherlock will analyze.

        Keyword Arguments:
        sites       -- a list of sites as strings
        ranked      -- rank the sites by their alexa ranking

        Return Value:
        Dictionary containing all the site data of the given sites. This site data
        is used by Sherlock to check if the username exists at those sites.
        '''
        response_json_online = None
        # Try to load json from website.
        try:
            response_json_online = requests.get(url=self.source)
        except requests.exceptions.MissingSchema:  # In case the schema is wrong it's because it may not be a website
            pass
        
        # Check if the response is appropriate.
        if response_json_online is not None and response_json_online.status_code == 200:
            # Since we got data from a website, try to load json and exit if parsing fails.
            try:
                site_data_all = response_json_online.json()
                return site_data_all
            except ValueError:
                print(Style.BRIGHT + Fore.RED + "Invalid JSON from website!")
                Loader.stop_all()
                sys.exit(1)
                pass

        # Load the data
        data_file_path = self.source
        with open(data_file_path, "r", encoding="utf-8") as raw:
            site_data_all = json.load(raw)

        if sites is None:
            # Not desired to look at a sub-set of sites
            site_data = site_data_all
        else:
            # User desires to selectively run queries on a sub-set of the site list.
            # Make sure that the sites are supported & build up pruned site database.
            site_data = dict()
            site_missing = []
            for site in sites:
                for existing_site in site_data_all:
                    if site.lower() in existing_site.lower():
                        site_data[existing_site] = site_data_all[existing_site]
                        site_data[existing_site]['original_query'] = site
                if not site_data:
                    # Build up list of sites not supported for future error message.
                    site_missing.append(f"'{site}'")

            if site_missing:
                print(Style.BRIGHT + Fore.RED + f"Error: Desired sites not found: {', '.join(site_missing)}.")
                Loader.stop_all()
                sys.exit(1)

        if ranked:
            # Sort data by rank 
            site_dataCpy = dict(site_data)
            ranked_sites = sorted(site_data, key=lambda k: ("rank" not in k, site_data[k].get("rank", sys.maxsize)))
            site_data = {}
            for site in ranked_sites:
                site_data[site] = site_dataCpy.get(site)
        
        return site_data

    def check(self, sites, verbose=False, tor=False, unique_tor=False, proxy=None, silent_on_error=False, ranked=False):
        '''Run Sherlock Analysis.

        Checks for existence of username on various social media sites.

        Keyword Arguments:
        site_data              -- Dictionary containing all of the site data.
        verbose                -- Boolean indicating whether to give verbose output.
        tor                    -- Boolean indicating whether to use a tor circuit for the requests.
        unique_tor             -- Boolean indicating whether to use a new tor circuit for each request.
        proxy                  -- String indicating the proxy URL.
        silent_on_error        -- Will not print errors to STDOUT.
        ranked                 -- Rank the results by alexa.com rankings.

        Return Value:
        Dictionary containing results from report.  Key of dictionary is the name
        of the social network site, and the value is another dictionary with
        the following keys:
            url_main:      URL of main site.
            url_user:      URL of user on site (if account exists).
            exists:        String indicating results of test for account existence.
            http_status:   HTTP status code of query which checked for existence on
                        site.
            response_text: Text that came back from request.  May be None if
                        there was an HTTP error when checking for existence.
        '''

        # Get site data
        if isinstance(sites, str):
            sites = [sites]
        site_data = self.__prepare_site_data(sites, ranked)

        # A user agent is needed because some sites don't
        # return the correct information since they think that
        # we are bots
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
        }

        # Allow 1 thread for each external service, so `len(site_data)` threads total
        executor = ThreadPoolExecutor(max_workers=len(site_data))

        # Create session based on request methodology
        if tor or unique_tor:
            underlying_request = TorRequest()
            underlying_session = underlying_request.session
        else:
            underlying_session = requests.session()
            underlying_request = requests.Request()

        # Create multi-threaded session for all requests. Use our custom FuturesSession that exposes response time
        session = ElapsedFuturesSession(executor=executor, session=underlying_session)

        # Results from analysis of all sites
        results_total = self.results

        # First create futures for all requests. This allows for the requests to run in parallel
        for social_network, net_info in site_data.items():

            # Results from analysis of this specific site
            results_site = {}

            # Record URL of main site
            results_site['url_main'] = net_info.get("urlMain")

            # Don't make request if username is invalid for the site
            regex_check = net_info.get("regexCheck")
            if regex_check and re.search(regex_check, self.username) is None:
                # No need to do the check at the site: this user name is not allowed.
                print((Style.BRIGHT + Fore.WHITE + "[" +
                    Fore.RED + "-" +
                    Fore.WHITE + "]" +
                    Fore.GREEN + " {}:" +
                    Fore.YELLOW + " Illegal Username Format For This Site!").format(social_network))
                print()
                results_site["exists"] = "illegal"
            else:
                # URL of user on site (if it exists)
                url = net_info["url"].format(self.username)
                results_site["url_user"] = url

                request_method = session.get
                if social_network != "GitHub":
                    # If only the status_code is needed don't download the body
                    if net_info["errorType"] == 'status_code':
                        request_method = session.head

                if net_info["errorType"] == "response_url":
                    #Site forwards request to a different URL if username not
                    #found.  Disallow the redirect so we can capture the
                    #http status from the original URL request.
                    allow_redirects = False
                else:
                    #Allow whatever redirect that the site wants to do.
                    #The final result of the request will be what is available.
                    allow_redirects = True

                # This future starts running the request in a new thread, doesn't block the main thread
                if proxy != None:
                    proxies = {"http": proxy, "https": proxy}
                    future = request_method(url=url, headers=headers,
                                            proxies=proxies,
                                            allow_redirects=allow_redirects
                                        )
                else:
                    future = request_method(url=url, headers=headers,
                                            allow_redirects=allow_redirects
                                        )

                # Store future in data for access later
                net_info["request_future"] = future

                # Reset identify for tor (if needed)
                if unique_tor:
                    underlying_request.reset_identity()

            # Add this site's results into final dictionary with all of the other results.
            if self.indexed_by_original_query:
                results_total[site_data[social_network]['original_query']] = results_site
            else:
                results_total[social_network] = results_site

        # Open the file containing account links
        # f = open_file(fname)

        # Core logic: If tor requests, make them here. If multi-threaded requests, wait for responses
        for social_network, net_info in site_data.items():

            # Retrieve results again
            results_site = results_total.get(social_network)

            # Retrieve other site information again
            url = results_site.get("url_user")
            exists = results_site.get("exists")
            if exists is not None:
                # We have already determined the user doesn't exist here
                continue

            # Get the expected error type
            error_type = net_info["errorType"]

            # Default data in case there are any failures in doing a request.
            http_status = "?"
            response_text = ""

            # Retrieve future and ensure it has finished
            future = net_info["request_future"]
            r, error_type, response_time = get_response(request_future=future,
                                                        error_type=error_type,
                                                        social_network=social_network,
                                                        verbose=verbose)

            # Attempt to get request information
            try:
                http_status = r.status_code
            except:
                pass
            try:
                response_text = r.text.encode(r.encoding)
            except:
                pass

            if error_type == "message":
                error = net_info.get("errorMsg")
                # Checks if the error message is in the HTML
                if not error in r.text:
                    # print_found(social_network, url, response_time, verbose)
                    exists = "yes"
                else:
                    # print_not_found(social_network, response_time, verbose)
                    exists = "no"

            elif error_type == "status_code":
                # Checks if the status code of the response is 2XX
                if not (r.status_code >= 300 or r.status_code < 200):
                    # print_found(social_network, url, response_time, verbose)
                    exists = "yes"
                else:
                    # print_not_found(social_network, response_time, verbose)
                    exists = "no"

            elif error_type == "response_url":
                # For this detection method, we have turned off the redirect.
                # So, there is no need to check the response URL: it will always
                # match the request.  Instead, we will ensure that the response
                # code indicates that the request was successful (i.e. no 404, or
                # forward to some odd redirect).
                if (r.status_code >= 200) and (r.status_code < 300):
                    # print_found(social_network, url, response_time, verbose)
                    exists = "yes"
                else:
                    # print_not_found(social_network, response_time, verbose)
                    exists = "no"

            elif error_type == "":
                exists = "error"

            # Save exists flag
            results_site['exists'] = exists

            # Save results from request
            results_site['http_status'] = http_status
            results_site['error_type'] = error_type
            results_site['response_object'] = r
            results_site['response_text'] = response_text
            results_site['response_time_ms'] = response_time

            # Add this site's results into final dictionary with all of the other results.
            results_total[social_network] = results_site

        if not silent_on_error:
            dump_errors()
        return results_total

