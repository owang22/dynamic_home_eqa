"""Simple methods playing the same search task as a person (lived_home.play).

Each method sees the same patrol notes and has the same looks as the player. It
walks to pieces of furniture in its own order, and stops when the thing asked
for is visible there (it recognises it perfectly, unlike a person or a camera).
A thing counts as visible when some look would show it: on a surface, or in the
hands of someone standing at a piece of furniture.

When it has not seen the thing after its looks, a method with memory answers from
its patrol notes, as a player may (lived_home.play_cli `answer`):
- someone has it: the last patrol that saw the thing saw it in a resident's hands;
- put away: the last patrol saw it on a piece of furniture, and it is not visible
  there now (or wherever the method looked): put away in that furniture's drawers or
  cupboards, or, if it has none, in the nearest furniture of the same room that has;
- otherwise "can't tell".
Until 2026-10-13 every method answered "can't tell" here, so questions about
things put away or carried were never right (`--no-memory-answers` restores that).

Answers are judged as the play page judges a person (play_cli.Game.judge): found,
the right furniture for a thing put away, or the right person, is right; the right
room, someone-but-the-other-person, and "can't tell" are partly right; the rest is
wrong. Every question is scored, not only those a look could answer.

- nearest: no memory; always the nearest piece of furniture not yet looked at
- last seen: first where a patrol last saw the thing (any thing that fits the
  question), then nearest
- most often: furniture ranked by how many patrols saw the thing there, then
  nearest

The robot starts at the entrance and carries on from wherever the previous
question ended, as the player's robot does.

Usage:
  python -m lived_home.play_baselines <run>/play/play_data.json     a session's questions
  python -m lived_home.play_baselines <run> [--seed S]               every question in the run
  [--no-memory-answers]  the old rule: "can't tell" whenever not found
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import re

METHODS = ("nearest", "last seen", "most often")


def positions(data: dict) -> dict:
    return {f["key"]: (f["x"], f["z"]) for f in data["layout"]["furniture"] if f["x"] is not None}


def entry(data: dict, pos: dict):
    spot = data["layout"]["entry"]
    for f in data["layout"]["furniture"]:
        if any(s["id"] == spot for s in f["spots"]):
            return pos.get(f["key"])
    return next(iter(pos.values()))


HANDS = re.compile(r"^in (.+)'s hands$")


class Notes:
    """The patrol notes, read once: for each thing, its sightings in time order as
    (day, time, furniture, holder or None)."""

    def __init__(self, data: dict):
        first = {r["name"].split()[0]: r["id"] for r in data["residents"]}
        self.seen = collections.defaultdict(list)
        for p in data["patrols"]:
            for s in p["seen"]:
                for t, oid in zip(s["things"], s["oids"]):
                    m = HANDS.match(t.get("where") or "")
                    self.seen[oid].append(((p["day"], p["time"]), s["furniture"],
                                           first.get(m.group(1)) if m else None))

    def before(self, oids, when) -> list:
        out = [x for o in oids for x in self.seen.get(o, []) if x[0] < when]
        return sorted(out, key=lambda x: x[0])


def memory(notes: Notes, q: dict) -> tuple[collections.Counter, tuple | None]:
    """(sightings per furniture, last sighting) before the question, of any thing it accepts."""
    sight = notes.before(q["accept"], (q["day"], q["time"]))
    return collections.Counter(f for _, f, _ in sight), (sight[-1] if sight else None)


def put_away_guess(data: dict, fkey: str, pos: dict) -> str | None:
    """The furniture a thing last seen on fkey was most likely put away in: fkey
    itself if it has a closed spot, else the nearest furniture in its room that has."""
    F = {f["key"]: f for f in data["layout"]["furniture"]}
    closed = lambda k: any(s["kind"] == "closed" for s in F[k]["spots"])
    if fkey not in F:
        return None
    if closed(fkey):
        return fkey
    room = [k for k, f in F.items() if f["room"] == F[fkey]["room"] and closed(k)]
    if not room:
        return None
    if fkey in pos:
        return min(room, key=lambda k: math.dist(pos[fkey], pos[k]) if k in pos else 1e9)
    return room[0]


def judge(q: dict, ans: dict, F: dict) -> str:
    """'good', 'part' or 'bad', as play_cli.Game.judge."""
    if ans["type"] == "found":
        return "good"
    keys = list(q["answer"].values())
    for a in keys:
        if ans["type"] == "putaway" and a["kind"] == "put away" and ans.get("fkey") == a.get("furniture"):
            return "good"
    for a in keys:
        if ans["type"] == "putaway" and a["kind"] == "put away":
            if ans.get("fkey") and F.get(ans["fkey"], {}).get("room") == a.get("room"):
                return "part"
        if ans["type"] == "someone" and a["kind"] == "someone has it":
            return "good" if ans["who"] == a["who"] else "part"
        if ans["type"] == "out" and a["kind"] == "out of the house":
            return "good" if ans["who"] == a["who"] else "part"
    if ans["type"] == "cant":
        return "part"
    return "bad"


def play(data: dict, method: str, memory_answers: bool = True, notes: Notes | None = None) -> list:
    pos = positions(data)
    F = {f["key"]: f for f in data["layout"]["furniture"]}
    notes = notes or Notes(data)
    at = entry(data, pos)
    rows = []
    for q in data["questions"]:
        count, last = memory(notes, q)
        last_f = last[1] if last else None
        if method == "last seen":
            first = [last_f] if last_f else []
        elif method == "most often":
            first = [f for f, _ in count.most_common()]
        else:
            first = []
        looked, metres, found = [], 0.0, False
        for _ in range(data["rules"]["max_looks"]):
            todo = [f for f in first if f not in looked and f in pos]
            if todo:
                f = todo[0]
            else:
                rest = [f for f in pos if f not in looked]
                if not rest:
                    break
                f = min(rest, key=lambda k: math.dist(at, pos[k]))
            metres += math.dist(at, pos[f])
            at = pos[f]
            looked.append(f)
            if any(t["oid"] in q["accept"] for t in q["looks"].get(f, [])):
                found = True
                break
        if found:
            ans = {"type": "found"}
        elif memory_answers and method != "nearest" and last is not None:
            holder = last[2]
            where = last_f
            if holder:
                ans = {"type": "someone", "who": holder}
            else:
                g = put_away_guess(data, where, pos)
                ans = {"type": "putaway", "fkey": g} if g else {"type": "cant"}
        else:
            ans = {"type": "cant"}
        # findable by a look: on a surface, or in the hands of someone standing at furniture
        findable = any(t["oid"] in q["accept"] for ts in q["looks"].values() for t in ts)
        truth = sorted({a["kind"] for a in q["answer"].values()})
        rows.append({"n": q["n"], "kind": q["kind"], "truth": "/".join(truth), "visible": findable,
                     "found": found, "answer": ans["type"], "verdict": judge(q, ans, F),
                     "looks": len(looked), "metres": round(metres, 1)})
    return rows


WITHIN = (1, 2, 3)


def summary(rows: list) -> dict:
    vis = [r for r in rows if r["visible"]]
    v = collections.Counter(r["verdict"] for r in rows)
    return {"questions": len(rows), "right": v["good"], "partly": v["part"], "wrong": v["bad"],
            "right_share": round(v["good"] / max(1, len(rows)), 3),
            "visible": len(vis), "found": sum(r["found"] for r in vis),
            **{f"found_within_{k}": sum(r["found"] and r["looks"] <= k for r in vis) for k in WITHIN},
            "looks_when_found": round(sum(r["looks"] for r in vis if r["found"]) / max(1, sum(r["found"] for r in vis)), 1),
            "metres": round(sum(r["metres"] for r in rows), 1)}


def by_truth(rows: list, field: str = "truth") -> dict:
    """Right / all, by where the thing really was (or by the question's kind)."""
    out = collections.defaultdict(collections.Counter)
    for r in rows:
        out[r[field]]["n"] += 1
        out[r[field]][r["verdict"]] += 1
    return {k: dict(v) for k, v in sorted(out.items())}


def score(data: dict, memory_answers: bool = True) -> dict:
    notes = Notes(data)
    res = {}
    for m in METHODS:
        rows = play(data, m, memory_answers, notes)
        res[m] = {"summary": summary(rows), "by_truth": by_truth(rows),
                  "by_kind": by_truth(rows, "kind"), "rows": rows}
    return res


def print_table(res: dict, title: str) -> None:
    print(title)
    print("method      | right / partly / wrong of all questions | found within 1/2/3/all looks (of visible)")
    for m, r in res.items():
        s = r["summary"]
        within = " / ".join(str(s[f"found_within_{k}"]) for k in WITHIN)
        print(f"{m:11s} | {s['right']} / {s['partly']} / {s['wrong']} of {s['questions']} "
              f"({100 * s['right_share']:.0f}% right) | {within} / {s['found']} of {s['visible']}")
    for field, label in (("by_truth", "where the thing really was"), ("by_kind", "question kind")):
        print(f"right / questions, by {label}:")
        kinds = sorted({k for r in res.values() for k in r[field]})
        for k in kinds:
            print(f"  {k:28s} " + "  ".join(
                f"{m}: {res[m][field].get(k, {}).get('good', 0)}/{res[m][field].get(k, {}).get('n', 0)}"
                for m in res))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=pathlib.Path, help="play_data.json, or a run folder for every question")
    ap.add_argument("--seed", type=int, help="patrol seed for a run folder (default: the session's)")
    ap.add_argument("--no-memory-answers", action="store_true")
    ap.add_argument("--out", type=pathlib.Path)
    a = ap.parse_args()
    if a.path.is_dir():
        from lived_home.play import build_all
        seed = a.seed
        if seed is None:
            sess = a.path / "play" / "play_data.json"
            seed = int(json.loads(sess.read_text())["session"].rsplit("-s", 1)[1]) if sess.exists() else 0
        data = build_all(a.path, seed)
        out = a.out or a.path / "play" / "baselines_all_questions.json"
    else:
        data = json.loads(a.path.read_text())
        out = a.out or a.path.parent / "baselines.json"
    res = score(data, not a.no_memory_answers)
    out.write_text(json.dumps({m: {k: v for k, v in r.items() if k != "rows" or len(r["rows"]) <= 500}
                               for m, r in res.items()}, indent=1))
    print_table(res, f"{data['session']}: {len(data['questions'])} questions"
                + (" (no answers from memory)" if a.no_memory_answers else ""))


if __name__ == "__main__":
    main()
