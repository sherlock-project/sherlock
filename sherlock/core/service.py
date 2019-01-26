# grequests and re imports
import grequests
import re

# Sherlock.Log import
from sherlock.core.log import Log

# Sherlock.Service
class Service:
    """
    Represents a service to verify if a username exists.
    """

    def __init__(
        self,
        username: str,
        recv=None,
        logger: Log = Log.getLogger(),
        regex: str = None,
        error_type="status_code",
        **kargs
    ):
        """
        Creates a service object which retries data though a asynchronous HTTP or HTTPs request.

        Parameters
        ----------
        username : str
            The username to search for.

        recv : func, optional, default = None
            The event handler which is called when response is received.

        logger : sherlock.Log, optional, default = new Log()
            The logger object to callback events occuring during requests or errors that may occur.

        regex/regexCheck : str, optional, default = None
            The regex filter for the username.

        url : str, optional, default = None
            Url for HTTP or HTTPS request.

        error_type/errorType : str, optional, default = "status_code"
            The error type expected from the response.

        """

        # Initialisation of private variables
        self._url = ""
        self._logger = logger
        self._serv = None
        self._recv = recv
        self._username = username
        self._regex = regex
        self._error_type = error_type

        # Make adjustments according to kargs
        if not kargs is None:
            if "url" in kargs:
                self._url = kargs["url"]
            if "errorType" in kargs:
                self._error_type = kargs["errorType"]
            if "regexCheck" in kargs:
                self._regex = kargs["regexCheck"]

        # Dict Initiasation
        self._header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0"
        }
        self._hooks = {"response": self._recv_event}
        self._request = grequests.get(self.url, headers=self._header, hooks=self._hooks)

    @property
    def grequest(self):
        """
        Gets the grequest object associated with this Object.

        Parameters
        ----------
        return : return, object
            grequest Object
        """
        return self._request

    @property
    def valid(self):
        """
        Returns

        Parameters
        ----------
        return :
        """
        if not self._regex is None and re.search(self._regex, self._username) is None:
            return False
        return True

    @property
    def url(self):
        """
        Parameters
        ----------
        return : str, return
            Returns a string object representing the url to be request.
        """
        url = self._url.replace("{}", self._username)
        return url

    @property
    def host(self):
        """
        Parameters
        ----------
        return : str, request
            The where the request will be sent too.
        """
        host = re.find(r"([a-z]*:[/]+[a-z0-1.]*)", self.url)
        if len(host) > 0:
            return host.group(1)
        else:
            return ""

    def _recv_event(self, response, *args, **kwargs):
        is_found = False
        config = self._config

        # Get the error type
        error_type = "status_code"
        if "errorType" in config:
            error_type = config["errorType"]

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
            self._code = response.status_code
            res = self._recv(self, is_found)
            self._logger.unlock()
            return res
        return 0
