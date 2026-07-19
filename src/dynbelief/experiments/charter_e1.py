"""E1 -- adaptation curve in atypical households (tests C1; fastest signal).

Forecasting only: no budget, no decisions. For each (bank, history-days D,
charter-text on/off), the model is shown a memory of observations over days
[0, D) (held-out objects stripped, per A3) and predicts the receptacle of each
day-D query object at its query time, with a verbalized probability.

Condition grid (spec E1):
  banks:         {typ_v1, atyp_v1}   (+ atyp_shift_v1 at D=7 for the C4 control)
  history days:  {0, 1, 3, 7, 14}
  charter text:  {history-only, history+charter-prose}

Primary endpoints (computed in summarise):
  - accuracy vs history-days per bank (C1 = atyp rises steeply, typ near-flat)
  - same restricted to moved-at-query episodes
  - ECE per cell (10 bins on p_correct)
  - held-out-only slice (C4 preview); atyp_shift at D=7 (attribution control)

One fixed prompt template per experiment, hash-logged. Guided-JSON output
{object_id, predicted_receptacle, p_correct}. Model: local Qwen (real endpoint)
or MockForecastClient (deterministic last-seen baseline) for offline dev.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass, field

from dynbelief import MIN_PER_DAY
from dynbelief.charters.schema import load_charter, Charter, default_class

HISTORY_DAYS = [0, 1, 3, 7, 14]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _when(t: int) -> str:
    day = t // MIN_PER_DAY
    mins = t % MIN_PER_DAY
    return f"{DAYS[day % 7]} {mins // 60:02d}:{mins % 60:02d}"


# ── memory table (observations up to day D, held-out stripped) ───────────────

def observation_memory(events: list[dict], placements: dict, heldout: set[str],
                       horizon_min: int) -> dict[str, tuple[str, int]]:
    """Per observed object, the most recent (receptacle, t_observed) at t <
    horizon_min. Day-0 homes seed the memory (t=0). Held-out objects excluded."""
    mem: dict[str, tuple[str, int]] = {}
    for o, p in placements.items():
        if o not in heldout:
            mem[o] = (p.home, 0)
    for e in sorted(events, key=lambda e: e["t_min"]):
        if e["t_min"] >= horizon_min:
            break
        if e["label"] in heldout:
            continue
        mem[e["label"]] = (e["parent_label"], e["t_min"])
    return mem


def render_memory(mem: dict[str, tuple[str, int]]) -> str:
    if not mem:
        return "(no prior observations)"
    rows = []
    for o in sorted(mem):
        recep, t = mem[o]
        rows.append(f"  {o}: last seen at {recep} ({_when(t)})")
    return "\n".join(rows)


# ── charter prose (deterministic render; NOT model-authored) ─────────────────

def charter_prose(ch: Charter) -> str:
    lines = [f"Household: {ch.household}.", "Residents and weekly routine:"]
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
    "memory of past observations of that home. Objects move as residents go about "
    "their routines (meals, work/school, tidying, evening wind-down, weekend "
    "rhythms). Reason about which activities plausibly happened between when the "
    "object was last seen and the query time, and how much time has elapsed. "
    "Answer with a single receptacle from the candidate list (or 'elsewhere' if it "
    "has left the tracked receptacles), and your probability that it is correct."
)


def build_prompt(mem_text: str, candidates: list[str], obj: str, t_query: int,
                 charter_text: str | None) -> tuple[str, str]:
    parts = [f"Current time: {_when(t_query)}.", "", "Memory of past observations:",
             mem_text, ""]
    if charter_text:
        parts += ["What is known about this household's routine:", charter_text, ""]
    parts += [f"Candidate receptacles: {', '.join(candidates)}, elsewhere.", "",
              f"Where is `{obj}` right now? Give the single most likely receptacle "
              f"and your probability it is correct."]
    return _SYSTEM, "\n".join(parts)


SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "predicted_receptacle": {"type": "string"},
        "p_correct": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["predicted_receptacle", "p_correct"],
    "additionalProperties": False,
}


def prompt_hash() -> str:
    return hashlib.sha256((_SYSTEM + json.dumps(SCHEMA)).encode()).hexdigest()[:12]


# ── clients ──────────────────────────────────────────────────────────────────

class MockForecastClient:
    """Deterministic offline dev client that reads the last-seen receptacle for
    the queried object straight out of the prompt's memory table (no external
    state, no re-derivation). Predicts that receptacle with confidence decaying
    in elapsed time; 'elsewhere' if the object is absent from memory. Lets the
    full harness + scoring + ECE run with no GPU. It is a genuine
    last-seen-from-memory baseline, NOT a stand-in for Qwen (it ignores the
    charter prose, so its charter_text on/off cells are identical by design)."""
    model = "mock_lastseen"

    def generate(self, system, user, schema, seed=None, temperature=0.0):
        obj = user.split("Where is `", 1)[1].split("`", 1)[0]
        # find "  <obj>: last seen at <recep> (<when>)" in the memory block
        recep = None
        for line in user.splitlines():
            s = line.strip()
            if s.startswith(f"{obj}: last seen at "):
                recep = s.split("last seen at ", 1)[1].split(" (", 1)[0].strip()
                break
        if recep is None:
            return json.dumps({"predicted_receptacle": "elsewhere", "p_correct": 0.2})
        return json.dumps({"predicted_receptacle": recep, "p_correct": 0.7})


# ── run one household-condition, one bank ────────────────────────────────────

@dataclass
class E1Config:
    banks_root: pathlib.Path
    manual_dir: pathlib.Path
    charter_text_variants: tuple[bool, ...] = (False, True)
    history_days: tuple[int, ...] = tuple(HISTORY_DAYS)
    seed: int = 7


def _load_household(bank_dir: pathlib.Path, hh_name: str):
    hd = bank_dir / hh_name
    reg = json.loads((hd / "registry.json").read_text())
    events = [json.loads(l) for l in (hd / "events.jsonl").open()]
    recep_label = {v: k for k, v in reg["receptacles"].items()}
    obj_label = {v: k for k, v in reg["objects"].items()}
    # events -> label form
    ev = [{"t_min": e["t_min"], "label": obj_label[e["object_id"]],
           "parent_label": recep_label[e["parent_id"]]} for e in events]
    queries = [json.loads(l) for l in (hd / "queries.jsonl").open()]
    gt = {(r["object"], r["t_query"]): r
          for r in (json.loads(l) for l in (hd / "ground_truth.jsonl").open())}
    targets = json.loads((hd / "targets.json").read_text())
    return reg, ev, queries, gt, targets, recep_label


def run_household(client, bank: str, bank_dir: pathlib.Path, hh_name: str,
                  manual_dir: pathlib.Path, D: int, use_charter: bool,
                  seed: int) -> list[dict]:
    reg, ev, queries, gt, targets, recep_label = _load_household(bank_dir, hh_name)
    base = reg["charter"]["household"].split("__")[0]
    ch = load_charter(manual_dir / f"{base}.yaml")
    if reg["charter"].get("transformation"):
        from dynbelief.charters import transforms
        tf = reg["charter"]["transformation"]
        ch = transforms.apply_transform(ch, tf["type"], **tf["params"])
    heldout = set(targets["held_out"])
    horizon = D * MIN_PER_DAY
    mem = observation_memory(ev, ch.placements, heldout, horizon)
    mem_text = render_memory(mem)
    candidates = sorted({p.home for p in ch.placements.values()}
                        | {r for r in recep_label.values() if r != "elsewhere"})
    prose = charter_prose(ch) if use_charter else None

    # queries evaluated on day D (predict the horizon day's queries)
    day_queries = [q for q in queries if q["day"] == D] if D < reg["n_days"] else []
    rows = []
    for q in day_queries:
        obj, tq = q["object"], q["t_query"]
        system, user = build_prompt(mem_text, candidates, obj, tq, prose)
        raw = client.generate(system, user, SCHEMA, seed=seed, temperature=0.2)
        try:
            parsed = json.loads(raw)
            pred = str(parsed["predicted_receptacle"])
            pc = float(parsed["p_correct"])
        except Exception:
            pred, pc = "elsewhere", 0.0
        g = gt.get((obj, tq), {})
        true_recep = g.get("true_receptacle")
        last_seen = mem.get(obj)
        moved = (last_seen is not None and last_seen[0] != true_recep)
        rows.append({
            "bank": bank, "household": hh_name, "history_days": D,
            "charter_text": use_charter, "object": obj, "class": default_class(obj),
            "tercile": g.get("tercile"), "held_out": obj in heldout,
            "t_query": tq, "true_receptacle": true_recep,
            "predicted": pred, "p_correct": pc,
            "correct": int(pred == true_recep),
            "moved_since_history": int(moved),
            "model": getattr(client, "model", "?"), "prompt_hash": prompt_hash(),
        })
    return rows


def run_grid(client, cfg: E1Config, banks=("typ_v1", "atyp_v1"),
             extra_c4=True) -> list[dict]:
    rows: list[dict] = []
    for bank in banks:
        bank_dir = cfg.banks_root / bank
        if not bank_dir.exists():
            continue
        hh_names = [p.name for p in sorted(bank_dir.iterdir())
                    if p.is_dir() and (p / "registry.json").exists()]
        for D in cfg.history_days:
            for use_ct in cfg.charter_text_variants:
                for hh in hh_names:
                    rows += run_household(client, bank, bank_dir, hh, cfg.manual_dir,
                                          D, use_ct, cfg.seed)
    # C4 control: atyp_shift_v1 at D=7 only
    if extra_c4 and (cfg.banks_root / "atyp_shift_v1").exists():
        bank_dir = cfg.banks_root / "atyp_shift_v1"
        hh_names = [p.name for p in sorted(bank_dir.iterdir())
                    if p.is_dir() and (p / "registry.json").exists()]
        for use_ct in cfg.charter_text_variants:
            for hh in hh_names:
                rows += run_household(client, "atyp_shift_v1", bank_dir, hh,
                                      cfg.manual_dir, 7, use_ct, cfg.seed)
    return rows


# ── endpoints ────────────────────────────────────────────────────────────────

def _acc(rows) -> float:
    return round(sum(r["correct"] for r in rows) / len(rows), 4) if rows else float("nan")


def ece(rows, n_bins: int = 10) -> float:
    if not rows:
        return float("nan")
    bins = [[] for _ in range(n_bins)]
    for r in rows:
        b = min(n_bins - 1, int(r["p_correct"] * n_bins))
        bins[b].append(r)
    tot, n = 0.0, len(rows)
    for b in bins:
        if not b:
            continue
        conf = sum(r["p_correct"] for r in b) / len(b)
        acc = sum(r["correct"] for r in b) / len(b)
        tot += len(b) / n * abs(conf - acc)
    return round(tot, 4)


def summarise(rows: list[dict]) -> str:
    banks = sorted({r["bank"] for r in rows})
    out = ["# E1 -- adaptation curve (forecasting)", "",
           f"rows: {len(rows)}  |  model: {sorted({r['model'] for r in rows})}  |  "
           f"prompt_hash: {sorted({r['prompt_hash'] for r in rows})[0]}", ""]
    for ct in (False, True):
        out.append(f"## charter_text = {ct}")
        out.append("| bank | " + " | ".join(f"D={d}" for d in HISTORY_DAYS)
                   + " | (moved-only D=7) | ECE(D=7) |")
        out.append("|---|" + "---|" * (len(HISTORY_DAYS) + 2))
        for bank in banks:
            if bank == "atyp_shift_v1":
                continue
            cells = []
            for d in HISTORY_DAYS:
                sub = [r for r in rows if r["bank"] == bank and r["history_days"] == d
                       and r["charter_text"] == ct]
                cells.append(f"{_acc(sub):.3f}" if sub else "-")
            moved = [r for r in rows if r["bank"] == bank and r["history_days"] == 7
                     and r["charter_text"] == ct and r["moved_since_history"]]
            d7 = [r for r in rows if r["bank"] == bank and r["history_days"] == 7
                  and r["charter_text"] == ct]
            out.append(f"| {bank} | " + " | ".join(cells)
                       + f" | {_acc(moved):.3f} | {ece(d7):.3f} |")
        out.append("")
    # C4 preview
    out.append("## C4 controls (D=7)")
    out.append("| slice | atyp_v1 | atyp_shift_v1 |")
    out.append("|---|---|---|")
    for label, held in [("all", None), ("held-out only", True), ("observed only", False)]:
        def cell(bank):
            sub = [r for r in rows if r["bank"] == bank and r["history_days"] == 7
                   and (held is None or r["held_out"] == held)]
            return f"{_acc(sub):.3f}" if sub else "-"
        out.append(f"| {label} | {cell('atyp_v1')} | {cell('atyp_shift_v1')} |")
    out.append("")
    out.append("Interpretation guardrail: numbers only. C1 = atyp accuracy rises with D "
               "while typ stays flat; C4 = atyp gains vanish under atyp_shift (per-object "
               "phase destroys shared routine). With the MOCK client these are a last-seen "
               "baseline, not an LLM result.")
    return "\n".join(out)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    import argparse
    from dynamic_home_eqa.paths import REPO_ROOT, REPORTS_DIR
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--client", choices=["mock", "qwen"], default="mock")
    ap.add_argument("--banks-root", type=pathlib.Path, default=REPO_ROOT / "banks")
    ap.add_argument("--manual-dir", type=pathlib.Path, default=REPO_ROOT / "charters" / "manual")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8300")
    ap.add_argument("--out", type=pathlib.Path, default=REPORTS_DIR.parent / "charter_e1")
    args = ap.parse_args(argv)

    cfg = E1Config(banks_root=args.banks_root, manual_dir=args.manual_dir)
    if args.client == "qwen":
        from dynbelief.llm_agent.clients import local_qwen
        client = local_qwen(args.endpoint)
    else:
        client = MockForecastClient()
    rows = run_grid(client, cfg)
    args.out.mkdir(parents=True, exist_ok=True)
    _write_rows(args.out / "rows.jsonl", rows)
    (args.out / "summary.md").write_text(summarise(rows))
    print(summarise(rows))
    print(f"\n[E1] {len(rows)} rows -> {args.out}")
    return 0


def _write_rows(path: pathlib.Path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
