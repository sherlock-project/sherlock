"""Local web interface for Sherlock."""

import argparse
import copy
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from sherlock_project import sherlock
from sherlock_project.notify import QueryNotify
from sherlock_project.sites import SitesInformation


LOGGER = logging.getLogger(__name__)
WEB_PAGE = Path(__file__).parent / "resources" / "web" / "index.html"
MAX_REQUEST_SIZE = 4096


class SherlockWebServer(ThreadingHTTPServer):
    """HTTP server carrying the loaded site data for request handlers."""

    daemon_threads = True

    def __init__(self, address, handler, site_data, nsfw_sites):
        self.site_data = site_data
        self.nsfw_sites = nsfw_sites
        super().__init__(address, handler)


class SherlockWebRequestHandler(BaseHTTPRequestHandler):
    server: SherlockWebServer

    def do_GET(self):
        if self.path != "/":
            self.send_error(404, "Not found")
            return

        try:
            page = WEB_PAGE.read_bytes()
        except OSError:
            LOGGER.exception("Could not load the Sherlock web interface")
            self.send_error(500, "Could not load the web interface")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self):
        if self.path != "/api/search":
            self.send_error(404, "Not found")
            return

        origin = self.headers.get("Origin")
        if origin and origin != f"http://{self.headers.get('Host', '')}":
            self._send_json({"error": "Cross-origin requests are not allowed"}, 403)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json({"error": "Invalid content length"}, 400)
            return

        if content_length <= 0 or content_length > MAX_REQUEST_SIZE:
            self._send_json({"error": "Request body must be between 1 and 4096 bytes"}, 400)
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json({"error": "Request body must be valid JSON"}, 400)
            return

        if not isinstance(payload, dict):
            self._send_json({"error": "Request body must be a JSON object"}, 400)
            return

        username = payload.get("username")
        if not isinstance(username, str):
            self._send_json({"error": "Username must be a string"}, 400)
            return
        username = username.strip()
        if not username or len(username) > 100:
            self._send_json({"error": "Username must contain between 1 and 100 characters"}, 400)
            return

        include_nsfw = payload.get("include_nsfw", False)
        if not isinstance(include_nsfw, bool):
            self._send_json({"error": "include_nsfw must be a boolean"}, 400)
            return

        usernames = (
            sherlock.multiple_usernames(username)
            if sherlock.check_for_parameter(username)
            else [username]
        )
        site_data = {
            name: info
            for name, info in self.server.site_data.items()
            if include_nsfw or name not in self.server.nsfw_sites
        }

        try:
            profiles = []
            for searched_username in usernames:
                results = sherlock.sherlock(
                    searched_username,
                    copy.deepcopy(site_data),
                    QueryNotify(),
                )
                profiles.append(
                    {
                        "username": searched_username,
                        "results": [
                            self._serialize_result(name, result)
                            for name, result in results.items()
                        ],
                    }
                )
        except Exception:
            LOGGER.exception("Sherlock search failed for username %r", username)
            self._send_json({"error": "Search failed. Check the server logs for details."}, 500)
            return

        self._send_json({"profiles": profiles})

    @staticmethod
    def _serialize_result(name: str, result: dict[str, Any]) -> dict[str, Any]:
        status = result["status"]
        return {
            "site": name,
            "status": status.status.value,
            "url": result.get("url_user", ""),
            "site_url": result.get("url_main", ""),
            "http_status": result.get("http_status", ""),
            "query_time": status.query_time,
        }

    def _send_json(self, payload, status=200):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)


def main():
    parser = argparse.ArgumentParser(description="Start Sherlock's local web interface.")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Interface to bind (default: 127.0.0.1)",
    )
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    args = parser.parse_args()

    data_file = Path(__file__).parent / "resources" / "data.json"
    sites = SitesInformation(str(data_file), honor_exclusions=False)
    nsfw_sites = {site.name for site in sites if site.is_nsfw}
    site_data = {site.name: site.information for site in sites}

    server = SherlockWebServer(
        (args.host, args.port),
        SherlockWebRequestHandler,
        site_data,
        nsfw_sites,
    )
    print(f"Sherlock web app running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Sherlock web app.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
