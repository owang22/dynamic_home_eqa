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
from typing import Any, Dict, List, Tuple
import pathlib
import re
import time
import sys

# WHERE THE PAGE COMES FROM AND WHERE IT IS BUILT. The shell is the page's whole source - its
# layout, its eight ready-made comparisons, the reader, the instructions panel - and until
# 2026-09-27 it lived ONLY in a session scratchpad under /tmp, so a day of work on it would have
# gone when that directory was cleared and this script would then have had nothing to build from.
# It is in the repository now. The built page and the per-cell trace files still go to the
# scratchpad, because they are large, regenerable, and published from there.
SHELL = pathlib.Path(__file__).resolve().parent / "the_live_page" / "live_runs.html"
HERE = pathlib.Path("/tmp/claude-1027/-home-oliver-robot-dynamic-home-eqa/"
                    "f251de4b-be46-424b-b263-ac9df03b04dc/scratchpad")
PAGE = HERE / "memory_inspector.html"
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
        # The reason-first wave, 2026-09-25 onward. Same shape and same three households; every
        # schema now puts the reasoning before the decision. The wave above is its ablation.
        pathlib.Path("results/self_improve/wave_reasons_first"),
        # 2026-09-26. Three waves, three output directories, because household names REPEAT
        # across bank sets and a cell directory is built from the arm and the household only:
        # the five wider homes carry the names hh_s32 and hh_s48 and are not those homes.
        pathlib.Path("results/self_improve/wave_wider_five"),
        pathlib.Path("results/self_improve/wave_the_family_reads_the_log"),
        pathlib.Path("results/self_improve/wave_the_second_illness"),
        # 2026-09-27, the observation budget sweep: the same homes and arms at 8 and at 4
        # questions a day, against the 24 a day above.
        # 2026-09-27: told, told-with-a-profile and the untold parent on the five wider homes,
        # which is where the prior-over-an-unseen-situation claim has to replicate.
        pathlib.Path("results/self_improve/wave_told_on_the_wider_homes"),
        pathlib.Path("results/self_improve/wave_the_budget_sweep_q8"),
        pathlib.Path("results/self_improve/wave_the_budget_sweep_q4"),
        # The faithful rebuilds, one directory each, shaped <run>/<home>/<arm>/<format>/.
        pathlib.Path("results/self_improve/ace_as_published"),
        pathlib.Path("results/self_improve/memgpt_as_published")]

# How many days each run was asked to reach, where it is not the usual 32 (day 0 to day 31).
LAST_DAY_BY_RUN = {"a second illness": 49}

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
    if root.name.startswith("overnight_wave") or root.name.startswith("wave_"):
        # <cells>/<arm>/<home>/searches.jsonl. Everything in this wave chooses rooms the same
        # way, so the arm names the memory and the sensing arm is read from the cell's own
        # header rather than guessed from the path.
        if parts[0] != "cells" or len(parts) < 3:
            return None
        fmt, home = parts[1], parts[2]
        run = {"overnight_wave": "overnight",
               "overnight_wave_24_questions": "overnight, 24 a day",
               "wave_reasons_first": "reasons first",
               "wave_wider_five": "five wider homes",
               "wave_the_family_reads_the_log": "the family reads the log",
               "wave_the_second_illness": "a second illness",
               "wave_told_on_the_wider_homes": "told, on the wider homes",
               "wave_the_budget_sweep_q8": "eight a day, wider homes",
               "wave_the_budget_sweep_q4": "four a day, wider homes",
               # A wave added without a label here used to fall through to the path's first
               # part, which for every one of these trees is the word "cells".
               }.get(root.name, root.name)
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
        # THE PROFILES, for the arm that keeps one per person. They are part of that arm's memory
        # and the page could not see them at all, which is the same fault as a run with no line:
        # a thing the study turns on, invisible on the page that exists to show it. A profile has
        # no per-night history, so each is shown as it stands, dated to the last night written.
        for name, text in sorted((nd.get("profiles") or {}).items()):
            notes.append({"cfg": run, "hh": home, "arm": arm, "fmt": fmt, "kind": "profile",
                          "id": "who " + name, "st": text,
                          "day": nd.get("written_up_to_day"), "stand": None, "rh": []})
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
    # THE LAST DAY IS PER CELL, NOT PER STUDY. Every run was 32 days until the two-illness
    # episodes, which are 50, and the page used one global 31 to decide whether a cell had
    # finished - so a 50-day cell would have read "still going" at day 31 and for ever after.
    # Taken from the cell's own record where it has one, and from the run's own length where it
    # is still writing.
    last_day = LAST_DAY_BY_RUN.get(run, 31)
    done_file = f.parent / "cell.json"
    if done_file.exists():
        try:
            said = json.loads(done_file.read_text()).get("last_day")
            if isinstance(said, int):
                last_day = said
        except (ValueError, OSError):
            pass
    # A CELL A GATE HELD BACK IS NOT A FINISHED CELL, and until 2026-09-28 the page could not tell
    # the difference. `run_one_cell` writes cell.json, then the gates run, and a cell that fails
    # one has its file renamed to cell_HELD_FOR_REVIEW.json with the reason in why.txt beside it
    # (overnight_wave.py:259-273). The held cell still has a full searches.jsonl - it ran to the
    # last day, it just wrote nothing on the night its completion did not parse - so it reached
    # this page as an ordinary complete cell and a reader had no way to know a gate rejected it.
    # Two such cells exist, both MemGPT as published at 24 questions a day. They are SHOWN rather
    # than skipped, because the parse failure is a number this study reports rather than reruns
    # away; what changes is that they are labelled.
    held = f.parent / "cell_HELD_FOR_REVIEW.json"
    why_held = ""
    if held.exists():
        note = f.parent / "why.txt"
        if note.exists():
            why_held = note.read_text().strip().splitlines()[-1].strip()
        why_held = why_held or "a gate held this cell back; see why.txt beside it"
    return questions, notes, {"cfg": run, "hh": home, "arm": arm, "fmt": fmt,
                              "n": n, "maxday": day_max, "lastday": last_day,
                              "held": why_held,
                              "quiet": None if quiet is None else round(quiet, 1)}


