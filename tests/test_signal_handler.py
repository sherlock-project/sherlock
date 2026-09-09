"""Tests for SIGINT shutdown handling."""

import pytest

import sherlock_project.sherlock as sherlock


class RecordingExecutor:
    def __init__(self):
        self.shutdown_kwargs = None

    def shutdown(self, **kwargs):
        self.shutdown_kwargs = kwargs


class RecordingSession:
    def __init__(self):
        self.executor = RecordingExecutor()


def test_handler_cancels_pending_futures_before_exit(monkeypatch):
    session = RecordingSession()
    monkeypatch.setattr(sherlock, "_active_session", session)

    with pytest.raises(SystemExit) as exc_info:
        sherlock.handler(None, None)

    assert exc_info.value.code == 0
    assert session.executor.shutdown_kwargs == {
        "wait": False,
        "cancel_futures": True,
    }


def test_handler_exits_even_if_session_shutdown_fails(monkeypatch):
    class FailingExecutor:
        def shutdown(self, **kwargs):
            raise RuntimeError("shutdown failed")

    class FailingSession:
        executor = FailingExecutor()

    monkeypatch.setattr(sherlock, "_active_session", FailingSession())

    with pytest.raises(SystemExit) as exc_info:
        sherlock.handler(None, None)

    assert exc_info.value.code == 0
