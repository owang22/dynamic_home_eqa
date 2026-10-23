"""Offline tests of watch_for on real pictures from 2026-10-22 16:05-16:27 (labelled by eye: watch_data/labels.json,
1 = a person in a teal t-shirt is visible, 0 = no such person, A = the target is there but the shirt is hidden or a
sliver; A frames are left out of per-frame scores and count as "target present" for the gate).

    python3 watch_eval.py frames --url http://127.0.0.1:8301/v1 --tag 8b     # per-frame P(yes), latency
    python3 watch_eval.py gate --tag 8b                                       # k-of-n over the frame sequence
    python3 watch_eval.py e2e --url http://127.0.0.1:8301/v1 --tag 8b        # against fake_console.py
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from llm import LLM  # noqa: E402
from watch import FrameJudge, http, watch_for  # noqa: E402

PICS = HERE.parents[1] / "data" / "lab_agent" / "pictures"
LAB = json.load(open(HERE / "watch_data" / "labels.json"))
OUT = HERE / "watch_data" / "results"
QUESTION = "Is there a person wearing a teal t-shirt in this picture?"


def save(name, obj):
    OUT.mkdir(exist_ok=True)
    p = OUT / f"{name}.json"
    if p.exists():
        n = 1
        while (OUT / f"{name}_v{n}.json").exists():
            n += 1
        p.rename(OUT / f"{name}_v{n}.json")
    p.write_text(json.dumps(obj, indent=1))
    print("->", p)


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def frames(url, tag, question=QUESTION):
    judge = FrameJudge(LLM(url), question)
    judge(PICS.joinpath(LAB[0]["id"] + ".jpg").read_bytes())          # warm-up, not counted
    rows = []
    for f in LAB:                                                      # one at a time: honest per-frame latency
        t0 = time.time()
        j = judge(PICS.joinpath(f["id"] + ".jpg").read_bytes())
        rows.append({"id": f["id"], "teal": f["teal"], **j, "wall_s": round(time.time() - t0, 3)})
    save(f"frames_{tag}", {"question": question, "model": judge.vlm.model, "rows": rows})
    report_frames(rows)


def report_frames(rows):
    lat = [r["wall_s"] for r in rows]
    print(f"latency per frame: median {statistics.median(lat):.3f} s, p90 {pct(lat, .9):.3f} s, max {max(lat):.3f} s")
    for thr in (0.1, 0.3, 0.5, 0.7, 0.9):
        tp = sum(r["p_yes"] >= thr and r["teal"] == "1" for r in rows)
        fn = sum(r["p_yes"] < thr and r["teal"] == "1" for r in rows)
        fp = sum(r["p_yes"] >= thr and r["teal"] == "0" for r in rows)
        tn = sum(r["p_yes"] < thr and r["teal"] == "0" for r in rows)
        a_yes = sum(r["p_yes"] >= thr and r["teal"] == "A" for r in rows)
        print(f"thr {thr}: recall {tp}/{tp + fn}, false yes {fp}/{fp + tn}, accuracy {(tp + tn) / (tp + tn + fp + fn):.3f}"
              f" (A frames said yes: {a_yes}/{sum(r['teal'] == 'A' for r in rows)})")


def gate(tag, thr=0.5):
    rows = json.load(open(OUT / f"frames_{tag}.json"))["rows"]
    present = [r["teal"] in ("1", "A") for r in rows]
    yes = [r["p_yes"] >= thr for r in rows]
    # target segments = runs of present frames
    segs, cur = [], None
    for i, p in enumerate(present):
        if p and cur is None:
            cur = [i, i]
        elif p:
            cur[1] = i
        elif cur:
            segs.append(cur)
            cur = None
    if cur:
        segs.append(cur)
    out = {}
    for k, n in ((1, 1), (2, 2), (2, 3), (3, 3), (3, 4)):
        trig, ring, cool = [], [], 0
        for i, y in enumerate(yes):
            ring = (ring + [y])[-n:]
            if sum(ring) >= k:
                trig.append(i)
                ring = []        # after a stop, the watcher restarts with an empty window
        true = [i for i in trig if any(present[max(0, i - n + 1): i + 1])]
        false = [i for i in trig if i not in true]
        caught = [s for s in segs if any(s[0] <= i <= s[1] + n - 1 for i in true)]
        delays = [min(i for i in true if s[0] <= i <= s[1] + n - 1) - s[0] for s in caught]
        out[f"{k}of{n}"] = {"triggers": len(trig), "false_triggers": len(false), "false_per_100_frames":
                            round(100 * len(false) / len(rows), 1), "segments": len(segs), "segments_caught": len(caught),
                            "delay_frames": delays, "false_at": [rows[i]["id"] for i in false]}
        print(k, "of", n, json.dumps(out[f"{k}of{n}"]))
    save(f"gate_{tag}_thr{thr}", {"thr": thr, "segments": segs, "gates": out})


def e2e(url, tag, fps=1.0, k=2, n=3, hz=3.0, start=26, go_to_s=40.0, port=8497):
    """Fake console plays the labelled frames from index `start` at `fps` frames/s while a go_to blocks for
    go_to_s; the watcher must stop it. Also a negative run (frames with no target) for false stops."""
    import fake_console
    res = {}
    runs = {"positive": [f["id"] for f in LAB[start:start + 40]],                       # target appears at index 31
            "negative": [f["id"] for f in LAB[78:102]]}                                  # 24 frames, all 0
    for name, ids in runs.items():
        srv, C = fake_console.serve(ids, port, fps=fps, go_to_s=go_to_s)
        console = f"http://127.0.0.1:{port}"
        judge = FrameJudge(LLM(url), QUESTION)
        t0 = time.time()
        out = watch_for(console, judge, during=lambda: http(console, "POST", "/agent/go_to", {"place": "desk_oliver"},
                                                              timeout=go_to_s + 10)[1],
                        k=k, n=n, hz=hz, max_s=go_to_s + 5)
        calls = C.calls
        srv.shutdown()
        srv.server_close()
        first_pos = next((c["t"] for c in calls if c.get("call") == "GET /frame.jpg"
                          and LAB[[f["id"] for f in LAB].index(c["frame"])]["teal"] == "1"), None)
        stop_t = next((c["t"] for c in calls if c.get("call") == "POST stop"), None)
        ret = next((c for c in calls if c.get("call") == "go_to returned"), None)
        res[name] = {"hit": out["hit"], "stop_received_at": stop_t, "first_target_frame_served_at": first_pos,
                     "stop_after_first_target_s": None if stop_t is None or first_pos is None else round(stop_t - first_pos, 2),
                     "go_to_returned": ret, "frames_judged": len(out["frames"]),
                     "judge_s_median": statistics.median([f["secs"] for f in out["frames"] if "secs" in f]),
                     "loop_hz": round(len(out["frames"]) / out["secs"], 2), "hit_frames": out["hit_frames"],
                     "frames_served": [c["frame"] for c in calls if c.get("call") == "GET /frame.jpg"],
                     "wall_s": round(time.time() - t0, 2)}
        print(name, json.dumps({kk: v for kk, v in res[name].items() if kk not in ("frames_served",)})[:900])
    save(f"e2e_{tag}", res)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["frames", "gate", "e2e"])
    ap.add_argument("--url", default="http://127.0.0.1:8301/v1")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--thr", type=float, default=0.5)
    ap.add_argument("--question", default=QUESTION)
    ap.add_argument("--fps", type=float, default=1.0)
    a = ap.parse_args()
    if a.what == "frames":
        frames(a.url, a.tag, a.question)
    elif a.what == "gate":
        gate(a.tag, a.thr)
    else:
        e2e(a.url, a.tag, fps=a.fps)
