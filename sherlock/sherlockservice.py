import requests
import grequests
import re

from sherlocklog import SherlockLog

class SherlockService:
    def __init__(self,
            username,
            config={}, 
            on_recv=None,
            logger=SherlockLog.getLogger(),
            mapper=[]
        ):
        self._config = config
        self._logger = logger
        self._serv = None
        self._on_recv=on_recv
        self._mapper = mapper
        self._username = username
    
    @property
    def url(self):
        if "url" in self._config:
            return self._config["url"]  
        return ""
        
    @property   
    def url_main(self):
        if "urlMain" in self._config:
            return self._config["urlMain"]
        return self.url
    
    def _response(self, response, *args, **kwargs):
        if not self._on_recv == None:
            self._logger.lock()
            self._config["code"] = response.status_code
            res = self._on_recv(self, self.results(), self._logger)
            self._logger.unlock()
            return res
        return 0

    def request(self):
        logger = self._logger
        config = self._config
        if "regexCheck" in config and re.search(config["regexCheck"], self._username) is None:
            return 412
            
        if "url" in config: config["url"] = config["url"].replace("{}", self._username)
        
        self._mapper.append(grequests.get(config["url"], headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
        }, hooks={
            'response': self._response
        }, timeout=10))
        
        return 200
            

    def results(self):
        config = self._config
        return {
            "url": config["url"],
            "found":  config["code"] == 200,
            "code": config["code"]
        }
