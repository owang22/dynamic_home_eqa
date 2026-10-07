"""Bank-intrinsic statistics against hand-computed expectations.

The synthetic fixture's numbers are derivable from its construction
(see baselines.bank.write_synthetic_bank), over its 7-day horizon:

* mug_static never leaves counter_k -> modal share 1.0, no displacement.
* keys_periodic: entry_e 15 h/day vs desk_o 9 h/day -> modal entry_e,
  share 15/24 = 0.625; one 9 h displacement stint per day (x7).
* laptop_mover: desk_o for 3.5 days, shelf_l for 3.5 days — an exact
  dwell tie, broken to desk_o (earliest first entry) -> share 0.5 and a
  single 84 h displacement stint.

Mean dwell-weighted modal share = (1.0 + 0.625 + 0.5) / 3 = 0.70833.
Questions (days 4-6): mug at modal (3), keys@20:05 at modal (3),
keys@10:05 not (truth desk, 3), laptop not (truth shelf, modal desk, 3)
-> modal share at query times = 6/12 = 0.5.
"""

from __future__ import annotations

import pathlib

import pytest

from baselines.bank import (write_gate_fail_static_bank, write_gate_pass_bank,
                            write_synthetic_bank)
from baselines.bankstats import (DEFAULT_MAX_MODAL_SHARE, compute_bank_stats,
                                 json_dict, render_text, stationarity_passes)


@pytest.fixture(scope="module")
def synthetic_stats(tmp_path_factory: pytest.TempPathFactory):  # type: ignore[no-untyped-def]
    bank = write_synthetic_bank(
        tmp_path_factory.mktemp("bank") / "bank.jsonl")
    return compute_bank_stats(bank)


def test_modal_shares_match_hand_derivation(synthetic_stats) -> None:  # type: ignore[no-untyped-def]
    assert synthetic_stats.per_object_modal_share == {
        "mug_static": 1.0, "keys_periodic": 0.625, "laptop_mover": 0.5}
    assert synthetic_stats.modal_share_time == pytest.approx(
        (1.0 + 0.625 + 0.5) / 3)
    assert synthetic_stats.modal_share_questions == pytest.approx(0.5)


def test_displacement_distribution(synthetic_stats) -> None:  # type: ignore[no-untyped-def]
    # Eight stints: seven 9 h keys excursions + one 84 h laptop stay.
    assert synthetic_stats.displacement_median_h == pytest.approx(9.0)
    assert synthetic_stats.displacement_p90_h == pytest.approx(84.0)
    assert synthetic_stats.displaced_time_share == pytest.approx(
        1 - (1.0 + 0.625 + 0.5) / 3)


def test_question_bookkeeping(synthetic_stats) -> None:  # type: ignore[no-untyped-def]
    assert synthetic_stats.n_questions == 12
    # keys_periodic is asked twice per question day.
    assert synthetic_stats.max_repeats_per_day == 2
    # keys: 2 real moves on day 0 (t=0 row is not a move), 2 on later days
    # (the midnight entry_e row repeats the standing location); laptop 1.
    assert synthetic_stats.moves_per_day == pytest.approx(15 / 7)


def test_stationarity_gate_on_engineered_banks(
        tmp_path: pathlib.Path) -> None:
    lively = compute_bank_stats(write_gate_pass_bank(tmp_path / "pass.jsonl"))
    static = compute_bank_stats(
        write_gate_fail_static_bank(tmp_path / "fail.jsonl"))
    assert stationarity_passes(lively)
    assert lively.modal_share_time <= DEFAULT_MAX_MODAL_SHARE
    assert not stationarity_passes(static)
    assert static.modal_share_time == pytest.approx(1.0)
    assert static.moves_per_day == 0.0
    assert static.displacement_median_h == 0.0


def test_report_forms(tmp_path: pathlib.Path) -> None:
    bank = write_synthetic_bank(tmp_path / "bank.jsonl")
    stats = compute_bank_stats(bank)
    text = render_text(bank.path, stats, DEFAULT_MAX_MODAL_SHARE)
    assert "stationarity" in text and "modal share" in text
    d = json_dict(bank, stats, DEFAULT_MAX_MODAL_SHARE)
    assert d["stationarity_pass"] == (
        stats.modal_share_time <= DEFAULT_MAX_MODAL_SHARE)
    assert d["bank_manifest_hash"] == bank.manifest_hash


def test_dynamics_figure_and_daily_series(tmp_path: pathlib.Path) -> None:
    from baselines.bankstats_figs import (compute_daily_series,
                                          write_dynamics_figure)

    bank = write_synthetic_bank(tmp_path / "bank.jsonl")
    series = compute_daily_series(bank)
    # keys move twice every day; the laptop's single move lands on day 3.
    assert sum(series.moves_by_day.values()) == 15
    assert series.moves_by_day[3] == 3
    # Question days 4-6 each hit home base on 2 of 4 questions.
    assert series.query_modal_by_day == {4: 0.5, 5: 0.5, 6: 0.5}
    # Eight stints, sorted hours: seven 9 h + one 84 h.
    assert series.stint_hours == tuple([9.0] * 7 + [84.0])
    out = tmp_path / "bank_dynamics.png"
    write_dynamics_figure(bank, compute_bank_stats(bank),
                          DEFAULT_MAX_MODAL_SHARE, out)
    assert out.exists() and out.stat().st_size > 10_000