def the_words_each_memory_is_given() -> Dict[str, Any]:
    """The ACTUAL instructions, lifted out of the module that writes them.

    Not a description of an arm, the words themselves. Written because "made to say what will
    change" is a phrase on a plot and a reader has no way to know what the model was really asked
    unless the prompt is on the page beside its line. Anything that is a paragraph added on only
    some nights says which nights, because an instruction that appears twice in a month is not the
    same as one that appears every night.
    """
    from self_improve import what_the_robot_is_told as told
    from self_improve import memory_notes as mem
    out: Dict[str, Any] = {}
    # KEYED THE WAY THE PAGE KEYS A LINE. The page's `fmt` is the cell directory name, which
    # `overnight_wave.cell_dir` builds from the ARM name as `arm.replace(" ", "_").replace(",", "")`
    # - not the memory format's name. Keyed by the format, every lookup on the page missed and the
    # panel would have read "no instructions recorded" for every arm.
    from self_improve.overnight_wave import ARMS
    for method, lines in told.HOW_YOUR_MEMORY_WORKS.items():
        out[method] = {"every night": [l for l in lines if l]}
    profile_arms = [mem.A_PROFILE_OF_EACH_PERSON, mem.A_PROFILE_AND_TOLD]
    for method in profile_arms:
        if method in out:
            out[method]["every night, about the people"] = [
                l for l in told.the_profiles({"Tomas": "(what it has worked out so far)"},
                                             "Tomas works from home, Ines is retired. "
                                             "They are a couple.") if l]
    if mem.TOLD_AND_ASKED_WHAT_CHANGES in out:
        out[mem.TOLD_AND_ASKED_WHAT_CHANGES][
            "ONLY on the two nights a sentence arrives, and on no other night"] = [
            l for l in told.what_to_write_before_you_have_seen_it() if l]
    told_arms = {mem.TOLD_THE_NIGHT_BEFORE: "the night BEFORE the routine changes, and the night "
                                            "before it changes back",
                 mem.TOLD_ON_THE_FIRST_NIGHT: "the first changed night, and the first ordinary "
                                              "night again",
                 mem.A_PROFILE_AND_TOLD: "the first changed night, and the first ordinary night "
                                         "again",
                 mem.TOLD_AND_ASKED_WHAT_CHANGES: "the night BEFORE the routine changes, and the "
                                                  "night before it changes back"}
    for method, when in told_arms.items():
        if method in out:
            out[method]["the one sentence it is told, on " + when] = [
                "Something you have been told, which you did not see for yourself: Tomas is "
                "unwell and is staying at home instead of going out.",
                "(and on the other night) Something you have been told, which you did not see "
                "for yourself: Tomas is better and is back to their usual routine."]
    for method in (mem.THE_LOG_AND_THE_ROUTINE_EIGHT, mem.THE_LOG_AND_THE_ROUTINE_SIXTEEN):
        if method in told.HOW_YOUR_MEMORY_WORKS:
            continue
        # these two share the parent's words and differ only in the number in this sentence
        out.setdefault(method, {"every night": [
            l for l in told.HOW_YOUR_MEMORY_WORKS[mem.THE_LOG_AND_THE_ROUTINE] if l]})
    n = {mem.THE_LOG_AND_THE_ROUTINE_EIGHT: 8, mem.THE_LOG_AND_THE_ROUTINE_SIXTEEN: 16}
    for method, many in n.items():
        out[method]["every night, the limit it is given"] = [
            l for l in told.how_many_notes_you_may_write(many) if l]
    # FOUR FORMATS INHERIT THEIR WORDS RATHER THAN DECLARING THEM, and the panel read "no
    # instructions recorded" for all four until this was added. The two told arms and the counted
    # allowance are our arm word for word, differing only in a sentence delivered on some nights or
    # in a number; ACE writes its memory through its own module and is not in the shared table at
    # all, so what it is told is stated rather than lifted, and says so.
    for method in (mem.TOLD_THE_NIGHT_BEFORE, mem.TOLD_ON_THE_FIRST_NIGHT,
                   mem.THE_LOG_AND_THE_ROUTINE_DERIVED_ALLOWANCE):
        out.setdefault(method, {"every night": [
            l for l in told.HOW_YOUR_MEMORY_WORKS[mem.THE_LOG_AND_THE_ROUTINE] if l]})
    out[mem.THE_LOG_AND_THE_ROUTINE_DERIVED_ALLOWANCE][
        "every night, the limit it is given"] = [
        "The same sentence as the arms above, with the number counted from what the night saw "
        "rather than fixed: it may write as many notes as the day earned, the same rule the "
        "control uses. Measured over the runs, that came out between 40 and 97 a night."]
    out[mem.ACE_AS_PUBLISHED] = {"how its memory works": [
        "ACE (Zhang et al., arXiv 2510.04618) is not in the shared table of instructions, because "
        "it writes its memory through its own module rebuilt from their shipped code rather than "
        "through the nightly prompt every other arm uses. What it is given each night: the day it "
        "just had, its own claims, a reflection step repeated up to three times whenever something "
        "went wrong, and a merging step with candidate pairs proposed by meaning and the merged "
        "wording written by the model. Only ADD is actually applied, as in their code.",
        "So the words below are not shown for this arm, because there are none to lift: its "
        "prompts live in src/self_improve/write_the_notes_told_if_right.py and the grouping module "
        "beside it."]}
    # now map every arm the runner knows onto the words of its format, under the directory name
    by_dir: Dict[str, Any] = {}
    for arm_name, (fmt, _sensing, _budget) in ARMS.items():
        words = out.get(fmt)
        if words:
            by_dir[arm_name.replace(" ", "_").replace(",", "")] = words
    # and keep the format names too, so a cell written before an arm was renamed still resolves
    for fmt, words in out.items():
        by_dir.setdefault(fmt.replace(" ", "_").replace(",", ""), words)
    return by_dir


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
    # ONE ROW PER QUESTION, AND THE PAGE HAS A 16 MB CEILING. Written out as objects, the
    # 73,665 rows came to 16.34 MB and the publish would have been refused: five of the eleven
    # fields are the cell's name, repeated on every one of its 744 questions, and the field
    # names themselves were repeated too. The five are 1:1 with each other, so they are listed
    # once per cell and a row carries the index. 16.3 MB becomes about 1.7 MB, and the page
    # rebuilds the same objects at load, so nothing downstream of `Q` changes.
    seen: Dict[Tuple[str, str, str, str, str], int] = {}
    cellkeys: List[List[str]] = []
    rows: List[List[Any]] = []
    for r in questions:
        name = (r["cfg"], r["hh"], r["arm"], r["fmt"], r["key"])
        if name not in seen:
            seen[name] = len(cellkeys)
            cellkeys.append(list(name))
        rows.append([seen[name], r["d"], r["mv"], r["n"],
                     r.get("f1"), r["fd"], r["cp"]])
    live = json.dumps({"cellkeys": cellkeys, "rows": rows, "cells": cells,
                       # The words each memory is actually given, keyed by the memory format, so a
                       # reader can see what "made to say what will change" really asked for
                       # rather than taking a line's name for it.
                       "words": the_words_each_memory_is_given()},
                      separators=(",", ":"))
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
    # THE VERDICT IGNORES THE "minutes quiet" CLOCK, and it did not until 2026-09-27. Every cell
    # carries how long since it last wrote, which ticks up whether or not anything happened - so
    # two builds of identical data always differed and the page always said CHANGED. On an idle
    # machine that made the check publish a new version every time, with nothing in it but larger
    # numbers in a staleness field. Diffed to be sure: between two builds of the same data, the
    # `quiet` values were the ONLY difference.
    def what_it_says_apart_from_how_stale_it_is(text: str) -> str:
        return re.sub(r'"quiet":[0-9.]+', '"quiet":0', text)

    before = (what_it_says_apart_from_how_stale_it_is(PAGE.read_text())
              if PAGE.exists() else "")
    PAGE.write_text(page)
    after = what_it_says_apart_from_how_stale_it_is(PAGE.read_text())

    # A held cell reached its last day, so counting by day alone called it finished.
    done = sum(1 for c in cells if c["maxday"] >= c["lastday"] and not c.get("held"))
    n_held = sum(1 for c in cells if c.get("held"))
    runs = sorted({c["cfg"] for c in cells})
    print(f"{len(questions)} questions · {len(notes)} notes entries · "
          f"{len(cells)} cells ({done} finished"
          + (f", {n_held} HELD BY A GATE" if n_held else "")
          + f") · runs: {', '.join(runs)}")
    print(f"page {PAGE.name} {PAGE.stat().st_size/1e6:.2f} MB · "
          f"{'unchanged' if before == after else 'CHANGED, worth republishing'}")
    print(f"{len(written)} trace files, {total_bytes/1e6:.2f} MB in total, "
          f"biggest {biggest[0]} at {biggest[1]/1e3:.0f} KB")
    if biggest[1] > 16_000_000:
        print("WARNING: a trace file is over the 16 MB limit for one published file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
