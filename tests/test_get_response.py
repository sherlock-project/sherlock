"""Tests for sherlock_project.sherlock.get_response."""
from concurrent.futures import Future
from unittest.mock import MagicMock

import pytest
import requests

from sherlock_project.sherlock import get_response


def _future_returning(value):
    """Build a Future that has already completed with the given value."""
    f = Future()
    f.set_result(value)
    return f


def test_get_response_success_clears_error_context():
    """A successful response (status_code=200) must clear the default error.

    Without that, downstream code would still report "General Unknown Error"
    even though we got a real HTTP response.
    """
    response = requests.Response()
    response.status_code = 200
    r, error_context, _ = get_response(
        request_future=_future_returning(response),
        error_type="status_code",
        social_network="example",
    )
    assert r is response
    assert error_context is None


def test_get_response_handles_zero_status_code():
    """A response with status_code=0 (e.g. InvalidURL, retry-exhausted) is
    still a valid response object. The old ``if response.status_code:`` check
    treated 0 as falsy, so error_context stayed at the "General Unknown
    Error" default and the rest of sherlock reported every site as an error
    even when the requests future had already returned cleanly.
    """
    response = requests.Response()
    response.status_code = 0
    r, error_context, _ = get_response(
        request_future=_future_returning(response),
        error_type="status_code",
        social_network="example",
    )
    assert r is response
    # The response is a real Response object, so the caller can still inspect
    # status_code / text / etc. error_context should be None because the
    # future returned successfully, not because the response was an error.
    assert error_context is None


def test_get_response_returns_none_on_connection_error():
    """When the future raises ConnectionError, get_response must return
    (None, <error context>, <exception str>) so the downstream WAF check
    doesn't crash trying to access ``None.text``.
    """
    future = Future()
    future.set_exception(requests.exceptions.ConnectionError("DNS failure"))
    r, error_context, exception_text = get_response(
        request_future=future,
        error_type="status_code",
        social_network="example",
    )
    assert r is None
    assert error_context == "Error Connecting"
    assert "DNS failure" in (exception_text or "")
