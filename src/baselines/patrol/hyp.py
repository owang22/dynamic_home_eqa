"""The hypothesis-based LLM arms (treeLongLeaf, notebook_llmDecide) on the
patrol banks, through the existing drivers.

    python3 -m baselines.patrol.hyp --bank ../results/overnight_2026-09-20/banks/hh_s0_p4.jsonl \
        --out ../results/overnight_2026-09-20/hyp --arms longleaf notebook --told told not_told

Steps per bank (each idempotent; LLM calls are cached by request hash):
1. expose the bank under the fleet's naming in ``banks/patrol/``;
2. ``longleaf``: elicit the library from the walkthrough (``elicit --longleaf``,
   once per bank, shared by the told and not-told arms), then run
   ``active:longleaf:longleaf_named:f0 --free-look [--told]``;
3. ``notebook``: run ``active:notebook_llmDecide_free:named:f0 --free-look [--told]``;
4. convert each arm's ``per_question.jsonl.gz`` into the patrol run-log rows
   (``<out>/logs/<hh>_p<h>_<arm>_<told>.jsonl``) so ``patrol.summary``,
   ``patrol.figures`` and the explorer read them like any other agent.

The free look is the patrol protocol's one room look per question
(:mod:`baselines.llm_hypotheses.protocol_text`, ``free_look``); belief
arms look at the VoI-argmax room (``--look-mode top`` for the argmax room).
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import pathlib
import subprocess
import sys
from typing import List

from baselines.household_analysis import MODEL_SLUG, REPO_ROOT

ENDPOINT = os.environ.get("PATROL_LLM_ENDPOINT", "http://127.0.0.1:8300")
MODEL = os.environ.get("PATROL_LLM_MODEL", "Qwen/Qwen3.8-27B")
PASSIVE_ARMS = {"longleaf": "passive:longleaf:longleaf_named",
                "longleaf_fixed": "passive:longleaf_fixed:longleaf_named"}
"""The confidence study: no looks at all; the mixture is weighted by the
patrol stream alone. ``longleaf`` re-asks the elicitor on its triggers,
``longleaf_fixed`` keeps the elicited library for the whole week."""
ARMS = {"longleaf": "active:longleaf:longleaf_named:f0",
        "notebook": "active:notebook_llmDecide_free:named:f0",
        "notebook_voi": "active:notebook_voi_free:named:f0"}
LABEL = {"longleaf": "llm_longleaf", "notebook": "llm_notebook_llmDecide", "notebook_voi": "llm_notebook_voi",
         "longleaf_fixed": "llm_longleaf_fixed"}


def convert_passive(arm_dir: pathlib.Path, bank: pathlib.Path, header: dict, arm: str, told: bool, out: pathlib.Path) -> int:
    """per_question.jsonl.gz (passive protocol) -> patrol run-log rows: the
    answer is the argmax of the mixture over in-house spots (ON_PERSON /
    OUT_OF_HOUSE mass dropped, the rest renormalized), the confidence is
    that spot's renormalized probability. Truth comes from the bank."""
    from baselines.types import ON_PERSON, OUT_OF_HOUSE
    from baselines.patrol.run import spots_only
    from baselines.patrol.bank import _Truth
    rows = [json.loads(l) for l in bank.read_text().splitlines() if l.strip()]
    truth = _Truth([r for r in rows if r["kind"] == "truth"])
    qs = {r["question_id"]: r for r in rows if r["kind"] == "question"}
    agent = f"{LABEL[arm]}/{'told' if told else 'not_told'}/look_off"
    n = 0
    with gzip.open(arm_dir / "per_question.jsonl.gz", "rt") as fh, open(out, "w") as o:
        for line in fh:
            r = json.loads(line)
            q = qs[r["question_id"]]
            dist, dropped = spots_only({k: float(v) for k, v in r.get("dist", {}).items()})
            answer = max(dist, key=lambda k: (dist[k], k)) if dist else r["argmax"]
            # agreement: the share of library weight whose own answer is this spot
            weights = r.get("weights") or {}
            agree = 0.0
            for name, pd in (r.get("particles") or {}).items():
                pdist, _ = spots_only({k: float(v) for k, v in pd.items()})
                if pdist and max(pdist, key=lambda k: (pdist[k], k)) == answer:
                    agree += float(weights.get(name, 0.0))
            tru = truth.at(q["object_id"], q["t_query"])
            row = {"household": header["household_id"], "patrol_hours": header["patrol_hours"],
                   "patrol_label": header.get("patrol_label"), "look": "off",
                   "agent": agent, "belief": agent, "day_index": q["day_index"], "question_id": q["question_id"],
                   "object_id": q["object_id"], "object_class": q["object_class"], "t_query": q["t_query"],
                   "answer": answer, "top_prob": round(dist.get(answer, 0.0), 4), "p_outside": round(dropped, 4),
                   "agreement": round(agree, 4),
                   "raw_answer": r["argmax"], "truth": tru, "correct": answer == tru,
                   "ess": r.get("ess"), "n_particles": len(r.get("particles") or []),
                   "fallback": False, "abstain_direct": False, "told": told}
            o.write(json.dumps(row, sort_keys=True) + "\n")
            n += 1
    return n


