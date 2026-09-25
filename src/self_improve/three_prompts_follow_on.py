"""Run each cell's diagnostics the moment that cell lands, unattended.

WHY THIS EXISTS. The live wave takes hours and the diagnostics that follow it take hours
more. Waiting for the whole wave before starting any of them leaves the GPU idle at the
end and leaves the work depending on somebody being awake to start it. This loops, notices
which finished cells have no diagnostics yet, and runs them - so the queue drains itself.

THE ORDER IS DELIBERATE, and it is the order that survives running out of time:

  1. the ANSWER-STEP TOKEN BUDGET contrast (`three_prompts_reanswer`), about a hundred
     calls a cell. Cheapest, and it re-asks only the questions the search did not find, so
     it is the exact test of a ceiling that 34% of answers were sitting on.
  2. the FROZEN DIAGNOSTIC at day 23 - the freeze point the design turns on - at 240
     questions a cell.
  3. the FROZEN DIAGNOSTIC at day 13, the control point, also 240.

Compliance, reachability and the four end-to-end headline measures are NOT here, because
they need no model call at all: they are computed from the cells directly whenever anyone
asks. If this driver never ran, the headline would still be complete.

IT THROTTLES ON THE WHOLE MACHINE. The live wave is the headline and must not be starved,
so this counts every `three_prompts` process before starting anything and stays under
`--max-total`. It also takes no cell that a live process still holds.

    python -m self_improve.three_prompts_follow_on --max-total 42
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

from self_improve.three_prompts import ARMS, PILOT_TEN, cell_dir

DAY_23 = "did it learn the new routine"
DAY_13 = "before anything changed"


def how_many_are_running() -> int:
    try:
        out = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True).stdout
    except OSError:
        return 999
    return sum(1 for line in out.splitlines()
               if ("three_prompts" in line and "--arm" in line and "grep" not in line)
               or ("three_prompts_reanswer" in line and "grep" not in line)
               or ("three_prompts_frozen" in line and "grep" not in line))


def jobs_for(root: pathlib.Path, arm: str, household: str) -> List[Dict[str, Any]]:
    """The diagnostics this cell still needs, cheapest first."""
    cell = cell_dir(root, arm, household)
    if not (cell / "cell.json").exists():
        return []
    out: List[Dict[str, Any]] = []
    done_reanswer = root / "reanswer" / arm / f"{household}.json"
    if not done_reanswer.exists():
        out.append({"what": "reanswer", "arm": arm, "household": household,
                    "marker": done_reanswer})
    for freeze_point in (DAY_23, DAY_13):
        answers = (root / "frozen" / "standard_reasoning" / arm / household
                   / freeze_point.replace(" ", "_") / "held_out_answers.json")
        if not answers.exists():
            out.append({"what": "frozen", "arm": arm, "household": household,
                        "freeze_point": freeze_point, "marker": answers})
    return out


def launch(job: Dict[str, Any], root: pathlib.Path, logs: pathlib.Path) -> Optional[int]:
    logs.mkdir(parents=True, exist_ok=True)
    arm, household = job["arm"], job["household"]
    if job["what"] == "reanswer":
        name = f"reanswer__{arm}__{household}"
        cmd = ["python3", "-m", "self_improve.three_prompts_reanswer",
               "--root", str(root), "--arms", arm, "--households", household]
    else:
        tag = job["freeze_point"].replace(" ", "_")
        name = f"frozen__{tag}__{arm}__{household}"
        cmd = ["python3", "-m", "self_improve.three_prompts_frozen",
               "--root", str(root), "--arms", arm, "--households", household,
               "--freeze-points", job["freeze_point"]]
    log = (logs / f"{name}.log").open("a")
    log.write(f"\n=== started {datetime.datetime.now().astimezone().isoformat()} "
              f"{' '.join(cmd)}\n")
    log.flush()
    process = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                               start_new_session=True)
    return process.pid


def write_the_reports(root: pathlib.Path, logs: pathlib.Path) -> None:
    """Produce the three reports once everything has landed, so the run finishes itself.

    Without this the overnight run ends with sixty cells and a hundred and twenty answer
    files and nothing that reads them, waiting for somebody to type three commands. Each
    report is written to a file AND left in a log, and each needs no model call.

    COMPLIANCE IS WRITTEN FIRST and named first, because an arm that did not do what its
    prompt asked is not an arm and its outcome numbers mean nothing. If only one of these
    files exists, it should be that one.
    """
    logs.mkdir(parents=True, exist_ok=True)
    steps = [
        ("COMPLIANCE_REPORT.txt",
         ["python3", "-m", "self_improve.three_prompts_compliance", "--root", str(root)]),
        # The noise floor comes BEFORE the outcomes, because the outcomes report reads
        # the_rerun_noise_floor.json and annotates every contrast with whether it clears
        # the floor. Run the other way round, every verdict would silently lose that line.
        ("THE_RERUN_NOISE_FLOOR.txt",
         ["python3", "-m", "self_improve.three_prompts_noise_floor", "--root", str(root)]),
        ("the_answer_step_token_budget.txt",
         ["python3", "-m", "self_improve.three_prompts_reanswer", "--root", str(root),
          "--gather"]),
        ("OUTCOMES_REPORT.txt",
         ["python3", "-m", "self_improve.three_prompts_outcomes", "--root", str(root)]),
    ]
    for name, cmd in steps:
        print(f"   writing {name}", flush=True)
        try:
            done = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
            (root / name).write_text(
                f"$ {' '.join(cmd)}\nexit {done.returncode}\n\n"
                + done.stdout + ("\n--- stderr ---\n" + done.stderr if done.stderr else ""))
        except (OSError, subprocess.SubprocessError) as why:
            (root / name).write_text(f"$ {' '.join(cmd)}\nFAILED: {why}\n")
            print(f"   {name} FAILED: {why}", flush=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/three_prompts"))
    parser.add_argument("--max-total", type=int, default=42,
                        help="cap on ALL three_prompts processes on the machine, so the "
                             "live wave is never starved by its own diagnostics")
    parser.add_argument("--every", type=float, default=60.0)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)

    # ONE DRIVER ONLY. Two copies of this would launch every diagnostic twice, and two
    # identical processes writing one answers file is the same corruption that cost the
    # wholesale cells earlier tonight. An advisory flock is held for the driver's whole
    # life and released by the kernel if it dies, so a crashed driver does not lock itself
    # out.
    import fcntl
    args.root.mkdir(parents=True, exist_ok=True)
    guard = (args.root / "follow_on.lock").open("w")
    try:
        fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another follow-on driver already holds "
              f"{args.root / 'follow_on.lock'}; exiting rather than duplicating its work")
        return 0
    guard.write(f"{os.getpid()}\n")
    guard.flush()

    logs = args.root / "logs" / "follow_on"
    started: Dict[str, int] = {}
    while True:
        outstanding: List[Dict[str, Any]] = []
        for arm in sorted(ARMS):
            for household in PILOT_TEN:
                outstanding += jobs_for(args.root, arm, household)
        # a job whose marker is still absent but which we already launched and which is
        # still alive is in flight, not outstanding
        in_flight = {k: p for k, p in started.items() if pathlib.Path(f"/proc/{p}").exists()}
        todo = [j for j in outstanding
                if f"{j['what']}:{j['arm']}:{j['household']}:{j.get('freeze_point','')}"
                not in in_flight]
        room = args.max_total - how_many_are_running()
        launched = 0
        for job in todo:
            if launched >= max(0, room):
                break
            key = f"{job['what']}:{job['arm']}:{job['household']}:{job.get('freeze_point','')}"
            pid = launch(job, args.root, logs)
            if pid:
                started[key] = pid
                launched += 1
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"{stamp} {len(outstanding)} diagnostics outstanding, "
              f"{len(in_flight)} in flight, {launched} launched, "
              f"{how_many_are_running()} processes on the machine", flush=True)
        state = {"at": time.time(), "n_outstanding": len(outstanding),
                 "n_in_flight": len(in_flight),
                 "outstanding": [f"{j['what']} {j['arm']} {j['household']} "
                                 f"{j.get('freeze_point','')}" for j in outstanding[:40]]}
        (args.root / "follow_on_state.json").write_text(json.dumps(state, indent=1))
        if args.once:
            return 0
        # Only stop when every cell EXISTS and has its diagnostics. "Nothing
        # outstanding" is not the same thing at the start of a wave, when no cell has
        # landed yet - and exiting then left the driver dead for the whole run, which is
        # the one failure this driver was written to prevent.
        n_cells = sum(1 for arm in ARMS for household in PILOT_TEN
                      if (cell_dir(args.root, arm, household) / "cell.json").exists())
        expected = len(ARMS) * len(PILOT_TEN)
        if n_cells >= expected and not outstanding and not in_flight:
            print(f"all {expected} cells present and every diagnostic done", flush=True)
            write_the_reports(args.root, logs)
            return 0
        if n_cells < expected:
            print(f"   {n_cells} of {expected} cells have landed; waiting", flush=True)
        time.sleep(args.every)


if __name__ == "__main__":
    raise SystemExit(main())
