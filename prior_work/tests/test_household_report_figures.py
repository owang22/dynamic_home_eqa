"""The three group-level figures of household_report draw from synthetic
cells and no-op when none of the three basic models is present."""
from __future__ import annotations

import pathlib

import pytest

pytest.importorskip("matplotlib")


def _synthetic():
    from baselines.household_report import AGE_ORDER
    models = ["LastObservation", "MostFrequentLocation(hl=24)",
              "PeriodicPersistence(bin=1h)", "Perpetua(lognormal)"]
    homes = {f"hh_{i:03d}": {"household_type": "working_professional_solo",
                             "residents": 1 + i % 3,
                             "resident_group": ("1", "2", "3+")[i % 3],
                             "archetype": "a", "overlay": "o", "variant": "v",
                             "wave": 1, "tags": []} for i in range(0, 6)}
    rows = []
    for hh in homes:
        for seed in (0, 1):
            for model in models + ["routine_oracle"]:
                for day in range(3, 28):
                    for i, age in enumerate(AGE_ORDER[:-1]):
                        rows.append({"household": hh, "seed": seed,
                                     "model": model, "mode": "continuous",
                                     "day": day, "horizon": 0.0,
                                     "age_bin": age, "n": 40,
                                     "correct": 30 - i * 2 + len(model) % 5,
                                     "logloss": 1.0})
    return rows, homes


def test_group_figures_render(tmp_path: pathlib.Path) -> None:
    from baselines.household_report import (fig_age_by_group,
                                            fig_learning_by_group,
                                            fig_learning_vs_age, models_in)
    rows, homes = _synthetic()
    ordered = models_in(rows)
    outs = [tmp_path / n for n in ("age.png", "learn.png", "cross.png")]
    fig_age_by_group(rows, homes, ordered, outs[0])
    fig_learning_by_group(rows, homes, ordered, outs[1])
    fig_learning_vs_age(rows, homes, ordered, outs[2])
    assert all(o.stat().st_size > 5000 for o in outs)


def test_group_figures_skip_without_basic_models(tmp_path: pathlib.Path
                                                 ) -> None:
    from baselines.household_report import (fig_age_by_group,
                                            fig_learning_by_group,
                                            fig_learning_vs_age, models_in)
    rows, homes = _synthetic()
    plain = [r for r in rows if r["model"] in ("LastObservation",
                                               "routine_oracle")]
    out = tmp_path / "none.png"
    for fn in (fig_age_by_group, fig_learning_by_group, fig_learning_vs_age):
        fn(plain, homes, models_in(plain), out)
    assert not out.exists()


def test_min_n_gate_drops_thin_cells(tmp_path: pathlib.Path) -> None:
    """A (group, age) cell under MIN_N questions is not drawn: the figure
    still renders and the thin bin is absent from the tick labels."""
    from baselines.household_report import (MIN_N, fig_age_by_group,
                                            models_in)
    rows, homes = _synthetic()
    for r in rows:
        if r["age_bin"] == "[72h,inf)":
            r["n"], r["correct"] = (1, 1) if r["day"] == 3 else (0, 0)
    n_thin = sum(r["n"] for r in rows if r["age_bin"] == "[72h,inf)"
                 and r["model"] == "LastObservation"
                 and homes[r["household"]]["resident_group"] == "1")
    assert 0 < n_thin < MIN_N     # present in the data, gated in the figure
    out = tmp_path / "age.png"
    fig_age_by_group(rows, homes, models_in(rows), out)
    assert out.stat().st_size > 5000
