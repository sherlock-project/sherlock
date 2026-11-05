import requests
from urllib3.exceptions import LocationParseError

from sherlock_project.sherlock import get_response


class _FailingFuture:
    """Minimal stand-in for a requests_futures Future whose result() raises."""

    def __init__(self, exc: Exception):
        self._exc = exc

    def result(self):
        raise self._exc


def test_get_response_handles_known_requests_exceptions():
    response, error_context, exception_text = get_response(
        request_future=_FailingFuture(requests.exceptions.ConnectionError("boom")),
        error_type="status_code",
        social_network="ExampleSite",
    )
    assert response is None
    assert error_context == "Error Connecting"
    assert "boom" in exception_text


def test_get_response_handles_non_requests_exceptions():
    # Regression test for https://github.com/sherlock-project/sherlock/issues/2970
    # A username ending in "." combined with a subdomain-based site URL (e.g.
    # "alice." -> "alice..example.com") produces a malformed host. urllib3
    # raises LocationParseError, which is *not* a requests.exceptions.RequestException
    # subclass, so it previously propagated uncaught and crashed the whole run.
    exc = LocationParseError("'alice..example.com', label empty or too long")
    response, error_context, exception_text = get_response(
        request_future=_FailingFuture(exc),
        error_type="status_code",
        social_network="ExampleSite",
    )
    assert response is None
    assert error_context == "Unknown Error"
    assert "label empty or too long" in exception_text
