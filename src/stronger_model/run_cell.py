"""Run one overnight_wave cell with a stronger model in place of plain Qwen3.8.

Everything except the client is the study's own code (`self_improve.overnight_wave.run_one_arm`):
same household banks, same questions, same prompts, same scoring. Only `complete()` changes.

    PYTHONPATH=src python3 -m stronger_model.run_cell --backend qwen-think --thinking-budget 1000 \
        --arm "log only, no notes" --household hh_s2_t03
    PYTHONPATH=src python3 -m stronger_model.run_cell --backend claude --claude-model sonnet \
        --arm "the log and notes about the routine" --household hh_s2_t03

Cells land at results/stronger_model/<tag>/cells/<arm>/<household>/ (gitignored, like every wave),
and each backend has its own cache under llm_prior_cache/stronger_model/<tag>/ - never the shared
Qwen cache (see clients.py for why).
"""
from __future__ import annotations

import argparse
import json
import pathlib

from self_improve.frozen_household import FrozenHousehold
from self_improve.overnight_wave import ARMS, cell_dir, run_one_arm
from stronger_model.clients import ClaudeClient, QwenThinkingClient

BANKS = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks")


def tag_for(args) -> str:
    if args.backend == "qwen-think":
        tag = f"qwen38_think{args.thinking_budget}"
    else:
        tag = f"claude_{args.claude_model}" + (f"_{args.effort}" if args.effort else "")
    # a repeat run needs its own cache and output, or it replays the first run's answers
    return tag + (f"_{args.repeat}" if args.repeat else "")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--backend", required=True, choices=["qwen-think", "claude"])
    p.add_argument("--thinking-budget", type=int, default=1000)
    p.add_argument("--claude-model", default="sonnet")
    p.add_argument("--effort", default=None)
    p.add_argument("--arm", required=True, choices=list(ARMS))
    p.add_argument("--household", required=True)
    p.add_argument("--banks", type=pathlib.Path, default=BANKS)
    p.add_argument("--last-day", type=int, default=31)
    p.add_argument("--questions-per-day", type=int, default=8)
    p.add_argument("--budget", type=int, default=3)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--repeat", default=None, help="e.g. rep2: separate cache and output for a rerun")
    args = p.parse_args(argv)

    tag = tag_for(args)
    cache = pathlib.Path("llm_prior_cache/stronger_model") / tag
    if args.backend == "qwen-think":
        client = QwenThinkingClient(cache, thinking_budget=args.thinking_budget)
    else:
        client = ClaudeClient(cache, model=args.claude_model, effort=args.effort)
    household = FrozenHousehold(args.banks / f"{args.household}.jsonl")
    out = cell_dir(pathlib.Path("results/stronger_model") / tag, args.arm, household.name)
    result = run_one_arm(household, args.arm, client, out, args.last_day,
                         args.questions_per_day, args.budget, args.seed)
    (out / "backend.json").write_text(json.dumps({"backend": args.backend, "tag": tag, "cache": str(cache),
                                                  "thinking_budget": args.thinking_budget if args.backend == "qwen-think" else None,
                                                  "claude_model": args.claude_model if args.backend == "claude" else None,
                                                  "effort": args.effort, "stats": client.stats}, indent=1))
    print(json.dumps(result["summary"], indent=1))
    print(json.dumps(client.stats, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
