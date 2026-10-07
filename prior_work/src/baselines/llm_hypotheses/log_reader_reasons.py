"""What the log reader reasons about, and how that relates to its errors.

For every log-reader arm in a run, joins each question to the model's
final ``answer`` decision (its ``why`` string) and its ``sense`` decisions,
tags each ``why`` with the kind of reasoning it contains, and writes

    figures/log_reader_reasons.md    tables + sampled reasonings per error type
    figures/log_reader_reasons.png   reasoning kinds by outcome, look-back depth
                                     per week, and what it answers when the
                                     truth is out of the house

Reasoning kinds (regular expressions on the ``why``; a why can carry several):

    last seen        "most recent sighting … no later event … still there"
    routine          "pattern / typically / usually / every morning"
    empty look       cites a look that found nothing / the object gone
    away             says the object left the house / is carried / at work
    unseen object    the object has never appeared in the log
    look-back        how many distinct log days the why cites, and how far
                     back the oldest one is from the question's day

    python -m baselines.llm_hypotheses.log_reader_reasons [--household hh_001__bank0]
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import random
import re
from typing import Any, Dict, List, Optional, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from baselines.llm_hypotheses.analyze_tour_start import STUDY_DIR, load
from baselines.llm_hypotheses.error_atlas import ET_COLOR, ET_LABEL, error_type, label, room_map
from baselines.types import DAY_SECONDS

SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "axes.titlelocation": "left",
                     "axes.titleweight": "bold", "axes.titlesize": 10})

KINDS = [
    ("last seen", r"most recent|last (seen|sighting|known|confirmed)|only sighting|still (there|at|be)|"
                  r"no (subsequent|later|further)|has not (been )?(moved|seen)|remain"),
    ("routine", r"pattern|routine|typical|usually|consistent|every (day|morning|evening|weekday)|"
                r"each (day|morning)|regular|habit|tends"),
    ("empty look", r"\(nothing\)|not found|found empty|was empty|wasn't there|was not (there|found|present)|"
                   r"no longer|have been moved|has been moved"),
    ("away", r"OUT_OF_HOUSE|out of (the )?house|left the house|not in the house|ON_PERSON|carr(y|ied|ying)|"
             r"took .* with|takes? .* (to work|along)|commut|at work|with (her|mara)"),
    ("unseen object", r"never (been )?(seen|appeared)|not (been )?seen in the log|no sighting|unknown"),
]
KIND_COLOR = {"last seen": "#2a78d6", "routine": "#eb6834", "empty look": "#1baf7a",
              "away": "#eda100", "unseen object": "#e87ba4", "none": "#c3c2b7"}
LOOKBACK_BINS = ["no day cited", "same day", "1 day back", "2–6 days back", "7+ days back"]


def tags_of(why: str) -> List[str]:
    return [k for k, p in KINDS if re.search(p, why, re.I)] or ["none"]


def lookback(day: int, why: str) -> str:
    ds = [int(x) for x in re.findall(r"\bd(\d\d)\b", why)]
    if not ds:
        return LOOKBACK_BINS[0]
    back = day - min(ds)
    return (LOOKBACK_BINS[1] if back <= 0 else LOOKBACK_BINS[2] if back == 1
            else LOOKBACK_BINS[3] if back < 7 else LOOKBACK_BINS[4])


def analyse(arm: Dict[str, Any], rooms: Dict[str, str]) -> Dict[str, Any]:
    dec = arm["diag"].get("decisions") or []
    answers = {(d["object"], d["t"]): d for d in dec if d.get("action") == "answer"}
    looks = collections.defaultdict(list)
    for d in dec:
        if d.get("action") == "sense":
            looks[(d["object"], d["t"])].append(d)
    q: List[dict] = []
    for r in arm["rows"]:
        d = answers.get((r["object_id"], r["t_query"]))
        why = (d or {}).get("why") or ""
        et = error_type(r["truth"], r["argmax"], rooms)
        q.append({"day": r["day"], "object": r["object_id"], "hour": (r["t_query"] % DAY_SECONDS) / 3600,
                  "truth": r["truth"], "answer": r["argmax"], "outcome": ET_LABEL[et] if et else "right",
                  "why": why, "answered": d is not None, "tags": tags_of(why) if d else ["none"],
                  "lookback": lookback(r["day"], why) if d else LOOKBACK_BINS[0],
                  "n_days_cited": len(set(re.findall(r"\bd(\d\d)\b", why))),
                  "looks": looks.get((r["object_id"], r["t_query"]), [])})
    look_reason = collections.Counter()
    for d in dec:
        if d.get("action") != "sense":
            continue
        w = d.get("why") or ""
        if re.search(r"last (seen|known|sighting)|most recent", w, re.I):
            look_reason["confirm the last-seen spot"] += 1
        elif re.search(r"never been seen|not (been )?seen|unknown|no sighting", w, re.I):
            look_reason["object never seen: guess a spot"] += 1
        elif re.search(r"moved|not (there|found)|empty|\(nothing\)", w, re.I):
            look_reason["last spot was empty: try the next"] += 1
        else:
            look_reason["other"] += 1
    return {"q": q, "n_answers": len(answers), "n_looks": sum(len(v) for v in looks.values()),
            "look_reason": look_reason,
            "look_targets": collections.Counter(d.get("receptacle") for d in dec if d.get("action") == "sense"),
            "stats": arm["diag"].get("log_reader") or {}}


def report(key: str, a: Dict[str, Any]) -> str:
    q = [x for x in a["q"] if x["answered"]]; n = len(q)
    L = [f"## {label(key)} (`{key}`)", "",
         f"{a['n_answers']} answer decisions, {a['n_looks']} looks, {a['stats'].get('invalid_decisions', '?')} "
         f"invalid replies (fallback answer used), {a['stats'].get('notes_versions', 0)} notes written, "
         f"{a['stats'].get('prompt_tokens', 0) / 1e6:.1f} M prompt tokens.", ""]
    L += ["### What the reasoning talks about", "", "| kind | answers | share | right when present |", "|---|---|---|---|"]
    for k, _ in KINDS + [("none", "")]:
        with_k = [x for x in q if k in x["tags"]]
        if with_k:
            L.append(f"| {k} | {len(with_k)} | {100 * len(with_k) / n:.0f}% | "
                     f"{sum(x['outcome'] == 'right' for x in with_k) / len(with_k):.2f} |")
    L += ["", "### How far back in the log the reasoning reaches", "",
          "| oldest day cited | answers | share |", "|---|---|---|"]
    c = collections.Counter(x["lookback"] for x in q)
    L += [f"| {b} | {c[b]} | {100 * c[b] / n:.0f}% |" for b in LOOKBACK_BINS]
    L += ["", "### By outcome", "", "| outcome | n | " + " | ".join(k for k, _ in KINDS) + " | none |",
          "|---|---|" + "---|" * (len(KINDS) + 1)]
    for oc in ["right"] + [ET_LABEL[e] for e in ET_LABEL]:
        sub = [x for x in q if x["outcome"] == oc]
        if sub:
            L.append(f"| {oc} | {len(sub)} | " + " | ".join(
                f"{100 * sum(k in x['tags'] for x in sub) / len(sub):.0f}%" for k, _ in KINDS) +
                f" | {100 * sum('none' in x['tags'] for x in sub) / len(sub):.0f}% |")
    out = [x for x in q if x["truth"] == "OUT_OF_HOUSE"]
    if out:
        L += ["", "### When the truth is OUT_OF_HOUSE", "",
              f"{len(out)} questions, {sum(x['outcome'] == 'right' for x in out)} right; the reasoning mentions "
              f"leaving / carrying / absence in {sum('away' in x['tags'] for x in out)} of them. What it answered instead: " +
              ", ".join(f"{k} ({v})" for k, v in collections.Counter(x["answer"] for x in out).most_common(6)) + "."]
    L += ["", "### Why it looked", "", "| reason | looks |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in a["look_reason"].most_common()]
    L += ["", "Most looked-at: " + ", ".join(f"{k} ({v})" for k, v in a["look_targets"].most_common(6)) + ".", ""]
    rng = random.Random(0)
    L += ["### Sampled reasonings", ""]
    for oc in ["right", "missed away", "wrong room", "right room, wrong spot", "false away", "missed carried"]:
        sub = [x for x in q if x["outcome"] == oc and x["why"]]
        if not sub:
            continue
        L.append(f"**{oc}** ({len(sub)})"); L.append("")
        for x in rng.sample(sub, min(4, len(sub))):
            L.append(f"- day {x['day']} {x['hour']:.0f} h, {x['object']} → **{x['answer']}** (truth {x['truth']}): "
                     f"{x['why'].strip()}")
        L.append("")
    return "\n".join(L)


def figure(results: Dict[str, Dict[str, Any]], out: pathlib.Path, household: str) -> None:
    keys = list(results)
    fig, axes = plt.subplots(len(keys), 3, figsize=(17, 4.2 * len(keys)), squeeze=False,
                             gridspec_kw={"wspace": 0.55, "hspace": 0.7, "width_ratios": [1.5, 0.8, 1]})
    for row, key in enumerate(keys):
        q = [x for x in results[key]["q"] if x["answered"]]
        outcomes = ["right"] + [ET_LABEL[e] for e in ET_LABEL if any(x["outcome"] == ET_LABEL[e] for x in q)]
        # A: share of each reasoning kind within each outcome (grouped bars)
        ax = axes[row, 0]
        kinds = [k for k, _ in KINDS] + ["none"]
        xs = np.arange(len(outcomes)); w = 0.8 / len(kinds)
        for i, k in enumerate(kinds):
            vals = [100 * sum(k in x["tags"] for x in q if x["outcome"] == oc) / max(1, sum(x["outcome"] == oc for x in q))
                    for oc in outcomes]
            ax.bar(xs + i * w - 0.4 + w / 2, vals, w, color=KIND_COLOR[k], label=k, edgecolor=SURF, lw=0.5)
        ax.set_xticks(xs); ax.set_xticklabels([f"{oc.replace(', ', chr(10))}\n(n={sum(x['outcome'] == oc for x in q)})"
                                              for oc in outcomes], fontsize=7.5, rotation=20, ha="right")
        ax.set_ylabel("% of that outcome's answers whose reasoning has the kind"); ax.set_ylim(0, 100)
        ax.legend(frameon=False, fontsize=7.5, ncol=3, loc="upper right"); ax.tick_params(length=0)
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
        ax.set_title(f"{label(key)}\nwhat the reasoning contains, by outcome (a why can carry several kinds)", fontsize=9)
        # B: look-back per week
        ax = axes[row, 1]
        weeks = sorted({x["day"] // 7 for x in q})
        bottom = np.zeros(len(weeks))
        shades = ["#c3c2b7", "#cde2fb", "#86b6ef", "#2a78d6", "#0d366b"]
        for b, col in zip(LOOKBACK_BINS, shades):
            vals = np.array([100 * sum(x["lookback"] == b for x in q if x["day"] // 7 == wk) /
                             max(1, sum(x["day"] // 7 == wk for x in q)) for wk in weeks])
            ax.bar([f"week {wk + 1}" for wk in weeks], vals, bottom=bottom, color=col, label=b, edgecolor=SURF, lw=0.6)
            bottom += vals
        ax.set_ylim(0, 100); ax.set_ylabel("% of answers"); ax.tick_params(length=0)
        ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
        ax.set_title("\nHow far back the cited log days reach", fontsize=9)
        # C: what it answers when truth is OUT_OF_HOUSE
        ax = axes[row, 2]
        oq = [x for x in q if x["truth"] == "OUT_OF_HOUSE"]
        c = collections.Counter(x["answer"] for x in oq).most_common(8)
        ys = np.arange(len(c))[::-1]
        ax.barh(ys, [v for _, v in c], color=["#2a78d6" if k == "OUT_OF_HOUSE" else "#c3c2b7" for k, _ in c],
                height=0.7, edgecolor=SURF)
        ax.set_yticks(ys); ax.set_yticklabels([k for k, _ in c], fontsize=8); ax.tick_params(length=0)
        ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
        ax.set_xlabel(f"answers on the {len(oq)} out-of-house questions")
        ax.set_title(f"Answers when the truth is OUT_OF_HOUSE\n({sum(x['outcome'] == 'right' for x in oq)} right; "
                     f"'away' reasoning in {sum('away' in x['tags'] for x in oq)} of {len(oq)})", fontsize=9)
    fig.suptitle(f"Log reader reasoning · {household}", x=0.02, ha="left", fontsize=13, fontweight="bold", y=0.995)
    fig.savefig(out, dpi=140, bbox_inches="tight"); plt.close(fig)


def main(argv: Optional[Sequence[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--household", default="hh_001__bank0")
    ap.add_argument("--study-dir", type=pathlib.Path, default=STUDY_DIR / "main")
    args = ap.parse_args(argv)
    arms = load(args.household, args.study_dir)
    keys = [k for k in arms if arms[k]["diag"].get("decisions")]
    if not keys:
        raise SystemExit("no log-reader arms (no 'decisions' in any diagnostics.json)")
    hh = next(iter(arms.values()))["diag"].get("household") or args.household.split("__")[0]
    spots = {r["truth"] for k in keys for r in arms[k]["rows"]} | {r["argmax"] for k in keys for r in arms[k]["rows"]}
    rooms = room_map(hh, sorted(spots))
    results = {k: analyse(arms[k], rooms) for k in sorted(keys)}
    fig_dir = args.study_dir / args.household / "figures"
    md = [f"# Log reader reasoning · {args.household}", "",
          "Each answer's `why` is tagged by regular expressions (see the module docstring); one why can carry "
          "several kinds. Shares are of answered questions (questions whose reply was invalid have no why).", ""]
    for k in results:
        md.append(report(k, results[k])); md.append("")
    (fig_dir / "log_reader_reasons.md").write_text("\n".join(md))
    figure(results, fig_dir / "log_reader_reasons.png", args.household)
    for k, a in results.items():
        q = [x for x in a["q"] if x["answered"]]
        print(f"{label(k)}: {len(q)} answers; " + ", ".join(
            f"{kind} {100 * sum(kind in x['tags'] for x in q) / len(q):.0f}%" for kind, _ in KINDS))
    print(f"  {fig_dir / 'log_reader_reasons.md'}\n  {fig_dir / 'log_reader_reasons.png'}")


if __name__ == "__main__":
    main()
