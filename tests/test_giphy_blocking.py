import json
import os

from sherlock_project.sherlock import sherlock, SherlockFuturesSession
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus


class DummyResponse:
    def __init__(self, status_code: int, text: str = "", encoding: str = "utf-8"):
        self.status_code = status_code
        self.text = text
        self.encoding = encoding
        self.elapsed = 0.0


class DummyFuture:
    def __init__(self, response):
        self._response = response

    def result(self):
        return self._response


def load_giphy_manifest():
    base = os.path.dirname(os.path.dirname(__file__))
    data_file = os.path.join(base, "sherlock_project", "resources", "data.json")
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["Giphy"].copy()


def test_giphy_blocking_marked_waf(monkeypatch):
    giphy = load_giphy_manifest()
    assert giphy.get("errorType") == "message"

    site_data = {"Giphy": giphy}

    def fake_get(self, *args, **kwargs):
        resp = DummyResponse(status_code=403, text="")
        return DummyFuture(resp)

    monkeypatch.setattr(SherlockFuturesSession, "get", fake_get)

    qn = QueryNotify()
    results = sherlock(username="doesNotExist", site_data=site_data, query_notify=qn)

    assert "Giphy" in results
    status = results["Giphy"]["status"].status
    assert status is QueryStatus.WAF, f"Expected Giphy to be marked WAF on 403+empty body, got {status}"
