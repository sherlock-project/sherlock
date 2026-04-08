"""
Sherlock Web UI — Flask application for Sherlock username lookup.
"""

import sys
import threading
import argparse
from pathlib import Path

# Ensure sherlock_project is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, request, jsonify, render_template

from sherlock_project.sherlock import SherlockFuturesSession, sherlock
from sherlock_project.result import QueryStatus
from sherlock_project.notify import QueryNotify
from sherlock_project.sites import SitesInformation


app = Flask(__name__, template_folder=str(Path(__file__).resolve().parent / "templates"))


@app.route("/")
def index():
    return render_template("index.html")


class WebNotify(QueryNotify):
    """Notify adapter that collects results for the web UI."""

    def __init__(self):
        self.results = {}
        self.lock = threading.Lock()

    def start(self, username):
        pass

    def update(self, result):
        with self.lock:
            self.results[result.site_name] = {
                "username": result.username,
                "site_name": result.site_name,
                "url_user": result.url_user,
                "status": result.status.value.lower(),
            }


@app.route("/api/search", methods=["POST"])
def search():
    data = request.get_json()
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"error": "Username is required."}), 400

    sites = SitesInformation()
    site_data = {site.name: site.information for site in sites}

    notify = WebNotify()

    # Run sherlock in a thread so it doesn't block the request
    result_holder = {}
    error_holder = [None]

    def run_search():
        try:
            result_holder["data"] = sherlock(
                username, site_data, notify,
                dump_response=False,
                proxy=None,
                timeout=30,
            )
        except Exception as e:
            error_holder[0] = str(e)

    thread = threading.Thread(target=run_search)
    thread.start()
    thread.join(timeout=60)

    if thread.is_alive():
        return jsonify({"error": "Search timed out."}), 504

    if error_holder[0]:
        return jsonify({"error": error_holder[0]}), 500

    # Build response from notify.results since sherlock() is synchronous
    results = []
    for site_name, res in notify.results.items():
        results.append({
            "site_name": res["site_name"],
            "url_user": res["url_user"],
            "status": res["status"],
            "response_time": None,
        })

    return jsonify({"results": results})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sherlock Web UI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=False)