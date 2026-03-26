#!/usr/bin/env python3
"""
Sherlock JSON Bridge

Reads a JSON config from stdin, runs sherlock searches, and writes
structured JSON results to stdout. Used by the Hono API layer to
interface with the sherlock Python module without a long-running process.

Usage:
    echo '{"usernames":["john"],"options":{}}' | python3 sherlock_bridge.py
"""

import json
import os
import sys
import time

from sherlock_project.sherlock import sherlock
from sherlock_project.sites import SitesInformation
from sherlock_project.result import QueryStatus
from sherlock_project.notify import QueryNotify

_LOCAL_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sherlock_project",
    "resources",
    "data.json",
)

MAX_TIMEOUT = 120  # Hard cap on per-request timeout (seconds)
MAX_USERNAMES = 10  # Hard cap on usernames per call


class QueryNotifyCollect(QueryNotify):
    """Silently collect every query result into a plain dict."""

    def __init__(self) -> None:
        super().__init__()
        self.results: dict = {}

    def start(self, message: str) -> None:  # noqa: D401
        pass

    def update(self, result) -> None:  # noqa: D401
        response_ms = (
            round(result.query_time * 1000) if result.query_time is not None else None
        )
        self.results[result.site_name] = {
            "status": result.status.value,
            "url": result.site_url_user,
            "responseTimeMs": response_ms,
            "context": result.context,
        }

    def finish(self, message=None) -> None:  # noqa: D401
        pass


def _fail(message: str) -> None:
    """Print a failure envelope and exit non-zero."""
    print(json.dumps({"success": False, "error": message}), flush=True)
    sys.exit(1)


def main() -> None:
    # ── Read config from stdin ────────────────────────────────────────────────
    try:
        config = json.loads(sys.stdin.read())
    except json.JSONDecodeError as exc:
        _fail(f"Invalid JSON on stdin: {exc}")

    usernames: list[str] = config.get("usernames", [])
    options: dict = config.get("options", {})

    if not usernames:
        _fail("No usernames provided.")

    if len(usernames) > MAX_USERNAMES:
        _fail(f"Too many usernames (max {MAX_USERNAMES}).")

    include_nsfw: bool = bool(options.get("nsfw", False))
    use_local: bool = bool(options.get("local", True))
    sites_filter: list[str] = options.get("sites", [])
    proxy: str | None = options.get("proxy")
    timeout: int = min(int(options.get("timeout", 60)), MAX_TIMEOUT)
    json_file: str | None = options.get("jsonFile")

    # ── Load site data ────────────────────────────────────────────────────────
    try:
        if json_file:
            # Custom JSON file / URL supplied by caller
            sites_info = SitesInformation(json_file, honor_exclusions=False)
        elif use_local:
            # Prefer the bundled data.json (fast, no network)
            sites_info = SitesInformation(_LOCAL_DATA_PATH, honor_exclusions=False)
        else:
            # Fetch the latest manifest from GitHub (slower)
            sites_info = SitesInformation()

        if not include_nsfw:
            sites_info.remove_nsfw_sites()

        if sites_filter:
            site_data = {
                site.name: site.information
                for site in sites_info
                if site.name in sites_filter
            }
        else:
            site_data = {site.name: site.information for site in sites_info}

    except Exception as exc:  # noqa: BLE001
        _fail(f"Failed to load site data: {exc}")

    if not site_data:
        _fail("No sites matched the given filter.")

    # ── Run searches ──────────────────────────────────────────────────────────
    results: dict = {}
    wall_start = time.monotonic()

    for username in usernames:
        notifier = QueryNotifyCollect()
        try:
            sherlock(
                username=username,
                site_data=site_data,
                query_notify=notifier,
                proxy=proxy,
                timeout=timeout,
            )
            results[username] = notifier.results
        except Exception as exc:  # noqa: BLE001
            results[username] = {"_error": str(exc)}

    elapsed = round(time.monotonic() - wall_start, 3)

    # ── Emit JSON result ──────────────────────────────────────────────────────
    print(
        json.dumps(
            {
                "success": True,
                "results": results,
                "meta": {
                    "totalSites": len(site_data),
                    "elapsedSeconds": elapsed,
                    "usernames": usernames,
                },
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
