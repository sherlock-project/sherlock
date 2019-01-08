

class SherlockService:
    def __init__(self,
        url: str,
        code_find: int=200):
        self._url = url
        self._code_match = code_find
        self._code = 0
        
    def request(self):
        if self._code == 0:
            r = request.get(self._url)
            self._code = r.status_code

    def results(self):
        return {
            "url": self._url,
            "found":  self._status ==  self._code_find,
            "code": self._status
        }
