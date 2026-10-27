"""Offline regression tests for the array form of a site's ``errorType``.

``data.schema.json`` documents ``errorType`` as either one detection method or a
list of them, but the request setup only compared it to a plain string.  A site
declaring ``["response_url", ...]`` therefore kept redirects enabled, so the
verdict was read from the "user not found" landing page instead of the original
response.  These tests stub the session so no network access is needed.
"""

import pytest
import requests

from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus
from sherlock_project.sherlock import SherlockFuturesSession, sherlock


class _FakeFuture:
    """Stand-in for the future returned by ``SherlockFuturesSession``."""

    def __init__(self, response: requests.Response) -> None:
        self._response = response

    def result(self) -> requests.Response:
        return self._response


def _response(url: str, status_code: int = 200, text: str = "") -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.url = url
    response.encoding = "utf-8"
    response._content = text.encode("utf-8")
    return response


@pytest.fixture
def recorded_requests(monkeypatch):
    """Record every request the probe makes and answer it with a 200 page."""
    calls: list[tuple[str, dict]] = []

    def _record(method: str):
        def _request(self, **kwargs):
            calls.append((method, kwargs))
            return _FakeFuture(_response(kwargs["url"], text="ok"))

        return _request

    monkeypatch.setattr(SherlockFuturesSession, "get", _record("GET"))
    monkeypatch.setattr(SherlockFuturesSession, "head", _record("HEAD"))
    return calls


def _query(error_type, **extra) -> tuple[QueryStatus, list[tuple[str, dict]]]:
    site = {
        "urlMain": "https://example.test",
        "url": "https://example.test/{}",
        "errorType": error_type,
        **extra,
    }
    results = sherlock(
        username="someone",
        site_data={"Example": site},
        query_notify=QueryNotify(),
    )
    return results["Example"]["status"].status, []


def test_response_url_in_a_list_disables_redirects(recorded_requests):
    status, _ = _query(["response_url"])
    assert len(recorded_requests) == 1
    method, kwargs = recorded_requests[0]
    assert method == "GET"
    assert kwargs["allow_redirects"] is False
    assert status is QueryStatus.CLAIMED


def test_response_url_as_a_string_still_disables_redirects(recorded_requests):
    _query("response_url")
    method, kwargs = recorded_requests[0]
    assert method == "GET"
    assert kwargs["allow_redirects"] is False


def test_message_in_a_list_keeps_redirects(recorded_requests):
    _query(["message"], errorMsg="not found")
    method, kwargs = recorded_requests[0]
    assert method == "GET"
    assert kwargs["allow_redirects"] is True


def test_status_code_alone_in_a_list_uses_a_head_request(recorded_requests):
    _query(["status_code"], errorCode=[404])
    method, kwargs = recorded_requests[0]
    assert method == "HEAD"
