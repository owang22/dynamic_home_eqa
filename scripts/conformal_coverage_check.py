#!/usr/bin/env python3
"""
conformal_coverage_check.py — Suite Buildout phase B2: measures realized
coverage of conformal_decay_threshold's calibrated theta on HELD-OUT data
(the eval day, never used for calibration), against the configured
1-alpha target. Six passing unit tests on belief.calibrate_conformal_theta
show the code runs correctly on synthetic data; this script is the actual
calibration check — does the guarantee hold on real held-out data.

While building this check, it caught two real bugs (not statistical
drift, both now fixed):

1. The state axis's dwell events were keyed by bare object_category, but
   state decay_models were keyed by the synthetic "{category}::{variable}"
   string, so calibrate_conformal_theta's own "if cat in decay_models"
   filter silently matched nothing and fell back to the uncalibrated
   default — state-axis conformal_decay_threshold was byte-for-byte
   identical to plain decay_threshold in the M3 gate report because of
   it. Fixed in belief.dwell_events (now change-type-aware).
2. Deeper, found while verifying fix #1's M3 gate rerun: even keyed
   correctly, theta was being calibrated against DecayModel.validity
   (elapsed) = exp(-lambda*elapsed) — a plain decay-to-zero curve — while
   every deployed threshold/VOI policy thresholds against
   PosteriorBeliefStore.validity(), which converges to the fitted
   kernel's own (possibly far-from-zero) stationary dest_dist instead.
   Calibrating against one statistic and deploying against a different
   one breaks the conformal guarantee regardless of how carefully theta
   is computed — the guarantee is a statement about quantiles of ONE
   distribution. Invisible on the location axis (many-anchor posteriors
   decay low enough within the swept wait-hours range for both curves to
   cross the same thresholds) but made state-axis conformal_decay_
   threshold indistinguishable from decay_threshold AND decay_voi/
   decay_voi_routing (a 2-value, sticky kernel's real posterior validity
   never came near either curve's calibrated theta). Fixed by calibrating
   directly against posterior.TransitionKernel.propagate — see belief.
   calibrate_conformal_theta's docstring.

This script exists so that class of bug — "the code runs, the number is
just wrong" — has a standing check, not a one-off catch.

Split-conformal exchangeability: calibrate_conformal_theta's 1-alpha
coverage guarantee only holds if calibration (train) and test (eval) data
are exchangeable draws from the same distribution. Day-to-day variation in
which activities/objects move, and (once the multi-profile pool lands)
profile-to-profile variation in routine structure, can both break this.
This script measures whether it currently holds for the frozen scene's own
train/eval split — not tuned to force a pass, reported straight either way.

Acceptance: the target coverage (1-alpha) falls within the Wilson score
interval of the OBSERVED held-out coverage, given the held-out sample
size — not "observed >= target exactly" (a small held-out sample will not
hit the target exactly even when genuinely well-calibrated). If the
target falls outside that interval: report the drift, do not adjust
alpha/theta to make it pass (see module docstring's standing rule).

Coverage-repair phase (found by this exact check, on the just-fixed
calibration): a single global theta showed 0.61/0.56 observed coverage
against 0.90/0.80 targets on the location axis — not drift, a 29-point
miss. Diagnosis: dwell-time covariate shift. calibrate_conformal_theta's
nonconformity scores come from calibration days' NATURAL dwell events
(however long an object happened to stay put); deployment (the M3 gate's
wait_hours sweep) asks about validity at FIXED elapsed times up to 4h,
but 82% of this scene's natural location dwell events are already over by
4h — a global quantile is dominated by short-dwell behavior and badly
miscalibrated for the longer swept waits. `diagnose_wait_hours_coverage`
below makes this visible directly: per-wait-hours coverage under the
GLOBAL theta, which should degrade monotonically with wait_hours if this
hypothesis is right (confirmed on the location axis: 0.90 -> 0.69 -> 0.57
-> 0.44 -> 0.24 as wait grows from 0.25h to 4h). The fix is Mondrian
(group-conditional) conformal — belief.calibrate_conformal_theta_by_wait
calibrates a SEPARATE theta per wait_hours bucket from only the
calibration events whose own natural dwell falls in that bucket, and
DecayThresholdConfig.theta_by_wait wires the deployed policy to look up
the bucket matching its current elapsed-since-observation time (embodied/
policy.py's DecayThreshold._theta_for). `verify_bucketed_coverage` below
re-checks coverage per bucket after this fix — the same check this
docstring's earlier bugs were caught by, now run per bucket instead of
once, globally.

Pure Python — no habitat_sim needed.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
from dataclasses import dataclass

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.attribution import (
    fit_location_kernels_from_train,
    fit_state_kernels_from_train,
)
from dynamic_home_eqa.embodied.belief import (
    _posterior_validity_at_dwell,
    calibrate_conformal_theta,
    calibrate_conformal_theta_by_wait,
    dwell_events,
)
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.posterior import TransitionKernel

_ALPHAS = (0.1, 0.2)
_Z_95 = 1.959963985  # two-sided 95% normal quantile

# Below this many held-out events, a coverage check is closer to a coin
# flip than a measurement — e.g. at n=1 there are only two possible
# observed values (0.0 or 1.0), and the Wilson interval is correspondingly
# so wide almost any target "passes" without that meaning anything. Not
# derived from a formal power calculation; a documented floor below which
# [OK]/[DRIFT] should not be read as a real finding, distinct from the
# state axis's own qualifying-scene shortfall (see scripts/yield_projector.py).
_MIN_MEANINGFUL_N = 30


def wilson_interval(hits: int, n: int, z: float = _Z_95) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion — well-behaved at
    small n and at p near 0/1, unlike the normal (Wald) approximation."""
    if n == 0:
        return (float("nan"), float("nan"))
    p_hat = hits / n
    denom = 1 + z * z / n
    center = (p_hat + z * z / (2 * n)) / denom
    margin = (z * math.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


@dataclass
class CoverageResult:
    axis:      str
    alpha:     float
    theta:     float
    n_held_out: int
    hits:      int
    observed:  float
    ci_lo:     float
    ci_hi:     float
    target:    float

    @property
    def within_ci(self) -> bool:
        return self.n_held_out > 0 and self.ci_lo <= self.target <= self.ci_hi

    @property
    def data_starved(self) -> bool:
        """True when there's SOME held-out data but not enough of it for
        [OK]/[DRIFT] to mean anything (see _MIN_MEANINGFUL_N) — a status
        distinct from both, not folded into either."""
        return 0 < self.n_held_out < _MIN_MEANINGFUL_N

    def summary(self) -> str:
        if self.n_held_out == 0:
            return f"{self.axis} alpha={self.alpha}: 0 held-out events — cannot check coverage"
        status = "OK" if self.within_ci else "DRIFT"
        suffix = (
            f"  [DATA-STARVED: n={self.n_held_out} < {_MIN_MEANINGFUL_N} — "
            f"not a meaningful coverage check yet, not a passing one]"
            if self.data_starved else ""
        )
        return (
            f"{self.axis} alpha={self.alpha}: theta={self.theta:.4f}  "
            f"observed={self.observed:.3f} ({self.hits}/{self.n_held_out})  "
            f"95% CI=[{self.ci_lo:.3f}, {self.ci_hi:.3f}]  target={self.target:.3f}  [{status}]{suffix}"
        )


def realized_coverage(
    axis: str,
    train_manifests: list[dict],
    eval_manifest: dict,
    kernels: dict[str, TransitionKernel],
    alpha: float,
) -> CoverageResult:
    theta = calibrate_conformal_theta(train_manifests, kernels, alpha=alpha)
    held_out = dwell_events(eval_manifest["changes"])
    scores = [
        _posterior_validity_at_dwell(kernels[key], start_state, dwell)
        for key, start_state, dwell in held_out if key in kernels
    ]
    n = len(scores)
    hits = sum(1 for s in scores if s >= theta)
    observed = (hits / n) if n else float("nan")
    ci_lo, ci_hi = wilson_interval(hits, n)
    return CoverageResult(
        axis=axis, alpha=alpha, theta=theta, n_held_out=n, hits=hits,
        observed=observed, ci_lo=ci_lo, ci_hi=ci_hi, target=1.0 - alpha,
    )


# ---------------------------------------------------------------------------
# Coverage-repair phase: per-wait-hours diagnosis and Mondrian-fix verification
# ---------------------------------------------------------------------------

@dataclass
class WaitCoverageResult:
    """Realized coverage AT one specific wait_hours value — the covariate
    the global check above pools away. n_trusted is how many held-out
    dwell events this theta would have judged "still valid" at exactly
    this wait; hits is how many of those genuinely dwelled at least that
    long (dwell_hours >= wait_hours)."""
    axis:       str
    wait_hours: float
    theta:      float
    n_trusted:  int
    hits:       int
    observed:   float
    ci_lo:      float
    ci_hi:      float
    target:     float

    @property
    def within_ci(self) -> bool:
        return self.n_trusted > 0 and self.ci_lo <= self.target <= self.ci_hi

    def summary(self) -> str:
        if self.n_trusted == 0:
            return f"{self.axis} wait={self.wait_hours}: 0 trusted held-out events — cannot check"
        status = "OK" if self.within_ci else "MISS"
        return (
            f"{self.axis} wait={self.wait_hours:>4}: theta={self.theta:.4f}  n_trusted={self.n_trusted:>3}  "
            f"observed={self.observed:.3f} ({self.hits}/{self.n_trusted})  "
            f"95% CI=[{self.ci_lo:.3f}, {self.ci_hi:.3f}]  target={self.target:.3f}  [{status}]"
        )


def dwell_time_summary(events: list[tuple[str, str, float]]) -> dict:
    """n / min / p25 / median / p75 / max of a dwell_events() list's own
    dwell_hours — the calibration-side half of the covariate-shift
    comparison (see this script's module docstring)."""
    dwells = sorted(d for _, _, d in events)
    n = len(dwells)
    if n == 0:
        return {"n": 0}
    return {
        "n": n, "min": dwells[0], "p25": dwells[n // 4],
        "median": dwells[n // 2], "p75": dwells[(3 * n) // 4], "max": dwells[-1],
    }


def coverage_at_wait(
    axis: str,
    theta: float,
    kernels: dict[str, TransitionKernel],
    held_out_events: list[tuple[str, str, float]],
    wait_hours: float,
    target: float,
) -> WaitCoverageResult:
    """Realized coverage of `theta` at exactly `wait_hours`: among
    held-out dwell events this theta would trust at that wait
    (_posterior_validity_at_dwell(kernel, start_state, wait_hours) >=
    theta), what fraction genuinely dwelled at least that long
    (dwell_hours >= wait_hours)? Reusable for both the global-theta
    diagnosis (theta fixed, sweep wait_hours) and the Mondrian-fix
    verification (theta = that bucket's own theta)."""
    n = 0
    hits = 0
    for key, start_state, dwell in held_out_events:
        kernel = kernels.get(key)
        if kernel is None:
            continue
        validity = _posterior_validity_at_dwell(kernel, start_state, wait_hours)
        if validity >= theta:
            n += 1
            if dwell >= wait_hours:
                hits += 1
    observed = (hits / n) if n else float("nan")
    ci_lo, ci_hi = wilson_interval(hits, n)
    return WaitCoverageResult(
        axis=axis, wait_hours=wait_hours, theta=theta, n_trusted=n, hits=hits,
        observed=observed, ci_lo=ci_lo, ci_hi=ci_hi, target=target,
    )


def diagnose_wait_hours_coverage(
    axis: str,
    train_manifests: list[dict],
    eval_manifest: dict,
    kernels: dict[str, TransitionKernel],
    wait_buckets: tuple[float, ...],
    alpha: float,
) -> list[WaitCoverageResult]:
    """Coverage per wait_hours bucket under the single GLOBAL theta — the
    diagnostic for dwell-time covariate shift. A monotonic decline as
    wait_hours grows (roughly matching how much of the calibration dwell
    distribution has already "expired" by that wait) confirms the
    hypothesis; a flat miss across all waits would NOT (see module
    docstring's standing rule: escalate rather than apply the Mondrian
    fix if this pattern doesn't hold)."""
    theta = calibrate_conformal_theta(train_manifests, kernels, alpha=alpha)
    held_out = dwell_events(eval_manifest["changes"])
    return [coverage_at_wait(axis, theta, kernels, held_out, w, target=1.0 - alpha) for w in wait_buckets]


def verify_bucketed_coverage(
    axis: str,
    train_manifests: list[dict],
    eval_manifest: dict,
    kernels: dict[str, TransitionKernel],
    wait_buckets: tuple[float, ...],
    alpha: float,
) -> tuple[dict[float, float], list[WaitCoverageResult]]:
    """The Mondrian fix, verified per bucket: calibrate_conformal_theta_
    by_wait's per-bucket thetas, each checked with coverage_at_wait AT
    that same bucket's wait_hours (not pooled) — the direct test of
    whether bucketing actually closed the gap diagnose_wait_hours_
    coverage found."""
    thetas = calibrate_conformal_theta_by_wait(train_manifests, kernels, wait_buckets, alpha=alpha)
    held_out = dwell_events(eval_manifest["changes"])
    results = [
        coverage_at_wait(axis, thetas[w], kernels, held_out, w, target=1.0 - alpha)
        for w in wait_buckets
    ]
    return thetas, results


def _plot_dwell_vs_wait(axis_summaries: dict[str, dict], out_path: pathlib.Path) -> None:
    """One histogram-style bar chart per axis of the calibration dwell-
    time distribution (min/p25/median/p75/max), with the swept wait_hours
    values overlaid as vertical lines — the covariate-shift mismatch in
    one plot, per this phase's instructions."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(axis_summaries), figsize=(6 * len(axis_summaries), 4), squeeze=False)
    for i, (axis, summary) in enumerate(axis_summaries.items()):
        ax = axes[0][i]
        if summary["n"] == 0:
            ax.set_title(f"{axis}: no calibration dwell events")
            continue
        box_stats = [{
            "med": summary["median"], "q1": summary["p25"], "q3": summary["p75"],
            "whislo": summary["min"], "whishi": summary["max"], "fliers": [],
        }]
        ax.bxp(box_stats, vert=False, showfliers=False)
        for w in FROZEN.wait_hours_sweep:
            ax.axvline(w, color="red", linestyle="--", alpha=0.6)
            ax.text(w, 1.15, f"wait={w}", color="red", fontsize=7, ha="center")
        ax.set_xlabel("dwell hours")
        ax.set_title(f"{axis} calibration dwell distribution (n={summary['n']}) vs. swept wait_hours")
        ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"
    out_results_dir = _DYNAMIC_EQA / "e1e4_results"
    out_results_dir.mkdir(parents=True, exist_ok=True)

    train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.train_folders
    ]
    eval_manifest = json.loads((out_dir / FROZEN.eval_folder / "manifest.json").read_text())
    location_kernels = fit_location_kernels_from_train(out_dir, FROZEN)

    state_train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in FROZEN.state_train_folders
    ]
    state_eval_manifest = json.loads((out_dir / FROZEN.state_eval_folder / "manifest.json").read_text())
    state_kernels = fit_state_kernels_from_train(out_dir, FROZEN)

    axes = [
        ("location", train_manifests, eval_manifest, location_kernels),
        ("state", state_train_manifests, state_eval_manifest, state_kernels),
    ]

    # -- 1. Global-theta check (unchanged from before this phase) -----------
    print("=" * 78)
    print("1. Global-theta coverage (pooled across all natural dwell events):\n")
    results = []
    for alpha in _ALPHAS:
        for axis, train_m, eval_m, kernels in axes:
            results.append(realized_coverage(axis, train_m, eval_m, kernels, alpha))
    any_drift = False
    any_data_starved = False
    for r in results:
        print("  " + r.summary())
        if r.data_starved:
            any_data_starved = True
        elif r.n_held_out > 0 and not r.within_ci:
            any_drift = True
    print()
    if any_drift:
        print("DRIFT/MISS under the single global theta — see part 2 below for the per-wait-hours "
              "diagnosis (dwell-time covariate shift) and part 3 for the Mondrian fix.")
    else:
        print("No drift detected among axes with enough held-out data to judge.")
    if any_data_starved:
        print("DATA-STARVED: flagged axis/alpha has too few held-out dwell events for [OK]/[DRIFT] "
              "to mean anything (see _MIN_MEANINGFUL_N) — distinct from the question-yield shortfall "
              "scripts/yield_projector.py reports (Suite Buildout phase B3); different populations.")

    # -- 2. Diagnosis: coverage per wait_hours bucket, under the SAME global theta
    print("\n" + "=" * 78)
    print("2. Diagnosis — coverage AT each swept wait_hours, under the global theta (alpha=0.1):\n")
    dwell_summaries = {}
    for axis, train_m, eval_m, kernels in axes:
        train_events = [c for m in train_m for c in dwell_events(m["changes"])]
        summary = dwell_time_summary(train_events)
        dwell_summaries[axis] = summary
        print(f"  {axis} calibration dwell-time distribution: {summary}")
        print(f"  {axis} swept wait_hours: {FROZEN.wait_hours_sweep}")
        wait_results = diagnose_wait_hours_coverage(
            axis, train_m, eval_m, kernels, FROZEN.wait_hours_sweep, alpha=0.1,
        )
        for wr in wait_results:
            print("    " + wr.summary())
        observed_seq = [wr.observed for wr in wait_results if wr.n_trusted > 0]
        monotonic = all(a >= b for a, b in zip(observed_seq, observed_seq[1:]))
        print(f"  {axis}: observed coverage {'DECLINES MONOTONICALLY' if monotonic else 'is NOT monotonic'} "
              f"with wait_hours -> {'covariate-shift hypothesis supported' if monotonic else 'hypothesis NOT confirmed for this axis; escalate before trusting the Mondrian fix below'}")
        print()

    plot_path = out_results_dir / "conformal_dwell_vs_wait.png"
    _plot_dwell_vs_wait(dwell_summaries, plot_path)
    print(f"Wrote {plot_path}")

    # -- 3. Fix verification: Mondrian per-bucket theta, checked per bucket -
    print("\n" + "=" * 78)
    print("3. Mondrian fix verification — per-bucket theta, checked at its own wait_hours (alpha=0.1):\n")
    any_bucket_miss = False
    for axis, train_m, eval_m, kernels in axes:
        train_events = [c for m in train_m for c in dwell_events(m["changes"])]
        n_events = sum(1 for key, _s, _d in train_events if key in kernels)
        n_distinct_pairs = len({(key, s) for key, s, _d in train_events if key in kernels})
        print(f"  {axis} calibration sample: {n_events} events matching a fitted kernel, spanning "
              f"{n_distinct_pairs} distinct (category/key, state) pairs — every bucket's theta is a "
              f"quantile over that many scores, but at most {n_distinct_pairs} of them are numerically "
              f"distinct (_posterior_validity_at_dwell depends only on kernel/state/wait_hours, not on "
              f"which specific event contributed it — see calibrate_conformal_theta_by_wait's own docstring).")

        thetas, bucket_results = verify_bucketed_coverage(
            axis, train_m, eval_m, kernels, FROZEN.wait_hours_sweep, alpha=0.1,
        )
        for br in bucket_results:
            print("    " + br.summary())
            if br.n_trusted > 0 and not br.within_ci:
                any_bucket_miss = True
        print()

    if any_bucket_miss:
        print("At least one bucket still misses its target after the Mondrian fix — reported "
              "straight, not tuned. Per the standing rule, this bucket's conformal_decay_threshold "
              "should not be presented as calibrated in a headline table until resolved.")
    else:
        print("Every bucket's realized coverage falls within its target's Wilson CI after the "
              "Mondrian fix.")


if __name__ == "__main__":
    main()
