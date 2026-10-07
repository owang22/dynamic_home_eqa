"""Stage 1.2 — displacement-probe harness.

Measures how well a belief model answers an MCQ about an object as a
function of WHEN the object was last seen and WHEN the question is asked.
No exploration, no Perceiver, no scheduler: last-seen is CONTROLLED by
injecting a single test-day observation, so the measurement is independent
of any policy.

The independent variable is the PAIR (t_seen, t_query), never the gap
Δt = t_query − t_seen: motion is routine-driven, so (9:00, 11:00) may cross
a routine transition that (13:00, 15:00) does not. This module aggregates
accuracy surfaces A(t_seen, t_query) and NEVER collapses to Δt; the gate
additionally reports a Δt-symmetry statistic so a Δt-collapsible
environment is detected and recorded rather than assumed away.

Per grid point, per target object:
  1. reset() a FRESH model at test-day start — trained routine parameters
     survive reset (BeliefModel contract); test-day observations do not.
  2. observe(t_seen, {obj: (true_parent(obj, t_seen), states)}) — a single
     injected observation.
  3. predict(t_query); answer the MCQ via the symbolic answerer; score
     exact-match on the option index. Store the model's probability on the
     true answer for calibration.

Training: "trained on N full observation days" = the model is fed the
complete ground-truth state on a fixed grid (train_feed_min) over the
training days, then reset. The train/test day split is FIXED and shared
across tiers (brief's data-split note), and test days are disjoint from
training days.

count_now (secondary): the injected observation becomes a region
observation — all class instances in {room} observed at t_seen.
"""
from __future__ import annotations

import numpy as np

from dynbelief import ELSEWHERE_ID, MIN_PER_DAY
from dynbelief.beliefs.base import object_class
from dynbelief.eqa.answerer import answer
from dynbelief.eqa.generate import make_question


def train_belief(belief, world, train_days: list[int], feed_min: int = 30) -> None:
    """Feed complete ground-truth observations over the training days."""
    t0 = min(train_days) * MIN_PER_DAY
    belief.reset(world.objects(), world.receptacles(), t0)
    for day in sorted(train_days):
        for t in range(day * MIN_PER_DAY, (day + 1) * MIN_PER_DAY, feed_min):
            belief.observe(t, world.state_at(t))


def make_ticks(day0: int, grid_min: int,
               transition_tods: list[int] | None = None,
               pad_min: tuple[int, ...] = (5, 15)) -> list[int]:
    """B4 transition-aware grid: the uniform grid plus extra points just
    before/after each routine-transition time-of-day, so accuracy cliffs at
    transitions are resolved instead of smeared. Heatmaps keep using the
    uniform subset; the fine points only feed the partitioned tables."""
    ticks = set(range(day0, day0 + MIN_PER_DAY, grid_min))
    for tr in transition_tods or []:
        for pad in pad_min:
            for t in (day0 + tr - pad, day0 + tr + pad):
                if day0 <= t < day0 + MIN_PER_DAY:
                    ticks.add(int(t))
    return sorted(ticks)


def probe_object(belief, world, obj: int, test_day: int, qtype: str,
                 grid_min: int = 30, seed: int = 0,
                 transition_tods: list[int] | None = None,
                 second_anchor: bool = False) -> list[dict]:
    """All (t_seen, t_query) grid points for one object on one test day.
    Returns one record per point: question fields + chosen index + correct
    + probabilities + transition features (B2/B3).

    second_anchor=True is the E1 DIAGNOSTIC variant: a second ground-truth
    observation is injected at the midpoint of (t_seen, t_query) —
    comparing against the single-injection primary attributes b3 error to
    prior quality vs. insufficient anchoring."""
    day0 = test_day * MIN_PER_DAY
    ticks = make_ticks(day0, grid_min, transition_tods)
    obj_events = sorted(world.change_times(obj))
    out = []
    for i, t_seen in enumerate(ticks):
        for t_query in ticks[i + 1:]:
            belief.reset(world.objects(), world.receptacles(), day0)
            # Restrict prediction scope to the probed object: predict()
            # iterates `objects`, and the probe only ever reads one — a
            # ~40x sweep speedup with identical per-object output.
            belief.objects = [obj]
            true_at_seen = world.true_parent(obj, t_seen)
            belief.observe(t_seen, {obj: (true_at_seen, {})})
            if second_anchor:
                t_mid = (t_seen + t_query) // 2
                if t_mid > t_seen:
                    belief.observe(t_mid, {obj: (world.true_parent(obj, t_mid), {})})
            q = make_question(world, qtype, obj, t_seen, t_query, seed=seed)
            choice = answer(world, belief, q)
            dist = belief.predict(t_query)[obj]
            if qtype == "location_now":
                p_true = float(dist[q["true_answer"]]) if q["true_answer"] < len(dist) else 0.0
            else:
                from dynbelief.eqa.answerer import _room_mass
                p_true = _room_mass(world, dist).get(q["true_answer"], 0.0)
            # B3 transition features from the event log
            trans_in = [t for t in obj_events if t_seen < t <= t_query]
            before_q = [t for t in obj_events if t <= t_query]
            t_since_last = (t_query - before_q[-1]) if before_q else -1
            true_at_query = world.true_parent(obj, t_query)
            displaced = int(true_at_seen != true_at_query)
            # p_chosen: the model's probability on ITS OWN answer (the
            # confidence the Stage-2 stopping rule consumes; D1 ECE input)
            if qtype == "location_now":
                opt = q["options"][choice]
                p_chosen = float(dist[opt]) if isinstance(opt, int) and opt < len(dist) else 0.0
            else:
                from dynbelief.eqa.answerer import _room_mass
                p_chosen = _room_mass(world, dist).get(q["options"][choice], 0.0)
            out.append({
                "obj": obj, "class": object_class(world.obj_label[obj]),
                "test_day": test_day, "qtype": qtype,
                "t_seen": t_seen, "t_query": t_query,
                "t_seen_tod": t_seen - day0, "t_query_tod": t_query - day0,
                "correct": int(choice == q["answer_index"]),
                "chosen_index": choice, "answer_index": q["answer_index"],
                "p_true": p_true, "p_chosen": p_chosen,
                "p_elsewhere": float(dist[ELSEWHERE_ID]),
                # B2 split: displaced (parent changed — the real predictive
                # test, b0 -> 0 by construction) vs returned (>=1 move but
                # parent restored — b0 trivially correct).
                "moved_between": displaced,
                "displaced": displaced,
                "returned": int(bool(trans_in) and not displaced),
                "n_transitions_in_interval": len(trans_in),
                "time_since_last_transition_at_query": t_since_last,
            })
    return out


