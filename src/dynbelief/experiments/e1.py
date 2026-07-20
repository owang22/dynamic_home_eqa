"""E1 -- adaptation curve from observation history (tests C1; fastest signal).

Forecasting only: no budget, no decisions. For each (bank, history-days D,
profile-text on/off), the model is shown the MULTI-DAY OBSERVATION HISTORY over
days [0, D) -- the bank's shared, jittered snapshot stream (held-out objects
stripped, per A3) -- and predicts where each day-D query object is now, as a
top-3 receptacle distribution.

Design (v2, 2026-07-19):
  * Memory = the frozen bank's `observations.jsonl` (2-4 jittered full-home
    snapshots/day). IDENTICAL stream feeds every arm (LLM + classical) -- the
    comparability invariant. Rendered as a per-object time series so routine
    structure (dish cycle, morning/evening carry) is visible.
  * Output = top-3 {receptacle, p} (remainder implicit) -> proper scoring:
    Brier + log-loss over the candidate set, not ECE-on-argmax.
  * Comprehension probes: hand-crafted episodes whose answer is blatant from
    the history alone. Fail them -> task-comprehension failure. Pass them but
    score ~0 on genuinely-moved episodes -> the failure is FORECASTING, which
    no prompt revision fixes. (Falsifiable diagnostic.)

Banks: typ_v1 (3 typical households a day-schedule prior fits) vs atyp_v2 (3
realistic atypical households the same prior should mishandle -- T1 night-shift,
T2 three-twelves, T2 weekend-worker), + atyp_shift_v1 (C4 routine-destroyed
control). Model: local Qwen (--client qwen), an API model (--client openai), or
MockForecastClient (offline dev).
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
from dataclasses import dataclass, field

from dynbelief import MIN_PER_DAY
from dynbelief.profiles.schema import load_profile, Profile, default_class

HISTORY_DAYS = [0, 1, 3, 7, 14]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _when(t: int) -> str:
    day = t // MIN_PER_DAY
    mins = t % MIN_PER_DAY
    return f"{DAYS[day % 7]} {mins // 60:02d}:{mins % 60:02d}"


# ── memory: multi-day observation history from the bank's shared stream ──────

def history_runs(observations: list[dict], heldout: set[str], D: int) -> dict[str, list]:
    """Per observed object, maximal runs of a constant observed receptacle over
    days [0, D): [[recep, t_first, t_last], ...]. Held-out objects excluded."""
    runs: dict[str, list] = {}
    for row in sorted(observations, key=lambda r: r["t_min"]):
        if row["day"] >= D:
            break
        for o, rec in row["parents"].items():
            if o in heldout:
                continue
            r = runs.setdefault(o, [])
            if r and r[-1][0] == rec:
                r[-1][2] = row["t_min"]
            else:
                r.append([rec, row["t_min"], row["t_min"]])
    return runs


def render_history(runs: dict[str, list]) -> str:
    if not runs:
        return "(no prior observations)"
    lines = []
    for o in sorted(runs):
        parts = []
        for rec, t0, t1 in runs[o]:
            parts.append(f"{rec} ({_when(t0)})" if t0 == t1
                         else f"{rec} ({_when(t0)}–{_when(t1)})")
        lines.append(f"  {o}: " + ", ".join(parts))
    return "\n".join(lines)


def last_observed(runs: dict[str, list], obj: str):
    r = runs.get(obj)
    return (r[-1][0], r[-1][2]) if r else None


# ── profile prose (deterministic render; NOT model-authored) ─────────────────

def profile_prose(ch: Profile) -> str:
    lines = [f"Household: {ch.household}.", f"Residents and weekly routine:"]
    for r in ch.residents:
        lines.append(f"- {r.id} ({r.description}):")
        for b in sorted(r.schedule, key=lambda b: (b.days[0], b.start_min)):
            days = ",".join(b.days)
            lines.append(f"    {b.activity} on {days} "
                         f"{b.start_min // 60:02d}:{b.start_min % 60:02d}-"
                         f"{b.end_min // 60:02d}:{b.end_min % 60:02d}")
    lines.append("Typical resting places:")
    for o, p in sorted(ch.placements.items()):
        lines.append(f"    {o} usually rests at {p.home}")
    return "\n".join(lines)


# ── prompt (one fixed template) ──────────────────────────────────────────────

_SYSTEM = (
    "You predict where a household object is located at a given time, based on a "
    "memory of past observations of that home.\n\n"
    "Facts about the setting:\n"
    "- Observations are snapshots taken at the listed times only. Between "
    "snapshots, residents' activities (meals, work/school, tidying, evening "
    "wind-down, weekend rhythms) may move objects; those movements are not "
    "recorded. An object's most recent observation may therefore no longer "
    "reflect where it is now.\n"
    "- 'elsewhere' means the object is not at any tracked receptacle (e.g., "
    "carried by a resident or out of the home).\n"
    "- Receptacle ids encode their room (e.g., counter_k1 is in the kitchen, "
    "nightstand_r1 in the bedroom).\n\n"
    "Consider the elapsed time since each relevant observation, the time of day "
    "and day of week now, and the movement patterns visible in the history. "
    "Answer with the single most likely receptacle from the candidate list and "
    "your probability that this answer is correct."
)


def build_prompt(hist_text: str, candidates: list[str], obj: str, t_query: int,
                 profile_text: str | None) -> tuple[str, str]:
    parts = [f"Current time: {_when(t_query)}.", "", "Observations so far "
             "(each object, receptacles it was seen at, in order):", hist_text, ""]
    if profile_text:
        parts += ["What is known about this household's routine:", profile_text, ""]
    parts += [f"Candidate receptacles: {', '.join(candidates)}, elsewhere.", "",
              f"Where is `{obj}` now? Give up to three candidate receptacles with "
              f"probabilities (most likely first); the remaining probability is "
              f"assumed spread over the others."]
    return _SYSTEM, "\n".join(parts)


SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "predictions": {
            "type": "array", "minItems": 1, "maxItems": 3,
            "items": {"type": "object",
                      "properties": {"receptacle": {"type": "string"},
                                     "p": {"type": "number", "minimum": 0, "maximum": 1}},
                      "required": ["receptacle", "p"], "additionalProperties": False},
        },
    },
    "required": ["reasoning", "predictions"],
    "additionalProperties": False,
}


def prompt_hash() -> str:
    return hashlib.sha256((_SYSTEM + json.dumps(SCHEMA)).encode()).hexdigest()[:12]


# ── proper scoring over the candidate set ────────────────────────────────────

def score_prediction(preds: list[dict], candidates: list[str], true: str):
    """preds: [{receptacle, p}] top-3. Returns (argmax, p_true, brier, logloss,
    top3_correct). top3_correct = the true receptacle is among the NAMED top-3
    predictions (the natural top-3-distribution accuracy). Distribution:
    predicted receptacles get their (clipped, capped-to-1) p; the remainder
    spreads uniformly over the un-predicted candidates."""
    C = list(candidates)
    idx = {c: i for i, c in enumerate(C)}
    dist = {c: 0.0 for c in C}
    named, mass = [], 0.0
    for pr in preds:
        rec = str(pr.get("receptacle", ""))
        p = min(max(float(pr.get("p", 0.0)), 0.0), 1.0)
        if rec in dist and rec not in named:
            named.append(rec)
            dist[rec] = p
            mass += p
    if mass > 1.0:                        # renormalise predicted mass to <=1
        for r in named:
            dist[r] /= mass
        mass = 1.0
    others = [c for c in C if c not in named]
    if others:
        rem = (1.0 - mass) / len(others)
        for c in others:
            dist[c] = rem
    argmax = max(dist, key=dist.get) if dist else "elsewhere"
    p_true = dist.get(true, 0.0)
    brier = sum((dist[c] - (1.0 if c == true else 0.0)) ** 2 for c in C)
    # log-loss with probabilities clipped to [0.01, 0.99] (C-tier brief;
    # stated in methods). The SAME scorer serves LLM and classical arms.
    logloss = -math.log(min(0.99, max(0.01, p_true)))
    top3_correct = int(true in named)
    return argmax, p_true, brier, logloss, top3_correct


# ── clients ──────────────────────────────────────────────────────────────────

class MockForecastClient:
    """Offline dev client: predicts each object's most-recent observed receptacle
    (read from the prompt's history), p=0.7 with 0.2 on its home as a 2nd guess.
    A genuine last-observation baseline, NOT a stand-in for an LLM."""
    model = "mock_lastobs"

    def generate(self, system, user, schema, seed=None, temperature=0.0):
        obj = user.split("Where is `", 1)[1].split("`", 1)[0]
        rec = None
        for line in user.splitlines():
            s = line.strip()
            if s.startswith(f"{obj}: "):
                # last receptacle token in the run list "rec (time), rec (time)"
                segs = s.split(": ", 1)[1].split(", ")
                rec = segs[-1].split(" (", 1)[0].strip()
                break
        if rec is None:
            return json.dumps({"reasoning": "unseen",
                               "predictions": [{"receptacle": "elsewhere", "p": 0.3}]})
        return json.dumps({"reasoning": "last observed there",
                           "predictions": [{"receptacle": rec, "p": 0.7}]})


# ── bank IO ──────────────────────────────────────────────────────────────────

def _load_household(bank_dir: pathlib.Path, hh_name: str):
    hd = bank_dir / hh_name
    reg = json.loads((hd / "registry.json").read_text())
    recep_label = {v: k for k, v in reg["receptacles"].items()}
    obj_label = {v: k for k, v in reg["objects"].items()}
    queries = [json.loads(l) for l in (hd / "queries.jsonl").open()]
    observations = [json.loads(l) for l in (hd / "observations.jsonl").open()]
    gt = {(r["object"], r["t_query"]): r
          for r in (json.loads(l) for l in (hd / "ground_truth.jsonl").open())}
    targets = json.loads((hd / "targets.json").read_text())
    return reg, observations, queries, gt, targets, recep_label


def _resolve_profile(reg, manual_dir):
    base = reg["profile"]["household"].split("__")[0]
    ch = load_profile(manual_dir / f"{base}.yaml")
    if reg["profile"].get("transformation"):
        from dynbelief.profiles import transforms
        tf = reg["profile"]["transformation"]
        ch = transforms.apply_transform(ch, tf["type"], **tf["params"])
    return ch


def _candidates(ch, recep_label):
    return sorted({p.home for p in ch.placements.values()}
                  | {r for r in recep_label.values() if r != "elsewhere"})


# ── run one household-condition ──────────────────────────────────────────────

@dataclass
class E1Config:
    banks_root: pathlib.Path
    manual_dir: pathlib.Path
    profile_text_variants: tuple[bool, ...] = (False, True)
    history_days: tuple[int, ...] = tuple(HISTORY_DAYS)
    seed: int = 7
    hh_limit: int | None = None


def run_household(client, bank: str, bank_dir: pathlib.Path, hh_name: str,
                  manual_dir: pathlib.Path, D: int, use_profile: bool,
                  seed: int) -> list[dict]:
    reg, observations, queries, gt, targets, recep_label = _load_household(bank_dir, hh_name)
    ch = _resolve_profile(reg, manual_dir)
    heldout = set(targets["held_out"])
    runs = history_runs(observations, heldout, D)
    hist_text = render_history(runs)
    candidates = _candidates(ch, recep_label)
    cand_set = candidates + ["elsewhere"]
    prose = profile_prose(ch) if use_profile else None

    day_queries = [q for q in queries if q["day"] == D] if D < reg["n_days"] else []
    rows = []
    for q in day_queries:
        obj, tq = q["object"], q["t_query"]
        system, user = build_prompt(hist_text, candidates, obj, tq, prose)
        try:
            raw = client.generate(system, user, SCHEMA, seed=seed, temperature=0.2)
            preds = json.loads(raw)["predictions"]
        except Exception as e:
            raw, preds = f"[error] {e}", []
        g = gt.get((obj, tq), {})
        true_recep = g.get("true_receptacle")
        argmax, p_true, brier, logloss, top3 = score_prediction(preds, cand_set, true_recep)
        lo = last_observed(runs, obj)
        moved = (lo is not None and lo[0] != true_recep)
        rows.append({
            "bank": bank, "household": hh_name, "history_days": D,
            "profile_text": use_profile, "object": obj, "class": default_class(obj),
            "tercile": g.get("tercile"), "held_out": obj in heldout,
            "t_query": tq, "true_receptacle": true_recep,
            "predicted": argmax, "p_true": round(p_true, 4),
            "brier": round(brier, 4), "logloss": round(logloss, 4),
            "correct": int(argmax == true_recep), "top3_correct": top3,
            "moved_since_obs": int(moved),
            "last_obs": (lo[0] if lo else None),
            "model": getattr(client, "model", "?"), "prompt_hash": prompt_hash(),
        })
    return rows


def run_grid(client, cfg: E1Config, banks=("typ_v1", "atyp_v2"),
             extra_c4=True) -> list[dict]:
    rows: list[dict] = []
    for bank in banks:
        bank_dir = cfg.banks_root / bank
        if not bank_dir.exists():
            continue
        hh_names = [p.name for p in sorted(bank_dir.iterdir())
                    if p.is_dir() and (p / "registry.json").exists()][:cfg.hh_limit]
        for D in cfg.history_days:
            for use_ct in cfg.profile_text_variants:
                for hh in hh_names:
                    rows += run_household(client, bank, bank_dir, hh, cfg.manual_dir,
                                          D, use_ct, cfg.seed)
    if extra_c4 and (cfg.banks_root / "atyp_shift_v1").exists():
        bank_dir = cfg.banks_root / "atyp_shift_v1"
        hh_names = [p.name for p in sorted(bank_dir.iterdir())
                    if p.is_dir() and (p / "registry.json").exists()][:cfg.hh_limit]
        for use_ct in cfg.profile_text_variants:
            for hh in hh_names:
                rows += run_household(client, "atyp_shift_v1", bank_dir, hh,
                                      cfg.manual_dir, 7, use_ct, cfg.seed)
    return rows


# ── comprehension probes (blatant-from-history diagnostic) ───────────────────

def build_probes(banks_root: pathlib.Path, manual_dir: pathlib.Path) -> list[dict]:
    """Hand-crafted episodes whose answer is unambiguous from the history alone,
    built on the frozen single_adult bank and VERIFIED against ground truth.
    Each: a static object, an immediate-parrot, and a periodic-cycle case."""
    bank_dir = banks_root / "typ_v1"
    hh = "single_adult_typ_v1"
    reg, observations, queries, gt, targets, recep_label = _load_household(bank_dir, hh)
    ch = _resolve_profile(reg, manual_dir)
    candidates = _candidates(ch, recep_label)
    ev = None  # GT comes from the ground_truth table + observations

    def true_at(obj, t):
        # nearest ground-truth receptacle: reuse the observation stream (exact)
        best = None
        for row in sorted(observations, key=lambda r: r["t_min"]):
            if row["t_min"] <= t and obj in row["parents"]:
                best = row["parents"][obj]
        return best

    probes = []

    # Probe 1 -- STATIC: vase never moves; query late, history shows it fixed.
    D = 14
    runs = history_runs(observations, set(), D)
    tq = D * MIN_PER_DAY + 12 * 60
    exp = true_at("vase", tq)
    probes.append(dict(name="static_vase", D=D, obj="vase", t_query=tq, expected=exp,
                       rationale="vase is decorative and never moves; history shows it "
                                 "at one receptacle throughout"))

    # Probe 2 -- IMMEDIATE PARROT: query an object 10 min after an observation
    # that saw it, where it does not change before the query.
    obs_sorted = sorted(observations, key=lambda r: r["t_min"])
    picked = None
    for row in obs_sorted:
        if row["day"] < 6:
            continue
        for o in ("toaster", "first_aid_kit", "vase"):
            t = row["t_min"] + 10
            if true_at(o, t) == row["parents"][o]:
                picked = (o, row["day"], t, row["parents"][o]); break
        if picked:
            break
    o, dd, tq2, exp2 = picked
    probes.append(dict(name="immediate_parrot", D=dd + 1, obj=o, t_query=tq2, expected=exp2,
                       rationale=f"{o} was observed at {exp2} minutes before the query and "
                                 f"nothing moved it"))

    # Probe 3 -- PERIODIC: find a (mobile object, hour) whose observed receptacle
    # is IDENTICAL across the last >=3 days at that hour, then query at that hour
    # on the next day. Blatant periodicity, verified from the stream (not assumed).
    D = 12
    mobile = ["knife", "mug", "phone", "plate", "bowl", "fork", "water_glass"]
    obs_by_dayhour: dict = {}
    for row in obs_sorted:
        obs_by_dayhour.setdefault((row["day"], (row["t_min"] % MIN_PER_DAY) // 60), row)
    probe3 = None
    for o in mobile:
        for hr in range(24):
            locs = [row["parents"][o] for (dd, hh_), row in obs_by_dayhour.items()
                    if hh_ == hr and D - 4 <= dd < D and o in row["parents"]]
            if len(locs) >= 3 and len(set(locs)) == 1 and locs[0] != "elsewhere":
                probe3 = (o, hr, locs[0]); break
        if probe3:
            break
    if probe3:
        o3, hr3, exp3 = probe3
        tq3 = D * MIN_PER_DAY + hr3 * 60 + 5
        probes.append(dict(name="periodic_object", D=D, obj=o3, t_query=tq3, expected=exp3,
                           rationale=f"the history shows {o3} at {exp3} every day around "
                                     f"{hr3:02d}:00 (a stable daily pattern)"))

    # attach the rendered prompt inputs
    for p in probes:
        runs = history_runs(observations, set(), p["D"])
        p["hist_text"] = render_history(runs)
        p["candidates"] = candidates
    return probes


def run_probes(client, banks_root, manual_dir) -> list[dict]:
    out = []
    for p in build_probes(banks_root, manual_dir):
        system, user = build_prompt(p["hist_text"], p["candidates"], p["obj"],
                                    p["t_query"], None)
        try:
            raw = client.generate(system, user, SCHEMA, seed=7, temperature=0.2)
            parsed = json.loads(raw)
            preds = parsed["predictions"]
            reasoning = parsed.get("reasoning", "")
        except Exception as e:
            preds, reasoning = [], f"[error] {e}"
        argmax, p_true, brier, logloss, _t3 = score_prediction(
            preds, p["candidates"] + ["elsewhere"], p["expected"])
        out.append({"probe": p["name"], "obj": p["obj"], "when": _when(p["t_query"]),
                    "expected": p["expected"], "predicted": argmax,
                    "pass": argmax == p["expected"], "p_true": round(p_true, 3),
                    "rationale": p["rationale"], "model_reasoning": reasoning[:300]})
    return out


# ── endpoints ────────────────────────────────────────────────────────────────

def _agg(rows, key):
    vals = [r[key] for r in rows]
    return round(sum(vals) / len(vals), 4) if vals else float("nan")


def summarise(rows: list[dict], probes: list[dict] | None = None) -> str:
    banks = sorted({r["bank"] for r in rows})
    out = ["# E1 v2 -- adaptation from observation history", "",
           f"rows: {len(rows)}  |  model: {sorted({r['model'] for r in rows})}  |  "
           f"prompt_hash: {sorted({r['prompt_hash'] for r in rows})[0]}", ""]

    if probes is not None:
        n_pass = sum(p["pass"] for p in probes)
        out += [f"## Comprehension probes: {n_pass}/{len(probes)} passed",
                "| probe | object | when | expected | predicted | pass | p(true) |",
                "|---|---|---|---|---|---|---|"]
        for p in probes:
            out.append(f"| {p['probe']} | {p['obj']} | {p['when']} | {p['expected']} | "
                       f"{p['predicted']} | {'YES' if p['pass'] else 'NO'} | {p['p_true']} |")
        out += ["", "If these fail, the model isn't reading the task. If they pass but "
                "moved-episode accuracy is ~0, the failure is forecasting (unrecorded "
                "movement), not prompt-fixable.", ""]

    for ct in (False, True):
        out.append(f"## profile_text = {ct}  (accuracy / Brier / log-loss vs history-days)")
        out.append("| bank | metric | " + " | ".join(f"D={d}" for d in HISTORY_DAYS)
                   + " | moved@D14 |")
        out.append("|---|---|" + "---|" * (len(HISTORY_DAYS) + 1))
        for bank in banks:
            if bank == "atyp_shift_v1":
                continue
            for metric in ("correct", "brier", "logloss"):
                cells = []
                for d in HISTORY_DAYS:
                    sub = [r for r in rows if r["bank"] == bank and r["history_days"] == d
                           and r["profile_text"] == ct]
                    cells.append(f"{_agg(sub, metric):.3f}" if sub else "-")
                moved = [r for r in rows if r["bank"] == bank and r["history_days"] == 14
                         and r["profile_text"] == ct and r["moved_since_obs"]]
                label = {"correct": "acc", "brier": "Brier", "logloss": "logloss"}[metric]
                out.append(f"| {bank} | {label} | " + " | ".join(cells)
                           + f" | {_agg(moved, metric):.3f} |")
        out.append("")

    # moved vs not split (pooled D>=1)
    out += ["## Moved vs not-moved (pooled D>=1, profile_text=False)",
            "| bank | not-moved acc | moved acc | moved Brier |", "|---|---|---|---|"]
    for bank in banks:
        if bank == "atyp_shift_v1":
            continue
        sub = [r for r in rows if r["bank"] == bank and r["history_days"] >= 1
               and not r["profile_text"]]
        nm = [r for r in sub if not r["moved_since_obs"]]
        mv = [r for r in sub if r["moved_since_obs"]]
        out.append(f"| {bank} | {_agg(nm, 'correct'):.3f} (n={len(nm)}) | "
                   f"{_agg(mv, 'correct'):.3f} (n={len(mv)}) | {_agg(mv, 'brier'):.3f} |")
    out += ["", "## C4 (held-out vs observed, atyp_v2 vs atyp_shift_v1, D=7)",
            "| slice | atyp_v2 | atyp_shift_v1 |", "|---|---|---|"]
    for label, f in [("all", lambda r: True), ("held-out", lambda r: r["held_out"]),
                     ("observed", lambda r: not r["held_out"])]:
        def cell(b):
            s = [r for r in rows if r["bank"] == b and r["history_days"] == 7 and f(r)]
            return f"{_agg(s, 'correct'):.3f}" if s else "-"
        out.append(f"| {label} | {cell('atyp_v2')} | {cell('atyp_shift_v1')} |")
    out += ["", "Numbers only. C1 = atyp accuracy rises with history while typ stays "
            "flatter; lower Brier/log-loss = better-calibrated. With the mock client "
            "these are a last-observation baseline, not an LLM result."]
    return "\n".join(out)


# ── CLI ──────────────────────────────────────────────────────────────────────

def _write_rows(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def streams_call_plan(banks_root, banks, d_grid, streams, n_per_cell):
    """Total forecasting calls for a (balanced) grid, without spending anything.
    n_per_cell is per (household, D, stream); every cell gets the same n (even
    spread across the settings)."""
    total, per_bank = 0, {}
    for bank in banks:
        bd = banks_root / bank
        if not bd.exists():
            continue
        hh = [p for p in bd.iterdir() if p.is_dir() and (p / "registry.json").exists()]
        n = len(hh) * len(d_grid) * len(streams) * n_per_cell
        per_bank[bank] = n
        total += n
    return total, per_bank


def run_streams_llm(client, banks_root, manual_dir, banks=("typ_v1", "atyp_v2"),
                    d_grid=(0, 1, 3, 7, 14, 28), streams=("natural", "moved_enriched"),
                    n_per_cell=36, seed=7, max_completion_tokens=None,
                    reasoning_effort=None):
    """Score the LLM on the SAME stream episodes the classical arms saw
    (apples-to-apples), profile_text=False. Memory = observation history over
    days [0,D) (held-out stripped). n_per_cell is per (household,D,stream) — the
    same for every cell, so coverage of the settings we care about is even.
    max_completion_tokens / reasoning_effort cap reasoning-model cost."""
    from dynbelief.experiments.streams import load_gt, sample_stream
    gen_kwargs = {}
    if max_completion_tokens is not None:
        gen_kwargs["max_completion_tokens"] = max_completion_tokens
    if reasoning_effort is not None:
        gen_kwargs["reasoning_effort"] = reasoning_effort
    rows = []
    for bank in banks:
        bank_dir = banks_root / bank
        if not bank_dir.exists():
            continue
        for hh in sorted(p.name for p in bank_dir.iterdir()
                         if p.is_dir() and (p / "registry.json").exists()):
            reg, observations, queries, gt, targets, recep_label = _load_household(bank_dir, hh)
            ch = _resolve_profile(reg, manual_dir)
            heldout = set(targets["held_out"])
            candidates = _candidates(ch, recep_label)
            cand_set = candidates + ["elsewhere"]
            for D in d_grid:
                runs = history_runs(observations, heldout, D)
                hist_text = render_history(runs)
                for stream in streams:
                    eps = sample_stream(bank_dir / hh, bank, hh, D, stream, n_per_cell)
                    for ep in eps:
                        obj, tq = ep["object"], ep["t_query"]
                        system, user = build_prompt(hist_text, candidates, obj, tq, None)
                        try:
                            preds = json.loads(client.generate(system, user, SCHEMA,
                                               seed=seed, temperature=0.2, **gen_kwargs))["predictions"]
                        except Exception as e:
                            preds = []
                        argmax, p_true, brier, logloss, t3 = score_prediction(
                            preds, cand_set, ep["true_receptacle"])
                        rows.append({
                            "bank": bank, "household": hh, "history_days": D,
                            "stream": stream, "query_id": ep["query_id"],
                            "profile_text": False, "object": obj,
                            "class": default_class(obj), "held_out": ep["held_out"],
                            "moved_since_obs": ep["moved_since_obs"], "t_query": tq,
                            "true_receptacle": ep["true_receptacle"], "predicted": argmax,
                            "p_true": round(p_true, 4), "brier": round(brier, 4),
                            "logloss": round(logloss, 4),
                            "correct": int(argmax == ep["true_receptacle"]),
                            "top3_correct": t3, "model": getattr(client, "model", "?"),
                        })
    return rows


def main(argv=None) -> int:
    import argparse
    from dynamic_home_eqa.paths import REPO_ROOT, REPORTS_DIR
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--client", choices=["mock", "qwen", "openai"], default="mock")
    ap.add_argument("--streams-rerun", action="store_true",
                    help="rerun on the classical stream grid -> rows_classical_grid_<model>.jsonl")
    ap.add_argument("--banks", default="typ_v1,atyp_v2", help="comma list of banks")
    ap.add_argument("--n-per-cell", type=int, default=36,
                    help="episodes per (household,D,stream) cell — same for every cell (even spread)")
    ap.add_argument("--max-tokens", type=int, default=None,
                    help="cap on completion (reasoning+output) tokens per call")
    ap.add_argument("--reasoning", default=None, choices=["low", "medium", "high"],
                    help="reasoning_effort for reasoning-class models")
    ap.add_argument("--plan-only", action="store_true",
                    help="print the call plan (count) and exit WITHOUT spending")
    ap.add_argument("--model", default="gpt-5.4-mini")
    ap.add_argument("--banks-root", type=pathlib.Path, default=REPO_ROOT / "banks")
    ap.add_argument("--manual-dir", type=pathlib.Path, default=REPO_ROOT / "profiles" / "manual")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8300")
    ap.add_argument("--out", type=pathlib.Path, default=REPORTS_DIR.parent / "e1")
    ap.add_argument("--smoke", action="store_true",
                    help="tiny pilot: 1 household/bank, D in {0,7}, probes only")
    args = ap.parse_args(argv)

    cfg = E1Config(banks_root=args.banks_root, manual_dir=args.manual_dir)
    extra_c4 = True
    if args.smoke:
        cfg.history_days = (0, 7)
        extra_c4 = False
    if args.client == "qwen":
        from dynbelief.llm_agent.clients import local_qwen
        client = local_qwen(args.endpoint)
    elif args.client == "openai":
        from dynbelief.llm_agent.clients import OpenAIClient
        client = OpenAIClient(model=args.model)
    else:
        client = MockForecastClient()

    if args.streams_rerun or args.plan_only:
        banks = tuple(args.banks.split(","))
        d_grid = (0, 1, 3, 7, 14, 28)
        streams = ("natural", "moved_enriched")
        total, per_bank = streams_call_plan(args.banks_root, banks, d_grid, streams,
                                            args.n_per_cell)
        print(f"[plan] banks={banks} D={d_grid} streams={streams} "
              f"n_per_cell={args.n_per_cell}")
        print(f"[plan] CALLS: {total} total  {per_bank}")
        if args.max_tokens:
            print(f"[plan] max_completion_tokens={args.max_tokens} "
                  f"-> <= {total * args.max_tokens:,} output tokens (hard cap)")
        if args.reasoning:
            print(f"[plan] reasoning_effort={args.reasoning}")
        if args.plan_only:
            print("[plan] --plan-only: exiting WITHOUT any API call.")
            return 0
        tag = getattr(client, "model", args.client).replace("/", "_")
        rows = run_streams_llm(client, args.banks_root, args.manual_dir, banks=banks,
                               d_grid=d_grid, streams=streams,
                               n_per_cell=args.n_per_cell,
                               max_completion_tokens=args.max_tokens,
                               reasoning_effort=args.reasoning)
        args.out.mkdir(parents=True, exist_ok=True)
        _write_rows(args.out / f"rows_classical_grid_{tag}.jsonl", rows)
        print(f"[E1 streams-rerun] {len(rows)} rows -> "
              f"{args.out / f'rows_classical_grid_{tag}.jsonl'}")
        return 0

    probes = run_probes(client, args.banks_root, args.manual_dir)
    rows = run_grid(client, cfg, extra_c4=extra_c4)
    args.out.mkdir(parents=True, exist_ok=True)
    tag = getattr(client, "model", args.client).replace("/", "_")
    suffix = "_smoke" if args.smoke else ""
    _write_rows(args.out / f"rows_{tag}{suffix}.jsonl", rows)
    (args.out / f"probes_{tag}{suffix}.json").write_text(json.dumps(probes, indent=1))
    (args.out / f"summary_{tag}{suffix}.md").write_text(summarise(rows, probes))
    print(summarise(rows, probes))
    print(f"\n[E1] {len(rows)} rows + {len(probes)} probes -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
