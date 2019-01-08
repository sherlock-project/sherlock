class SherlockFinder:
    def __init__(self):
        pass
        
        
    
   def get_response(self, 
    request_future, 
    error_type, 
    social_network, 
    verbose=False,
    logger):
    
    try:
        rsp = request_future.result()
        if rsp.status_code:
            return rsp, error_type
    except requests.exceptions.HTTPError as errh:
        print_error(errh, "HTTP Error:", social_network, verbose)
    except requests.exceptions.ConnectionError as errc:
        print_error(errc, "Error Connecting:", social_network, verbose)
    except requests.exceptions.Timeout as errt:
        print_error(errt, "Timeout Error:", social_network, verbose)
    except requests.exceptions.RequestException as err:
        print_error(err, "Unknown error:", social_network, verbose)
    return None, ""
