from sherlocklog import SherlockLog

class SherlockFinder:
    def __init__(self, 
            logger: SherlockLog=SherlockLog.getLogger()):
        self._logger = logger



    def get_response(self, 
        request_future, 
        error_type, 
        social_network, 
        verbose=False):
        logger = self._logger
    
        try:
            rsp = request_future.result()
            if rsp.status_code:
                return rsp, error_type
        except requests.exceptions.HTTPError as errh:
            logger.error(str(errh) + " HTTP Error:" + str(social_network))
        except requests.exceptions.ConnectionError as errc:
            logger.error(str(errc) + " Error Connecting:" + str(social_network))
        except requests.exceptions.Timeout as errt:
            logger.error(str(errt) + " Timeout Error:" + str(social_network))
        except requests.exceptions.RequestException as err:
            logger.error(str(err) + " Unknown error:" + str(social_network))
        return None, ""
