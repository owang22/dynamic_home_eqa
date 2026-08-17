#!/usr/bin/env python3
"""Serve the object-trace viewer. Stdlib only.

Serves the dynamic_home_eqa repo root (so both /visualization/viewer/ and
the trace.json files under /profiles/.../timelines/ are reachable) with
no-store cache headers — regenerated traces and re-baked maps must never be
served stale. Binds to 127.0.0.1 unless --host is given explicitly.

  python serve.py                  # http://127.0.0.1:8710/
  python serve.py --port 9000
"""

from __future__ import annotations

import argparse
import functools
import http.server
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
VIEWER = "/visualization/viewer/index.html"


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        # No trace pinned here: the viewer opens the first entry of
        # visualization/traces.json, which is the one manifest both pages read.
        if self.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", VIEWER)
            self.end_headers()
            return
        super().do_GET()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8710)
    args = ap.parse_args()

    handler = functools.partial(Handler, directory=str(REPO_ROOT))
    with http.server.ThreadingHTTPServer((args.host, args.port), handler) as srv:
        print(f"serving {REPO_ROOT}")
        print(f"viewer: http://{args.host}:{args.port}/")
        srv.serve_forever()


if __name__ == "__main__":
    main()
