import pytest
from concurrent.futures import Future

import sherlock_project.sherlock as sherlock_module
from sherlock_project.sherlock import sherlock
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus


class FakeResponse:
    """Stand-in for a requests.Response object.

    Only the attributes that Sherlock reads are provided.
    """

    def __init__(self, url: str = "http://goodsite/user"):
        self.status_code = 200
        self.text = ""
        self.encoding = "utf-8"
        self.elapsed = 0.05
        self.url = url


class FakeFuturesSession:
    """Stand-in for SherlockFuturesSession.

    Every request is answered immediately with a canned response, so that the
    tests never reach the network.
    """

    def __init__(self, *args, **kwargs):
        pass

    def _resolved_future(self) -> Future:
        future = Future()
        future.set_result(FakeResponse())
        return future

    def get(self, *args, **kwargs) -> Future:
        return self._resolved_future()

    def head(self, *args, **kwargs) -> Future:
        return self._resolved_future()

    def post(self, *args, **kwargs) -> Future:
        return self._resolved_future()

    def put(self, *args, **kwargs) -> Future:
        return self._resolved_future()


# Sentinel used to drop a field from an otherwise valid manifest entry.
REMOVE = object()


def manifest_entry(**overrides) -> dict:
    """Build a valid manifest entry, optionally overriding (or dropping) fields."""
    entry = {
        "urlMain": "http://goodsite/",
        "url": "http://goodsite/{}",
        "errorType": "status_code",
        "username_claimed": "claimed",
        "username_unclaimed": "unclaimed",
    }
    for key, value in overrides.items():
        if value is REMOVE:
            entry.pop(key, None)
        else:
            entry[key] = value
    return entry


@pytest.mark.parametrize("overrides,offending_field", [
    ({"regexCheck": "*bad("}, "regexCheck"),
    ({"errorType": REMOVE}, "errorType"),
    ({"errorType": "message"}, "errorMsg"),
    ({"request_method": "PATCH"}, "request_method"),
    ({"errorType": "status_code", "errorCode": "404"}, "errorCode"),
], ids=[
    "invalid-regex",
    "missing-error-type",
    "missing-error-msg",
    "unsupported-request-method",
    "invalid-error-code",
])
def test_malformed_entry_does_not_abort_scan(monkeypatch, overrides, offending_field):
    """A malformed manifest entry may only degrade its own site to Unknown.

    The healthy site and every username must still be scanned, and the reason
    for the bad site has to name the offending field.
    """
    monkeypatch.setattr(sherlock_module, "SherlockFuturesSession", FakeFuturesSession)

    site_data = {
        "GoodSite": manifest_entry(),
        "BrokenSite": manifest_entry(**overrides),
    }

    for username in ("user1", "user2"):
        results = sherlock(username, site_data, QueryNotify())

        broken_status = results["BrokenSite"]["status"]
        assert broken_status.status is QueryStatus.UNKNOWN
        assert broken_status.context
        assert offending_field in broken_status.context

        good_status = results["GoodSite"]["status"]
        assert good_status.status is QueryStatus.CLAIMED
