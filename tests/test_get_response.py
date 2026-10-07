"""Tests for sherlock_project.sherlock.get_response.

These tests focus on the failure surface of the get_response helper.
The previous implementation used ``if response.status_code:`` to decide
whether a response had been received, which silently mishandled
``status_code == 0`` (an impossible HTTP status) and also any future
case where the ``Response`` object might legitimately report
``status_code is None``. A mock-based test is enough to lock in the
fixed behaviour: when the future returns a Response, the
``error_context`` must be ``None`` regardless of which status code the
Response reports; when the future raises, the right error context is
recorded.
"""
import pytest
import requests

from sherlock_project.sherlock import get_response


class _FakeResponse:
    """Mimics enough of requests.Response for get_response's needs."""

    def __init__(self, status_code):
        self.status_code = status_code


class _RaisingFuture:
    def __init__(self, exc):
        self._exc = exc

    def result(self):
        raise self._exc


class _OkFuture:
    def __init__(self, response):
        self._response = response

    def result(self):
        return self._response


def test_get_response_returns_error_context_none_for_200():
    response, error_context, exception_text = get_response(
        request_future=_OkFuture(_FakeResponse(200)),
        error_type="status_code",
        social_network="Example",
    )
    assert response.status_code == 200
    assert error_context is None
    assert exception_text is None


def test_get_response_returns_error_context_none_for_404():
    """A 404 response is still a valid HTTP response -- error_context must
    be cleared. The pre-fix code happened to pass here too, but only as
    a side effect of ``if response.status_code:`` (any non-zero value is
    truthy). The mock-based test pins down the contract that any
    integer status code is treated as a successfully-received response.
    """
    response, error_context, exception_text = get_response(
        request_future=_OkFuture(_FakeResponse(404)),
        error_type="status_code",
        social_network="Example",
    )
    assert response.status_code == 404
    assert error_context is None
    assert exception_text is None


def test_get_response_records_timeout():
    _, error_context, exception_text = get_response(
        request_future=_RaisingFuture(requests.exceptions.Timeout("read timed out")),
        error_type="status_code",
        social_network="Example",
    )
    assert error_context == "Timeout Error"
    assert "timed out" in (exception_text or "")


def test_get_response_records_connection_error():
    _, error_context, _ = get_response(
        request_future=_RaisingFuture(
            requests.exceptions.ConnectionError("dns failure")
        ),
        error_type="status_code",
        social_network="Example",
    )
    assert error_context == "Error Connecting"


def test_get_response_records_proxy_error():
    _, error_context, _ = get_response(
        request_future=_RaisingFuture(
            requests.exceptions.ProxyError("proxy refused")
        ),
        error_type="status_code",
        social_network="Example",
    )
    assert error_context == "Proxy Error"


def test_get_response_returns_error_context_none_for_0():
    response, error_context, exception_text = get_response(
        request_future=_OkFuture(_FakeResponse(0)),
        error_type="status_code",
        social_network="Example",
    )
    assert response.status_code == 0
    assert error_context is None
    assert exception_text is None
