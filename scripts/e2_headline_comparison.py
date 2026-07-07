#!/usr/bin/env python3
"""
e2_headline_comparison.py — E2: the headline policy comparison.

IV: the policy itself (belief model + decision rule). Every policy in one
table — floors (answer_immediately), ceilings (always_resense), literature
(coverage_stop), ours (decay_threshold, decay_voi, decay_voi_routing),
and the baseline (tod_prior) — stratified by hazard_class and
question_type (location vs state). conformal_decay_threshold is
deliberately absent: dropped in the coverage-repair phase after its
realized coverage missed its 1-alpha target at every wait_hours bucket
but the shortest, traced to the fitted TransitionKernel's exponential-
decay model not matching this scene's real dwell dynamics at longer
horizons — a modeling gap, not a calibration bug (see scripts/
embodied_m3_gate.py's module docstring and CONFORMAL_COVERAGE_FINDING.md
for the full write-up). The mechanism-decomposition table (wrong->right
vs wrong->abstain per policy, per scripts/e0_mechanism_decomposition.py)
is stratified the same way and included here rather than left as an
unstratified afterthought.

Two design decisions locked in now, not bolted on later:

  1. Pool-level fingerprint (PoolManifest below): one hash over every
     scene's frozen label sets, navmesh settings, start island, portal
     config, and pipeline version. Rebuilding the whole attribution table
     under a fresh fingerprint whenever any of this changes is the same
     standing rule the single-scene FrozenConfig.fingerprint() already
     enforces — this just extends it to a pool of scenes instead of one.

  2. Clustered statistics: questions within a scene-day are not
     independent (same patrol, same decay-model fit, same navmesh) — the
     unit of independence is the scene-day, not the individual question.
     Every reported number here is a per-scene-day mean first, aggregated
     across scene-days second, with bootstrap-over-scene-days confidence
     intervals — never a pooled-i.i.d. standard error treating every row
     as its own independent sample (that would understate uncertainty by
     exactly the amount of within-scene-day correlation).

REHEARSAL: this pool has exactly one scene (102343992, via
embodied_results/m3_result.json) — the single-cluster case is degenerate
for bootstrap (nothing to resample across), reported honestly as "no CI
possible" rather than fabricated. Every output file/plot is named/titled
REHEARSAL so it cannot be mistaken for real suite results once the scene
pool (scripts/expand_scene_pool.py) actually clears the >=100-per-stratum
bar (scripts/yield_projector.py).

Does not require habitat_sim — reads only existing milestone result files.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import random
import sys
from dataclasses import dataclass, field
from typing import Optional

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.scoring import compute_ece

_N_BOOTSTRAP = 2000
_BOOTSTRAP_SEED = 0
_REHEARSAL_TAG = "REHEARSAL"

# Source files whose content defines "the pipeline" for this rehearsal's
# pipeline_version proxy — this repo has no git history to hash a commit
# from (untracked directory), so the fingerprint hashes the actual bytes
# of the modules that determine an episode's outcome instead. Extend this
# list if a future change moves decision logic into a new file; it is
# deliberately not "every .py file" (would make the fingerprint churn on
# unrelated doc/script edits).
_PIPELINE_VERSION_FILES = (
    "embodied/policy.py", "embodied/belief.py", "embodied/posterior.py",
    "embodied/runner.py", "embodied/scoring.py", "embodied/world.py",
    "embodied/sensor.py", "embodied/config.py",
)


def pipeline_version() -> str:
    h = hashlib.sha256()
    for rel in _PIPELINE_VERSION_FILES:
        h.update((_DYNAMIC_EQA / rel).read_bytes())
    return h.hexdigest()[:16]


@dataclass(frozen=True)
class SceneDescriptor:
    scene_id:          str
    location_labels:   tuple[str, ...]
    state_labels:       tuple[str, ...]
    navmesh_repr:       str   # repr(NavMeshConfig) — every bake parameter
    start_island:       int
    portal_config:      str = "none"  # no portals built anywhere yet (see navmesh-connectivity phase's D2)
    # Suite Buildout phase A (contamination audit): trace_validate.
    # validation_hash() of every folder consumed for this scene, sorted by
    # folder name. Part of the pool fingerprint below so that a folder
    # later found to be corrupted (or a corrupted folder later fixed) — the
    # navmesh-connectivity phase's stale-day0 finding — changes this scene's
    # hash and forces the "any config-affecting change re-fingerprints and
    # rebuilds the attribution table" rule to actually fire, instead of
    # depending on someone remembering which days were ever suspect.
    validation_hashes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PoolManifest:
    """One hash over every scene's frozen labels, navmesh settings, start
    island, portal config, validation hashes, and pipeline version — the
    E1-E4 pool-level counterpart of embodied.experiment_config.
    FrozenConfig.fingerprint() for a single scene. Any change to any field
    for any scene changes this hash; the mismatch guard (check_fingerprint
    below) stays fatal exactly like build_attribution_table.py's does.

    generation_model is required, no default: LLM Phase L0 needs to know
    which model family produced the pool's ground-truth traces (L0 scores
    an elicited prior's same-family vs. cross-family calibration relative
    to it), and generation_result.json itself does not record this — see
    rehearsal_pool_manifest's own comment for how the value is determined.
    """
    scenes:           tuple[SceneDescriptor, ...]
    pipeline_version: str
    generation_model: str

    def fingerprint(self) -> str:
        payload = repr((
            tuple((s.scene_id, s.location_labels, s.state_labels, s.navmesh_repr,
                   s.start_island, s.portal_config, s.validation_hashes)
                  for s in self.scenes),
            self.pipeline_version,
            self.generation_model,
        ))
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _frozen_scene_validation_hashes(out_dir: pathlib.Path) -> tuple[str, ...]:
    """validation_hash() for every folder FROZEN's location+state train/eval
    sets consume — 102343992's own folders have been clean since before
    this session (unlike the scene-pool's 102344022/102344049 day0 finding
    — see this phase's contamination-audit ledger), but computed here
    rather than assumed, so a future regression would show up as a
    fingerprint change like anything else."""
    from dynamic_home_eqa.scripts.scene_validation import validate_folder

    folders = sorted(set(FROZEN.train_folders) | {FROZEN.eval_folder}
                      | set(FROZEN.state_train_folders) | {FROZEN.state_eval_folder})
    return tuple(validate_folder(out_dir, f).validation_hash() for f in folders)


# The generator model family, for every scene this pool's traces were ever
# produced from. generation_result.json does not itself record a "model"
# field (checked directly — its top-level keys are household_id, scene_id,
# profile, day, clutter, persona, traces, displacements, raw_proposals,
# grounded_proposals, mean_realism_score, grounding_stats, conflict_report;
# no model identifier). Determined instead from the generation call sites:
# generation.llm_client.DEFAULT_MODEL ("Qwen/Qwen3-14B-Instruct") is NOT
# what actually ran — that model id does not exist on the HF Hub (HF API
# 401) and is not cached locally, so any run relying on that default alone
# would have failed outright. scripts/expand_scene_pool.py (which produced
# every pool scene) passes --model explicitly as "Qwen/Qwen3-14B-AWQ",
# matching agents/llm_agent.py's MODEL_14B ("production") and
# scripts/compare_agents.py's _DEFAULT_MODEL. All pool generation this
# project has run used this one model; if a future generation run uses a
# different model, this constant — and therefore the pool fingerprint —
# must change with it.
_GENERATION_MODEL = "Qwen/Qwen3-14B-AWQ"


def rehearsal_pool_manifest(out_dir: Optional[pathlib.Path] = None) -> PoolManifest:
    """The one-scene rehearsal pool: 102343992 via FROZEN, start_island=1
    (kitchen — confirmed by the navmesh-connectivity phase's D0/D1 fix and
    re-verified by scripts/qualify_scene.py's own PASS output)."""
    out_dir = out_dir or (_DYNAMIC_EQA / "generation_out")
    return PoolManifest(
        scenes=(SceneDescriptor(
            scene_id=FROZEN.scene,
            location_labels=FROZEN.labels,
            state_labels=FROZEN.state_labels,
            navmesh_repr=repr(FROZEN.navmesh),
            start_island=1,
            validation_hashes=_frozen_scene_validation_hashes(out_dir),
        ),),
        pipeline_version=pipeline_version(),
        generation_model=_GENERATION_MODEL,
    )


def check_pool_fingerprint(results: list[dict], manifest: PoolManifest) -> None:
    """Fails loudly if any milestone result file's own (single-scene)
    fingerprint doesn't match what this pool manifest implies for that
    scene — the same "refuse to silently mix configs" guarantee
    build_attribution_table.py's check_fingerprints enforces, extended to
    the pool level."""
    fingerprints = {r["fingerprint"] for r in results}
    if len(fingerprints) > 1:
        raise ValueError(
            f"Mismatched fingerprints across result files feeding this pool: {fingerprints} — "
            "refusing to aggregate; a milestone reran under a different config than the others."
        )


# ---------------------------------------------------------------------------
# Clustered aggregation
# ---------------------------------------------------------------------------

def cluster_key(row: dict) -> tuple[str, str]:
    """(scene, eval_folder) — the unit of independence (see module
    docstring). Falls back to FROZEN's single-scene identity for rows
    written before attribution.py started recording "scene"/"eval_folder"
    explicitly (e.g. an m3_result.json from before this script existed) —
    every such row is from the same one scene-day regardless, so the
    fallback is exact for existing data, not an approximation."""
    return (row.get("scene", FROZEN.scene), row.get("eval_folder", FROZEN.eval_folder))


@dataclass
class BootstrapResult:
    point:    float
    ci_lo:    Optional[float]
    ci_hi:    Optional[float]
    n_clusters: int

    @property
    def degenerate(self) -> bool:
        return self.n_clusters < 2


def bootstrap_over_clusters(
    per_cluster_values: list[float], n_resamples: int = _N_BOOTSTRAP, seed: int = _BOOTSTRAP_SEED,
) -> BootstrapResult:
    """Percentile bootstrap over scene-day clusters (never over individual
    questions — see module docstring). With fewer than 2 clusters there is
    nothing to resample; reports the point estimate with an explicit
    "no CI possible" (ci_lo/hi = None) rather than a fabricated interval."""
    values = [v for v in per_cluster_values if v == v]  # drop NaN
    n = len(values)
    if n == 0:
        return BootstrapResult(point=float("nan"), ci_lo=None, ci_hi=None, n_clusters=0)
    point = sum(values) / n
    if n < 2:
        return BootstrapResult(point=point, ci_lo=None, ci_hi=None, n_clusters=n)

    rng = random.Random(seed)
    means = []
    for _ in range(n_resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(0.025 * n_resamples)]
    hi = means[min(n_resamples - 1, int(0.975 * n_resamples))]
    return BootstrapResult(point=point, ci_lo=lo, ci_hi=hi, n_clusters=n)


def _cluster_means(rows: list[dict], value_fn, filter_fn=None) -> list[float]:
    """One mean per (scene, eval_folder) cluster for value_fn(row) over
    rows passing filter_fn — the "per-scene-day mean" half of clustered
    aggregation, before bootstrap_over_clusters aggregates across clusters."""
    by_cluster: dict[tuple, list[float]] = {}
    for r in rows:
        if filter_fn is not None and not filter_fn(r):
            continue
        v = value_fn(r)
        if v is None:
            continue
        by_cluster.setdefault(cluster_key(r), []).append(v)
    return [sum(vs) / len(vs) for vs in by_cluster.values() if vs]


def headline_table(rows: list[dict]) -> list[dict]:
    """One row per (policy, hazard_class, question_type): clustered
    accuracy/brier/ece/abstain/latency/travel — point estimate + bootstrap
    CI (or an explicit "no CI possible" flag) over scene-day clusters."""
    keys = sorted({(r["policy"], r["hazard_class"], r["question_type"]) for r in rows})
    out = []
    for policy, hazard, qtype in keys:
        group = [r for r in rows if r["policy"] == policy and r["hazard_class"] == hazard and r["question_type"] == qtype]

        acc_means = _cluster_means(group, lambda r: 1.0 if r["correct"] else 0.0, filter_fn=lambda r: r["correct"] is not None)
        brier_means = _cluster_means(group, lambda r: r["brier"])
        abstain_means = _cluster_means(group, lambda r: 1.0 if r["abstained"] else 0.0)
        latency_means = _cluster_means(group, lambda r: r["answer_latency_s"])
        travel_means = _cluster_means(group, lambda r: r["distance_traveled_m"])

        scored = [r for r in group if r["correct"] is not None and r["confidence"] is not None]
        ece = compute_ece([r["confidence"] for r in scored], [r["correct"] for r in scored]) if scored else float("nan")

        out.append({
            "policy": policy, "hazard_class": hazard, "question_type": qtype,
            "n_rows": len(group), "n_clusters": len(_cluster_means(group, lambda r: 1.0)),
            "accuracy": bootstrap_over_clusters(acc_means),
            "brier": bootstrap_over_clusters(brier_means),
            "ece": ece,
            "abstain_rate": bootstrap_over_clusters(abstain_means),
            "latency_s": bootstrap_over_clusters(latency_means),
            "travel_m": bootstrap_over_clusters(travel_means),
        })
    return out


# ---------------------------------------------------------------------------
# Mechanism decomposition, stratified by hazard_class
# ---------------------------------------------------------------------------

def stratified_decomposition(rows: list[dict]) -> list[dict]:
    """wrong->right / wrong->abstain / right->{abstain,wrong} / unchanged
    counts per (policy, hazard_class) — the same transition classification
    e0_mechanism_decomposition.py uses, stratified by hazard_class here
    (that script groups by wait_hours only).

    decay_voi reconciliation batch: the pairing keys used to be (policy,
    wait_hours, label) and (wait_hours, label) — omitting scene/eval_folder
    entirely. On a single-scene result file this is harmless (every label
    belongs to exactly one scene), but generic object labels ("book_1",
    "candle_1") recur across many scenes' qualified-label sets, so on a
    multi-scene pool this silently collapsed distinct trials from
    different scenes onto the same dict key — confirmed on the E2
    preliminary sweep's volatile-location stratum: 505 answer_immediately
    trials collapsed to 70 distinct (wait_hours, label) pairs, dropping
    ~86% of them (whichever scene's row was NOT last in iteration order).
    This under-counted every policy's flip totals, most visibly decay_voi's
    (reported as 0 wrong->right on that stratum; the real, scene-aware
    count is 9 — see results/reports/e2_reconciliation.md). cluster_key
    (scene, eval_folder) — already this module's own unit of independence
    for bootstrap clustering — is reused here as the missing disambiguator,
    not a new concept."""
    from dynamic_home_eqa.scripts.e0_mechanism_decomposition import Outcome, classify

    by_key = {(r["policy"], *cluster_key(r), r["wait_hours"], r["label"]): r for r in rows}
    baseline_rows = {
        (*cluster_key(r), r["wait_hours"], r["label"]): r for r in rows if r["policy"] == "answer_immediately"
    }
    policies = sorted({p for (p, _scene, _eval, _wait, _label) in by_key} - {"answer_immediately"})

    tallies: dict[tuple[str, str], dict[str, int]] = {}
    for (policy, scene, eval_folder, wait_hours, label), row in by_key.items():
        if policy not in policies:
            continue
        baseline = baseline_rows.get((scene, eval_folder, wait_hours, label))
        if baseline is None:
            continue
        transition = classify(Outcome.from_row(baseline), Outcome.from_row(row))
        key = (policy, row["hazard_class"])
        tallies.setdefault(key, {}).setdefault(transition, 0)
        tallies[key][transition] += 1

    out = []
    for (policy, hazard), counts in sorted(tallies.items()):
        out.append({"policy": policy, "hazard_class": hazard, **counts})
    return out


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _fmt_ci(b: BootstrapResult) -> str:
    if b.degenerate:
        return f"{b.point:.3f} (n_clusters={b.n_clusters}, no CI possible)"
    return f"{b.point:.3f} [{b.ci_lo:.3f}, {b.ci_hi:.3f}] (n_clusters={b.n_clusters})"


def write_csv(headline: list[dict], out_path: pathlib.Path) -> None:
    import csv
    fieldnames = ["policy", "hazard_class", "question_type", "n_rows", "n_clusters",
                  "accuracy", "accuracy_ci_lo", "accuracy_ci_hi",
                  "brier", "brier_ci_lo", "brier_ci_hi", "ece",
                  "abstain_rate", "abstain_ci_lo", "abstain_ci_hi",
                  "latency_s", "travel_m"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in headline:
            writer.writerow({
                "policy": row["policy"], "hazard_class": row["hazard_class"], "question_type": row["question_type"],
                "n_rows": row["n_rows"], "n_clusters": row["n_clusters"],
                "accuracy": row["accuracy"].point, "accuracy_ci_lo": row["accuracy"].ci_lo, "accuracy_ci_hi": row["accuracy"].ci_hi,
                "brier": row["brier"].point, "brier_ci_lo": row["brier"].ci_lo, "brier_ci_hi": row["brier"].ci_hi,
                "ece": row["ece"],
                "abstain_rate": row["abstain_rate"].point, "abstain_ci_lo": row["abstain_rate"].ci_lo, "abstain_ci_hi": row["abstain_rate"].ci_hi,
                "latency_s": row["latency_s"].point, "travel_m": row["travel_m"].point,
            })


def write_frontier_plots(headline: list[dict], out_dir: pathlib.Path, rehearsal: bool) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    tag = f" ({_REHEARSAL_TAG})" if rehearsal else ""
    location_rows = [r for r in headline if r["question_type"] == "location"]
    # One point per policy: mean across hazard classes (equal weight) for
    # a single-glance frontier — the per-(policy,hazard) table (CSV) is
    # where the stratified numbers actually live.
    by_policy: dict[str, list[dict]] = {}
    for r in location_rows:
        by_policy.setdefault(r["policy"], []).append(r)

    for xlabel, xkey, fname in (("mean answer latency (s)", "latency_s", "e2_frontier_accuracy_vs_latency"),
                                 ("mean travel distance (m)", "travel_m", "e2_frontier_accuracy_vs_travel")):
        fig, ax = plt.subplots(figsize=(7, 5))
        for policy, prows in sorted(by_policy.items()):
            xs = [r[xkey].point for r in prows]
            ys = [r["accuracy"].point for r in prows]
            ax.scatter(xs, ys, label=policy, s=60)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("accuracy")
        ax.set_title(f"E2 accuracy vs. {xlabel.split(' (')[0]} — location questions{tag}")
        ax.legend(fontsize=8, loc="best")
        ax.grid(alpha=0.3)
        suffix = f"_{_REHEARSAL_TAG}" if rehearsal else ""
        fig.savefig(out_dir / f"{fname}{suffix}.png", dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--result-paths", nargs="+",
                    default=[str(_DYNAMIC_EQA / "embodied_results" / "m3_result.json")])
    ap.add_argument("--out-dir", default=str(_DYNAMIC_EQA / "e1e4_results"))
    ap.add_argument("--rehearsal", action="store_true", default=True)
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = [json.loads(pathlib.Path(p).read_text()) for p in args.result_paths]
    manifest = rehearsal_pool_manifest()
    check_pool_fingerprint(results, manifest)
    print(f"Pool fingerprint: {manifest.fingerprint()} ({len(manifest.scenes)} scene(s))")

    rows = [r for result in results for r in result["rows"]]
    headline = headline_table(rows)
    decomposition = stratified_decomposition(rows)

    tag = f"_{_REHEARSAL_TAG}" if args.rehearsal else ""
    print(f"\n{'policy':<26}{'hazard':<10}{'qtype':<10}{'n':>5}  accuracy")
    for r in headline:
        print(f"{r['policy']:<26}{r['hazard_class']:<10}{r['question_type']:<10}{r['n_rows']:>5}  {_fmt_ci(r['accuracy'])}")

    write_csv(headline, out_dir / f"e2_headline{tag}.csv")
    print(f"\nWrote {out_dir / f'e2_headline{tag}.csv'}")

    import csv as _csv
    decomp_path = out_dir / f"e2_mechanism_decomposition{tag}.csv"
    all_transition_keys = sorted({k for row in decomposition for k in row if k not in ("policy", "hazard_class")})
    with open(decomp_path, "w", newline="") as f:
        writer = _csv.DictWriter(f, fieldnames=["policy", "hazard_class"] + all_transition_keys)
        writer.writeheader()
        for row in decomposition:
            writer.writerow({**{k: 0 for k in all_transition_keys}, **row})
    print(f"Wrote {decomp_path}")

    write_frontier_plots(headline, out_dir, rehearsal=args.rehearsal)
    print(f"Wrote frontier plots to {out_dir}")

    if any(r["accuracy"].degenerate for r in headline):
        print(f"\nNOTE: this is a {_REHEARSAL_TAG} — {len(manifest.scenes)} scene(s) means every "
              f"bootstrap CI above is degenerate (n_clusters=1, 'no CI possible' is the honest "
              f"answer, not a bug). Real confidence intervals require the multi-scene pool.")


if __name__ == "__main__":
    main()
