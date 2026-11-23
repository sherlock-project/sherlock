import time

import requests
from requests.adapters import BaseAdapter

from sherlock_project.sherlock import SherlockFuturesSession

DELAY = 0.1


class SlowAdapter(BaseAdapter):
    """Answers every request after DELAY seconds, without touching the network."""

    def send(self, request, **kwargs):
        time.sleep(DELAY)
        response = requests.Response()
        response.status_code = 200
        if request.url.endswith("/redirect"):
            response.status_code = 302
            response.headers["Location"] = "mock://site/final"
        response.url = request.url
        response.request = request
        response._content = b""
        return response

    def close(self):
        pass


def test_response_time_excludes_queue_wait() -> None:
    # One worker, five requests: the later requests wait in the pool queue
    # before they are sent. That wait must not count as response time.
    session = SherlockFuturesSession(max_workers=1)
    session.mount("mock://", SlowAdapter())
    futures = [session.get(f"mock://site/{i}") for i in range(5)]
    elapsed = [future.result().elapsed for future in futures]
    session.close()

    assert all(DELAY <= t < 2.5 * DELAY for t in elapsed), elapsed


def test_response_time_includes_redirect_hops() -> None:
    session = SherlockFuturesSession(max_workers=1)
    session.mount("mock://", SlowAdapter())
    response = session.get("mock://site/redirect").result()
    session.close()

    assert response.url == "mock://site/final"
    assert 2 * DELAY <= response.elapsed < 3.5 * DELAY, response.elapsed
