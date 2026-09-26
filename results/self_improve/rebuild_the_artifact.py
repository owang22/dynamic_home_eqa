#!/usr/bin/env python3
"""Rebuild the artifact page from whatever is on disk right now.

Run it as often as you like. It reads every finished and half-finished run under
results/self_improve/search_driven/ and three_prompts/, rewrites the page, and
prints one line saying what changed. It never deletes anything and never touches
a run. Publishing the page is a separate step and stays manual.

    python3 results/self_improve/rebuild_the_artifact.py
"""
import hashlib
import json
import pathlib
import re
import time
import sys

HERE = pathlib.Path("/tmp/claude-1027/-home-oliver-robot-dynamic-home-eqa/"
                    "f251de4b-be46-424b-b263-ac9df03b04dc/scratchpad")
SHELL, PAGE = HERE / "live_runs.html", HERE / "memory_inspector.html"
# Everything the reader shows in full - reasoning for each room, claim wordings, the
# wording a claim used to have, whole nightly summaries - goes into one file per cell
# instead of into the page. Two reasons. Nothing has to be cut short to keep the page
# under its 16 MB limit, which is what was cutting the nightly summaries off at 900
# characters when they already reach 1,733; and the page stays small while the wave grows
# from 29 cells to 70 full-length ones, which inline would be tens of megabytes.
TRACES = HERE / "traces"
RUNS = [pathlib.Path("results/self_improve/search_driven"),
        pathlib.Path("results/self_improve/three_prompts"),
        # the third way of writing notes, the one told whether its answers worked.
        # Same path shape as search_driven: <variant>/<home>/<arm>/<format>/
        pathlib.Path("results/self_improve/told_if_right"),
        # The overnight wave: the first comparison between these arms that means anything,
        # and the artifact could not see it. Its shape is <cells>/<arm>/<home>/ - two levels
        # rather than four, and the arm IS the memory format.
        pathlib.Path("results/self_improve/overnight_wave"),
        # The higher-resolution run: same shape as overnight_wave, 24 questions a day.
        pathlib.Path("results/self_improve/overnight_wave_24_questions"),
        # The faithful rebuilds, one directory each, shaped <run>/<home>/<arm>/<format>/.
        pathlib.Path("results/self_improve/ace_as_published"),
        pathlib.Path("results/self_improve/memgpt_as_published")]

ARM_ORDER = ["memory-guided_search", "prior_only,_no_notes",
             "newest_sighting,_no_model", "random"]


def was_text(w):
    """What a claim used to say, in full. Nothing is cut: the reader is for reading."""
    if isinstance(w, dict):
        return w.get("statement") or ""
    return w if isinstance(w, str) else ""


def read_cell(f, root):
    """One cell's questions and its notes. Path shape: <run>/<home>/<arm>/<format>/"""
    parts = f.relative_to(root).parts
    # Superseded and stopped-early trees are on disk on purpose and must never reach the
    # page: every one of them was set aside because something in it made a number mean
    # something other than what it said.
    if len(parts) < 4 or parts[0].startswith(("superseded", "stopped_early")):
        return None
    run, home, arm, fmt = parts[0], parts[1], parts[2], parts[3]
    if root.name.startswith("overnight_wave"):
        # <cells>/<arm>/<home>/searches.jsonl. Everything in this wave chooses rooms the same
        # way, so the arm names the memory and the sensing arm is read from the cell's own
        # header rather than guessed from the path.
        if parts[0] != "cells" or len(parts) < 3:
            return None
        fmt, home = parts[1], parts[2]
        run = "overnight" if root.name == "overnight_wave" else "overnight, 24 a day"
        try:
            arm = json.loads(f.open().readline()).get("sensing_arm") or "memory-guided_search"
        except (ValueError, OSError):
            arm = "memory-guided_search"
        arm = arm.replace(" ", "_")
    elif root.name == "three_prompts":
        # this tree is <run>/cells/<variant>/<home>/... so re-read it
        parts = f.relative_to(root).parts
        if "cells" in parts:
            i = parts.index("cells")
            run = parts[i + 1] if len(parts) > i + 1 else run
            home = parts[i + 2] if len(parts) > i + 2 else home
            arm, fmt = "memory-guided_search", "incremental_edits"
    questions, day_max, n = [], 0, 0
    for line in f.open():
        try:
            d = json.loads(line)
        except ValueError:
            continue          # a half-written final line while a run is live
        if d.get("kind") != "search":
            continue
        rooms = d.get("rooms_opened") or []
        questions.append({
            "cfg": run, "hh": home, "arm": arm, "fmt": fmt, "d": d.get("day"),
            "per": d.get("period"), "mv": 1 if d.get("is_a_mover") else 0,
            "n": d.get("n_rooms_opened") or len(rooms),
            "f1": 1 if (rooms and rooms[0] == d.get("true_room")) else 0,
            "fd": 1 if d.get("found_it") else 0,
            "cp": 1 if d.get("correct_place") else 0,
            "o": d.get("object_id"), "tp": d.get("true_place"),
            "ap": d.get("answer_place"), "ro": rooms,
            "wy": [w or "" for w in (d.get("why_each_room") or [])],
            "af": d.get("answered_from"), "ok": 1 if d.get("correct_place") else 0,
            "nl": d.get("n_lines_of_notes_available"),
        })
        n += 1
        day_max = max(day_max, d.get("day") or 0)
    notes = []
    npath = f.parent / "notes.json"
    if npath.exists():
        try:
            nd = json.loads(npath.read_text())
        except ValueError:
            nd = {}
        for c in nd.get("claims") or []:
            notes.append({"cfg": run, "hh": home, "arm": arm, "fmt": fmt, "kind": "claim",
                          "id": c.get("claim_id"), "st": c.get("statement") or "",
                          "day": c.get("first_written_day"), "stand": c.get("standing"),
                          # The evidence each claim cites. It was in notes.json all along
                          # and this script never read it, so the artifact could not show
                          # it. Both lists, because the interesting number is that the
                          # contradicting one is empty in 1,906 claims out of 1,906.
                          "sup": c.get("supporting_observation_ids") or [],
                          "con": c.get("contradicting_observation_ids") or [],
                          "holds": c.get("holds_under") or "",
                          "status": c.get("status") or "",
                          "rh": [{"d": r.get("day"), "was": was_text(r.get("was")),
                                  "why": r.get("why") or ""}
                                 for r in (c.get("revision_history") or [])]})
        for s in nd.get("nightly_summaries") or []:
            t = s.get("summary")
            notes.append({"cfg": run, "hh": home, "arm": arm, "fmt": fmt, "kind": "summary",
                          "id": "night " + str(s.get("day")),
                          "st": "\n".join(t) if isinstance(t, list) else str(t or ""),
                          "day": s.get("day"), "stand": None, "rh": []})
    # `fresh` is how many minutes ago this cell last wrote a question, so the page can tell a
    # cell that is STILL GOING from one that stopped part way. Without it every unfinished cell
    # looked the same, and a stalled cell read as a running one - which is the difference
    # between "wait" and "something is wrong".
    try:
        quiet = (time.time() - f.stat().st_mtime) / 60.0
    except OSError:
        quiet = None
    return questions, notes, {"cfg": run, "hh": home, "arm": arm, "fmt": fmt,
                              "n": n, "maxday": day_max,
                              "quiet": None if quiet is None else round(quiet, 1)}


