import json
import os
import re
from concurrent.futures import ThreadPoolExecutor

import requests
from colorama import init, Fore, Style

from requests_futures.sessions import FuturesSession
from torrequest import TorRequest

from logger import Logger


# TODO: fix tumblr


class Sherlock:
    def __init__(self, username, debug=False):
        self.username = username
        self.log = Logger(debug)
        self.amount = 0

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
        }

        data_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.json")
        self.data = self.__load_data(data_file_path)

    def search(self, use_tor: bool = False, use_unique_tor: bool = False) -> dict:
        """Run Sherlock Analysis.

            Checks for existence of username on various social media sites.

            Keyword Arguments:
            username               -- String indicating username that report
                                      should be created against.
            verbose                -- Boolean indicating whether to give verbose output.
            tor                    -- Boolean indicating whether to use a tor circuit for the requests.
            unique_tor             -- Boolean indicating whether to use a new tor circuit for each request.

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
            """
        results_filename = f"{self.username.lower()}.txt"
        self.__remove_old_file(results_filename)
        self.log.info(f"Checking username {self.username} on:")

        executor = ThreadPoolExecutor(max_workers=len(self.data))
        underlying_session = requests.session()
        underlying_request = requests.Request()
        if use_tor or use_unique_tor:
            underlying_request = TorRequest()
            underlying_session = underlying_request.session()
        session = FuturesSession(executor=executor, session=underlying_session)

        prepared_sites = self.__prepare_sites(session, underlying_request, use_unique_tor)
        total_results = self.__perform_search(prepared_sites)

        self.__save_results(results_filename, total_results)

        return total_results

    def __prepare_sites(self, session, underlying_request, use_unique_tor: bool) -> dict:
        # TODO: complex business logic, refactor.
        prepared_sites = dict()
        for social_network, network_info in self.data.items():
            site_info = dict()
            site_info['url_main'] = network_info.get("urlMain")
            regex_check = network_info.get("regexCheck")

            if regex_check and re.search(regex_check, self.username) is None:
                self.log.warn(f"Illegal Username Format for {social_network} website!")
                site_info["exists"] = "illegal"
            else:
                url = network_info["url"].format(self.username)
                site_info["url_user"] = url
                request_method = session.get

                # FIXME: add request method for specific websites.
                if social_network != "GitHub":
                    if network_info["errorType"] == 'status_code':
                        request_method = session.head

                future = request_method(url=url, headers=self.headers)
                site_info["request_future"] = future

                if use_unique_tor:
                    underlying_request.reset_identity()
            prepared_sites[social_network] = site_info
        return prepared_sites

    def __perform_search(self, sites) -> dict:
        total_results = dict()
        for social_network, net_info in self.data.items():
            # Retrieve results again
            site_info = sites.get(social_network)
            if "exists" in site_info:
                continue

            # Retrieve other site information again
            url = site_info.get("url_user")

            error_type = net_info["errorType"]
            future = sites[social_network]["request_future"]

            response, error_type = self.__get_response(future, error_type, social_network)
            if not response:
                # FIXME: don't check for existence if no response.
                self.log.error(f"No response from: {url}!")

            response_code, response_body = self.__get_response_info(response)
            response_code = response_code if response_code else "?"
            response_body = response_body if response_body else str()

            exists = "no"
            if error_type == "message":
                error = net_info.get("errorMsg")
                # Checks if the error message is in the HTML
                if error not in response.text:
                    self.log.fine(social_network, url)
                    exists = "yes"
                    self.amount += 1
                else:
                    self.log.warn("Not found!", social_network)

            elif error_type == "status_code":
                # Checks if the status code of the response is 2XX
                if not response.status_code >= 300 or response.status_code < 200:
                    self.log.fine(social_network, url)
                    exists = "yes"
                    self.amount += 1
                else:
                    self.log.warn("Not found!", social_network)

            elif error_type == "response_url":
                error = net_info.get("errorUrl")
                # Checks if the redirect url is the same as the one defined in data.json
                if error not in response.url:
                    self.log.fine(social_network, url)
                    exists = "yes"
                    self.amount += 1
                else:
                    self.log.warn("Not found!", social_network)

            elif error_type == "":
                self.log.error(f"Error! {social_network}")
                exists = "error"

            # Save exists flag
            site_info['exists'] = exists

            # Save results from request
            site_info['http_status'] = response_code
            site_info['response_text'] = response_body

            # Add this site's results into final dictionary with all of the other results.
            total_results[social_network] = site_info
        return total_results

    def __get_response_info(self, response):
        code, body = None, None
        try:
            code = response.status_code
        except Exception as e:
            self.log.error("Unexpected exception while getting code", e)

        try:
            body = response.text.encode(response.encoding)
        except Exception as e:
            self.log.error("Unexpected exception while getting body", e)

        return code, body

    def __load_data(self, filename: str) -> dict:
        with open(filename, "r", encoding="utf-8") as raw:
            data = json.load(raw)
        return data

    def __get_response(self, request_future, error_type, social_network):
        try:
            rsp = request_future.result()
            if rsp.status_code:
                return rsp, error_type
        except requests.exceptions.HTTPError as err:
            self.log.error(f"HTTP Error: {social_network}", err)
        except requests.exceptions.ConnectionError as err:
            self.log.error(f"Error Connecting: {social_network}", err)
        except requests.exceptions.Timeout as err:
            self.log.error(f"Timeout Error: {social_network}", err)
        except requests.exceptions.RequestException as err:
            self.log.error(f"Unknown error: {social_network}", err)
        return None, ""

    def __remove_old_file(self, filename: str):
        if os.path.isfile(filename):
            os.remove(filename)
            self.log.info("Removing previous file", filename)

    def __save_results(self, filename, results):
        with open(filename, 'a') as file:
            for social_network in results:
                if results[social_network]['exists'] == 'yes':
                    file.write(f"{results[social_network]['url_user']}\n")
            file.write(f"Total: {str(self.amount)}\n")
        self.log.info("Saved", filename)
