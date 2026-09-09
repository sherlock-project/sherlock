"""Tests for handling usernames with special/unicode characters."""

from concurrent.futures import Future
import time

import pytest

from sherlock_project import sherlock
from sherlock_project.sherlock import get_response


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


class SlowFuture:
    def __init__(self):
        self.calls = 0

    def result(self, timeout=None):
        self.calls += 1
        raise sherlock.FutureTimeoutError()



def test_get_response_propagates_keyboard_interrupt_from_polling(monkeypatch):
    future = SlowFuture()
    original_handler = sherlock.handler

    def fake_handler(signal_received, frame):
        raise KeyboardInterrupt

    monkeypatch.setattr(sherlock, "handler", fake_handler)

    def interrupting_result(timeout=None):
        future.calls += 1
        if future.calls >= 2:
            raise KeyboardInterrupt
        raise sherlock.FutureTimeoutError()

    future.result = interrupting_result

    with pytest.raises(KeyboardInterrupt):
        get_response(
            request_future=future,
            error_type=["status_code"],
            social_network="TestSite",
        )



def test_shutdown_request_session_cancels_futures_and_closes_sessions():
    cancelled = []
    shutdown_calls = []
    closed = []

    class FakeFuture:
        def cancel(self):
            cancelled.append(True)

    class FakeExecutor:
        def shutdown(self, wait=True, cancel_futures=False):
            shutdown_calls.append((wait, cancel_futures))

    class FakeSession:
        executor = FakeExecutor()

    class FakeUnderlyingSession:
        def close(self):
            closed.append(True)

    site_data = {
        "SiteA": {"request_future": FakeFuture()},
        "SiteB": {"request_future": FakeFuture()},
        "SiteC": {},
    }

    sherlock.shutdown_request_session(FakeSession(), FakeUnderlyingSession(), site_data)

    assert len(cancelled) == 2
    assert shutdown_calls == [(False, True)]
    assert closed == [True]
