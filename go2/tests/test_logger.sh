#!/bin/bash
# Logger test with a fake console: off 3 s -> on 5 s -> off. Expect exactly one session file, with only live records.
#   bash go2/tests/test_logger.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; T="$(mktemp -d)"; trap 'kill $FAKE $LOG 2>/dev/null || true; rm -rf "$T"' EXIT
python3 - "$T" <<'PY' & FAKE=$!
import http.server, json, sys, time
T0 = time.time()
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.end_headers()
        try:
            while True:
                t = time.time() - T0; on = 3 < t < 8
                e = {"odom": {"pos": [t, 0, 0.3], "yaw": 0} if on else None, "age": {"odom": 0.05} if on else {},
                     "map_pose": None, "rec": {"running": False}, "cloud": {"n_total": int(t), "obs": [[0, 0, 0.2]]} if on else None}
                self.wfile.write(b"data: " + json.dumps(e).encode() + b"\n\n"); self.wfile.flush(); time.sleep(0.1)
        except (BrokenPipeError, ConnectionResetError): pass
http.server.ThreadingHTTPServer(("127.0.0.1", 8599), H).serve_forever()
PY
sleep 0.5
GO2_CONSOLE=http://127.0.0.1:8599 GO2_EVENT_LOGS="$T/logs" GO2_LOGGER_FAST=1 python3 -u "$HERE/../console/log_events.py" > "$T/out.txt" 2>&1 & LOG=$!
sleep 16; kill -TERM $LOG; wait $LOG || true
cat "$T/out.txt"
python3 - "$T/logs" <<'PY'
import gzip, json, sys, pathlib
files = sorted(pathlib.Path(sys.argv[1]).glob("*.jsonl.gz"))
assert len(files) == 1, files
recs = [json.loads(l) for l in gzip.open(files[0], "rt")]
assert recs and all(r["odom"] is not None for r in recs), "a dog-off record was written"
assert 15 <= len(recs) <= 50, len(recs)
print(f"PASS: one session file, {len(recs)} records, all with odometry, {sum('cloud' in r for r in recs)} lidar grids")
PY
