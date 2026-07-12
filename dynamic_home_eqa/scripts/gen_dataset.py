#!/usr/bin/env python3
"""
gen_dataset.py — Run the LLM generation pipeline on a set of HSSD scenes.

Runs all three stages (persona → activity trace → displacement) followed by
grounding validation and multi-agent conflict verification where applicable.

Outputs one JSON file per (scene, profile) under the output directory.
Prints three independent numbers at the end: grounding survival split into
infra vs. model rejection rate, and the mean realism score of the final
selected displacements (behavioral plausibility, judged separately from
physical placeability).

Usage:
    # Small sample run (semantic grounding only, no Habitat-sim)
    python -m dynamic_home_eqa.scripts.gen_dataset --n 10 --profile work_from_home_adult

    # Full batch with model selection probe
    python -m dynamic_home_eqa.scripts.gen_dataset --n 20 --profile family_with_kids \\
        --model Qwen/Qwen3-14B-Instruct --out generation_out/ --report

    # Force regeneration ignoring cache
    python -m dynamic_home_eqa.scripts.gen_dataset --n 5 --force

    # With specific scene IDs
    python -m dynamic_home_eqa.scripts.gen_dataset --scenes 102343992 102344280

Measure model rejection rate (not raw survival — see infra vs. model split)
before tuning prompts or escalating to a larger model; a high infra
rejection rate points at a grounding/region data gap, not model quality.
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
from typing import Optional

from dynamic_home_eqa.generation.pipeline import run_batch, DEFAULT_MODEL
from dynamic_home_eqa.generation.llm_client import DEFAULT_TEMPERATURE, DEFAULT_CACHE_DIR
from dynamic_home_eqa.generation.persona import HOUSEHOLD_PROFILES
from dynamic_home_eqa.paths import HSSD_DIR

_DEFAULT_TEST_SCENE = "102343992"  # the same fixture scene every other pipeline
                                     # stage's own no-arg default resolves to —
                                     # see the top-level README's pipeline order.

_ALL_SCENES: list[str] = sorted(
    pathlib.Path(p).name.split(".scene_instance.json")[0]
    for p in glob.glob(f"{HSSD_DIR}/scenes-uncluttered/*.scene_instance.json")
)
# _DEFAULT_TEST_SCENE first (when present) so the --n default (1) picks it
# deterministically without needing --scenes spelled out, while --n N for
# N>1 still walks the rest of the pool in a stable, reproducible order.
if _DEFAULT_TEST_SCENE in _ALL_SCENES:
    _ALL_SCENES.remove(_DEFAULT_TEST_SCENE)
    _ALL_SCENES.insert(0, _DEFAULT_TEST_SCENE)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Default n=1 (was 10): a bare `gen_dataset.py` invocation is a single-
    # scene smoke test of the full pipeline, not a 10-scene batch job — see
    # the top-level README. Pass --n/--scenes explicitly for a real batch run.
    ap.add_argument("--n", type=int, default=1,
                    help="Number of scenes to process (default: 1, a fast smoke test — "
                         "pass a larger --n for a real batch run)")
    ap.add_argument("--profile", default="family_with_kids",
                    help="Household profile to generate (free-form label, e.g. "
                         f"{', '.join(HOUSEHOLD_PROFILES)}, or any other description)")
    ap.add_argument("--scenes", nargs="+", default=None,
                    help="Specific scene IDs (overrides --n)")
    ap.add_argument("--day", type=int, default=0,
                    help="Day index for trace seeding (default: 0)")
    ap.add_argument("--n-variants", type=int, default=1,
                    help="Distinct persona variants to generate per scene (default: 1). "
                         "Each variant is a different household for the same house — "
                         "different occupants/ages/habits/tidiness, and (since every "
                         "downstream seed derives from the household id) a different "
                         "activity trace and displacement set too — not a different day "
                         "of the same household.")
    ap.add_argument("--n-days", type=int, default=1,
                    help="Independent days to generate per household (default: 1), "
                         "starting at --day. Persona is held fixed (day-invariant by "
                         "design); activity traces and displacements vary per day. This "
                         "is the train/eval day split the DecayModel calibration "
                         "protocol needs, not a different household (--n-variants).")
    ap.add_argument("--model", default=DEFAULT_MODEL,
                    help=f"vLLM model string (default: {DEFAULT_MODEL})")
    ap.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE,
                    help=f"Sampling temperature (default: {DEFAULT_TEMPERATURE})")
    ap.add_argument("--out", default="generation_out",
                    help="Output directory (default: generation_out/)")
    ap.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR,
                    help=f"Response cache directory (default: {DEFAULT_CACHE_DIR} — "
                         "outside the repo deliberately; see --no-cache to disable "
                         "entirely). Holds raw per-call LLM responses keyed by seed, "
                         "including full candidate pools and realism scores that "
                         "generation_result.json doesn't keep (it only keeps the "
                         "final selected subset) — useful for debugging/reruns, not "
                         "meant as a permanent artifact.")
    ap.add_argument("--no-cache", action="store_true",
                    help="Disable response caching entirely (every call hits the "
                         "LLM fresh; --force and --cache-dir are ignored)")
    ap.add_argument("--force", action="store_true",
                    help="Ignore cached responses and regenerate")
    ap.add_argument("--no-semantic-grounding", action="store_true",
                    help="Skip semantic grounding check (accept all proposals)")
    ap.add_argument("--judge-thinking", action="store_true",
                    help="LLM Option Evaluation round (Arm 1): score realism with Qwen3 "
                         "thinking mode — no guided decoding on the judge call (impossible "
                         "alongside a think block on this vLLM version); output shapes are "
                         "normalized and the reasoning trace is stored in the response cache. "
                         "Proposer stays guided/non-thinking.")
    ap.add_argument("--judge-style", choices=["asis", "strict"], default="asis",
                    help="Judge prompt style: 'asis' = the existing realism prompt; 'strict' = "
                         "the selective variant calibrated for over-generated pools (most "
                         "candidates should score low; see stages._REALISM_SYSTEM_STRICT). "
                         "Folded into the judge cache seed, so styles never share cached scores.")
    ap.add_argument("--reachability-filtering", action="store_true",
                    help="Reachability Removal Phase 1: off by default. With interior "
                         "doors closed and out of scope, navmesh reachability is wrong "
                         "for most indoor rooms and was the confirmed driver of outdoor "
                         "objects being selected for indoor instructions. Pass this flag "
                         "to restore the old always-on navmesh-reachability vocabulary "
                         "pruning + hard-gate rejection (generation/anchor_reachability_"
                         "filter.py, generation/manifest.py) for comparison/regression "
                         "testing — not intended for normal use until door handling lands.")
    ap.add_argument("--no-validate-trace", action="store_true",
                    help="Skip the trace_validate hard-invariant gate on each manifest "
                         "(default: on — a scene whose manifest fails chain-consistency, "
                         "insert-once, no-op, or attendance checks is reported as an error "
                         "and skipped, same as a generation failure). Only disable this to "
                         "rebuild manifests from older generation_result.json data for "
                         "before/after comparison, where violations are expected.")
    ap.add_argument("--report", action="store_true",
                    help="Print detailed grounding survival report at end")
    ap.add_argument("--gen-questions", action="store_true",
                    help="Run gen_questions.py on each manifest after writing")
    args = ap.parse_args()

    scenes = args.scenes or _ALL_SCENES[:args.n]
    if not scenes:
        sys.exit("No scenes found. Check HSSD_DIR in this script.")

    out_dir = pathlib.Path(args.out)
    if not out_dir.is_absolute():
        out_dir = (_PKG_ROOT / out_dir).resolve()

    cache_dir: Optional[pathlib.Path] = None
    if not args.no_cache:
        cache_dir = pathlib.Path(args.cache_dir)
        if not cache_dir.is_absolute():
            cache_dir = (_PKG_ROOT / cache_dir).resolve()

    print(f"Scenes       : {len(scenes)}")
    print(f"Profile      : {args.profile}")
    print(f"Day          : {args.day}")
    print(f"Variants     : {args.n_variants}")
    print(f"Days         : {args.n_days}")
    print(f"Model        : {args.model}")
    print(f"Output       : {out_dir}")
    print(f"Cache        : {cache_dir if cache_dir else 'disabled (--no-cache)'}")
    print(f"Force regen  : {args.force}")
    print(f"Semantic gnd : {not args.no_semantic_grounding}")
    print(f"Trace gate   : {not args.no_validate_trace}")
    print(f"Reachability filtering: {args.reachability_filtering}")
    print(f"Judge        : {'thinking' if args.judge_thinking else 'guided'} / style={args.judge_style}")
    print()

    agg, mean_realism = run_batch(
        scene_ids=scenes,
        household_type=args.profile,
        out_dir=out_dir,
        day=args.day,
        n_variants=args.n_variants,
        n_days=args.n_days,
        model=args.model,
        temperature=args.temperature,
        cache_dir=str(cache_dir) if cache_dir else None,
        force=args.force,
        use_semantic_grounding=not args.no_semantic_grounding,
        validate_trace=not args.no_validate_trace,
        reachability_filtering=args.reachability_filtering,
        judge_thinking=args.judge_thinking,
        judge_style=args.judge_style,
    )

    if args.gen_questions:
        import subprocess
        gen_script = pathlib.Path(__file__).parent / "gen_questions.py"
        subprocess.run([sys.executable, str(gen_script), str(out_dir)], check=False)

    # Three independent numbers, reported plainly rather than blended into one
    # survival rate with a threshold verdict — infra gaps, model quality, and
    # behavioral realism are different failure modes with different fixes.
    print(f"\n{'═'*60}")
    print(f"Grounding survival     : {agg.survival_rate:.1%}  ({agg.accepted}/{agg.total} proposals)")
    print(f"Infra rejection rate   : {agg.infra_rejection_rate:.1%}  "
          f"(no_anchor={agg.no_anchor_in_scene} — region/anchor data gap, not model error)")
    print(f"Model rejection rate   : {agg.model_rejection_rate:.1%}  "
          f"(no_object={agg.no_object_in_scene}, no_placement={agg.no_valid_placement}, "
          f"bad_relation={agg.unsupported_relation})")
    print(f"Mean realism (selected): {mean_realism:.3f}  "
          f"(behavioral plausibility of the final selected displacements, "
          f"independent of grounding)")
    if args.report and agg.rejected_categories:
        print()
        print("no_object rejections by category (recurring names may be a")
        print("vocabulary mismatch to fix, not hallucination to discard):")
        for cat, n in sorted(agg.rejected_categories.items(), key=lambda kv: -kv[1]):
            print(f"  {cat:20s} {n}")
    print(f"{'═'*60}")


if __name__ == "__main__":
    main()
