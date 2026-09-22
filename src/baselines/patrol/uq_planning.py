"""Search-cost planning metric on top of the existing uq/regime logs — no new agent runs.

    python3 -m baselines.patrol.uq_planning --regime sick10_all --agents none_tt,none_tt72,none_lastseen,mart_tt72,bma_tt,ocp_tt \
        --tau 0.6 --k 3 --costs 2,4 --out ../results/confidence_shift_2026-09-20/uq/planning

For every question of every named agent (their uq/regime/<regime>/<agent>/hh_s*.jsonl logs, which carry the full
``dist``): rank = 1-indexed position of the truth receptacle in ``dist`` sorted by probability descending, ties broken
the same way the logged ``answer`` was picked (highest receptacle id wins on a tie) so the logged answer is always
rank 1; a truth below the logging floor (p < 1e-4, so absent from ``dist``) gets the worst-case rank = the household's
total spot count. rooms = number of distinct rooms (receptacle -> room, from the bank header) entered by the time that
rank position is reached, walking the same probability order. See ``uq/planning/README.md`` for the exact ask-or-search
policy this feeds into. Output: one row per (agent, household, day) with mean places/rooms/cost, written to
``<out>/<regime>_by_day.csv``, plus a per-stage summary table printed and written to ``<out>/<regime>_summary.md``.
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]   # .../dynamic_home_eqa
REGIME_DIR = ROOT / "results" / "regime_search"
UQ_DIR = ROOT / "results" / "confidence_shift_2026-09-20" / "uq" / "regime"


def load(p: pathlib.Path):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def bank_geometry(regime: str, hh: str):
    """(spots: sorted tuple of receptacle ids, rec_room: {receptacle: room}, n_spots: int) for one household."""
    header = json.loads((REGIME_DIR / regime / "banks" / f"{hh}_t03.jsonl").read_text().splitlines()[0])
    rec_room = {r: rm for r, rm in (header.get("receptacle_rooms") or {}).items() if r not in ("ON_PERSON", "OUT_OF_HOUSE")}
    spots = tuple(sorted(rec_room))
    return spots, rec_room


def rank_and_rooms(dist: dict, truth: str, spots: tuple, rec_room: dict) -> tuple:
    """(rank, rooms) for one question: search order = dist's listed spots sorted (prob desc, id desc — the same
    tie-break `max(dist, key=lambda s: (dist[s], s))` uses to pick the logged answer), then any unlisted spots
    (prob < the 1e-4 logging floor) appended in id order as a fixed tail."""
    listed = sorted(dist.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    listed_ids = {s for s, _ in listed}
    order = [s for s, _ in listed] + sorted(s for s in spots if s not in listed_ids)
    seen_rooms: set = set()
    for i, rec in enumerate(order, start=1):
        if rec in rec_room:
            seen_rooms.add(rec_room[rec])
        if rec == truth:
            return i, len(seen_rooms)
    return len(order), len(seen_rooms)   # truth not a sensable spot at all (shouldn't happen on these banks)


def load_raw(regime: str, agent: str) -> list:
    """One row per question: places, rooms, stage, and the agent's own raw confidence SIGNAL (not yet thresholded) —
    ``sig_type`` is "set" (smaller = more confident; the honest-sets agents) or "prob" (bigger = more confident;
    everyone else), ``sig`` is that raw value. Threshold this with :func:`apply_policy`."""
    rows = []
    cache: dict = {}
    for p in sorted((UQ_DIR / regime / agent).glob("hh_s*_t03.jsonl")):
        hh = p.stem.split("_t03")[0]
        if hh not in cache:
            cache[hh] = bank_geometry(regime, hh)
        spots, rec_room = cache[hh]
        for r in load(p):
            rank, rooms = rank_and_rooms(r["dist"], r["truth"], spots, rec_room)
            if "set_size" in r:
                sig_type, sig = "set", r["set_size"]
            else:
                sig_type, sig = "prob", r.get("top_prob", 0.0)
            rows.append({"household": hh, "day": r["day_index"], "stage": r.get("stage", ""),
                         "places": rank, "rooms": rooms, "sig_type": sig_type, "sig": sig})
    return rows


def threshold_for_rate(rows: list, target_rate: float) -> float:
    """The threshold (on LEAD-stage rows only) that makes the ask rate closest to ``target_rate``: the
    ``target_rate``-quantile of the confidence signal, oriented so "ask" = the least-confident tail. For a "prob"
    signal (bigger = more confident) that is the ``target_rate``-th percentile from the bottom; for a "set" signal
    (smaller = more confident) it is from the top."""
    lead = [r for r in rows if r["stage"] == "lead"]
    if not lead:
        return 0.0
    sig_type = lead[0]["sig_type"]
    vals = sorted(r["sig"] for r in lead)
    n = len(vals)
    if sig_type == "prob":
        idx = min(n - 1, max(0, round(target_rate * n)))
        return vals[idx]           # confident if sig >= this
    idx = min(n - 1, max(0, round((1 - target_rate) * n) - 1))
    return vals[idx]                # confident if sig <= this


def apply_policy(rows: list, threshold: float, costs: list) -> list:
    out = []
    for r in rows:
        confident = (r["sig"] >= threshold) if r["sig_type"] == "prob" else (r["sig"] <= threshold)
        row = {**r, "confident": confident}
        for c in costs:
            row[f"cost_c{c}"] = r["places"] if confident else c
        out.append(row)
    return out


def process(regime: str, agent: str, tau: float, k: int, costs: list) -> list:
    """The original "raw stated confidence" policy: fixed tau (prob-type agents) or fixed k (set-type agents)."""
    raw = load_raw(regime, agent)
    if not raw:
        return []
    threshold = tau if raw[0]["sig_type"] == "prob" else k
    return apply_policy(raw, threshold, costs)


def summarize(rows: list, costs: list) -> dict:
    """{stage: {n, confident_share, mean_places, mean_rooms, mean_cost_c<c>...}}"""
    by_stage = collections.defaultdict(list)
    for r in rows:
        by_stage[r["stage"] or "?"].append(r)
        by_stage["any"].append(r)
    out = {}
    for stage, rs in by_stage.items():
        n = len(rs)
        d = {"n": n, "confident_share": sum(r["confident"] for r in rs) / n,
             "mean_places": sum(r["places"] for r in rs) / n, "mean_rooms": sum(r["rooms"] for r in rs) / n}
        for c in costs:
            d[f"mean_cost_c{c}"] = sum(r[f"cost_c{c}"] for r in rs) / n
        out[stage] = d
    return out


def run_matched(regime: str, agents: list, rates: list, costs: list, out: pathlib.Path) -> None:
    """Matched-ask-rate control: per agent, pick its own threshold from LEAD-day data so its ask rate equals
    ``target_rate`` there, then report lead/sick/return cost at that threshold. Controls for agents whose raw
    confidence sits on a different scale (e.g. last-seen is almost always >= 0.6, so a fixed tau=0.6 never lets it
    ask) — the claim under test is that the UQ-aware agents ask MORE on sick days than on lead days even when every
    agent starts from the SAME lead-day ask rate, not just that their raw numbers happen to cross a fixed bar."""
    stages = ["lead", "sick", "return"]
    for rate in rates:
        md = [f"# Planning metric — {regime}, matched ask rate {rate:.0%} on lead days (ask costs {costs})", "",
              "tau/k chosen per agent so lead-day ask rate = " + f"{rate:.0%}" + "; same threshold then applied to sick/return.", "",
              "| agent | threshold | lead ask% | sick ask% | return ask% | " + " | ".join(f"{s} cost(c={c})" for s in stages for c in costs) + " |",
              "|---|---|---|---|---|" + "---|" * (len(stages) * len(costs))]
        for agent in agents:
            raw = load_raw(regime, agent)
            if not raw:
                print(f"  skip {agent}: no logs found", file=sys.stderr)
                continue
            threshold = threshold_for_rate(raw, rate)
            rows = apply_policy(raw, threshold, costs)
            s = summarize(rows, costs)
            asks = [100 * (1 - s.get(st, {}).get("confident_share", float("nan"))) for st in stages]
            cells = [agent, f"{threshold:.3f}" if raw[0]["sig_type"] == "prob" else f"{threshold:.0f}",
                     f"{asks[0]:.0f}%", f"{asks[1]:.0f}%", f"{asks[2]:.0f}%"]
            for st in stages:
                d = s.get(st)
                for c in costs:
                    cells.append(f"{d[f'mean_cost_c{c}']:.2f}" if d else "-")
            md.append("| " + " | ".join(cells) + " |")
            print(f"{regime} matched{rate:.0%} {agent:14s} thr={threshold:.3f} ask% lead/sick/return = {asks[0]:.0f}/{asks[1]:.0f}/{asks[2]:.0f}", file=sys.stderr)
        (out / f"{regime}_matched{int(rate*100)}.md").write_text("\n".join(md) + "\n")
        print("\n".join(md), file=sys.stderr)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--regime", required=True)
    ap.add_argument("--agents", required=True, help="comma-separated agent dir names under uq/regime/<regime>/")
    ap.add_argument("--tau", type=float, default=0.6, help="confident if top_prob >= tau (agents without a set)")
    ap.add_argument("--k", type=int, default=3, help="confident if set_size <= k (agents with a conformal set)")
    ap.add_argument("--costs", default="2,4", help="comma-separated flat ask costs c to evaluate")
    ap.add_argument("--out", type=pathlib.Path, default=UQ_DIR.parent / "planning")
    ap.add_argument("--match-rates", default="0.25,0.5", help="comma-separated lead-day ask-rate targets for the matched control; empty to skip")
    a = ap.parse_args(argv)
    agents = a.agents.split(",")
    costs = [float(x) for x in a.costs.split(",")]
    a.out.mkdir(parents=True, exist_ok=True)

    all_rows = []
    summaries = {}
    for agent in agents:
        rows = process(a.regime, agent, a.tau, a.k, costs)
        if not rows:
            print(f"  skip {agent}: no logs found", file=sys.stderr)
            continue
        for r in rows:
            r["agent"] = agent
        all_rows.extend(rows)
        summaries[agent] = summarize(rows, costs)
        s = summaries[agent]
        print(f"{a.regime} {agent:14s} lead: places {s.get('lead',{}).get('mean_places',float('nan')):5.1f} rooms {s.get('lead',{}).get('mean_rooms',float('nan')):4.1f} "
              f"conf {100*s.get('lead',{}).get('confident_share',float('nan')):3.0f}%  |  "
              f"sick: places {s.get('sick',{}).get('mean_places',float('nan')):5.1f} rooms {s.get('sick',{}).get('mean_rooms',float('nan')):4.1f} "
              f"conf {100*s.get('sick',{}).get('confident_share',float('nan')):3.0f}%  |  "
              f"return: places {s.get('return',{}).get('mean_places',float('nan')):5.1f} conf {100*s.get('return',{}).get('confident_share',float('nan')):3.0f}%",
              file=sys.stderr)

    with (a.out / f"{a.regime}_by_day.csv").open("w", newline="") as f:
        cols = ["agent", "household", "day", "stage", "confident", "places", "rooms"] + [f"cost_c{c}" for c in costs]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in all_rows:
            w.writerow({c: r[c] for c in cols})

    stages = ["lead", "sick", "return"]
    md = [f"# Planning metric — {a.regime} (tau={a.tau}, k={a.k}, ask costs {costs})", "",
          "mean places searched | mean rooms entered | confident share | " + " | ".join(f"mean total cost (c={c})" for c in costs), "",
          "| agent | " + " | ".join(f"{s} places / rooms / conf%" for s in stages) + " | " + " | ".join(f"{s} cost(c={c})" for s in stages for c in costs) + " |",
          "|---|" + "---|" * (len(stages) + len(stages) * len(costs))]
    for agent, s in summaries.items():
        cells = []
        for st in stages:
            d = s.get(st)
            cells.append(f"{d['mean_places']:.1f} / {d['mean_rooms']:.1f} / {100*d['confident_share']:.0f}%" if d else "-")
        for st in stages:
            d = s.get(st)
            for c in costs:
                cells.append(f"{d[f'mean_cost_c{c}']:.2f}" if d else "-")
        md.append(f"| {agent} | " + " | ".join(cells) + " |")
    (a.out / f"{a.regime}_summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md), file=sys.stderr)

    if a.match_rates:
        rates = [float(x) for x in a.match_rates.split(",")]
        run_matched(a.regime, agents, rates, costs, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
