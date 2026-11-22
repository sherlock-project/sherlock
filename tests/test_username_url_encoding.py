"""Username characters that are meaningful to a URL parser must be encoded.

`url` is the URL reported to the user for a given username, and it is also the
URL probed when a target has no separate `urlProbe`. Substituting a username
verbatim therefore lets a username address a different resource than the one
reported: everything after "#" is a fragment and is never sent, so a username
"a#b" was checked as "a" and reported as that profile's result.
"""
from concurrent.futures import Future

import pytest

from sherlock_project.notify import QueryNotify
from sherlock_project.sherlock import SherlockFuturesSession, sherlock


class _StubResponse:
    status_code = 200
    encoding = "utf-8"
    text = "<html>profile</html>"
    elapsed = 0.0


def _query(monkeypatch, username, url, **extra):
    """Run one target offline, capturing the URL actually probed."""
    probed: list[str] = []

    def fake_head(self, url, **kwargs):
        probed.append(url)
        future = Future()
        future.set_result(_StubResponse())
        return future

    monkeypatch.setattr(SherlockFuturesSession, "head", fake_head)

    target = {
        "urlMain": "https://example.invalid",
        "url": url,
        "errorType": "status_code",
        "errorCode": [404],
        "username_claimed": "blue",
    }
    target.update(extra)

    results = sherlock(username, {"Example": target}, QueryNotify())
    return results["Example"]["url_user"], probed


@pytest.mark.parametrize("username,expected_component", [
    ("a#b", "a%23b"),   # fragment would swallow the rest of the username
    ("a?b", "a%3Fb"),   # query would swallow the rest of the username
    ("a/b", "a%2Fb"),   # extra path segment, different resource
    ("a%b", "a%25b"),   # stray percent escape, malformed URL
    ("a b", "a%20b"),   # space is not valid in a URL
])
def test_username_is_percent_encoded_in_profile_url_and_probe(
    monkeypatch, username, expected_component
):
    """Distinct usernames must resolve to distinct URLs, and the probe must
    address the profile URL that is reported for that username."""
    expected = f"https://example.invalid/u/{expected_component}"

    url_user, probed = _query(monkeypatch, username, "https://example.invalid/u/{}")

    assert url_user == expected
    assert probed == [expected]


def test_username_is_percent_encoded_in_separate_probe_url(monkeypatch):
    """A target with urlProbe gets the same encoding on the probe URL."""
    url_user, probed = _query(
        monkeypatch,
        "a#b",
        "https://example.invalid/u/{}",
        urlProbe="https://example.invalid/probe/{}",
    )

    assert url_user == "https://example.invalid/u/a%23b"
    assert probed == ["https://example.invalid/probe/a%23b"]


@pytest.mark.parametrize("username,expected_component", [
    ("a+b", "a%2Bb"),   # servers decode a literal "+" in a query as a space
    ("a&b", "a%26b"),   # would start a new query parameter
    ("a=b", "a%3Db"),   # would split key from value
])
def test_username_is_encoded_in_query_position(
    monkeypatch, username, expected_component
):
    """In a query template, delimiters would probe a different username."""
    url_user, probed = _query(
        monkeypatch, username, "https://example.invalid/search?username={}"
    )

    assert url_user == f"https://example.invalid/search?username={expected_component}"
    assert probed == [url_user]


@pytest.mark.parametrize("username", ["a-b_c.d", "a@b", "a!b", "a*b"])
def test_username_without_url_meaning_is_left_alone(monkeypatch, username):
    """Characters that are legal in a path segment keep their usual form, so
    existing profile URLs do not change."""
    expected = f"https://example.invalid/u/{username}"

    url_user, probed = _query(monkeypatch, username, "https://example.invalid/u/{}")

    assert url_user == expected
    assert probed == [expected]


def test_username_is_not_encoded_in_host_position(monkeypatch):
    """Subdomain-style templates take a bare host label, where percent
    encoding is not valid, so the username is substituted as before."""
    url_user, probed = _query(
        monkeypatch, "blue", "https://{}.example.invalid/"
    )

    assert url_user == "https://blue.example.invalid/"
    assert probed == ["https://blue.example.invalid/"]
