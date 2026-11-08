"""Offline regression tests for WAF/challenge-page fingerprints.

Reddit serves its JavaScript challenge page (HTTP 200, no profile content)
when it decides a requester looks automated. Before the fix for
sherlock-project/sherlock#2296, that page contained neither Reddit's
configured errorMsg nor any WAF fingerprint, so *every* username — real or
garbage — was reported CLAIMED. The challenge page must yield WAF instead.

These tests stub the HTTP layer so they run offline: the fixture is a real
challenge page captured 2026-11-08 (single-use token values redacted).
"""

import datetime
import json
from pathlib import Path

from sherlock_project import sherlock as sherlock_mod
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus


class _FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
        self.encoding = "utf-8"
        self.elapsed = datetime.timedelta(seconds=0.1)


class _FakeFuture:
    def __init__(self, response):
        self._response = response

    def result(self):
        return self._response


def _reddit_site():
    data_path = (
        Path(__file__).resolve().parent.parent
        / "sherlock_project"
        / "resources"
        / "data.json"
    )
    with data_path.open(encoding="utf-8") as f:
        sites_info = json.load(f)
    return {"Reddit": sites_info["Reddit"]}


def _challenge_page():
    fixture = Path(__file__).resolve().parent / "fixtures" / "reddit_challenge_page.html"
    return fixture.read_text(encoding="utf-8")


def _query(monkeypatch, html, username):
    def fake_get(self, *args, **kwargs):
        return _FakeFuture(_FakeResponse(html))

    monkeypatch.setattr(sherlock_mod.SherlockFuturesSession, "get", fake_get)
    result = sherlock_mod.sherlock(
        username=username,
        site_data=_reddit_site(),
        query_notify=QueryNotify(),
    )
    return result["Reddit"]["status"].status


def test_reddit_challenge_page_is_waf_for_unknown_username(monkeypatch):
    # Regression test for #2296: a garbage username served the challenge
    # page used to be reported CLAIMED.
    status = _query(monkeypatch, _challenge_page(), "zzzqqqxxyywwvvuu12345nonexistent")
    assert status is QueryStatus.WAF


def test_reddit_challenge_page_is_waf_for_known_username(monkeypatch):
    # The challenge page is served for real users too, so it must not
    # confirm them either — WAF, not a false CLAIMED.
    status = _query(monkeypatch, _challenge_page(), "blue")
    assert status is QueryStatus.WAF


def test_reddit_not_found_page_is_still_available(monkeypatch):
    # Negative control: a genuine "user does not exist" page must still
    # be AVAILABLE (the fingerprint must not swallow real verdicts).
    html = "<html><body>Sorry, nobody on Reddit goes by that name.</body></html>"
    status = _query(monkeypatch, html, "zzzqqqxxyywwvvuu12345nonexistent")
    assert status is QueryStatus.AVAILABLE


def test_reddit_profile_page_is_still_claimed(monkeypatch):
    # Negative control: a genuine profile page (no errorMsg, no
    # challenge marker) must still be CLAIMED.
    html = "<html><body><h1>blue</h1><p>u/blue profile page</p></body></html>"
    status = _query(monkeypatch, html, "blue")
    assert status is QueryStatus.CLAIMED
