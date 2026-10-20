"""Write the robot's memory from the patrol pictures, one day at a time.

    python write_memory.py --height 1.0 [--days 3-7] [--spots 16] [--workers 16]

Two kinds of notes, both from the local Qwen3.8-27B with vision:
  caption   one picture -> a list of what is on the place (the plain baseline: ReMEmbR-style).
  evidence  the previous picture of this place and the new one, plus what is usually here ->
            what changed, how important it is to remember (0-3), and a guess at what happened.
            At the end of each day, a short "usually here" note per place is rewritten from the
            day's evidence notes (used by the next day's writer and at question time).
Picture keeping (which pictures stay for looking back) is decided in arms.py from these notes.
Writes out/memory_<height>.json: {"visits": [...], "usual": {day: {spot: text}}}. Resumable through
the call cache.
"""
from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor

import common as C

SYSTEM = ("You are the memory of a small home robot that patrols a house every two hours and photographs "
          "fixed places. Write short, factual notes. Name things by colour and kind (\"blue speckled mug\").")

CAPTION_SCHEMA = {"type": "object", "properties": {
    "things": {"type": "string", "maxLength": 300}}, "required": ["things"]}

CAPTION_ASK = ("This is the {place} at {time} on day {day}. List every object you can see on or at the {place}, "
               "short names with colour, separated by commas (at most 40 words). If the place is empty, say so.")

EVIDENCE_SCHEMA = {"type": "object", "properties": {
    "things": {"type": "string", "maxLength": 300},
    "changes": {"type": "array", "maxItems": 8, "items": {"type": "object", "properties": {
        "thing": {"type": "string", "maxLength": 60},
        "change": {"type": "string", "enum": ["appeared", "gone", "moved here", "moved within place", "state changed"]}},
        "required": ["thing", "change"]}},
    "importance": {"type": "integer", "enum": [0, 1, 2, 3]},
    "why_important": {"type": "string", "maxLength": 200},
    "guess": {"type": "string", "maxLength": 240}},
    "required": ["things", "changes", "importance", "why_important", "guess"]}

EVIDENCE_ASK = """The first picture is the {place} at {prev_time} (your previous visit). The second is the same place now, at {time} on day {day}.
What is usually here (your own note): {usual}

Write:
- things: every object you can see on or at the {place} now, short names with colour, separated by commas (at most 40 words).
- changes: what appeared, went, moved, or changed state since the previous visit (empty if nothing changed).
- importance: how important it is to keep this picture to answer later questions about what people did here, what was left behind, or what changed:
  0 nothing changed or ordinary; 1 small ordinary change; 2 a notable change (several things, someone's belongings, signs of an activity);
  3 unusual (something left behind or out of place, a mess, a safety issue).
- why_important: one sentence.
- guess: what probably happened here between the two visits, and who, if the pictures and the people sheet suggest it (say "unclear" otherwise).

People sheet:
{people}"""

EVIDENCE_FIRST = """This is the {place} at {time} on day {day} (your first visit; no earlier picture).
What is usually here (your own note): {usual}

Write: things (every object you can see on or at the {place}, short names with colour, comma separated, at most 40 words);
changes (empty); importance (0-3, how important it is to keep this picture for later questions about what people did,
what was left behind, or what changed); why_important; guess ("unclear" if nothing to say).

People sheet:
{people}"""

USUAL_SCHEMA = {"type": "object", "properties": {"usual": {"type": "string", "maxLength": 400}}, "required": ["usual"]}
USUAL_ASK = """Your notes about the {place} so far (oldest first):
{notes}

Previous "usually here" note: {usual}

Rewrite the "usually here" note: what is normally on this place, what comes and goes, and who uses it if the notes show it.
At most 60 words."""


def visits(height, days, spots):
    out = []
    for d in days:
        for t in C.TIMES:
            for s in spots:
                out.append({"id": f"d{d}_{t}_{s}", "day": d, "time": t, "spot": s, "place": C.spot_name(s),
                            "picture": str(p) if (p := C.picture(height, d, t, s)) else None})
    return out


