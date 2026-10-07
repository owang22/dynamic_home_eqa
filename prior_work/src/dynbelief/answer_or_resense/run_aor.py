"""Answer-or-Resense driver.

  # offline arms (no LLM): classical + oracle
  python -m dynbelief.answer_or_resense.run_aor --bank conf --arm classical --tau 0.45 ...
  # LLM arms (server needed): llm / hybrid / llm_thresh
  python -m dynbelief.answer_or_resense.run_aor --bank conf --arm llm --prompt v1 ...

--bank dev  = v22dev (4 households, sweeps only)
--bank conf = v22 + v22b (24 households, expanded pool; staggered offsets by index)

Rows -> reports/answer_or_resense/rows_<arm>_<bank>_<cfgtag>.jsonl
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor

from dynbelief.h2 import core
import dynbelief.reflect.run as R
from dynbelief.answer_or_resense import env
from dynbelief.answer_or_resense import arms as A
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

OUT = core.OUT.parent / "answer_or_resense"


def households(bank_key):
    """(hh_idx, hh, cfg, bank_dir) — conf = v22 + v22b concatenated so offsets
    stagger across the full 24-household pool."""
    out = []
    keys = (["v22", "v22b"] if bank_key == "conf"
            else ["typ"] if bank_key == "typ" else ["v22dev"])
    i = 0
    for bk in keys:
        bank_dir, cfgmap, _, _ = R.bank_of(bk)
        for hh, cfg in cfgmap.items():
            out.append((i, hh, cfg, bank_dir)); i += 1
    return out


def make_llm_client(endpoint, model):
    return OpenAIHTTPClient(endpoint, model)


def build_arm(name, tau, client, prompt):
    if name == "classical":
        return A.ClassicalThreshold(tau)
    if name == "oracle":
        return A.Oracle()
    if name == "llm":
        return A.LLMArm(client, prompt)
    if name == "hybrid":
        return A.HybridArm(client, tau, prompt_key=prompt)
    if name == "llm_thresh":
        return A.LLMThreshold(client, tau, prompt_key=prompt)
    raise ValueError(name)


def run(bank_key, arm_name, tau, Q, B, r_resense, wrong, endpoint, model, prompt,
        warm=False, tag=None):
    OUT.mkdir(parents=True, exist_ok=True)
    client = (make_llm_client(endpoint, model)
              if arm_name in ("llm", "hybrid", "llm_thresh") else None)
    hhs = households(bank_key)

    def one(item):
        i, hh, cfg, bank_dir = item
        h = core.load_hh(bank_dir, hh)
        arm = build_arm(arm_name, tau, client, prompt)   # fresh arm per household
        rows = env.run_episode(arm, i, hh, cfg, h, Q=Q, B=B,
                               r_resense=r_resense, wrong=wrong, warm=warm)
        for r_ in rows:
            r_.update({"arm": arm_name, "bank": bank_key, "tau": tau, "Q": Q,
                       "B": B, "r": r_resense, "wrong": wrong, "prompt": prompt})
        print(f"[aor:{arm_name}] {hh} done "
              f"(resense rate {sum(x['action']=='resense' for x in rows)/len(rows):.2f})",
              flush=True)
        return rows

    workers = len(hhs) if client else 1     # LLM arms parallel over households
    if client:
        with ThreadPoolExecutor(max_workers=min(12, workers)) as ex:
            all_rows = [r for rs in ex.map(one, hhs) for r in rs]
    else:
        all_rows = [r for item in hhs for r in one(item)]

    tag = tag or f"Q{Q}_B{B}_r{r_resense}_w{wrong}" + (f"_t{tau}" if tau else "") \
        + ("_warm" if warm else "")
    f = OUT / f"rows_{arm_name}_{bank_key}_{tag}.jsonl"
    f.write_text("".join(json.dumps(r_) + "\n" for r_ in all_rows))
    tot = sum(r_["reward"] for r_ in all_rows)
    print(f"[aor:{arm_name}] wrote {len(all_rows)} rows -> {f} | total reward {tot:.0f}")
    return all_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", choices=["dev", "conf", "typ"], required=True)
    ap.add_argument("--arm", choices=["classical", "oracle", "llm", "hybrid",
                                      "llm_thresh"], required=True)
    ap.add_argument("--tau", type=float, default=0.45)
    ap.add_argument("--Q", type=int, default=6)
    ap.add_argument("--B", type=int, default=2)
    ap.add_argument("--r", type=float, default=0.4)
    ap.add_argument("--wrong", type=float, default=0.0)
    ap.add_argument("--warm", action="store_true")
    ap.add_argument("--prompt", default="v1")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    run(args.bank, args.arm, args.tau, args.Q, args.B, args.r, args.wrong,
        args.endpoint, args.model, args.prompt, warm=args.warm, tag=args.tag)


if __name__ == "__main__":
    main()
