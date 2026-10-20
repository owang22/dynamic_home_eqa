"""The evidence notes written by Opus instead of Qwen (tests "Qwen is fine as the note writer"), 2026-10-19.

    python opus_write.py --height 1.0 [--workers 6]

Same prompts and output format as write_memory.py (EVIDENCE_ASK / EVIDENCE_FIRST / USUAL_ASK); Opus opens the two
pictures itself with the Read tool (only those two paths are given). Captions are copied from the Qwen memory
(no arm here uses them). Day by day, because the next day's writer reads the "usually here" notes.
Writes out/memory_<height>_opuswriter.json, answered with  opus.py --memory ... --tag _opuswriter.
"""
from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor

import common as C
import opus as OP
import write_memory as WM


def ask_opus(prompt, pictures, schema):
    files = "\n".join(f"picture {i + 1}: {p}" for i, p in enumerate(pictures))
    full = (f"{WM.SYSTEM}\n\nOpen these pictures with the Read tool, in this order, and no other file:\n{files}\n\n"
            f"{prompt}\n\nReply with only one JSON object that fits this JSON schema (use the enum values exactly):\n"
            f"{json.dumps(schema)}")
    r = OP.run_claude(full)
    return OP.parse(r.get("result")), r


def evidence(v, prev, usual):
    if not v["picture"]:
        return {"things": "(no view of this place from the robot's camera)", "changes": [], "importance": 0,
                "why_important": "no view", "guess": "unclear"}, {}
    fill = dict(place=v["place"], time=C.hhmm(v["time"]), day=v["day"], usual=usual or "(no note yet)",
                people=C.PEOPLE_SHEET)
    if prev and prev["picture"]:
        text = WM.EVIDENCE_ASK.format(prev_time=f"{C.hhmm(prev['time'])} on day {prev['day']}", **fill)
        text = text.replace("The first picture", "Picture 1").replace("The second", "Picture 2")
        return ask_opus(text, [prev["picture"], v["picture"]], WM.EVIDENCE_SCHEMA)
    return ask_opus(WM.EVIDENCE_FIRST.format(**fill), [v["picture"]], WM.EVIDENCE_SCHEMA)


def usual_note(spot, vs_so_far, usual):
    notes = "\n".join(WM.note_text(v) for v in vs_so_far[-24:])
    out, _ = ask_opus(WM.USUAL_ASK.format(place=C.spot_name(spot), notes=notes, usual=usual or "(none)"), [],
                      WM.USUAL_SCHEMA)
    return (out or {}).get("usual", usual or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--height", default="1.0")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    qmem = json.loads((C.OUT / f"memory_{a.height}.json").read_text())
    vs = [dict(v, evidence=None) for v in qmem["visits"]]
    spots = qmem["spots"]
    usual, t0, bad = {}, time.time(), []
    with ThreadPoolExecutor(a.workers) as pool:
        for d in qmem["days"]:
            today = [v for v in vs if v["day"] == d]
            last = usual.get(d - 1, {})

            def one(v):
                same = [w for w in vs if w["spot"] == v["spot"] and (w["day"], w["time"]) < (v["day"], v["time"])]
                ev, info = evidence(v, same[-1] if same else None, last.get(v["spot"]))
                if ev is None:
                    bad.append(v["id"])
                    ev = {"things": "?", "changes": [], "importance": 0, "why_important": "writer failed", "guess": "unclear"}
                v["evidence"] = ev
                return v
            list(pool.map(one, today))
            usual[d] = dict(zip(spots, pool.map(
                lambda s: usual_note(s, [v for v in vs if v["spot"] == s and v["day"] <= d and v.get("evidence")],
                                     last.get(s)), spots)))
            print(f"{time.strftime('%H:%M:%S')} opus writer {a.height} day {d}: {len(today)} visits, "
                  f"{len(bad)} failed so far, {time.time() - t0:.0f} s", flush=True)
            C.dump({"height": a.height, "days": qmem["days"], "spots": spots, "writer": "opus",
                    "visits": [v for v in vs if v["day"] <= d], "usual": usual},
                   C.OUT / f"memory_{a.height}_opuswriter.json")


if __name__ == "__main__":
    main()
