#!/usr/bin/env python3
"""
regenerate_comparison_set.py — Phase 2.4b: regenerate the 3-scene comparison
set end to end under the winning enriched configuration:

  proposer: per-occupant Tier-3 ownership, bedroom scoping, fixtures excluded,
            occupant_card + temporal_context + surface_occupancy in the prompt
  judge:    strict + context + few-shot exemplars (the harness winner,
            strict_ctx_fs — Spearman 0.79, 15% over-scoring)

Runs with force=True so the new persona schema (owned_items/bedroom_index) and
the new prompt hashes regenerate the whole chain coherently, overwriting the
existing generation_out_labelset folders.

Usage:
    python -m dynamic_home_eqa.scripts.regenerate_comparison_set
"""
from __future__ import annotations

import argparse
import pathlib

from dynamic_home_eqa.generation.llm_client import DEFAULT_CACHE_DIR, DEFAULT_MODEL
from dynamic_home_eqa.generation.pipeline import run_batch
from dynamic_home_eqa.judge_eval.exemplars import build_exemplar_block
from dynamic_home_eqa.judge_eval.labels import load_split
from dynamic_home_eqa.paths import REPO_ROOT

_SCENES = ["102343992", "102344022", "102344049"]
_PROFILE = "family_with_kids"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None,
                    help="output dir; default generation_out_labelset, or "
                         "generation_out_labelset_<model-slug> for a non-default model")
    ap.add_argument("--cache-dir", default=None,
                    help="response cache dir; NON-default models get their own "
                         "(<default>-<model-slug>) — the cache is seed-keyed, so "
                         "sharing one dir across models replays the wrong model")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--no-force", action="store_true", help="reuse cache where tags match (not recommended)")
    args = ap.parse_args()

    from dynamic_home_eqa.generation.llm_client import model_slug
    is_default_model = args.model == DEFAULT_MODEL
    slug = model_slug(args.model)
    if args.out is None:
        args.out = str(REPO_ROOT / ("generation_out_labelset" if is_default_model
                                    else f"generation_out_labelset_{slug}"))
    if args.cache_dir is None:
        args.cache_dir = DEFAULT_CACHE_DIR if is_default_model else f"{DEFAULT_CACHE_DIR}-{slug}"
    print(f"model={args.model}  (label: {slug})\n  out={args.out}\n  cache={args.cache_dir}")

    exemplar_block = build_exemplar_block(
        load_split(REPO_ROOT / "results" / "judge_label_set" / "labeled_candidates.csv",
                   REPO_ROOT / "results" / "judge_label_set" / "split_manifest.json")[1]
    )
    print("Enriched regeneration: proposer context + ownership/bedroom/fixtures, "
          "judge strict+context+exemplars")
    print(f"Scenes: {_SCENES}  ->  {args.out}")

    agg, mean_realism = run_batch(
        scene_ids=_SCENES, household_type=_PROFILE, out_dir=pathlib.Path(args.out),
        model=args.model, cache_dir=args.cache_dir, force=not args.no_force,
        judge_style="strict", enrich_context=True, exemplar_block=exemplar_block,
    )
    print(f"\nDONE  survival={agg.survival_rate:.1%}  mean_realism(selected)={mean_realism:.3f}")


if __name__ == "__main__":
    main()
