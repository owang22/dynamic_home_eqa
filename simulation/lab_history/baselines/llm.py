"""Open-model answerer on the lab history runs: Qwen3.6-35B-A3B given the history as text, two ways.

    python -m simulation.lab_history.baselines.llm --per-length 100 --workers 3

  flat:   the dog's events up to the question's t, one line each, newest last; for long histories only the most
          recent events that fit the token budget.
  table:  a compact per-object and per-person table built from the same events: last seen (place, time), the
          three most frequent places, the most frequent place on each weekday, and when each place was last looked at.

The answer is constrained by json_schema to one of the lab's places or "not in the lab", so scoring is exact match,
as in rules.py. The same stratified sample is scored for the rules too, for a side-by-side.
Writes llm_results.json and llm_answers.jsonl (raw answers; not in git).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import time
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zoneinfo import ZoneInfo

from .rules import AWAY, RUNS, History, answer_rules, gold, load, table

TZ = ZoneInfo("America/Los_Angeles")
URL = "http://127.0.0.1:8302/v1/chat/completions"
MODEL = "Qwen/Qwen3.6-35B-A3B-FP8"
HERE = Path(__file__).resolve().parent
TOKEN_BUDGET = 12000          # history tokens; the server's context is 16k
CHARS_PER_TOKEN = 2.0         # measured 2.14 with the server tokenizer on these lines; rounded down
STRATA = [("where_now", "stale", 30), ("where_now", "fresh", 30), ("where_now", "away", 15),
          ("usual_place", None, 15), ("last_in_lab", None, 5), ("desk_now", None, 5)]


def clock(t):
    return dt.datetime.fromtimestamp(t, TZ).strftime("%a %Y-%m-%d %H:%M")


def stratum(q):
    if q["kind"] != "where_now":
        return (q["kind"], None)
    if q["answer"] == AWAY:
        return ("where_now", "away")
    return ("where_now", "stale" if q["stale"] else "fresh")


def sample(per_length, rng, runs=RUNS):
    """About per_length questions per history length, pooled over seeds, in the STRATA proportions
    (for runs other than runs/: drawn at random, which keeps the phase balance of the shift-targeted runs)."""
    out = []
    if runs != RUNS:
        for days in (30, 60, 90):
            pool = [(d, q) for d in sorted(runs.glob(f"d{days}_s*")) for q in load(d / "questions.jsonl")]
            out += rng.sample(pool, min(per_length, len(pool)))
        return out
    scale = per_length / sum(n for *_, n in STRATA)
    for days in (30, 60, 90):
        pool = defaultdict(list)
        for d in sorted(RUNS.glob(f"d{days}_s*")):
            for q in load(d / "questions.jsonl"):
                pool[stratum(q)].append((d, q))
        for kind, sub, n in STRATA:
            items = pool[(kind, sub)]
            out += rng.sample(items, min(len(items), max(1, round(n * scale))))
    return out


def event_line(e):
    s = e["seen"]
    objs = ", ".join(f"{o['colour']} {o['name']}".strip() for o in s["objects"]) or "nothing"
    ppl = f"; people: {s['people_notes']}" if s["people"] else ""
    return f"{clock(e['t'])} {e['place']}: {objs}{ppl}"


def flat_history(h: History, t):
    lines = [event_line(e) for e in h.events if e["t"] <= t]
    budget, kept = TOKEN_BUDGET * CHARS_PER_TOKEN, []
    for line in reversed(lines):
        budget -= len(line) + 1
        if budget < 0:
            break
        kept.append(line)
    kept.reverse()
    head = f"(the {len(lines) - len(kept)} older events don't fit and are left out)\n" if len(kept) < len(lines) else ""
    return head + "\n".join(kept)


def table_history(h: History, t):
    rows = []
    names = list(h.desc) + list(h.look)
    for name in names:
        s = h.before(name, t)
        label = h.desc.get(name) or h.look[name]
        if not s:
            rows.append(f"{label}: never seen")
            continue
        top = ", ".join(f"{p} x{n}" for p, n in Counter(p for _, p in s).most_common(3))
        wd = defaultdict(Counter)
        for ts, p in s:
            wd[dt.datetime.fromtimestamp(ts, TZ).strftime("%a")][p] += 1
        by_wd = "; ".join(f"{d} {c.most_common(1)[0][0]}" for d, c in sorted(
            wd.items(), key=lambda kv: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].index(kv[0])))
        rows.append(f"{label}: last seen {s[-1][1]} at {clock(s[-1][0])}; seen {len(s)} times, most at {top}; "
                    f"by weekday: {by_wd}")
    looked = [f"{p} {clock(max(x for x in ts if x <= t))}" for p, ts in sorted(h.looks_at.items())
              if any(x <= t for x in ts)]
    return "\n".join(rows) + "\n\nLast look at each place: " + "; ".join(looked)


def prompt(h: History, q, places, mode):
    hist = flat_history(h, q["t"]) if mode == "flat" else table_history(h, q["t"])
    what = "the events (what the robot's camera reported at each place it looked at, oldest first)" \
        if mode == "flat" else "a summary of the robot's sightings so far"
    return (f"A robot dog patrols a university lab and reports what it sees at named places. The camera sometimes "
            f"misses or misnames things. People keep routines, and some objects follow them; routines can change.\n\n"
            f"Places: {', '.join(places)}.\n\nBelow is {what}.\n\n{hist}\n\n"
            f"It is now {clock(q['t'])}. Question: {q['question']}\n"
            f"Answer with the single most likely place, or \"{AWAY}\" if it is most likely out of the lab.")


def ask(text, choices):
    schema = {"type": "object", "properties": {"answer": {"type": "string", "enum": choices}},
              "required": ["answer"], "additionalProperties": False}
    body = {"model": MODEL, "max_tokens": 50, "temperature": 0,
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}},
            "messages": [{"role": "user", "content": text}]}
    for attempt in range(30):          # the proxy says 503 while no GPU is free; wait and retry
        try:
            req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=900))
            return json.loads(r["choices"][0]["message"]["content"])["answer"], r["usage"]["prompt_tokens"]
        except urllib.error.HTTPError as e:
            if e.code != 503:
                raise
            time.sleep(60)
    raise RuntimeError("no GPU for 30 minutes")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-length", type=int, default=100)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--runs", default="runs", help="folder under simulation/lab_history with the runs")
    a = ap.parse_args()
    runs = RUNS.parent / a.runs
    tag = "" if a.runs == "runs" else "_" + a.runs.removeprefix("runs_")
    items = sample(a.per_length, random.Random(a.seed), runs)
    hist = {}
    for d, _ in items:
        if d not in hist:
            routines = json.loads((d / "routines.json").read_text())
            hist[d] = (History(load(d / "events.jsonl"), routines), list(routines["places"]))

    jobs = [(d, q, mode) for d, q in items for mode in ("flat", "table")]

    def one(job):
        d, q, mode = job
        h, places = hist[d]
        ans, ptok = ask(prompt(h, q, places, mode), places + [AWAY])
        return {"run": d.name, "q": q["id"], "mode": mode, "answer": ans, "prompt_tokens": ptok}

    t0 = time.time()
    answers = []
    with ThreadPoolExecutor(a.workers) as ex:
        for i, r in enumerate(ex.map(one, jobs)):
            answers.append(r)
            if (i + 1) % 50 == 0:
                print(f"{i + 1}/{len(jobs)} in {time.time() - t0:.0f}s", flush=True)

    rows = []
    qmap = {(d.name, q["id"]): (d, q) for d, q in items}
    for r in answers:
        d, q = qmap[(r["run"], r["q"])]
        kind, sub = stratum(q)
        rows.append({"run": r["run"], "days": int(r["run"][1:].split("_")[0]), "kind": kind, "stratum": sub or kind,
                     "phase": q.get("phase"), "rule": f"llm_{r['mode']}", "answer": r["answer"], "gold": gold(q),
                     "correct": r["answer"] == gold(q)})
    for d, q in items:                 # the rules on the same sample
        kind, sub = stratum(q)
        for rule, ans in answer_rules(hist[d][0], q).items():
            rows.append({"run": d.name, "days": int(d.name[1:].split("_")[0]), "kind": kind, "stratum": sub or kind,
                         "phase": q.get("phase"), "rule": rule, "answer": ans, "gold": gold(q), "correct": ans == gold(q)})
    res = {"about": __doc__.strip().split("\n\n")[0], "model": MODEL, "n_questions": len(items),
           "token_budget": TOKEN_BUDGET,
           "mean_prompt_tokens": {m: round(sum(r["prompt_tokens"] for r in answers if r["mode"] == m) /
                                           max(1, sum(r["mode"] == m for r in answers))) for m in ("flat", "table")},
           "by_stratum": table(rows, ["stratum", "rule"]),
           "by_stratum_days": table(rows, ["stratum", "days", "rule"]),
           "by_kind_phase": table(rows, ["kind", "phase", "rule"]),
           "overall": table(rows, ["rule"])}
    (HERE / f"llm_results{tag}.json").write_text(json.dumps(res, indent=1))
    with open(HERE / f"llm_answers{tag}.jsonl", "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in answers)
    for r in res["by_stratum"]:
        if r["rule"].startswith("llm") or r["rule"] in ("last_seen", "claims", "weekday_4w_or_away", "recency_vote"):
            print(f"  {r['stratum']:12} {r['rule']:20} {r['acc']:.2f} {r['ci95']} n={r['n']}")


if __name__ == "__main__":
    main()
