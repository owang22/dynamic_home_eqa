"""Notice when a cell stops. A dead run must announce itself instead of looking slow.

Every cell appends one timestamped line per completed night to
`results/self_improve/three_prompts/heartbeats.jsonl` (see `three_prompts.beat`). That
file records where each cell got to; it does not notice when one stops. This does.

Every pass it writes `HEARTBEAT.md` - one file a reader can open - with, for each cell
launched: the last night it finished, how long ago that was, whether its process is
still alive, and its session id, so the detachment can be checked rather than inferred
from the command that was typed. Anything silent for longer than `--stall-minutes` is
listed at the TOP under STALLED, with the verdict spelled out.

WHY THE SESSION ID IS IN HERE. A bare `nohup ... &` from a tool shell dies with that
shell. `setsid` is supposed to prevent it, and whether it did cannot be read off the
command line: it has to be read off the process. A child whose session id differs from
the launcher's is detached; one that shares it is not, and will die when the launcher is
reaped. A pids.txt full of dead PIDs is worse than no file, because it looks like
evidence of a running job.

    python -m self_improve.watch_the_heartbeats --once
    python -m self_improve.watch_the_heartbeats --every 60      # loops
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import time
from typing import Any, Dict, List, Optional, Tuple


EXPECTED_ARMS = ("control", "rival_beliefs", "describe_the_person", "told_unwell",
                 "rival_and_describe", "control_wholesale")
EXPECTED_HOMES = 10

WAVE_LEGEND = {
    "home1": "FIRST WAVE, SUPERSEDED. The 8-line read budget was still applied at answer "
             "time. Stopped deliberately at 19:59 and moved to "
             "superseded_8_line_budget_2026-09-24/.",
    "control9": "FIRST WAVE, SUPERSEDED, same reason as home1.",
    "nolimit": "Second wave: no read cap and no budget sentence. Its launcher was killed "
               "at 20:14 because it kept filling freed slots with queued cells while a "
               "relaunch of the same cells was in flight. Its non-wholesale cells are "
               "sound and still running; its control_wholesale cells were discarded.",
    "wholesale_nolimit": "SUPERSEDED. A relaunch of control_wholesale that collided with "
                         "still-alive pre-patch processes, because the launcher recorded a "
                         "subshell pid instead of python's. All discarded to "
                         "superseded_two_writers_same_cell/.",
    "rest": "Third wave, current: every cell not already running or finished, launched "
            "after the launcher was fixed to exec python and after run_one_arm took a "
            "per-cell lock. control_wholesale also has its 2400-character schema ceiling "
            "lifted to 24000 here.",
}


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def session_of(pid: int) -> Optional[int]:
    try:
        stat = pathlib.Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    # comm can contain spaces and brackets, so split after the closing bracket
    fields = stat[stat.rfind(")") + 2:].split()
    try:
        return int(fields[3])          # session id is field 6 overall
    except (IndexError, ValueError):
        return None


def read_the_beats(path: pathlib.Path, by_pid: bool = False
                   ) -> Dict[Tuple[Any, ...], Dict[str, Any]]:
    """The newest beat per cell, or per PROCESS when `by_pid`.

    Keying only on (arm, home) let a dead process inherit its live replacement's beat, so a
    cell that had been killed eighteen minutes earlier showed as running. A row must be
    judged on the beats of ITS OWN process.
    """
    latest: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    if not path.exists():
        return latest
    for line in path.open():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        key = ((row.get("pid"),) if by_pid
               else (row.get("arm", "?"), row.get("household", "?")))
        if key not in latest or row.get("epoch", 0) >= latest[key].get("epoch", 0):
            latest[key] = row
    return latest


def launched_pids(root: pathlib.Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for pid_file in sorted(root.glob("logs/*/pids.txt")):
        for line in pid_file.read_text().splitlines():
            bits = line.split()
            if len(bits) < 3 or not bits[0].isdigit():
                continue
            pid = int(bits[0])
            out.append({"wave": pid_file.parent.name, "pid": pid,
                        "arm": bits[1], "household": bits[2],
                        "alive": alive(pid), "sid": session_of(pid)})
    return out


def live_cells() -> Dict[Tuple[str, str], List[int]]:
    """(arm, household) -> the pids of the PYTHON processes writing it, from ps.

    This is the authoritative liveness signal. `pids.txt` is not: the second wave's
    launcher wrapped python in a subshell, so it recorded subshell pids whose children
    outlived them - keying on those made 27 live cells look dead. pids.txt is used only to
    label which wave a cell belongs to.
    """
    import subprocess
    out: Dict[Tuple[str, str], List[int]] = {}
    try:
        ps = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True).stdout
    except OSError:
        return out
    for line in ps.splitlines():
        if "three_prompts --arm" not in line or "grep" in line:
            continue
        bits = line.split()
        try:
            key = (bits[bits.index("--arm") + 1], bits[bits.index("--household") + 1])
        except ValueError:
            continue
        out.setdefault(key, []).append(int(bits[0]))
    return out


def wave_of(root: pathlib.Path) -> Dict[Tuple[str, str], str]:
    """The LAST wave that listed each cell, from the pids files in modification order."""
    out: Dict[Tuple[str, str], str] = {}
    for pid_file in sorted(root.glob("logs/*/pids.txt"), key=lambda p: p.stat().st_mtime):
        for line in pid_file.read_text().splitlines():
            bits = line.split()
            if len(bits) < 3 or not bits[0].isdigit():
                continue
            out[(bits[1], bits[2])] = pid_file.parent.name
    return out


def one_pass(root: pathlib.Path, stall_minutes: float) -> Dict[str, Any]:
    now = time.time()
    beats = read_the_beats(root / "heartbeats.jsonl")
    living = live_cells()
    waves = wave_of(root)
    finished_cells = {(arm, path.name)
                      for arm in EXPECTED_ARMS
                      for path in sorted((root / "cells" / arm).glob("*"))
                      if (path / "cell.json").exists()}

    rows: List[Dict[str, Any]] = []
    for key in sorted(set(beats) | set(living) | finished_cells):
        arm, household = key
        beat = beats.get(key)
        pids_here = living.get(key, [])
        finished = key in finished_cells
        quiet = (now - beat["epoch"]) / 60 if beat else None
        is_alive = bool(pids_here)
        rows.append({
            "arm": arm, "household": household,
            "wave": waves.get(key, "(not in any pids.txt)"),
            "pid": pids_here[0] if pids_here else (beat.get("pid") if beat else None),
            "n_live_processes": len(pids_here),
            "alive": is_alive,
            "sid": (session_of(pids_here[0]) if pids_here
                    else (beat.get("sid") if beat else None)),
            "last_night": beat.get("day") if beat else None,
            "last_day": beat.get("last_day") if beat else None,
            "minutes_since_its_last_night": round(quiet, 1) if quiet is not None else None,
            "finished": finished,
            "dead_and_unfinished": not finished and not is_alive,
            "stalled": (not finished and (not is_alive or quiet is None
                                          or quiet > stall_minutes)),
        })

    stalled = [r for r in rows if r["stalled"]]
    dead = [r for r in rows if r["dead_and_unfinished"]]
    running = [r for r in rows if not r["finished"] and not r["stalled"]]
    done = [r for r in rows if r["finished"]]
    duplicates = {(r["arm"], r["household"]): r["n_live_processes"]
                  for r in rows if r["n_live_processes"] > 1}
    sids = sorted({r["sid"] for r in rows if r["alive"] and r["sid"] is not None})
    mine = os.getsid(0)

    lines = [
        "# three_prompts heartbeat",
        "",
        f"Written {datetime.datetime.now().astimezone().isoformat(timespec='seconds')} "
        f"by `watch_the_heartbeats.py`. A cell beats once per completed night. "
        f"Silence longer than {stall_minutes:g} minutes counts as STALLED.",
        "",
        f"**{len(done)} finished, {len(running)} running, {len(stalled)} STALLED** "
        f"(of which {len(dead)} have no live process at all). "
        f"One row per CELL, liveness read from `ps` rather than from a pids file.",
        "",
    ]
    if stalled:
        lines += ["## STALLED - these are not slow, they have stopped", "",
                  "| arm | home | last night | quiet for | pid | alive | sid | wave |",
                  "|---|---|---|---|---|---|---|---|"]
        for r in sorted(stalled, key=lambda r: (r["arm"], r["household"])):
            lines.append(
                f"| {r['arm']} | {r['household']} | "
                f"{r['last_night'] if r['last_night'] is not None else 'never beat'} of "
                f"{r['last_day']} | "
                f"{r['minutes_since_its_last_night'] if r['minutes_since_its_last_night'] is not None else '-'} min | "
                f"{r['pid']} | {'yes' if r['alive'] else 'NO'} | {r['sid']} | {r['wave']} |")
        lines += ["",
                  "A stalled cell whose process is **NO** longer alive died or was "
                  "stopped; one that is alive is wedged. Neither will finish on its own.",
                  ""]
    else:
        lines += ["No cell has been silent longer than the stall threshold.", ""]

    lines += ["## detachment", "",
              f"This watcher's session id is `{mine}`. Live cell session ids: "
              f"{sids or 'none alive'}.",
              "",
              "A cell sharing a session id with the shell that launched it is NOT "
              "detached and will be reaped with it. Distinct session ids here are the "
              "proof that `setsid` took effect; the command line alone is not.",
              "", "## every cell", "",
              "| arm | home | last night | quiet for | alive | finished | pid | sid | wave |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["arm"], r["household"])):
        lines.append(
            f"| {r['arm']} | {r['household']} | "
            f"{r['last_night'] if r['last_night'] is not None else '-'}/{r['last_day'] or '-'} | "
            f"{r['minutes_since_its_last_night'] if r['minutes_since_its_last_night'] is not None else '-'} | "
            f"{'yes' if r['alive'] else 'no'} | {'yes' if r['finished'] else 'no'} | "
            f"{r['pid']} | {r['sid']} | {r['wave']} |")
    lines.append("")

    # ---- the accounting: what is running, finished, or simply absent
    import subprocess
    running_now = {k: len(v) for k, v in living.items()}
    lines += ["## the accounting: 10 homes x 6 arms = "
              f"{len(EXPECTED_ARMS) * EXPECTED_HOMES} cells", "",
              "| arm | finished | running now | neither | duplicate writers |",
              "|---|---|---|---|---|"]
    total_missing = 0
    for arm in EXPECTED_ARMS:
        fin = sum(1 for a, _h in finished_cells if a == arm)
        run = sum(n for (a, _h), n in running_now.items() if a == arm)
        neither = EXPECTED_HOMES - fin - run
        total_missing += max(0, neither)
        dup = sum(1 for (a, _h) in duplicates if a == arm)
        lines.append(f"| {arm} | {fin}/{EXPECTED_HOMES} | {run} | "
                     f"{'**' + str(neither) + '**' if neither > 0 else '0'} | "
                     f"{'**' + str(dup) + '**' if dup else '0'} |")
    lines += ["",
              f"**'neither' is the number that will be missing from the comparison unless "
              f"something launches them: {total_missing} right now.** Queued cells count as "
              f"'neither' - this watcher cannot see a launcher's queue, so a non-zero "
              f"number means either queued or lost.", ""]
    try:
        launchers = subprocess.run(["pgrep", "-af", "launch.sh"], capture_output=True,
                                   text=True).stdout.strip().splitlines()
    except OSError:
        launchers = []
    launchers = [x for x in launchers if "pgrep" not in x]
    if launchers:
        lines += [f"**{len(launchers)} launcher(s) still alive, so the "
                  f"{total_missing} are QUEUED and will start as slots free:**", ""]
        for x in launchers:
            lines.append(f"  * `{x.strip()}`")
    else:
        lines += [f"**NO launcher is alive.** So the {total_missing} cells counted as "
                  f"'neither' will never start unless something launches them. If that "
                  f"number is not zero, the comparison is incomplete."]
    lines.append("")
    if duplicates:
        lines += ["**TWO WRITERS ON ONE CELL - this corrupts the look stream and the "
                  "notes:**", ""]
        for (arm, household), n in sorted(duplicates.items()):
            lines.append(f"  * `{arm}/{household}`: {n} processes")
        lines.append("")

    # ---- the no-length-limit proof, from the artifacts rather than from the code
    lines += ["## is the memory really uncapped? read off the notes, not the code", "",
              "The wholesale summary's schema used to cap the WHOLE memory at 2400 "
              "characters and its prompt told it to fit 8 lines. A summary longer than "
              "2400 characters, or longer than 8 lines, is direct evidence from the "
              "artifact that both caps are gone in the process that wrote it.", "",
              "| arm | home | longest summary so far | fact-lines | over the old 2400 "
              "cap? | over the old 8-line instruction? |",
              "|---|---|---|---|---|---|"]
    any_wholesale = False
    for arm in ("control_wholesale",):
        for path in sorted((root / "cells" / arm).glob("*")):
            notes_file = path / "notes.json"
            if not notes_file.exists():
                continue
            try:
                raw = json.loads(notes_file.read_text())
            except ValueError:
                continue
            summaries = [s.get("summary") or "" for s in raw.get("nightly_summaries", [])]
            if not summaries:
                continue
            any_wholesale = True
            longest = max(summaries, key=len)
            # counted in the unit the budget was stated in - "one fact to a line" - which
            # is `summary_lines`, not raw newlines: the model writes one long paragraph and
            # splitting on newlines reported every summary as a single line.
            from self_improve.memory_notes import summary_lines
            n_lines = len(summary_lines(longest))
            lines.append(f"| {arm} | {path.name} | {len(longest)} chars | {n_lines} | "
                         f"{'YES' if len(longest) > 2400 else 'not yet'} | "
                         f"{'YES' if n_lines > 8 else 'not yet'} |")
    if not any_wholesale:
        lines.append("| - | - | no wholesale summary written yet | - | - | - |")
    lines += ["",
              "'not yet' is not evidence of a cap: an early night may simply be short. "
              "A single YES in either column is conclusive for that cell.", ""]

    lines += ["## the waves", ""]
    for wave, what in WAVE_LEGEND.items():
        here = [r for r in rows if r["wave"] == wave]
        if not here:
            continue
        lines.append(f"* **{wave}** ({len(here)} cells recorded, "
                     f"{sum(1 for r in here if r['alive'])} alive): {what}")
    lines.append("")

    (root / "HEARTBEAT.md").write_text("\n".join(lines) + "\n")
    (root / "heartbeat_state.json").write_text(json.dumps(
        {"at": time.time(), "stall_minutes": stall_minutes, "rows": rows,
         "n_finished": len(done), "n_running": len(running),
         "n_stalled": len(stalled)}, indent=1))
    return {"n_finished": len(done), "n_running": len(running),
            "n_stalled": len(stalled), "stalled": stalled}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/three_prompts"))
    parser.add_argument("--stall-minutes", type=float, default=15.0)
    parser.add_argument("--every", type=float, default=0.0,
                        help="seconds between passes; 0 or --once means one pass")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)

    while True:
        got = one_pass(args.root, args.stall_minutes)
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"{stamp} {got['n_finished']} finished, {got['n_running']} running, "
              f"{got['n_stalled']} STALLED", flush=True)
        for r in got["stalled"]:
            print(f"   STALLED {r['arm']}/{r['household']}: night "
                  f"{r['last_night']}, quiet {r['minutes_since_its_last_night']} min, "
                  f"process {'alive' if r['alive'] else 'DEAD'}", flush=True)
        if args.once or args.every <= 0:
            return 0
        time.sleep(args.every)


if __name__ == "__main__":
    raise SystemExit(main())
