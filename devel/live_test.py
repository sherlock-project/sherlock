#!/usr/bin/env python3
"""Live test runner for Sherlock heuristics.

This script loads the local `data.json`, selects a small subset of sites,
and runs `sherlock()` for a demo username. Set `LIVE_TEST_USERNAME`
environment variable to test a specific username.
"""
import os
import sys

# Ensure local package imports resolve
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from sherlock_project.sites import SitesInformation
from sherlock_project.notify import QueryNotifyPrint
from sherlock_project.sherlock import sherlock


def main():
    username = os.environ.get("LIVE_TEST_USERNAME", "sherlock_live_test_user_12345")
    data_path = os.path.join(ROOT, "sherlock_project", "resources", "data.json")

    print(f"Using username: {username}")
    print(f"Loading site data from: {data_path}")

    sites = SitesInformation(data_file_path=data_path, honor_exclusions=False)

    # Select a short, deterministic subset to keep this quick
    keys = list(sites.sites.keys())[:12]
    site_data = {k: sites.sites[k].information for k in keys}

    notify = QueryNotifyPrint(verbose=True, print_all=True, browse=False)

    results = sherlock(username, site_data, notify, dump_response=False, proxy=None, timeout=15)

    print("\nSummary:")
    for site, info in results.items():
        status = info.get("status")
        http_status = info.get("http_status")
        print(f"{site}: {status} (http: {http_status})")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Live test runner for Sherlock (demo)."""
import sys

from sherlock_project.sites import SitesInformation
from sherlock_project.sherlock import sherlock
from sherlock_project.notify import QueryNotifyPrint


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "exampleuser"

    # Load local data.json to avoid network requests for manifest
    data_path = "sherlock_project/resources/data.json"
    sites_info = SitesInformation(data_file_path=data_path, honor_exclusions=False)

    # Use a small subset to keep runtime short for demo
    site_names = list(sites_info.sites.keys())[:30]
    site_data = {name: sites_info.sites[name].information for name in site_names}

    notifier = QueryNotifyPrint(verbose=True, print_all=True, browse=False)

    results = sherlock(username, site_data, notifier, dump_response=False, proxy=None, timeout=15)

    # Print a concise summary
    claimed = [s for s, r in results.items() if r.get("status") and r.get("status").status == r.get("status").status.CLAIMED]
    print("\nSummary:")
    print(f"Checked {len(results)} sites, potential matches: {len(claimed)}")


if __name__ == "__main__":
    main()
