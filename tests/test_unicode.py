"""Tests for handling usernames with special/unicode characters."""

from concurrent.futures import Future

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
