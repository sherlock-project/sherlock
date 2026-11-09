"""Exercise the real HTTP adapter against a local server, without external sites."""

from concurrent.futures import Future
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from time import monotonic
from unittest.mock import Mock

import pytest
import requests
from urllib3.util.retry import Retry

from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus
from sherlock_project.sherlock import SherlockRetry, get_response, sherlock


@contextmanager
def serving(statuses, headers=None, body=b"profile", method="GET"):
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def handle_request(self):
            calls.append((self.command, self.path))
            self.send_response(statuses[min(len(calls) - 1, len(statuses) - 1)])
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        do_GET = do_HEAD = do_POST = handle_request

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}"
    try:
        site = {
            "urlMain": url,
            "url": url + "/{}",
            "errorType": "message",
            "errorMsg": "not found",
            "request_method": method,
        }
        yield site, calls
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def scan(site):
    notify = QueryNotify()
    result = sherlock("testuser", {"Local": site}, notify, timeout=2)["Local"]
    assert notify.result is result["status"]
    return result


@pytest.fixture
def sleeps(monkeypatch):
    sleep = Mock()
    monkeypatch.setattr("urllib3.util.retry.time.sleep", sleep)
    return sleep


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_transient_failure_recovers(status, sleeps):
    with serving([status, status, 200]) as (site, calls):
        result = scan(site)
    assert len(calls) == 3
    assert result["status"].status is QueryStatus.CLAIMED
    assert result["http_status"] == 200
    sleeps.assert_called_once_with(2.0)


@pytest.mark.parametrize("error_type", ["message", "status_code", "response_url"])
@pytest.mark.parametrize("status", [403, 429, 500, 502, 503, 504, 501])
def test_failures_never_become_account_verdicts(status, error_type, sleeps):
    with serving([status]) as (site, calls):
        site["errorType"] = error_type
        site["errorCode"] = status
        result = scan(site)
    assert len(calls) == (3 if status in (429, 500, 502, 503, 504) else 1)
    assert result["status"].status is QueryStatus.UNKNOWN
    assert str(status) in result["status"].context
    assert result["http_status"] == status


@pytest.mark.parametrize("error_type", ["message", "status_code", "response_url"])
@pytest.mark.parametrize("status", [200, 404])
def test_normal_results_unchanged(status, error_type, sleeps):
    body = b"profile" if status == 200 else b"not found"
    with serving([status], body=body) as (site, calls):
        site["errorType"] = error_type
        result = scan(site)
    assert len(calls) == 1
    expected = QueryStatus.CLAIMED if status == 200 else QueryStatus.AVAILABLE
    assert result["status"].status is expected
    sleeps.assert_not_called()


def test_post_is_not_replayed(sleeps):
    with serving([503, 200], method="POST") as (site, calls):
        result = scan(site)
    assert calls == [("POST", "/testuser")]
    assert result["status"].status is QueryStatus.UNKNOWN
    sleeps.assert_not_called()


def test_head_is_retried(sleeps):
    with serving([503, 200], method="HEAD") as (site, calls):
        site["errorType"] = "status_code"
        result = scan(site)
    assert calls == [("HEAD", "/testuser"), ("HEAD", "/testuser")]
    assert result["status"].status is QueryStatus.CLAIMED


@pytest.mark.parametrize("header,delay", [("3", 3), ("999999", 30), ("invalid", None)])
def test_retry_after(header, delay, sleeps):
    with serving([429, 200], headers={"Retry-After": header}) as (site, calls):
        result = scan(site)
    assert len(calls) == 2
    assert result["status"].status is QueryStatus.CLAIMED
    if delay is None:
        sleeps.assert_not_called()
    else:
        sleeps.assert_called_once_with(delay)


def test_retry_after_http_date(monkeypatch):
    monkeypatch.setattr("urllib3.util.retry.time.time", lambda: 1445412470)
    response = requests.Response()
    response.headers["Retry-After"] = "Wed, 21 Oct 2015 07:28:00 GMT"
    assert SherlockRetry().get_retry_after(response) == 10


@pytest.mark.parametrize("exception", [requests.Timeout, requests.ConnectionError])
def test_transport_errors_remain_unknown(exception):
    future = Future()
    future.set_exception(exception("unavailable"))
    response, context, text = get_response(future, "message", "Local")
    assert response is None
    assert context in ("Timeout Error", "Error Connecting")
    assert text == "unavailable"


def test_retry_configuration(monkeypatch, sleeps):
    session = requests.Session()
    monkeypatch.setattr(requests, "session", lambda: session)
    with serving([200]) as (site, _):
        scan(site)
    for prefix in ("http://", "https://"):
        retry = session.get_adapter(prefix).max_retries
        assert isinstance(retry, Retry)
        assert retry.total == 2
        assert retry.connect == retry.read == retry.other == 0
        assert "POST" not in retry.allowed_methods
        assert not retry.raise_on_status


def test_real_backoff_wait():
    with serving([503, 503, 200]) as (site, calls):
        started = monotonic()
        result = scan(site)
        elapsed = monotonic() - started
    assert len(calls) == 3
    assert result["status"].status is QueryStatus.CLAIMED
    assert elapsed >= 2


def test_site_failure_does_not_change_other_results(sleeps):
    with (
        serving([429]) as (limited, limited_calls),
        serving([200]) as (healthy, healthy_calls),
    ):
        results = sherlock(
            "testuser", {"Limited": limited, "Healthy": healthy},
            QueryNotify(), timeout=2,
        )
    assert len(limited_calls) == 3
    assert len(healthy_calls) == 1
    assert results["Limited"]["status"].status is QueryStatus.UNKNOWN
    assert results["Healthy"]["status"].status is QueryStatus.CLAIMED


def test_redirect_detection_unchanged(sleeps):
    with serving([302], headers={"Location": "/missing"}) as (site, calls):
        site["errorType"] = "response_url"
        result = scan(site)
    assert len(calls) == 1
    assert result["status"].status is QueryStatus.AVAILABLE
    sleeps.assert_not_called()


def test_unrelated_status_is_not_retried(sleeps):
    with serving([413], headers={"Retry-After": "3"}) as (site, calls):
        scan(site)
    assert len(calls) == 1
    sleeps.assert_not_called()
