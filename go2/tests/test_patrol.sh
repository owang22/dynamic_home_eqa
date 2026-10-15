#!/bin/bash
# Runs inside the go2-lab image (no robot needed):
#   docker run --rm -v "$PWD/go2/tests":/tests go2-lab bash /tests/test_patrol.sh
set -euo pipefail
mkdir -p /data && cd /data && rm -rf positions.yaml position_previews patrols fake_webrtc.jsonl
python3 /tests/fake_robot.py & FAKE=$!
trap 'kill $FAKE 2>/dev/null || true' EXIT
sleep 3

echo "== record_positions: dock, two spots, one bad name, a list, then quit"
(sleep 3; printf 'dock\nbench_A 15\nshelf-1\nbad name!\nlist\nquit\n') | timeout 30 ros2 run go2_patrol record_positions \
  --ros-args -p positions_file:=/data/positions.yaml
cat positions.yaml
test "$(grep -c '^- id:' positions.yaml)" = 3
test -f position_previews/bench_A.jpg

echo "== add a position Nav2 will refuse, then patrol"
cat >> positions.yaml <<'EOF'
- id: unreachable
  x: 99.0
  y: 0.0
  yaw_deg: 0.0
  pitch_deg: 0
EOF
set +e; timeout 120 ros2 run go2_patrol patrol --ros-args -p positions_file:=/data/positions.yaml \
  -p out_root:=/data/patrols -p settle_s:=0.5 -p tries:=2; code=$?; set -e
echo "patrol exit code $code (1 expected: one position failed)"
test "$code" = 1
log=$(ls /data/patrols/*/*/patrol.json)
python3 - "$log" <<'EOF'
import json, sys, pathlib
log = json.load(open(sys.argv[1])); d = pathlib.Path(sys.argv[1]).parent
r = {p["id"]: p for p in log["positions"]}
assert set(r) == {"bench_A", "shelf-1", "unreachable"}, r.keys()
assert r["bench_A"]["result"] == "photographed" and (d / "bench_A.jpg").exists()
assert r["bench_A"]["pitch_commanded_deg"] == 15
assert r["shelf-1"]["result"] == "photographed" and "pitch_commanded_deg" not in r["shelf-1"]
assert r["unreachable"]["result"].startswith("failed") and len(r["unreachable"]["attempts"]) == 2
assert abs(r["bench_A"]["off_by_m"] - 0.05) < 0.01, r["bench_A"]["off_by_m"]
assert log["return_to_dock"]["outcome"] == "reached"
assert log["summary"] == "2 of 3 photographed", log["summary"]
print("patrol.json checks passed:", log["summary"], "| ended:", log["ended_because"])
EOF
echo "== tilt commands the driver would have sent"
cat /data/fake_webrtc.jsonl
python3 - <<'EOF'
import json
reqs = [json.loads(l) for l in open("/data/fake_webrtc.jsonl")]
assert [r["api_id"] for r in reqs] == [1002, 1007, 1007], reqs
assert json.loads(reqs[1]["parameter"])["y"] < 0 and json.loads(reqs[2]["parameter"])["y"] == 0
print("tilt sequence ok: balance stand, nose up, level")
EOF
echo ALL PASSED
