#!/bin/bash
# Runs inside the go2-lab image with robot_brain/ at /brain (no robot, no vision model):
#   docker run --rm -v "$PWD/go2/tests":/tests -v "$PWD/robot_brain":/brain:ro go2-lab bash /tests/test_search.sh
set -euo pipefail
mkdir -p /data && cd /data && rm -rf searches fake_brain_calls.jsonl
cat > positions.yaml <<'P'
positions:
- {id: dock, x: 0.0, y: 0.0, yaw_deg: 0.0, pitch_deg: 0}
- {id: shelf-1, x: 1.0, y: 0.5, yaw_deg: 90.0, pitch_deg: 0}
- {id: bench_A, x: 2.0, y: -1.0, yaw_deg: 0.0, pitch_deg: 15}
- {id: unreachable, x: 99.0, y: 0.0, yaw_deg: 0.0, pitch_deg: 0}
P
python3 /tests/fake_robot.py & R=$!
python3 /tests/fake_brain.py & B=$!
trap 'kill $R $B 2>/dev/null || true' EXIT
sleep 3
set +e; timeout 120 ros2 run go2_patrol search --ros-args -p positions_file:=/data/positions.yaml \
  -p out_root:=/data/searches -p settle_s:=0.5 -p brain_url:=http://127.0.0.1:8499 \
  -p question:="where is the red mug?"; code=$?; set -e
echo "search exit code $code (0 expected: found)"
test "$code" = 0
python3 - <<'PY'
import json, glob, pathlib
f = glob.glob("/data/searches/*/*/search.json"); assert len(f) == 1, f
log = json.load(open(f[0])); d = pathlib.Path(f[0]).parent
assert log["found_at"] == "bench_A" and log["ended_because"] == "found at bench_A", log["ended_because"]
looks = [(l["id"], l["result"]) for l in log["looks"]]
assert [i for i, _ in looks] == ["unreachable", "shelf-1", "bench_A"], looks
assert looks[0][1].startswith("failed") and looks[1][1] == looks[2][1] == "photographed", looks
assert (d / "look_02_shelf-1.jpg").exists() and (d / "look_03_bench_A.jpg").exists()
calls = [json.loads(l) for l in open("/data/fake_brain_calls.jsonl")]
assert [c["path"] for c in calls] == ["/ask", "/feedback", "/look", "/look"], [c["path"] for c in calls]
assert calls[1]["failed"] and calls[1]["place"] == "unreachable"
assert all(c["image"]["jpeg"] and c["image"]["bytes"] > 1000 for c in calls[2:]), calls[2:]
print("search.json and brain calls ok:", looks, "->", log["ended_because"])
PY
echo "== brain not running: the search must stop at once and say so"
set +e; timeout 60 ros2 run go2_patrol search --ros-args -p positions_file:=/data/positions.yaml \
  -p out_root:=/data/searches -p brain_url:=http://127.0.0.1:8498 -p question:="where is the red mug?"; code=$?; set -e
test "$code" = 2
grep -h '"ended_because"' /data/searches/*/*/search.json | grep -q "not answering"
echo ALL PASSED
