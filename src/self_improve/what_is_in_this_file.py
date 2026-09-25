"""The first lines of a report say what is in it, and what is not in it yet.

Tonight showed repeatedly that a number reported while a run was still going gets read as
final, and a footnote at the bottom does not stop that. So the header is built from the
directories at the moment the report runs - not from a hand-written note that can go stale -
and it names: which arms are in, how many cells each has of the number it should have, which
cells are running, which are being rerun, and that the file will be regenerated.

It is deliberately the first thing printed, ahead of the ceiling and everything else.
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
from typing import Dict, List, Optional


def _the_pid_is_alive(lock: pathlib.Path) -> bool:
    try:
        pid = json.loads(lock.read_text()).get("pid")
    except (OSError, ValueError):
        return False
    if not isinstance(pid, int):
        return False
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False


def _dir_name(arm: str) -> str:
    return arm.replace(" ", "_").replace(",", "")


def what_is_in_this_file(root: pathlib.Path, kind: str,
                         expected: Optional[Dict[str, int]] = None) -> List[str]:
    """`expected` maps arm name -> how many cells that arm should have when finished."""
    if expected is None:
        # A WAVE'S OWN TABLE FIRST. `EXPECTED_CELLS.json` in the wave directory says how many
        # cells each arm should have in THAT wave: the 24-questions wave runs three homes for
        # the model arms and ten for the no-model rule, so the ten-home default would have
        # reported five arms as permanently incomplete and buried the real gaps.
        here = root / "EXPECTED_CELLS.json"
        if here.exists():
            try:
                expected = {a: int(n) for a, n in json.loads(here.read_text()).items()}
            except (ValueError, TypeError):
                expected = None
    if expected is None:
        try:                                     # otherwise the runner's table
            from self_improve.overnight_wave import ARMS
            expected = {arm: spec[2] for arm, spec in ARMS.items()}
        except Exception:
            expected = {}
    by_dir = {_dir_name(arm): (arm, n) for arm, n in expected.items()}

    cells = root / "cells"
    complete, partial, missing, running, crashed = [], [], [], [], []
    for d in sorted(cells.glob("*")) if cells.exists() else []:
        if not d.is_dir():
            continue
        arm, want = by_dir.get(d.name, (d.name.replace("_", " "), 0))
        done = len(list(d.glob("*/cell.json")))
        # A LOCK FILE IS NOT A LIVE PROCESS. Until 2026-09-25 the runner removed the lock only
        # when a gate held a cell back, so a finished or crashed cell left one behind and any
        # count built from lock files overstated what was running. The lock records the pid
        # that took it, so that is what gets checked.
        alive = sum(1 for lock in d.glob("*/RUNNING.lock") if _the_pid_is_alive(lock))
        if alive:
            running.append(f"{arm} {alive}")
        for mark in sorted(d.glob("*/CRASHED.txt")):
            crashed.append(f"{arm} / {mark.parent.name}")
        if want and done >= want:
            complete.append(f"{arm} ({done})")
        else:
            partial.append(f"{arm} {done} of {want or '?'}")
    for dir_name, (arm, want) in sorted(by_dir.items()):
        if not (cells / dir_name).exists():
            missing.append(f"{arm} (0 of {want})")

    # QUESTIONS A DAY, read from the cells rather than from an argument, and every distinct
    # value shown. Two waves exist - ten homes at 8 a day, three homes at 24 - and a number
    # from one pooled with the other would be a pooled average of two designs. If more than
    # one value appears under one root, that is stated first and loudly.
    # from each cell's own searches.jsonl header, which every cell has written since long
    # before this was recorded in arm.json, so it also covers the cells already on disk
    found = set()
    for log in (cells.glob("*/*/searches.jsonl") if cells.exists() else ()):
        try:
            with log.open() as fh:
                found.add(str(json.loads(fh.readline()).get("questions_per_day",
                                                            "not recorded")))
        except (OSError, ValueError):
            found.add("unreadable")
    per_day = sorted(found)

    now = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    pending = partial + missing
    lines = [
        "",
        "#" * 100,
        f"# WHAT IS IN THIS FILE: {kind}, "
        f"{('QUESTIONS A DAY: ' + ', '.join(per_day)) if per_day else 'questions a day not recorded'}"
        f", generated {now}. "
        + ("NOT FINAL - see below." if pending or running else "All arms complete."),
        "#" * 100,
        f"#   COMPLETE: {', '.join(complete) if complete else 'none'}",
    ]
    if pending:
        lines.append(f"#   NOT COMPLETE: {'; '.join(pending)}")
    if running:
        lines.append(f"#   RUNNING RIGHT NOW: {'; '.join(running)} cells")
    if crashed:
        lines.append(f"#   CRASHED, not finished and not held by a gate: {'; '.join(crashed)}")
    for note in sorted((root / "cells").parent.glob("superseded_*/WHY.md")):
        if "socket" in note.parent.name:
            lines.append("#   BEING RERUN: the cells listed in "
                         f"{note.parent.name}/WHY.md, moved aside after a socket-timeout bug "
                         "was fixed. Not counted above.")
    if pending or running:
        lines.append("#   THIS FILE WILL BE REGENERATED when those land, and any number in it "
                     "can move.")
    if len(per_day) > 1:
        lines.insert(4, f"#   ** TWO DESIGNS UNDER ONE ROOT: cells here ran at "
                        f"{' and '.join(per_day)} questions a day. Nothing below should be "
                        f"pooled across them; separate the roots.")
    lines.append("#" * 100)
    return lines


def print_what_is_in_this_file(root: pathlib.Path, kind: str,
                               expected: Optional[Dict[str, int]] = None) -> List[str]:
    lines = what_is_in_this_file(root, kind, expected)
    for line in lines:
        print(line)
    return lines