def key_for(cell):
    """One filename-safe name for a cell, used as the key of its trace file."""
    raw = "~".join(str(cell[k]) for k in ("cfg", "hh", "arm", "fmt"))
    return re.sub(r"[^A-Za-z0-9_~.-]", "_", raw)


def main():
    questions, notes, cells = [], [], []
    for root in RUNS:
        if not root.is_dir():
            continue
        for f in sorted(root.rglob("searches.jsonl")):
            got = read_cell(f, root)
            if not got:
                continue
            q, nt, cell = got
            cell["key"] = key_for(cell)
            for row in q:
                row["key"] = cell["key"]
            for row in nt:
                row["key"] = cell["key"]
            questions += q
            notes += nt
            cells.append(cell)
    if not questions:
        print("no runs have written anything yet; page left alone")
        return 1

    # The page carries only what the plot needs. Everything the reader shows in full goes
    # into one file per cell, fetched when a point on the plot is clicked.
    live = json.dumps({"q": [{k: v for k, v in r.items()
                              if k in ("cfg", "hh", "arm", "fmt", "key",
                                       "d", "mv", "n", "f1", "fd", "cp")}
                             for r in questions],
                       "cells": cells}, separators=(",", ":"))
    if "</script>" in live:
        print("refusing to write: the page data would break out of its script tag")
        return 2

    TRACES.mkdir(parents=True, exist_ok=True)
    by_key = {}
    for row in questions:
        by_key.setdefault(row["key"], {"q": [], "notes": []})["q"].append(row)
    for row in notes:
        by_key.setdefault(row["key"], {"q": [], "notes": []})["notes"].append(row)
    written, total_bytes, biggest = [], 0, ("", 0)
    for key, payload in sorted(by_key.items()):
        blob = json.dumps(payload, separators=(",", ":"))
        if "</script>" in blob:
            print(f"refusing to write {key}: its text would break out of a script tag")
            return 2
        text = ("window.TR=window.TR||{};window.TR[" + json.dumps(key) + "]="
                + blob + ";\n")
        path = TRACES / f"{key}.js"
        path.write_text(text)
        written.append(path)
        total_bytes += len(text)
        if len(text) > biggest[1]:
            biggest = (path.name, len(text))
    # A trace file left behind by a cell that has since been moved away would still be
    # published and would still be loadable, so it goes.
    keep = {q.name for q in written}
    for stale in TRACES.glob("*.js"):
        if stale.name not in keep:
            stale.unlink()
            print(f"removed a trace file whose cell is gone: {stale.name}")

    page = SHELL.read_text().replace("__LIVE__", live)
    if "__TRACES__" in page:
        print("refusing to write: the page still expects its traces inline. Update "
              "live_runs.html to load them from the trace files instead.")
        return 3
    before = hashlib.sha256(PAGE.read_bytes()).hexdigest() if PAGE.exists() else ""
    PAGE.write_text(page)
    after = hashlib.sha256(PAGE.read_bytes()).hexdigest()

    done = sum(1 for c in cells if c["maxday"] >= 31)
    runs = sorted({c["cfg"] for c in cells})
    print(f"{len(questions)} questions · {len(notes)} notes entries · "
          f"{len(cells)} cells ({done} finished) · runs: {', '.join(runs)}")
    print(f"page {PAGE.name} {PAGE.stat().st_size/1e6:.2f} MB · "
          f"{'unchanged' if before == after else 'CHANGED, worth republishing'}")
    print(f"{len(written)} trace files, {total_bytes/1e6:.2f} MB in total, "
          f"biggest {biggest[0]} at {biggest[1]/1e3:.0f} KB")
    if biggest[1] > 16_000_000:
        print("WARNING: a trace file is over the 16 MB limit for one published file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
