import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

import pytest

from sherlock_project.result import QueryResult, QueryStatus
from sherlock_project.web import SherlockWebRequestHandler, SherlockWebServer


@pytest.fixture
def web_server():
    server = SherlockWebServer(
        ("127.0.0.1", 0),
        SherlockWebRequestHandler,
        {"Public": {}, "Adult": {}},
        {"Adult"},
    )
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def post_search(url, payload):
    request = Request(
        f"{url}/api/search",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return json.loads(response.read())


def test_web_page_is_served(web_server):
    with urlopen(web_server) as response:
        assert response.status == 200
        assert b"Sherlock" in response.read()


def test_search_returns_serialized_results_and_expands_variations(web_server):
    calls = []

    def fake_search(username, site_data, query_notify):
        calls.append((username, set(site_data)))
        return {
            name: {
                "status": QueryResult(username, name, "", QueryStatus.CLAIMED),
                "url_user": f"https://example.com/{username}",
                "url_main": "https://example.com",
                "http_status": 200,
            }
            for name in site_data
        }

    with patch("sherlock_project.web.sherlock.sherlock", side_effect=fake_search):
        payload = post_search(web_server, {"username": "test{?}"})

    assert [profile["username"] for profile in payload["profiles"]] == [
        "test_", "test-", "test."
    ]
    assert calls == [
        ("test_", {"Public"}),
        ("test-", {"Public"}),
        ("test.", {"Public"}),
    ]
    assert payload["profiles"][0]["results"][0]["status"] == "Claimed"
    assert payload["profiles"][0]["results"][0]["http_status"] == 200

    calls.clear()
    with patch("sherlock_project.web.sherlock.sherlock", side_effect=fake_search):
        post_search(web_server, {"username": "test", "include_nsfw": True})
    assert calls == [("test", {"Public", "Adult"})]


def test_search_rejects_blank_username(web_server):
    request = Request(
        f"{web_server}/api/search",
        data=b'{"username":"  "}',
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with pytest.raises(HTTPError) as error:
        urlopen(request)
    assert error.value.code == 400


def test_search_rejects_cross_origin_request(web_server):
    request = Request(
        f"{web_server}/api/search",
        data=b'{"username":"test"}',
        headers={
            "Content-Type": "application/json",
            "Origin": "https://example.org",
        },
        method="POST",
    )
    with pytest.raises(HTTPError) as error:
        urlopen(request)
    assert error.value.code == 403
