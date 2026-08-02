"""Tests for handling usernames with special/unicode characters."""

from concurrent.futures import Future

import requests

from sherlock_project.notify import QueryNotify
from sherlock_project.sherlock import get_response
import sherlock_project.sherlock as sherlock_module


def _make_future_with_exception(exc):
    """Create a Future that raises the given exception."""
    future = Future()
    future.set_exception(exc)
    return future


def test_get_response_handles_unicode_decode_error():
    """Regression test for issue #2730.

    Usernames with special characters (e.g. 'Émile') can trigger a
    UnicodeDecodeError inside the requests library during redirect
    handling. This must not crash the program.
    """
    future = _make_future_with_exception(
        UnicodeDecodeError("utf-8", b"\xe9", 0, 1, "invalid continuation byte")
    )
    response, error_context, exception_text = get_response(
        request_future=future,
        error_type=["status_code"],
        social_network="TestSite",
    )
    assert response is None
    assert error_context == "Encoding Error"
    assert "utf-8" in exception_text


def test_get_response_handles_unicode_encode_error():
    """UnicodeEncodeError should also be caught (subclass of UnicodeError)."""
    future = _make_future_with_exception(
        UnicodeEncodeError("ascii", "É", 0, 1, "ordinal not in range(128)")
    )
    response, error_context, exception_text = get_response(
        request_future=future,
        error_type=["status_code"],
        social_network="TestSite",
    )
    assert response is None
    assert error_context == "Encoding Error"
    assert "ascii" in exception_text


def test_sherlock_percent_encodes_username_in_profile_url(monkeypatch):
    """Usernames must be URL-encoded before they are inserted into templates."""
    captured_urls = []

    class FakeSession:
        def __init__(self, *args, **kwargs):
            pass

        def head(self, url, **kwargs):
            captured_urls.append(url)
            response = requests.Response()
            response.status_code = 404
            response._content = b""
            response.encoding = "utf-8"

            future = Future()
            future.set_result(response)
            return future

    monkeypatch.setattr(sherlock_module, "SherlockFuturesSession", FakeSession)

    result = sherlock_module.sherlock(
        username="\u00c9mile Doe/Dev+Ops",
        site_data={
            "Example": {
                "url": "https://example.com/users/{}",
                "urlMain": "https://example.com",
                "errorType": "status_code",
                "errorCode": 404,
            }
        },
        query_notify=QueryNotify(),
    )

    expected_url = "https://example.com/users/%C3%89mile%20Doe/Dev%2BOps"
    assert captured_urls == [expected_url]
    assert result["Example"]["url_user"] == expected_url
