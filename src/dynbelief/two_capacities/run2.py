"""Two-Capacities Section 2 driver (mirrors run_aor; frozen env params)."""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor

from dynbelief.h2 import core
from dynbelief.answer_or_resense.run_aor import households, OUT as AOR_OUT
from dynbelief.answer_or_resense import env
from dynbelief.two_capacities.arms2 import LLMSelfConf, LLMVariant
from dynbelief.two_capacities.scaffold_arm import LLMScaffold, ScaffoldFusion
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

OUT = AOR_OUT          # rows co-located with the aor rows (same report tooling)
FROZEN = dict(Q=10, B=5, r_resense=0.4, wrong=0.0)


def run(bank_key, arm_name, tau, variant, endpoint, model, tag, alpha=6.07):
    client = OpenAIHTTPClient(endpoint, model)
    hhs = households(bank_key)

    def one(item):
        i, hh, cfg, bank_dir = item
        h = core.load_hh(bank_dir, hh)
        arm = (LLMSelfConf(client, tau) if arm_name == "llm_selfconf"
               else LLMScaffold(client) if arm_name == "llm_scaffold"
               else ScaffoldFusion(client, tau, alpha_star=alpha) if arm_name == "scaffold_fusion"
               else LLMVariant(client, variant))
        rows = env.run_episode(arm, i, hh, cfg, h, Q=FROZEN["Q"], B=FROZEN["B"],
                               r_resense=FROZEN["r_resense"], wrong=FROZEN["wrong"])
        for r_ in rows:
            r_.update({"arm": arm.name, "bank": bank_key, "tau": tau,
                       "alpha": alpha, "variant": variant,
                       **{k: v for k, v in FROZEN.items()}})
        import numpy as np
        print(f"[2cap:{arm.name}] {hh} done "
              f"(rr {np.mean([x['action']=='resense' for x in rows]):.2f})", flush=True)
        return rows

    with ThreadPoolExecutor(max_workers=12) as ex:
        all_rows = [r for rs in ex.map(one, hhs) for r in rs]
    name = arm_name if arm_name in ("llm_selfconf", "llm_scaffold", "scaffold_fusion") else f"llm_{variant}"
    f = OUT / f"rows_{name}_{bank_key}_{tag}.jsonl"
    f.write_text("".join(json.dumps(r_) + "\n" for r_ in all_rows))
    print(f"[2cap] wrote {len(all_rows)} rows -> {f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", choices=["dev", "conf", "typ"], required=True)
    ap.add_argument("--arm", choices=["llm_selfconf", "variant", "llm_scaffold", "scaffold_fusion"], required=True)
    ap.add_argument("--tau", type=float, default=0.8)
    ap.add_argument("--variant", default="v1_recency",
                    choices=["v1_recency", "v1_pinned", "v1_explicit"])
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--alpha", type=float, default=6.07,
                    help="alpha* = observations the prior is worth; per-model, from "
                         "that model's own dev track record")
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    run(args.bank, args.arm, args.tau, args.variant, args.endpoint, args.model,
        args.tag, alpha=args.alpha)


if __name__ == "__main__":
    main()