def previous(vs, v):
    """The robot's last picture of this place (it keeps the last one per place in any case)."""
    same = [w for w in vs if w["spot"] == v["spot"] and (w["day"], w["time"]) < (v["day"], v["time"])]
    return same[-1] if same else None


def write_caption(v):
    if not v["picture"]:
        return {"things": "(no view of this place from the robot's camera)"}, {}
    out, info = C.ask(CAPTION_ASK.format(place=v["place"], time=C.hhmm(v["time"]), day=v["day"]),
                      images=[v["picture"]], schema=CAPTION_SCHEMA, system=SYSTEM, max_tokens=400)
    return out, info


def write_evidence(v, prev, usual):
    if not v["picture"]:
        return {"things": "(no view of this place from the robot's camera)", "changes": [], "importance": 0,
                "why_important": "no view", "guess": "unclear"}, {}
    fill = dict(place=v["place"], time=C.hhmm(v["time"]), day=v["day"], usual=usual or "(no note yet)",
                people=C.PEOPLE_SHEET)
    if prev and prev["picture"]:
        out, info = C.ask(EVIDENCE_ASK.format(prev_time=f"{C.hhmm(prev['time'])} on day {prev['day']}", **fill),
                          images=[prev["picture"], v["picture"]], schema=EVIDENCE_SCHEMA, system=SYSTEM, max_tokens=900)
    else:
        out, info = C.ask(EVIDENCE_FIRST.format(**fill), images=[v["picture"]], schema=EVIDENCE_SCHEMA,
                          system=SYSTEM, max_tokens=900)
    return out, info


def note_text(v):
    e = v.get("evidence") or {}
    ch = "; ".join(f"{c['thing']} {c['change']}" for c in e.get("changes", [])) or "no change"
    return f"day {v['day']} {C.hhmm(v['time'])}: {ch}. guess: {e.get('guess', '')}"


def write_usual(spot, place, vs_so_far, usual):
    notes = "\n".join(note_text(v) for v in vs_so_far[-24:])     # the last three days of visits at most
    out, _ = C.ask(USUAL_ASK.format(place=place, notes=notes, usual=usual or "(none)"), schema=USUAL_SCHEMA,
                   system=SYSTEM, max_tokens=300)
    return (out or {}).get("usual", usual or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--height", default="1.0")
    ap.add_argument("--days", default="3-7")
    ap.add_argument("--spots", type=int, default=len(C.PATROL))
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    lo, _, hi = a.days.partition("-")
    days = list(range(int(lo), int(hi or lo) + 1))
    spots = C.PATROL[:a.spots]
    vs = visits(a.height, days, spots)
    usual = {}                                   # usual[day][spot]: the note written at the end of that day
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as pool:
        for d in days:
            today = [v for v in vs if v["day"] == d]
            last_usual = usual.get(d - 1, {})

            def one(v):
                cap, ci = write_caption(v)
                ev, ei = write_evidence(v, previous(vs, v), last_usual.get(v["spot"]))
                v["caption"], v["evidence"] = cap, ev
                v["calls"] = {"caption": {k: ci.get(k) for k in ("seconds", "finish", "bad_text")},
                              "evidence": {k: ei.get(k) for k in ("seconds", "finish", "bad_text")}}
                return v
            list(pool.map(one, today))
            bad = [v["id"] for v in today if v["caption"] is None or v["evidence"] is None]
            usual[d] = dict(zip(spots, pool.map(
                lambda s: write_usual(s, C.spot_name(s), [v for v in vs if v["spot"] == s and v["day"] <= d
                                                         and v.get("evidence")], last_usual.get(s)), spots)))
            print(f"{time.strftime('%H:%M:%S')} height {a.height} day {d}: {len(today)} visits, "
                  f"{len(bad)} failed parses {bad[:4]}, {time.time() - t0:.0f} s, {C.stats()}", flush=True)
            C.dump({"height": a.height, "days": days, "spots": spots, "visits": [v for v in vs if "caption" in v],
                    "usual": usual}, a.out or C.OUT / f"memory_{a.height}.json")


if __name__ == "__main__":
    main()
