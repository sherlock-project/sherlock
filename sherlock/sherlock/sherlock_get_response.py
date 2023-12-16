import requests

def get_response(request_future, error_type, social_network):
    # Default for Response object if some failure occurs.
    response = None

    error_context = "General Unknown Error"
    exception_text = None
    try:
        response = request_future.result()
        if response.status_code:
            # Status code exists in response object
            error_context = None
    except requests.exceptions.HTTPError as errh:
        error_context = "HTTP Error"
        exception_text = str(errh)
    except requests.exceptions.ProxyError as errp:
        error_context = "Proxy Error"
        exception_text = str(errp)
    except requests.exceptions.ConnectionError as errc:
        error_context = "Error Connecting"
        exception_text = str(errc)
    except requests.exceptions.Timeout as errt:
        error_context = "Timeout Error"
        exception_text = str(errt)
    except requests.exceptions.RequestException as err:
        error_context = "Unknown Error"
        exception_text = str(err)

    return response, error_context, exception_text