def accuracy_surface(records: list[dict], grid_min: int = 30) -> np.ndarray:
    """A[t_seen_bin, t_query_bin] aggregated over records; NaN where the
    pair is empty/invalid (t_seen >= t_query)."""
    return accuracy_surface_n(records, grid_min)[0]


def accuracy_surface_n(records: list[dict], grid_min: int = 30
                       ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(acc, n_probe, n_obj) grids — the sample-count companions every
    heatmap must ship with (stage1c global-N requirement)."""
    n = MIN_PER_DAY // grid_min
    cnt = np.zeros((n, n))
    tot = np.zeros((n, n))
    objs: dict[tuple[int, int], set] = {}
    for r in records:
        i = r["t_seen_tod"] // grid_min
        j = r["t_query_tod"] // grid_min
        tot[i, j] += 1
        cnt[i, j] += r["correct"]
        objs.setdefault((i, j), set()).add(r["obj"])
    n_obj = np.zeros((n, n))
    for (i, j), s in objs.items():
        n_obj[i, j] = len(s)
    with np.errstate(invalid="ignore"):
        acc = np.where(tot > 0, cnt / np.maximum(tot, 1), np.nan)
    return acc, tot, n_obj


def delta_t_symmetry(records: list[dict]) -> float:
    """R^2 of a Δt-only predictor of accuracy against the full-pair table —
    close to 1.0 means the surface IS collapsible to Δt (the environment
    lacks time-of-day structure; the gate records that outcome)."""
    from collections import defaultdict
    pair_acc: dict[tuple[int, int], list[int]] = defaultdict(list)
    for r in records:
        pair_acc[(r["t_seen_tod"], r["t_query_tod"])].append(r["correct"])
    pairs = {k: float(np.mean(v)) for k, v in pair_acc.items()}
    dt_acc: dict[int, list[float]] = defaultdict(list)
    for (s, q), a in pairs.items():
        dt_acc[q - s].append(a)
    dt_mean = {d: float(np.mean(v)) for d, v in dt_acc.items()}
    y = np.array(list(pairs.values()))
    yhat = np.array([dt_mean[q - s] for (s, q) in pairs])
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0


def plot_surface(acc: np.ndarray, transitions_tod: list[int], grid_min: int,
                 title: str, out_path,
                 n_probe: np.ndarray | None = None,
                 n_obj: np.ndarray | None = None,
                 min_probe: int = 20, min_obj: int = 3) -> None:
    """2D heatmap of A(t_seen, t_query) with the day's routine-transition
    times overlaid on BOTH axes (never an accuracy-vs-Δt plot).

    When the n grids are provided, cells below the reliability thresholds
    (< min_probe probes or < min_obj objects) are hatched grey instead of
    colored as if solid — a thin cell must look thin."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    shown = acc.copy()
    unreliable = None
    if n_probe is not None and n_obj is not None:
        unreliable = (~np.isnan(acc)) & ((n_probe < min_probe) | (n_obj < min_obj))
        shown = np.where(unreliable, np.nan, acc)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(shown.T, origin="lower", aspect="auto", vmin=0, vmax=1,
                   extent=[0, 24, 0, 24], cmap="viridis")
    if unreliable is not None and unreliable.any():
        mask = np.ma.masked_where(~unreliable.T, np.ones_like(shown.T))
        ax.imshow(mask, origin="lower", aspect="auto", extent=[0, 24, 0, 24],
                  cmap="Greys", vmin=0, vmax=2, alpha=0.45)
        frac = float(unreliable.sum()) / max(1, int((~np.isnan(acc)).sum()))
        ax.text(0.02, 0.98, f"grey = unreliable (<{min_probe} probes or "
                f"<{min_obj} objects): {frac:.0%} of cells",
                transform=ax.transAxes, fontsize=7, va="top",
                bbox=dict(fc="white", alpha=0.8, ec="none"))
    for tr in transitions_tod:
        h = tr / 60.0
        ax.axvline(h, color="red", lw=0.5, alpha=0.5)
        ax.axhline(h, color="red", lw=0.5, alpha=0.5)
    ax.set_xlabel("t_seen (hour of day)")
    ax.set_ylabel("t_query (hour of day)")
    ax.set_title(title, fontsize=9)
    fig.colorbar(im, ax=ax, label="MCQ accuracy")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
