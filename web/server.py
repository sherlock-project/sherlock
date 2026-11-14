"""Giao diện web cho Sherlock.

Chạy:
    python web/server.py            # mở http://127.0.0.1:8000
    python web/server.py --port 9000 --host 0.0.0.0

Server chỉ dùng thư viện chuẩn của Python cộng với chính gói sherlock_project.
Kết quả được đẩy về trình duyệt theo thời gian thực qua Server-Sent Events.
"""

import argparse
import json
import os
import queue
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ROOT))

from sherlock_project.notify import QueryNotify  # noqa: E402
from sherlock_project.result import QueryStatus  # noqa: E402
from sherlock_project.sherlock import sherlock  # noqa: E402
from sherlock_project.sites import SitesInformation  # noqa: E402

DATA_FILE = os.path.join(os.path.dirname(ROOT), "sherlock_project", "resources", "data.json")
MAX_USERNAME_LEN = 100


def load_sites(include_nsfw: bool) -> dict:
    sites = SitesInformation(DATA_FILE, honor_exclusions=False)
    if not include_nsfw:
        sites.remove_nsfw_sites()
    return {site.name: site for site in sites}


class QueueNotify(QueryNotify):
    """Chuyển từng kết quả của Sherlock vào một hàng đợi để stream ra web."""

    def __init__(self, out: queue.Queue):
        super().__init__()
        self.out = out

    def update(self, result):
        self.out.put({
            "type": "result",
            "site": result.site_name,
            "url": result.site_url_user,
            "status": result.status.value,
            "time": round(result.query_time, 3) if result.query_time else None,
            "context": result.context,
        })


class Handler(BaseHTTPRequestHandler):
    server_version = "SherlockWeb/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("[web] " + fmt % args + "\n")

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path in ("/", "/index.html"):
            with open(os.path.join(ROOT, "index.html"), "rb") as fh:
                self._send(200, fh.read(), "text/html; charset=utf-8")
        elif parsed.path == "/api/sites":
            nsfw = qs.get("nsfw", ["0"])[0] == "1"
            sites = load_sites(nsfw)
            self._json(200, [
                {"name": s.name, "home": s.url_home, "nsfw": s.is_nsfw}
                for s in sorted(sites.values(), key=lambda s: s.name.lower())
            ])
        elif parsed.path == "/api/search":
            self._search(qs)
        else:
            self._json(404, {"error": "Not found"})

    def _search(self, qs):
        username = qs.get("username", [""])[0].strip()
        if not username or len(username) > MAX_USERNAME_LEN or any(c.isspace() for c in username):
            self._json(400, {"error": "Username không hợp lệ (không rỗng, không có khoảng trắng, tối đa 100 ký tự)."})
            return

        nsfw = qs.get("nsfw", ["0"])[0] == "1"
        try:
            timeout = max(1, min(120, int(qs.get("timeout", ["30"])[0])))
        except ValueError:
            timeout = 30
        wanted = [s for s in qs.get("sites", [""])[0].split(",") if s]

        all_sites = load_sites(nsfw or bool(wanted))
        if wanted:
            lookup = {name.lower(): name for name in all_sites}
            names = [lookup[w.lower()] for w in wanted if w.lower() in lookup]
        else:
            names = list(all_sites)
        site_data = {n: all_sites[n].information for n in names}
        if not site_data:
            self._json(400, {"error": "Không có trang nào hợp lệ để kiểm tra."})
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()

        events: queue.Queue = queue.Queue()
        done = object()

        def worker():
            try:
                sherlock(username, site_data, QueueNotify(events), timeout=timeout)
            except Exception as exc:  # pragma: no cover - báo lỗi về trình duyệt
                events.put({"type": "error", "message": str(exc)})
            finally:
                events.put(done)

        threading.Thread(target=worker, daemon=True).start()

        def emit(obj):
            self.wfile.write(f"data: {json.dumps(obj, ensure_ascii=False)}\n\n".encode())
            self.wfile.flush()

        try:
            emit({"type": "start", "username": username, "total": len(site_data)})
            while True:
                item = events.get()
                if item is done:
                    break
                emit(item)
            emit({"type": "done"})
        except (BrokenPipeError, ConnectionResetError):
            # Người dùng đã bấm Dừng hoặc đóng tab; luồng sherlock sẽ tự kết thúc.
            pass


def main():
    parser = argparse.ArgumentParser(description="Giao diện web cho Sherlock")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--open", action="store_true", help="Tự mở trình duyệt")
    args = parser.parse_args()

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{'127.0.0.1' if args.host in ('0.0.0.0', '') else args.host}:{args.port}"
    print(f"Sherlock Web đang chạy tại {url}  (Ctrl+C để dừng)")
    if args.open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng.")


if __name__ == "__main__":
    main()
