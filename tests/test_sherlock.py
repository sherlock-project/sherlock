import pytest
from argparse import ArgumentTypeError
import requests
from sherlock_project.result import QueryStatus
from sherlock_project.sherlock import (
    interpolate_string,
    check_for_parameter,
    multiple_usernames,
    timeout_check,
    sherlock,
    SherlockFuturesSession,
    get_response,
)

def test_interpolate_and_multiple_functions():
    """
    Test interpolate_string, check_for_parameter, multiple_usernames, and timeout_check.
    This ensures that:
    - interpolate_string correctly replaces '{}' in strings, dicts, and lists
    - check_for_parameter correctly detects the pattern '{?}'
    - multiple_usernames returns the correct variations of a username with placeholder '{?}'
    - timeout_check returns a float for valid timeouts and raises an error on non-positive timeouts.
    """
    # Test interpolate_string with a string
    result_str = interpolate_string("Hello {}", "World")
    assert result_str == "Hello World"
    
    # Test interpolate_string with a dictionary
    input_dict = {"greeting": "Hi, {}!"}
    expected_dict = {"greeting": "Hi, World!"}
    assert interpolate_string(input_dict, "World") == expected_dict
    
    # Test interpolate_string with a list
    input_list = ["{}1", "2{}"]
    expected_list = ["World1", "2World"]
    assert interpolate_string(input_list, "World") == expected_list
    
    # Test interpolate_string with a non-string/dict/list (should return the value unchanged)
    non_string_value = 42
    assert interpolate_string(non_string_value, "ignored") == 42
    
    # Test check_for_parameter: returns True if '{?}' is in the input string
    assert check_for_parameter("user{?}") is True
    assert check_for_parameter("username") is False
    
    # Test multiple_usernames: should generate a list with replacements for '{?}'
    expected_usernames = ["test_", "test-", "test."]
    assert multiple_usernames("test{?}") == expected_usernames
    
    # Test timeout_check: valid numeric string returns a float
    assert timeout_check("30") == 30.0
    
    # Test timeout_check: zero or negative timeout should raise an ArgumentTypeError.
    with pytest.raises(ArgumentTypeError):
        timeout_check("-5")

def test_get_response_success():
    """
    Test get_response returns a valid response when the future returns a successful response.
    """
    # Create a fake response object with the necessary attributes.
    class FakeResponse:
        def __init__(self):
            self.status_code = 200
            self.text = "Success"
            self.encoding = "utf-8"
            self.elapsed = 0.123

    # Create a fake future that returns FakeResponse on result() call.
    class FakeFuture:
        def result(self):
            return FakeResponse()

    fake_future = FakeFuture()
    response, error_context, exception_text = get_response(
        request_future=fake_future, error_type="status_code", social_network="dummy"
    )
    assert response is not None
    assert response.status_code == 200
    # On a successful response, error_context should be set to None.
    assert error_context is None
    assert exception_text is None

class FakeFutureException:
    """
    A helper fake future that raises a specified exception when result() is called.
    """
    def __init__(self, exception):
        self.exception = exception

    def result(self):
        raise self.exception

@pytest.mark.parametrize("exception,expected_context", [
    (requests.exceptions.HTTPError("http error"), "HTTP Error"),
    (requests.exceptions.ProxyError("proxy error"), "Proxy Error"),
    (requests.exceptions.ConnectionError("connection error"), "Error Connecting"),
    (requests.exceptions.Timeout("timeout error"), "Timeout Error"),
    (requests.exceptions.RequestException("generic request error"), "Unknown Error"),
])
def test_get_response_exceptions(exception, expected_context):
    """
    Test get_response returns the correct error context and exception text when the future raises an exception.
    """
    fake_future = FakeFutureException(exception)
    response, error_context, exception_text = get_response(
        request_future=fake_future, error_type="status_code", social_network="dummy"
    )
    # In case of exceptions, response should be None.
    assert response is None
    assert error_context == expected_context
    # The exception text should match the raised exception.
    assert exception_text is not None

def test_sherlock_illegal_username():
    """
    Test that 'sherlock' correctly marks a username as ILLEGAL when the username doesn't
    match the regexCheck criteria. In this test, we use a numeric username "123" while the site
    only allows alphabetical usernames.
    """
    site_data = {
        "TestSite": {
            "urlMain": "http://testsite.com",
            "url": "http://testsite.com/{}",
            "regexCheck": "^[A-Za-z]+$",  # only letters allowed
            "errorType": "status_code",
            "errorCode": 404,
        }
    }
    class DummyQueryNotify:
        def __init__(self):
            self.results = []
        def start(self, username):
            pass
        def update(self, result):
            self.results.append(result)
        def finish(self):
            return 0

    dummy_notify = DummyQueryNotify()
    results = sherlock("123", site_data, dummy_notify)
    test_site_result = results["TestSite"]
    assert test_site_result["status"].status == QueryStatus.ILLEGAL

def test_sherlock_message_error(monkeypatch):
    """
    Test that sherlock correctly handles the errorType 'message' scenario.
    This test monkeypatches the request method of SherlockFuturesSession to always
    return a fake future that yields a fake response containing the error message.
    The fake response text includes 'NotFound' (as per the site's errorMsg),
    so this should cause the query status to be set to AVAILABLE.
    """
    # Define a fake response class with the desired attributes.
    class FakeResponse:
        def __init__(self):
            self.status_code = 200
            # Simulate a response text containing the error message "NotFound"
            self.text = "Error: NotFound"
            self.encoding = "utf-8"
            self.elapsed = 0.456

    # Define a fake future class that returns the fake response.
    class FakeFuture:
        def result(self):
            return FakeResponse()

    # Monkeypatch the request method of SherlockFuturesSession so that it always returns FakeFuture.
    def fake_request(self, method, url, hooks=None, *args, **kwargs):
        return FakeFuture()

    monkeypatch.setattr(SherlockFuturesSession, "request", fake_request)

    # Create a fake site_data entry for errorType 'message'
    site_data = {
        "MessageSite": {
            "urlMain": "http://messagesite.com",
            "url": "http://messagesite.com/{}",
            "errorType": "message",
            "errorMsg": "NotFound"
        }
    }

    # Create a dummy QueryNotify object that just collects results.
    class DummyQueryNotify:
        def __init__(self):
            self.results = []
        def start(self, username):
            pass
        def update(self, result):
            self.results.append(result)
        def finish(self):
            return 0

    dummy_notify = DummyQueryNotify()
    # Call sherlock with a username that is legal (no regexCheck provided)
    results = sherlock("ValidUsername", site_data, dummy_notify)
    message_site_result = results["MessageSite"]
    # For errorType 'message', if the error message is found in the returned text,
    # the branch sets the query status to AVAILABLE.
    assert message_site_result["status"].status == QueryStatus.AVAILABLE
