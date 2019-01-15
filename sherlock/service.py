import requests
import grequests
import re

from log import SherlockLog

class Service:
    def __init__(
        self, username: str, config: dict=None, recv =None, logger: SherlockLog=SherlockLog.getLogger(), regex: str=None
    ):

        # Standard Initiasation
        self._url = ""
        self._logger = logger
        self._serv = None
        self._recv = recv
        self._username = username
        self._regex = regex
        self._config = config
        
        if not config is None:
            if "url" in config: self._url = config["url"]
            if "errorType" in config: self._error_type = config["errorType"]
            if "regexCheck" in config: self._regex = config["regexCheck"]
            
            
            
            
        # Dict Initiasation
        self._header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0"
        }
        self._hooks = {
            "response": self._recv_event
        }
        self._request = grequests.get(
            self.url,
            headers=self._header,
            hooks=self._hooks
        )


    @property
    def grequest(self):
        return self._request

    @property
    def valid(self):
        if (
            not self._regex is None
            and re.search(self._regex, self._username) is None
        ):
            return False
        return True
        
    @property
    def url(self):
        url = self._url.replace("{}", self._username)
        return url
        
    @property
    def host(self):
        host = re.find(r"([a-z]*:[/]+[a-z0-1.]*)", self.url)
        if len(host)>0:
            return host.group(1)
        else:
            return ""
    
    def _recv_event(self, response, *args, **kwargs):
        is_found = False
        config = self._config

        # Get the error type
        error_type = "status_code"
        if "errorType" in config: error_type = config["errorType"]

        # Depends on error type
        if error_type == "message" and "errorMsg" in config:
            is_found = not config["errorMsg"] in response.text

        # Based on error code
        elif error_type == "status_code":
            is_found = not response.status_code >= 300 or response.status_code < 200

        # Based on response url
        elif error_type == "response_url" and "errorUrl" in config:
            is_found = not config["errorUrl"] in response.url

        # Anything else
        else:
            self._logger.error("Error, no error type for %s" % (self._config))

        # Trigger event
        if not self._recv == None:
            self._logger.lock()
            self._config["code"] = response.status_code
            res = self._recv(self, is_found)
            self._logger.unlock()
            return res
        return 0


    @property
    def url(self):
        url = self._url.replace("{}", self._username)
        return url
        
    @property
    def host(self):
        host = re.fin
