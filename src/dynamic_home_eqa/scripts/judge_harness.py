#!/usr/bin/env python3
"""
judge_harness.py — Phase 1.2: score the EVAL set under one or more judge
configurations and write a markdown report per config plus an accumulating
index, all under results/reports/judge_harness/.

Metrics per config: Spearman rank correlation vs human bands, per-band judge
score mean/std (band separation), a 4-band confusion at fixed thresholds,
the worst per-candidate disagreements, and where the dinner-laptop cases
landed. Uses the normal ResponseCache, so repeat runs are free.

Configs are named presets (see _PRESETS). --config baseline runs the current
judge variants (asis, strict, strict+thinking) for the P1b baseline.

Usage:
    python -m dynamic_home_eqa.scripts.judge_harness --config baseline
    python -m dynamic_home_eqa.scripts.judge_harness --config strict
"""
from __future__ import annotations

import argparse
import pathlib

from dynamic_home_eqa.generation.cache import ResponseCache
from dynamic_home_eqa.generation.llm_client import DEFAULT_CACHE_DIR, DEFAULT_MODEL
from dynamic_home_eqa.judge_eval import harness
from dynamic_home_eqa.judge_eval.exemplars import build_exemplar_block
from dynamic_home_eqa.judge_eval.harness import JudgeConfig
from dynamic_home_eqa.judge_eval.labels import load_split
from dynamic_home_eqa.paths import REPO_ROOT

_LABELED_CSV = REPO_ROOT / "results" / "judge_label_set" / "labeled_candidates.csv"
_SPLIT_MANIFEST = REPO_ROOT / "results" / "judge_label_set" / "split_manifest.json"
_GEN_DIR = REPO_ROOT / "generation_out_labelset"
_FOLDERS = [
    "102343992_family_with_kids",
    "102344022_family_with_kids",
    "102344049_family_with_kids",
]
_OUT_DIR = REPO_ROOT / "results" / "reports" / "judge_harness"

_PRESETS: dict[str, list[JudgeConfig]] = {
    "baseline": [
        JudgeConfig(name="asis", judge_style="asis"),
        JudgeConfig(name="strict", judge_style="strict"),
        JudgeConfig(name="strict_thinking", judge_style="strict", judge_thinking=True),
    ],
    # Phase 2.4 factorial: context and exemplars over the strict baseline,
    # plus self-consistency (k=3 thinking) on the fully-enriched config.
    "matrix": [
        JudgeConfig(name="strict", judge_style="strict"),
        JudgeConfig(name="strict_ctx", judge_style="strict", include_context=True),
        JudgeConfig(name="strict_fs", judge_style="strict", use_exemplars=True),
        JudgeConfig(name="strict_ctx_fs", judge_style="strict", include_context=True, use_exemplars=True),
        JudgeConfig(name="strict_ctx_fs_k3", judge_style="strict", include_context=True,
                    use_exemplars=True, judge_thinking=True, k=3),
    ],
    "asis": [JudgeConfig(name="asis", judge_style="asis")],
    "strict": [JudgeConfig(name="strict", judge_style="strict")],
    "strict_thinking": [JudgeConfig(name="strict_thinking", judge_style="strict", judge_thinking=True)],
    "strict_ctx_fs": [JudgeConfig(name="strict_ctx_fs", judge_style="strict",
                                  include_context=True, use_exemplars=True)],
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="baseline",
                    choices=sorted(_PRESETS) + ["moe"], help="preset config set to run")
    ap.add_argument("--gen-dir", default=str(_GEN_DIR))
    ap.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    # --config moe: score strict+thinking against an out-of-process model
    # (the vllm_q MoE endpoint), to compare vs Qwen3-32B strict_thinking.
    ap.add_argument("--endpoint", default="http://127.0.0.1:8123")
    ap.add_argument("--model-name", default="Qwen/Qwen3-Next-80B-A3B-Thinking-FP8")
    ap.add_argument("--model-tag", default="moe80b")
    args = ap.parse_args()

    if args.config == "moe":
        configs = [JudgeConfig(
            name="moe_strict_thinking", judge_style="strict", judge_thinking=True,
            endpoint=args.endpoint, model_name=args.model_name, model_tag=args.model_tag,
        )]
    else:
        configs = _PRESETS[args.config]

    eval_set, exemplar_set = load_split(_LABELED_CSV, _SPLIT_MANIFEST)
    print(f"EVAL set: {len(eval_set)} candidates (EXEMPLAR held out: {len(exemplar_set)})")
    exemplar_block = build_exemplar_block(exemplar_set)
    gen = harness.load_generation(pathlib.Path(args.gen_dir), _FOLDERS)
    cache = ResponseCache(args.cache_dir)

    for config in configs:
        print(f"\n=== scoring config: {config.name} (style={config.judge_style}, "
              f"ctx={config.include_context}, fs={config.use_exemplars}, "
              f"think={config.judge_thinking}, k={config.k}) ===")
        scores = harness.score_eval(eval_set, gen, config, cache, model=args.model,
                                    exemplar_block=exemplar_block)
        res = harness.evaluate(eval_set, scores)
        report = harness.write_report(config, res, _OUT_DIR)
        harness.update_index(config, res, _OUT_DIR)
        c = res["confusion"]
        rho = "—" if res["spearman"] is None else f"{res['spearman']:.3f}"
        print(f"  scored {res['n_scored']}/{res['n_eval']}  Spearman={rho}")
        print(f"  exact={c['exact_rate']:.0%}  over={c['over_rate']:.0%}  under={c['under_rate']:.0%}")
        print(f"  -> {report}")

    print(f"\nindex: {_OUT_DIR / 'INDEX.md'}")


if __name__ == "__main__":
    main()