def convert(arm_dir: pathlib.Path, header: dict, arm: str, told: bool, out: pathlib.Path) -> int:
    """per_question.jsonl.gz -> patrol run-log rows."""
    rooms = header["receptacle_rooms"]
    agent = f"{LABEL[arm]}/{'told' if told else 'not_told'}/look_on"
    n = 0
    with gzip.open(arm_dir / "per_question.jsonl.gz", "rt") as fh, open(out, "w") as o:
        for line in fh:
            r = json.loads(line)
            looks = [a for a in r.get("actions", []) if a.get("type") == "look_room"]
            look_room = looks[0]["room"] if looks else None
            found = any(r["object_id"] in objs for a in looks for objs in a.get("contents", {}).values())
            dist = r.get("dist", {})
            row = {"household": header["household_id"], "patrol_hours": header["patrol_hours"], "look": "llm",
                   "agent": agent, "belief": agent, "day_index": r["day_index"], "question_id": r["question_id"],
                   "object_id": r["object_id"], "object_class": header["object_classes"].get(r["object_id"], ""),
                   "t_query": r["t_query"], "answer": r["argmax"], "top_prob": round(float(dist.get(r["argmax"], 0.0)), 4),
                   "truth": r["truth"], "correct": bool(r["correct"]), "look_room": look_room, "found_in_look": found,
                   "answer_before_look": r["argmax"], "correct_before_look": bool(r["correct"]),
                   "fallback": False, "abstain_direct": False, "told": told}
            o.write(json.dumps(row, sort_keys=True) + "\n")
            n += 1
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=pathlib.Path, nargs="+", required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--arms", nargs="+", default=["longleaf", "notebook"], choices=sorted(set(ARMS) | set(PASSIVE_ARMS)))
    ap.add_argument("--passive", action="store_true", help="no looks: the passive patrol stream (confidence study)")
    ap.add_argument("--told", nargs="+", default=["told", "not_told"], choices=["told", "not_told"])
    ap.add_argument("--look-mode", default="voi", choices=("voi", "top"))
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--endpoint", default=ENDPOINT)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "logs").mkdir(exist_ok=True)
    bank_dir = REPO_ROOT / "banks" / "patrol"
    bank_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"))
    rc = 0
    for bank in a.bank:
        header = json.loads(bank.read_text().splitlines()[0])
        hh, ph = header["household_id"], int(header["patrol_hours"])
        # the fleet naming the drivers expect; one "household" per (hh, density)
        hh_name = f"{hh}_p{ph}"
        link = bank_dir / f"households__generated__{MODEL_SLUG}__{hh_name}_bank.jsonl"
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(bank.resolve())
        hyp_subdir = "patrol"
        cmds: List[List[str]] = []
        if any(arm.startswith("longleaf") for arm in a.arms):
            cmds.append([sys.executable, "-m", "baselines.llm_hypotheses.elicit", "--longleaf",
                         "--households", hh_name, "--bank-dir", str(bank_dir), "--conditions", "named",
                         "--hyp-subdir", hyp_subdir, "--endpoint", a.endpoint, "--model", a.model])
        study = a.out / "study"
        for arm in a.arms:
            for told in a.told:
                if a.passive:
                    # --room-look only skips the driver's first_question_day check (the passive path takes no looks)
                    cmd = [sys.executable, "-m", "baselines.llm_hypotheses.run_tour_start", "--household", hh_name,
                           "--arm", PASSIVE_ARMS[arm], "--bank-dir", str(bank_dir), "--room-look",
                           "--endpoint", a.endpoint, "--model", a.model, "--out-dir", str(study)]
                else:
                    cmd = [sys.executable, "-m", "baselines.llm_hypotheses.run_tour_start", "--household", hh_name,
                           "--arm", ARMS[arm], "--bank-dir", str(bank_dir), "--free-look", "--look-mode", a.look_mode,
                           "--endpoint", a.endpoint, "--model", a.model, "--out-dir", str(study)]
                if arm.startswith("longleaf"):
                    cmd += ["--hyp-subdir", hyp_subdir]
                if told == "told":
                    cmd.append("--told")
                if a.days:
                    cmd += ["--days", str(a.days)]
                cmds.append(cmd)
        for c in cmds:
            print("$", " ".join(c), flush=True)
            if a.dry_run:
                continue
            r = subprocess.run(c, env=env, cwd=str(REPO_ROOT / "src"))
            if r.returncode:
                print(f"!! exit {r.returncode}: {' '.join(c)}", file=sys.stderr, flush=True)
                rc = r.returncode
        if a.dry_run:
            continue
        for arm in a.arms:
            for told in a.told:
                spec = PASSIVE_ARMS[arm] if a.passive else ARMS[arm]
                dirname = spec.replace(":", "__") + f"__{'told' if told == 'told' else 'nottold'}"
                arm_dir = study / f"{hh_name}__bank0" / "arms" / ("passive" if a.passive else "active") / dirname
                if not (arm_dir / "per_question.jsonl.gz").exists():
                    print(f"!! no output for {arm_dir}", file=sys.stderr)
                    continue
                out = a.out / "logs" / f"{hh}_{header.get('patrol_label', 'p' + str(ph))}_{arm}_{told}.jsonl"
                n = convert_passive(arm_dir, bank, header, arm, told == "told", out) if a.passive \
                    else convert(arm_dir, header, arm, told == "told", out)
                print(f"converted {n} rows -> {out}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
