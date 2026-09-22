#!/usr/bin/env python3
"""Serve viz/ on :8788. Rebuild data.js before index/data.js if runs are newer."""
from __future__ import annotations

import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

VIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(VIZ))
from build import is_stale, main as build_main  # noqa: E402

PORT = int(os.environ.get("LIBERO_VIZ_PORT", "8788"))
_lock = threading.Lock()


def maybe_rebuild() -> None:
    with _lock:
        if not is_stale():
            return
        print("viz: runs newer than data.js, rebuilding", flush=True)
        build_main(["--no-win"])


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html", "/data.js"):
            maybe_rebuild()
        return SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html", "/data.js"):
            self.send_header("Cache-Control", "no-store")
        SimpleHTTPRequestHandler.end_headers(self)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.log_date_time_string(), fmt % args))


def main() -> None:
    os.chdir(VIZ)
    maybe_rebuild()
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"viz: http://127.0.0.1:{PORT}/  (rebuilds data.js on refresh)", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
