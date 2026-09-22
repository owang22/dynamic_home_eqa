#!/usr/bin/env python3
"""Stall watchdog for the LLM chain: every run appends one line to chain_progress.log with the aggregate calls/min
over the last ~10 minutes across every arm under chain_person/*/ (and knowno_person/*/), and a "VERDICT: STALLED"
line for any arm that logged 0 new calls in the last 15 minutes while the rest of its pass kept moving — the
failure mode that hung the chain at 23:35 (one lost vLLM request, no exception, pool never exits). Keeps its own
sample history in chain_watch_state.json; meant to be run from a loop (chain_watch.sh) every 5 minutes.

    python3 chain_watch.py   (run from uq/llm_strategies)
"""
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "chain_progress.log")
STATE = os.path.join(HERE, "chain_watch_state.json")
WINDOW_S = 10 * 60
STALL_S = 15 * 60
KEEP_S = 60 * 60


def arm_counts():
    out = {}
    for pat in ("chain_person/*/hh_s*_look*", "chain_person2x/*/hh_s*_look*", "knowno_person/*"):
        for d in glob.glob(os.path.join(HERE, pat)):
            if not os.path.isdir(d):
                continue
            # llm.py arms write run_log.jsonl at the end; uq_llm.py (knowno channel) writes stats.json instead
            finished = os.path.exists(os.path.join(d, "run_log.jsonl")) or ("knowno" in d and os.path.exists(os.path.join(d, "stats.json")))
            n = 0
            for f in ("calls.jsonl",) if "chain_person" in d else tuple(x for x in os.listdir(d) if x.endswith(".jsonl") and "knowno" not in x):
                p = os.path.join(d, f)
                if os.path.exists(p):
                    with open(p, "rb") as fh:
                        n += sum(1 for _ in fh)
            out[os.path.relpath(d, HERE)] = (n, finished)
    return out


def main():
    now = time.time()
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    counts = arm_counts()
    for arm, (n, _fin) in counts.items():
        hist = state.setdefault(arm, [])
        hist.append([now, n])
        state[arm] = [h for h in hist if now - h[0] <= KEEP_S]
    json.dump(state, open(STATE, "w"))

    def delta(arm, span):
        hist = state.get(arm, [])
        cur = hist[-1][1] if hist else 0
        past = [h for h in hist if now - h[0] >= span]
        if not past:
            return None  # not enough history yet
        return cur - past[-1][1]

    total10 = 0
    known10 = 0
    moving = 0
    stalled = []
    import fnmatch
    # Two distinct states, deliberately not the same mechanism:
    #  ABANDONED (chain_watch_abandoned.txt) is TERMINAL — those arms are never stall-checked again, whatever their
    #    files do. A run we have decided not to finish must not be able to come back as a false stall, because a
    #    false stall is exactly what hides a real one.
    #  PAUSED (chain_watch_pause.txt) is temporary — skipped only until the arm's calls.jsonl moves again.
    def globs(name):
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            return [], 0
        gs = [l.strip() for l in open(path) if l.strip() and not l.startswith("#")]
        return gs, os.path.getmtime(path)
    abandoned_globs, _ = globs("chain_watch_abandoned.txt")
    paused_globs, pause_t = globs("chain_watch_pause.txt")
    def abandoned(arm):
        return any(fnmatch.fnmatch(arm, g) for g in abandoned_globs)
    def paused(arm):
        if abandoned(arm):
            return True
        if not any(fnmatch.fnmatch(arm, g) for g in paused_globs):
            return False
        cj = os.path.join(HERE, arm, "calls.jsonl")
        return not (os.path.exists(cj) and os.path.getmtime(cj) > pause_t)
    active = {a: v for a, v in counts.items() if not v[1] and not paused(a)}   # unfinished, not paused
    for arm in active:
        d10 = delta(arm, WINDOW_S)
        if d10 is not None:
            total10 += d10
            known10 += 1
            if d10 > 0:
                moving += 1
    for arm in active:
        d15 = delta(arm, STALL_S)
        if d15 is not None and d15 == 0 and moving > 0 and counts[arm][0] > 0:
            stalled.append(arm)
    n_fin = sum(1 for v in counts.values() if v[1])
    rate = total10 / (WINDOW_S / 60) if known10 else float("nan")
    with open(LOG, "a") as f:
        n_aband = sum(1 for a, v in counts.items() if not v[1] and abandoned(a))
        n_paused = sum(1 for a, v in counts.items() if not v[1] and paused(a) and not abandoned(a))
        f.write(f"{time.strftime('%H:%M')} watch: {len(active)} arms running, {n_fin} finished, {n_paused} paused, {n_aband} abandoned, "
                f"aggregate {rate:.0f} calls/min over last 10 min ({known10} arms with history, {moving} moving)\n")
        for arm in stalled:
            f.write(f"{time.strftime('%H:%M')} VERDICT: STALLED ARM {arm} — 0 new calls in 15 min while {moving} others moved "
                    f"(count {counts[arm][0]}); this is the 23:35 hang pattern, check the process\n")


if __name__ == "__main__":
    main()
