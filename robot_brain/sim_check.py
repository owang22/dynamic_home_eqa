"""End-to-end check of the brain through HTTP, with rendered household A standing in for the robot.

Acts as the controller would:
  1. writes a positions file (one position per piece of furniture) and patrol folders in the
     go2_patrol layout (<date>/<HHMM>/<id>.jpg + patrol.json) from the rendered patrol pictures;
  2. POST /ingest_patrol for each patrol;
  3. for where-is questions: POST /ask, then walk the plan, POST /look with the rendered picture of
     that place at the question time, until done.
Scored with the renderer's truth (a look counts as found when the thing shows in that picture).

    python robot_brain/server.py --data robot_brain/data/sim --positions robot_brain/data/sim/positions.yaml &
    python robot_brain/sim_check.py prepare        # positions + patrol folders (needs no server)
    python robot_brain/sim_check.py run --days 1-6 --questions 20
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import shutil
import sys
import time

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "3d_rendering/results/vlm_night/questions"))
from client import Brain  # noqa: E402

SIM = HERE / "data" / "sim"
DAY0 = dt.datetime(2026, 9, 30, tzinfo=dt.timezone(dt.timedelta(hours=-7)))


def when(day, hhmm):
    return (DAY0 + dt.timedelta(days=day, hours=int(hhmm[:2]), minutes=int(hhmm[2:]))).isoformat()


def slug(key):
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")


def prepare(days):
    import yaml
    from world import World
    W = World()
    xz = W.furniture_xz()
    pos = [{"id": slug(f), "x": round(xz[f][0], 2), "y": round(xz[f][1], 2), "yaw_deg": 0.0, "pitch_deg": 0}
           for f in sorted(W.furniture)]
    SIM.mkdir(parents=True, exist_ok=True)
    (SIM / "positions.yaml").write_text(yaml.safe_dump({"positions": pos}, sort_keys=False))
    places = [{"id": slug(f), "description": f.split("|")[1], "room": f.split("|")[0].replace("_", " ")} for f in sorted(W.furniture)]
    (SIM / "places.json.in").write_text(json.dumps(places))
    n = 0
    for day, t, rooms in W.patrol_plan():
        if day not in days or not W.rendered(day, t):
            continue
        d = SIM / "patrols" / (DAY0 + dt.timedelta(days=day)).strftime("%Y-%m-%d") / t
        d.mkdir(parents=True, exist_ok=True)
        rows = []
        for f, spots in sorted(W.furniture.items()):
            if W.places[spots[0]]["room"] not in rooms:
                continue
            pid = slug(f)
            shutil.copy(W.picture(day, t, spots[0]), d / f"{pid}.jpg")
            rows.append({"id": pid, "result": "photographed", "picture": f"{pid}.jpg", "taken": when(day, t),
                         "target": {"x": xz[f][0], "y": xz[f][1]}})
        (d / "patrol.json").write_text(json.dumps({"started": when(day, t), "positions": rows}, indent=1))
        n += 1
    print(f"{len(pos)} positions, {n} patrol folders under {SIM / 'patrols'}")


def run(days, nq, url):
    from world import World
    import search
    W = World()
    b = Brain(url)
    print(b.health())
    b.set_places(json.loads((SIM / "places.json.in").read_text()))
    for folder in sorted((SIM / "patrols").glob("*/*")):
        d = dt.date.fromisoformat(folder.parent.name)
        if (d - DAY0.date()).days not in days:
            continue
        t0 = time.time()
        r = b.ingest_patrol(folder)
        print(f"ingested {folder.parent.name} {folder.name}: {len(r['observed'])} pictures in {time.time() - t0:.0f}s", flush=True)
    by_slug = {slug(f): f for f in W.furniture}
    qs = [q for q in json.loads((search.OUT / "questions.json").read_text())
          if q["day"] in days and q["day"] >= min(days) + 2][:nq]
    rows = []
    for q in qs:
        t0 = time.time()
        s = b.ask(search.where_q(q["type"]), time=when(q["day"], q["time"]))
        place, looks, res = s["plan"][0], [], "not found"
        while place:
            f = by_slug[place]
            r = b.look(s["session"], place, image_path=str(W.picture(q["day"], q["time"], W.furniture[f][0])),
                       time=when(q["day"], q["time"]), remember=False)
            there = search.present(W, q, f)
            looks.append((place, r["found"], there, r.get("first_answer")))
            if r["found"]:
                res = "found" if there else "false find"
                break
            place = r["next_place"]
        first = next((l for l in looks if l[3] == "yes"), None)   # where the search would have stopped without the close-up check
        res0 = "not found" if first is None else ("found" if first[2] else "false find")
        rows.append({"id": q["id"], "type": q["type"], "target": s["target"], "answer_type": s["answer_type"],
                     "plan": s["plan"], "looks": looks, "result": res, "result_without_check": res0,
                     "seconds": round(time.time() - t0, 1)})
        print(f"{q['type']:>20} day {q['day']} {q['time']}: {res} after {len(looks)} looks ({rows[-1]['seconds']}s) "
              f"target={s['target']!r} type={s['answer_type']}", flush=True)
    (SIM / "sim_results.json").write_text(json.dumps(rows, indent=1))
    n = len(rows)
    print(f"without the close-up check: found {sum(r['result_without_check'] == 'found' for r in rows)}/{n}, "
          f"false finds {sum(r['result_without_check'] == 'false find' for r in rows)}")
    print(f"found {sum(r['result'] == 'found' for r in rows)}/{n}, false finds {sum(r['result'] == 'false find' for r in rows)}, "
          f"median {sorted(r['seconds'] for r in rows)[n // 2]}s per question")


def parse_days(s):
    a, b = s.split("-")
    return set(range(int(a), int(b) + 1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "run"])
    ap.add_argument("--days", default="1-6")
    ap.add_argument("--questions", type=int, default=20)
    ap.add_argument("--url", default="http://127.0.0.1:8400")
    a = ap.parse_args()
    (prepare if a.cmd == "prepare" else lambda d: run(d, a.questions, a.url))(parse_days(a.days))
