"""Confidence-based shift study: banks, classical runs, tables, criteria.

    python3 -m baselines.patrol.confshift classical --config cfg.yaml --seeds 0-9 --out DIR
    python3 -m baselines.patrol.confshift report --logs DIR/classical/*.jsonl [more logs] --banks DIR/banks --out DIR/report
    python3 -m baselines.patrol.confshift criteria --logs DIR/classical/*.jsonl --banks DIR/banks

A config (YAML) names the households' generator rates, the patrol
schedule and the question mix:

    name: t03-11-19_all
    sim_dir: ../data/situation_sim/week8       # sim runs hh_s<seed>; regenerated when events differ
    day0: Tuesday
    days: 8
    events: {guest_visit: {weekday: 0.05, weekend: 0.14}, sick_day: {weekday: 0.03, weekend: 0.02}}
    patrol_hours: 4              # or
    patrol_times: "03:00,11:00,19:00"
    classes: null                # or a list of eligible object classes
    per_day: 32
    oversample: 60

``events`` lists the p_day overrides written into ``situation_sim/events.yaml``
(the only generator knob touched); the households for a config live in
``<sim_dir>`` and are regenerated only when the rates differ from what
they were generated with (a ``rates.json`` next to them records that).

Every agent answers one in-house spot with a confidence in [0, 1]. Score is
plain accuracy; coverage / selective accuracy at a threshold and the
reliability diagram are computed here from the logged confidence.
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Optional, Sequence, Tuple

import yaml

from baselines.patrol.bank import MAJOR_EVENTS, WEEKEND, build_bank, parse_times, patrol_label
from baselines.patrol.run import BELIEFS, SPOTS_ONLY, run_bank
from baselines.patrol.sweep import parse_seeds

REPO = pathlib.Path(__file__).resolve().parents[3]
EVENTS_YAML = REPO / "src" / "situation_sim" / "events.yaml"
THRESHOLDS = (0.5, 0.7, 0.9)
CONFIDENCE_FIELD = "top_prob"
"""Which logged number is 'confidence' in the tables: ``top_prob`` (the
belief's probability on its answer) or ``agreement`` (the share of the
hypothesis library's weight behind the answer; only the mixture logs it,
everyone else falls back to top_prob)."""
MAIN_THRESHOLD = 0.7
DAY_SHORT = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu",
             "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}
CLASSICAL = ("last_observation", "most_frequent", "timetable", "periodic_persistence", "perpetua_star")
AGENT_LABEL = {"LastObservation": "last seen", "MostFrequentLocation": "most frequent",
               "TimetableLookup": "timetable", "PeriodicPersistence": "periodic",
               "PerpetuaStar": "Perpetua*"}


# ------------------------------------------------------------------ config --

def load_config(path: pathlib.Path) -> dict:
    cfg = yaml.safe_load(path.read_text())
    cfg.setdefault("day0", "Tuesday")
    cfg.setdefault("days", 8)
    cfg.setdefault("events", {})
    cfg.setdefault("classes", None)
    cfg.setdefault("per_day", 32)
    cfg.setdefault("oversample", 60)
    cfg.setdefault("patrol_hours", 4)
    cfg.setdefault("patrol_times", None)
    cfg.setdefault("questions", "activity")
    cfg.setdefault("timetable_bin_hours", 1)
    cfg.setdefault("negative_evidence", "off")
    cfg["sim_dir"] = (path.parent / cfg["sim_dir"]).resolve() if not pathlib.Path(cfg["sim_dir"]).is_absolute() \
        else pathlib.Path(cfg["sim_dir"])
    return cfg


DEFAULT_RATES = {"rain": {"weekday": 0.14, "weekend": 0.14}, "guest_visit": {"weekday": 0.05, "weekend": 0.14},
                 "late_work": {"weekday": 0.10, "weekend": 0.0}, "grocery_delivery": {"weekday": 0.08, "weekend": 0.10},
                 "laundry_day": {"weekday": 0.08, "weekend": 0.22}, "sick_day": {"weekday": 0.03, "weekend": 0.02}}
"""The committed events.yaml rates (git HEAD 5b6bbe52d). A config's
``events`` overrides these; every other event is reset to its default, so
a config fully determines the rates in force."""


def current_rates() -> Dict[str, dict]:
    ev = yaml.safe_load(EVENTS_YAML.read_text())["events"]
    return {k: dict(v["p_day"]) for k, v in sorted(ev.items())}


def apply_rates(overrides: Dict[str, dict]) -> Dict[str, dict]:
    """Write p_day overrides into events.yaml (text edit of the one line per
    event, so comments and everything else stay put). Returns the rates in
    force afterwards."""
    text = EVENTS_YAML.read_text()
    lines = text.splitlines()
    cur = None
    for i, line in enumerate(lines):
        if line.startswith("  ") and not line.startswith("    ") and line.rstrip().endswith(":"):
            cur = line.strip()[:-1]
        if cur in DEFAULT_RATES and line.startswith("    p_day:"):
            r = {**DEFAULT_RATES[cur], **overrides.get(cur, {})}
            lines[i] = f"    p_day: {{weekday: {r['weekday']}, weekend: {r['weekend']}}}"
    new = "\n".join(lines) + "\n"
    if new != text:
        EVENTS_YAML.write_text(new)
    return current_rates()


def ensure_households(cfg: dict, seeds: Sequence[int]) -> pathlib.Path:
    """Generate hh_s<seed> under cfg['sim_dir'] with the config's event rates
    (only the seeds that are missing or were generated with other rates)."""
    rates = apply_rates(cfg["events"])
    sim_dir: pathlib.Path = cfg["sim_dir"]
    sim_dir.mkdir(parents=True, exist_ok=True)
    stamp = sim_dir / "rates.json"
    want = {"rates": rates, "day0": cfg["day0"], "days": cfg["days"]}
    have = json.loads(stamp.read_text()) if stamp.exists() else None
    todo = [s for s in sorted(seeds) if have != want or not (sim_dir / f"hh_s{s}" / "hidden_state.json").exists()]
    if have is not None and have != want:
        todo = sorted(seeds)  # rates changed: every requested seed is stale
    for s in todo:
        cmd = [sys.executable, "-m", "situation_sim.run", "--seed", str(s), "--out", str(sim_dir / f"hh_s{s}"),
               "--days", str(cfg["days"]), "--day0", cfg["day0"], "--no-checks"]
        r = subprocess.run(cmd, cwd=str(REPO / "src"), capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(f"sim seed {s} failed: {r.stderr[-2000:]}")
    if todo or have != want:
        stamp.write_text(json.dumps(want, indent=1, sort_keys=True))
    return sim_dir


def bank_for(cfg: dict, seed: int, out_dir: pathlib.Path) -> pathlib.Path:
    times = parse_times(cfg["patrol_times"]) if cfg.get("patrol_times") else None
    label = patrol_label(int(cfg["patrol_hours"]), times)
    return build_bank(cfg["sim_dir"] / f"hh_s{seed}", out_dir / "banks" / f"hh_s{seed}_{label}.jsonl",
                      int(cfg["patrol_hours"]), times, cfg["questions"], cfg["classes"], int(cfg["per_day"]), int(cfg["oversample"]))


def _one(job: Tuple[pathlib.Path, pathlib.Path, tuple]) -> str:
    bank, out, beliefs = job
    recs = run_bank(bank, "off", beliefs, answers=SPOTS_ONLY)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    with open(tmp, "w") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    tmp.rename(out)
    return str(out)


def cmd_classical(a) -> int:
    cfg = load_config(a.config)
    seeds = parse_seeds(a.seeds)
    ensure_households(cfg, seeds)
    out_dir = a.out
    names = tuple(a.beliefs or CLASSICAL)
    beliefs = tuple(({**b, "bin_hours": int(cfg["timetable_bin_hours"])} if b["name"] == "timetable" else b)
                    for b in BELIEFS if b["name"] in names)
    if cfg["negative_evidence"] == "off":
        # The pure classical baselines answer from sightings alone: the base pipeline's
        # empty-look suppression (1 - 2^(-age / half-life) per spot) is switched off by a
        # vanishing half-life, so every factor is 1 for any age > 0. Perpetua* handles
        # empties in its own filter and is left as is.
        beliefs = tuple(({**b, "negative_half_life_h": 1e-9} if not b["name"].startswith("perpetua") else b)
                        for b in beliefs)
    jobs = []
    for s in seeds:
        bank = bank_for(cfg, s, out_dir)
        log = out_dir / "classical" / f"{bank.stem}{a.suffix}.jsonl"
        if log.exists():
            continue
        jobs.append((bank, log, beliefs))
    (out_dir / "config.yaml").write_text(yaml.safe_dump({**cfg, "sim_dir": str(cfg["sim_dir"]),
                                                          "rates_in_force": current_rates()}, sort_keys=True))
    print(f"{len(jobs)} bank jobs, beliefs {names}", file=sys.stderr, flush=True)
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(_one, j) for j in jobs]
        for i, f in enumerate(as_completed(futs), 1):
            print(f"[{i}/{len(jobs)}] {f.result()}", file=sys.stderr, flush=True)
    return 0


# ----------------------------------------------------------------- tables --

def load_logs(paths: Sequence[str]) -> List[dict]:
    rows: List[dict] = []
    for p in sorted(set(paths)):
        with open(p) as f:
            rows += [json.loads(l) for l in f if l.strip()]
    for r in rows:
        r["agent"] = r.get("agent") or r["belief"]
        for k, v in AGENT_LABEL.items():
            if r["agent"].startswith(k):
                r["agent"] = v
        r["conf"] = float(r.get("top_prob", 0.0))
        if CONFIDENCE_FIELD != "top_prob" and r.get(CONFIDENCE_FIELD) is not None:
            r["conf"] = float(r[CONFIDENCE_FIELD])
    return rows


def load_headers(bank_dir: pathlib.Path) -> Dict[str, dict]:
    out = {}
    for p in sorted(bank_dir.glob("*.jsonl")):
        h = json.loads(p.read_text().splitlines()[0])
        out[h["household_id"]] = h
    return out


def day_label(d: int, day_names: Dict[int, str]) -> str:
    return DAY_SHORT.get(day_names.get(d, ""), f"d{d}")


def acc(rows: Sequence[dict]) -> float:
    return sum(r["correct"] for r in rows) / len(rows) if rows else float("nan")


def cover(rows: Sequence[dict], thr: float) -> Tuple[float, float, int]:
    sel = [r for r in rows if r["conf"] >= thr]
    return (len(sel) / len(rows) if rows else float("nan")), acc(sel), len(sel)


def pct(x: float) -> str:
    return "-" if x != x else f"{100 * x:.0f}%"


def by(rows: Sequence[dict], *keys: str) -> Dict[tuple, List[dict]]:
    g: Dict[tuple, List[dict]] = defaultdict(list)
    for r in rows:
        g[tuple(r[k] for k in keys)].append(r)
    return g


def shift_marks(headers: Dict[str, dict]) -> Dict[str, set]:
    return {h: set(hd["shift_days"]) for h, hd in headers.items()}


def event_days(headers: Dict[str, dict]) -> Dict[str, List[int]]:
    """Scored days carrying a major event, per household."""
    out = {}
    for h, hd in headers.items():
        days = []
        for d_str, causes in hd["day_causes"].items():
            d = int(d_str)
            if d in hd["scored_days"] and any(c.split(":")[0] in MAJOR_EVENTS for c in causes):
                days.append(d)
        out[h] = sorted(days)
    return out


def per_day_table(rows: List[dict], headers: Dict[str, dict], thr: Optional[float] = None) -> str:
    """Accuracy per agent per day (thr None) or coverage / selective accuracy."""
    day_names = {int(k): v for k, v in next(iter(headers.values()))["day_names"].items()}
    days = sorted({r["day_index"] for r in rows})
    agents = sorted({r["agent"] for r in rows})
    shift_count = defaultdict(int)
    hh = sorted({r["household"] for r in rows})
    marks = shift_marks(headers)
    for h in hh:
        for d in days:
            shift_count[d] += int(d in marks.get(h, set()))
    head = "| agent | " + " | ".join(f"{day_label(d, day_names)} ({shift_count[d]}/{len(hh)} shift)" for d in days) + " | all |"
    L = [head, "|" + "---|" * (len(days) + 2)]
    g = by(rows, "agent", "day_index")
    for ag in agents:
        cells = []
        for d in days + [None]:
            rs = [r for r in rows if r["agent"] == ag] if d is None else g.get((ag, d), [])
            if thr is None:
                cells.append(pct(acc(rs)))
            else:
                c, sa, n = cover(rs, thr)
                cells.append(f"{pct(c)} / {pct(sa)}")
        L.append(f"| {ag} | " + " | ".join(cells) + " |")
    return "\n".join(L)


def reliability(rows: List[dict], bins: Sequence[float] = (0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0001)) -> List[dict]:
    out = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        rs = [r for r in rows if lo <= r["conf"] < hi]
        out.append({"lo": lo, "hi": min(hi, 1.0), "n": len(rs), "acc": acc(rs),
                    "mean_conf": (sum(r["conf"] for r in rs) / len(rs)) if rs else float("nan")})
    return out


def ece(rows: List[dict]) -> float:
    tot = len(rows)
    return sum(b["n"] / tot * abs(b["acc"] - b["mean_conf"]) for b in reliability(rows) if b["n"]) if tot else float("nan")


def reliability_table(rows: List[dict]) -> str:
    agents = sorted({r["agent"] for r in rows})
    L = ["| agent | " + " | ".join(f"[{b['lo']:.2g},{b['hi']:.2g})" for b in reliability([])) + " | ECE |",
         "|" + "---|" * (len(reliability([])) + 2)]
    for ag in agents:
        rs = [r for r in rows if r["agent"] == ag]
        cells = [f"{pct(b['acc'])} (n={b['n']})" if b["n"] else "-" for b in reliability(rs)]
        L.append(f"| {ag} | " + " | ".join(cells) + f" | {ece(rs):.3f} |")
    return "\n".join(L)


def household_table(rows: List[dict], headers: Dict[str, dict], agent: str) -> str:
    day_names = {int(k): v for k, v in next(iter(headers.values()))["day_names"].items()}
    days = sorted({r["day_index"] for r in rows})
    marks = shift_marks(headers)
    ev = event_days(headers)
    L = [f"| household | " + " | ".join(day_label(d, day_names) for d in days) + " | shift days | event days |",
         "|" + "---|" * (len(days) + 3)]
    g = by([r for r in rows if r["agent"] == agent], "household", "day_index")
    for h in sorted({r["household"] for r in rows}):
        cells = []
        for d in days:
            a = acc(g.get((h, d), []))
            cells.append(("**" + pct(a) + "**") if d in marks.get(h, set()) else pct(a))
        L.append(f"| {h} | " + " | ".join(cells) + f" | {sorted(marks.get(h, []))} | {ev.get(h, [])} |")
    return "\n".join(L)


def household_kind(header: dict) -> str:
    """'retired' if any resident's intro card says retired (their weekday
    and weekend look alike), else 'working'. Read from the cards every
    agent sees, not from hidden state."""
    cards = header["protocol"]["residents"]
    return "retired" if any("retired" in c["occupation"] for c in cards) else "working"


def strata_table(rows: List[dict], headers: Dict[str, dict]) -> str:
    """Per-day accuracy per agent, split by household kind, with the Fri->Sat
    and weekday->weekend drops."""
    kind = {h: household_kind(hd) for h, hd in headers.items()}
    day_names = {int(k): v for k, v in next(iter(headers.values()))["day_names"].items()}
    days = sorted({r["day_index"] for r in rows})
    agents = sorted({r["agent"] for r in rows})
    L = ["| household kind (n) | agent | " + " | ".join(day_label(d, day_names) for d in days) + " | weekday | weekend | drop |",
         "|" + "---|" * (len(days) + 5)]
    for k in ("working", "retired"):
        hh = sorted(h for h in headers if kind[h] == k)
        sub = [r for r in rows if kind.get(r["household"]) == k]
        g = by(sub, "agent", "day_index")
        for ag in agents:
            cells = [pct(acc(g.get((ag, d), []))) for d in days]
            wk = [r for r in sub if r["agent"] == ag and day_names[r["day_index"]] not in WEEKEND]
            we = [r for r in sub if r["agent"] == ag and day_names[r["day_index"]] in WEEKEND]
            L.append(f"| {k} ({len(hh)}) | {ag} | " + " | ".join(cells) + f" | {pct(acc(wk))} | {pct(acc(we))} | {100 * (acc(wk) - acc(we)):+.0f} |")
    return "\n".join(L)


def class_share(rows: List[dict]) -> str:
    qs = {(r["household"], r["question_id"]): r["object_class"] for r in rows}
    cnt = defaultdict(int)
    for c in qs.values():
        cnt[c] += 1
    tot = sum(cnt.values())
    return ", ".join(f"{c} {100 * n / tot:.0f}%" for c, n in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])))


# --------------------------------------------------------------- criteria --

def day_of(headers: Dict[str, dict], weekday: str) -> int:
    hd = next(iter(headers.values()))
    for d, name in hd["day_names"].items():
        if name == weekday and int(d) in hd["scored_days"]:
            return int(d)
    raise KeyError(weekday)


def criteria(rows: List[dict], headers: Dict[str, dict]) -> dict:
    """The tuning acceptance numbers, pooled and per household."""
    wed, fri, sat = day_of(headers, "Wednesday"), day_of(headers, "Friday"), day_of(headers, "Saturday")
    g = by(rows, "agent", "day_index")
    gh = by(rows, "agent", "household", "day_index")
    agents = sorted({r["agent"] for r in rows})
    ev = event_days(headers)
    out: dict = {"rise_wed_fri": {}, "drop_sat_fri": {}, "drop_event": {}, "range": {}, "per_household": {}}
    for ag in agents:
        out["rise_wed_fri"][ag] = round(acc(g.get((ag, fri), [])) - acc(g.get((ag, wed), [])), 4)
        out["drop_sat_fri"][ag] = round(acc(g.get((ag, fri), [])) - acc(g.get((ag, sat), [])), 4)
        # event day vs the day before, pooled over the households' event days (weekend event days excluded:
        # they are already a shift day, and "the day before" would be a weekend day as well)
        before, on, per_h = [], [], {}
        for h, days in sorted(ev.items()):
            for d in days:
                hd = headers[h]
                if hd["day_names"][str(d)] in WEEKEND or d - 1 not in hd["scored_days"]:
                    continue
                if hd["day_names"][str(d - 1)] in WEEKEND:
                    continue
                on += gh.get((ag, h, d), [])
                before += gh.get((ag, h, d - 1), [])
                per_h[f"{h}:d{d}"] = round(acc(gh.get((ag, h, d - 1), [])) - acc(gh.get((ag, h, d), [])), 4)
        out["drop_event"][ag] = {"pooled": round(acc(before) - acc(on), 4) if on else None, "n_event_days": len(per_h),
                                 "per_household": per_h}
        days = sorted({r["day_index"] for r in rows})
        accs = [acc(g.get((ag, d), [])) for d in days]
        out["range"][ag] = {"min": round(min(accs), 4), "max": round(max(accs), 4)}
        out["per_household"][ag] = {h: {"rise_wed_fri": round(acc(gh.get((ag, h, fri), [])) - acc(gh.get((ag, h, wed), [])), 4),
                                        "drop_sat_fri": round(acc(gh.get((ag, h, fri), [])) - acc(gh.get((ag, h, sat), [])), 4)}
                                    for h in sorted({r["household"] for r in rows})}
    hh = sorted(headers)
    out["households_with_major_event_on_scored_day"] = f"{sum(1 for h in hh if ev[h])}/{len(hh)}"
    out["event_days"] = ev
    return out


def criteria_text(c: dict) -> str:
    L = ["| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |",
         "|---|---|---|---|---|---|"]
    for ag in sorted(c["rise_wed_fri"]):
        de = c["drop_event"][ag]
        ev_cell = "-" if de["pooled"] is None else f"{100 * de['pooled']:+.0f}"
        L.append(f"| {ag} | {100 * c['rise_wed_fri'][ag]:+.0f} | {100 * c['drop_sat_fri'][ag]:+.0f} | "
                 f"{ev_cell} ({de['n_event_days']}) | "
                 f"{100 * c['range'][ag]['min']:.0f} | {100 * c['range'][ag]['max']:.0f} |")
    L.append("")
    L.append(f"Households with a major event on a scored day: {c['households_with_major_event_on_scored_day']}; "
             f"event days: {c['event_days']}")
    return "\n".join(L)


def cmd_criteria(a) -> int:
    rows = load_logs(a.logs)
    headers = load_headers(a.banks)
    c = criteria(rows, headers)
    print(criteria_text(c))
    if a.json:
        a.json.write_text(json.dumps(c, indent=1, sort_keys=True))
    return 0


def cmd_report(a) -> int:
    rows = load_logs(a.logs)
    headers = load_headers(a.banks)
    a.out.mkdir(parents=True, exist_ok=True)
    day_names = {int(k): v for k, v in next(iter(headers.values()))["day_names"].items()}
    hh = sorted({r["household"] for r in rows})
    agents = sorted({r["agent"] for r in rows})
    counts = defaultdict(int)
    for r in rows:
        counts[(r["household"], r["agent"])] += 1
    L = [f"# {a.title}", "",
         f"{len(hh)} households, {len(agents)} agents, {len(rows)} agent-question records. "
         f"Shift days per household (weekend + major event days): "
         + "; ".join(f"{h} {sorted(headers[h]['shift_days'])}" for h in hh) + ".", "",
         "Questions per household per agent: " + ", ".join(f"{h} {counts[(h, agents[0])]}" for h in hh) + ".", "",
         "Object classes in the questions: " + class_share(rows) + ".", "",
         "## Figure 1: accuracy per day (all questions)", "", per_day_table(rows, headers), ""]
    for thr in THRESHOLDS:
        L += [f"## Figure 2 (threshold {thr}): coverage / selective accuracy per day", "",
              f"Coverage = share of questions answered with confidence >= {thr}; selective accuracy = accuracy on those.", "",
              per_day_table(rows, headers, thr), ""]
    L += ["## Reliability (stated confidence vs observed accuracy, pooled over the week)", "", reliability_table(rows), ""]
    L += ["## Split by household kind (from the intro cards: any retired resident, or none)", "",
          "Retired residents are home on weekdays too, so the weekend is not a routine shift for their household.", "",
          strata_table(rows, headers), ""]
    L += ["## Tuning criteria numbers", "", criteria_text(criteria(rows, headers)), ""]
    for ag in agents:
        L += [f"## Per household: {ag} (bold = shift day)", "", household_table(rows, headers, ag), ""]
    (a.out / "summary.md").write_text("\n".join(L))
    (a.out / "criteria.json").write_text(json.dumps(criteria(rows, headers), indent=1, sort_keys=True))
    print("\n".join(L[:12]))
    print(criteria_text(criteria(rows, headers)))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classical")
    c.add_argument("--config", type=pathlib.Path, required=True)
    c.add_argument("--seeds", default="0-9")
    c.add_argument("--out", type=pathlib.Path, required=True)
    c.add_argument("--beliefs", nargs="*", default=None)
    c.add_argument("--suffix", default="")
    c.add_argument("--workers", type=int, default=10)
    c.set_defaults(fn=cmd_classical)
    r = sub.add_parser("report")
    r.add_argument("--logs", nargs="+", required=True)
    r.add_argument("--banks", type=pathlib.Path, required=True)
    r.add_argument("--out", type=pathlib.Path, required=True)
    r.add_argument("--title", default="Confidence shift study")
    r.set_defaults(fn=cmd_report)
    k = sub.add_parser("criteria")
    k.add_argument("--logs", nargs="+", required=True)
    k.add_argument("--banks", type=pathlib.Path, required=True)
    k.add_argument("--json", type=pathlib.Path, default=None)
    k.set_defaults(fn=cmd_criteria)
    for sp in (r, k):
        sp.add_argument("--confidence", default="top_prob", choices=("top_prob", "agreement"))
    a = ap.parse_args(argv)
    global CONFIDENCE_FIELD
    CONFIDENCE_FIELD = getattr(a, "confidence", "top_prob")
    a.logs = [p for pat in getattr(a, "logs", []) or [] for p in glob.glob(pat)] or getattr(a, "logs", None)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
