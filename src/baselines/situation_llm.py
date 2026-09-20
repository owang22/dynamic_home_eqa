"""LLM arms under the human inspector's protocol, on one situation_sim run.

    cd src && python3 -m baselines.situation_llm --run ../data/situation_sim/runs/hh_s11 \
        --arms longleaf notebook_llmDecide [--days 1] [--dry-run]

Steps (each idempotent; LLM calls are cached by request hash):
1. build the protocol bank (:func:`baselines.situation_eval.build_bank`) and
   expose it under the fleet's bank naming in ``banks/situation/`` so the
   existing elicit / run_tour_start drivers find it;
2. ``longleaf``: elicit the treeLongLeaf library from the walkthrough
   (``elicit --longleaf``), then run ``active:longleaf:longleaf_named:f0``;
3. ``notebook_llmDecide``: run ``active:notebook_llmDecide:named:f0``;
both through ``run_tour_start --room-look`` so a Sense is a room look priced
by the bank's protocol block, and the prompts describe that protocol
(:mod:`baselines.llm_hypotheses.protocol_text`).

Outputs under ``results/situation_sim/llm/<hh>/`` (bank, prompt review) and
the study folder ``run_tour_start`` writes (``--out-dir``, default
``results/situation_sim/llm/<hh>/study``); ``--dry-run`` only builds the bank
and prints the commands.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys

from baselines.household_analysis import MODEL_SLUG, REPO_ROOT
from baselines.situation_eval import build_bank

ENDPOINT = os.environ.get("GENERATION_ENDPOINT", "http://127.0.0.1:8300")
MODEL = os.environ.get("GENERATION_MODEL", "Qwen/Qwen3.6-35B-A3B")
ARMS = {"longleaf": "active:longleaf:longleaf_named:f0",
        "notebook_llmDecide": "active:notebook_llmDecide:named:f0",
        "notebook_voi": "active:notebook_voi:named:f0",
        "log_reader": "active:log_reader:named:f0"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=pathlib.Path, required=True)
    ap.add_argument("--arms", nargs="+", default=["longleaf", "notebook_llmDecide"], choices=sorted(ARMS))
    ap.add_argument("--days", type=int, default=None, help="only the first N question days (smoke test)")
    ap.add_argument("--endpoint", default=ENDPOINT)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out-dir", type=pathlib.Path, default=None)
    a = ap.parse_args(argv)
    hh = a.run.name
    out = a.out_dir or (REPO_ROOT / "results" / "situation_sim" / "llm" / hh)
    out.mkdir(parents=True, exist_ok=True)
    bank, _ = build_bank(a.run, out / "bank.jsonl")
    bank_dir = REPO_ROOT / "banks" / "situation"
    bank_dir.mkdir(parents=True, exist_ok=True)
    link = bank_dir / f"households__generated__{MODEL_SLUG}__{hh}_bank.jsonl"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(bank.resolve())
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"))
    cmds = []
    if "longleaf" in a.arms:
        cmds.append([sys.executable, "-m", "baselines.llm_hypotheses.elicit", "--longleaf",
                     "--households", hh, "--bank-dir", str(bank_dir), "--conditions", "named",
                     "--hyp-subdir", "situation", "--endpoint", a.endpoint, "--model", a.model])
    for arm in a.arms:
        cmd = [sys.executable, "-m", "baselines.llm_hypotheses.run_tour_start", "--household", hh,
               "--arm", ARMS[arm], "--bank-dir", str(bank_dir), "--room-look",
               "--endpoint", a.endpoint, "--model", a.model, "--out-dir", str(out / "study")]
        if arm == "longleaf":
            cmd += ["--hyp-subdir", "situation"]
        if a.days:
            cmd += ["--days", str(a.days)]
        cmds.append(cmd)
    for c in cmds:
        print("$", " ".join(c), flush=True)
        if not a.dry_run:
            r = subprocess.run(c, env=env, cwd=str(REPO_ROOT / "src"))
            if r.returncode:
                print(f"!! exit {r.returncode}", file=sys.stderr)
                return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
