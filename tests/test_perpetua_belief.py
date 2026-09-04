"""Perpetua / Perpetua* belief models: edge-stream construction from
mixed Observations and SenseResults, normalisation, exclusion handling
without double counting, never-observed fallback, determinism, the
switching prior, and registry wiring. Times are seconds since episode
start."""

from __future__ import annotations

import math
import random

import pytest

from baselines.beliefs import perpetua_filters as pfl
from baselines.beliefs.perpetua_belief import (PerpetuaBelief,
                                               PerpetuaConfig,
                                               PerpetuaStarBelief,
                                               PerpetuaStarConfig)
from baselines.registry import (BELIEF_REGISTRY, CANDIDATE_SLATE,
                                build_registered_belief)
from baselines.types import (DAY_SECONDS, EpisodeContext, Observation,
                             SenseResult)

RECS = ("a", "b", "c", "d")
H = 3600


def _context(objects: dict[str, str] | None = None) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes=objects or {"o": "mug"}, budget_per_day=1, n_days=8)


def _obs(rec: str, t: int, obj: str = "o") -> Observation:
    return Observation(object_id=obj, object_class="mug", receptacle_id=rec,
                       t=t, source="scripted")


def _sense(rec: str, t: int, contents: tuple = ()) -> SenseResult:
    return SenseResult(receptacle_id=rec, t=t, contents=contents)


FAST = dict(k_range=(1, 2), em_max_iter=30, num_steps=3)


def _perpetua(**kw) -> PerpetuaBelief:
    cfg = PerpetuaConfig(**{**FAST, **kw})
    m = PerpetuaBelief(random.Random(0), cfg)
    m.reset(_context())
    return m


def _star(**kw) -> PerpetuaStarBelief:
    base = {k: v for k, v in FAST.items() if k != "num_steps"}
    cfg = PerpetuaStarConfig(**{**base, **kw})
    m = PerpetuaStarBelief(random.Random(0), cfg)
    m.reset(_context())
    return m


# --------------------------------------------------- edge streams

@pytest.mark.parametrize("make", [_perpetua, _star])
def test_sighting_creates_edge_and_negates_the_others(make) -> None:
    m = make()
    m.update(_obs("a", 0))
    m.update(_obs("b", 2 * H))
    edges = m._edges["o"]
    assert set(edges) == {"a", "b"}
    # at t=2h edge a got y=0 and edge b got y=1
    assert edges["a"].times == [0.0, 2.0 * H] and edges["a"].ys == [True, False]
    assert edges["b"].times == [2.0 * H] and edges["b"].ys == [True]
    assert edges["b"].t0 == 2 * H


@pytest.mark.parametrize("make", [_perpetua, _star])
def test_sense_result_feeds_positive_and_negative_edges(make) -> None:
    m = make()
    m.reset(_context({"o": "mug", "p": "pen"}))
    m.update(_obs("a", 0))
    m.update(_obs("a", 0, obj="p"))
    m.update(_sense("a", H, contents=("p",)))        # o absent from a, p present
    m.update(_sense("c", 2 * H, contents=()))         # no edge (o, c): nothing fed
    assert m._edges["o"]["a"].ys == [True, False]
    assert m._edges["p"]["a"].ys == [True, True]
    assert "c" not in m._edges["o"]


@pytest.mark.parametrize("make", [_perpetua, _star])
def test_prediction_is_normalised_over_support(make) -> None:
    m = make()
    m.update(_obs("a", 0))
    m.update(_obs("b", 3 * H))
    m.update(_obs("a", 6 * H))
    pred = m.predict("o", 7 * H)
    assert set(pred.distribution) == {"a", "b"}
    assert sum(pred.distribution.values()) == pytest.approx(1.0)
    assert pred.argmax == "a"
    diag = m.last_prediction_diagnostics()
    assert diag is not None and 0.0 <= diag["max_edge_belief"] <= 1.0
    assert diag["n_edges"] == 2


@pytest.mark.parametrize("make", [_perpetua, _star])
def test_fresh_sighting_dominates(make) -> None:
    m = make()
    for k, (rec, t) in enumerate([("a", 0), ("b", 5), ("a", 9), ("b", 16),
                                  ("a", 19), ("b", 27)]):
        m.update(_obs(rec, t * H))
    m.update(_obs("c", 30 * H))
    pred = m.predict("o", 30 * H + 60)
    assert pred.argmax == "c"
    assert pred.distribution["c"] > 0.5


# --------------------------------------------------- exclusions

@pytest.mark.parametrize("make", [_perpetua, _star])
def test_exclusion_is_not_double_counted(make) -> None:
    # The base class would zero an excluded receptacle; here the sense
    # result reaches the filter as y=0 and the base machinery is bypassed:
    # the excluded receptacle keeps whatever the filter says (non-zero),
    # and the distribution is untouched by _apply_exclusions.
    m = make()
    m.update(_obs("a", 0))
    m.update(_obs("b", H))
    m.update(_obs("a", 2 * H))
    m.update(_sense("a", 3 * H))                       # o not in a at 3h
    assert m._active_exclusions("o") == {"a"}          # base recorded it ...
    pred = m.predict("o", 3 * H + 600)
    base = m._predict_for_object("o", m._history["o"], 3 * H + 600)
    assert pred.distribution == base.distribution      # ... but did not rezero
    assert pred.distribution["a"] > 0.0
    assert m._edges["o"]["a"].ys[-1] is False          # the filter saw the y=0


@pytest.mark.parametrize("make", [_perpetua, _star])
def test_negative_evidence_lowers_the_excluded_receptacle(make) -> None:
    m = make()
    m.update(_obs("a", 0))
    m.update(_obs("b", H))
    m.update(_obs("a", 2 * H))
    before = m.predict("o", 2 * H + 1800).distribution["a"]
    m.update(_sense("a", 2 * H + 1800))
    after = m.predict("o", 2 * H + 1801).distribution["a"]
    assert after < before


# --------------------------------------------------- fallbacks / misc

@pytest.mark.parametrize("make", [_perpetua, _star])
def test_never_observed_object_is_uniform(make) -> None:
    m = make()
    m.reset(_context({"o": "mug", "ghost": "sock"}))
    m.update(_obs("a", 0))
    pred = m.predict("ghost", H)
    assert set(pred.distribution) == set(RECS)
    assert all(p == pytest.approx(0.25) for p in pred.distribution.values())


@pytest.mark.parametrize("make", [_perpetua, _star])
def test_sighting_at_prediction_instant_short_circuits(make) -> None:
    m = make()
    m.update(_obs("a", 0))
    m.update(_obs("b", H))
    assert m.predict("o", H).distribution == {"b": 1.0}


@pytest.mark.parametrize("make", [_perpetua, _star])
def test_deterministic_and_rng_free(make) -> None:
    def run() -> tuple:
        m = make()
        rng_before = m._rng.getstate()
        stream = [_obs("a", 0), _obs("b", 2 * H), _sense("a", 3 * H),
                  _obs("a", 26 * H), _obs("b", 30 * H), _sense("b", 50 * H),
                  _obs("a", 52 * H)]
        for ev in stream:
            m.update(ev)
        preds = [m.predict("o", t).distribution for t in (53 * H, 60 * H, 100 * H)]
        assert m._rng.getstate() == rng_before
        return preds
    assert run() == run()


@pytest.mark.parametrize("make", [_perpetua, _star])
def test_fallback_then_fit_after_day_boundary(make) -> None:
    m = make(min_segments=2)
    # day 0: alternate a/b every 2 h -> plenty of completed segments
    for k in range(10):
        m.update(_obs("a" if k % 2 == 0 else "b", k * 2 * H))
    m.predict("o", 21 * H)
    assert all(e.any_fallback for e in m._edges["o"].values())
    m.update(_obs("a", DAY_SECONDS + H))              # first update of day 1: refit
    assert m.n_refits == 2
    edge = m._edges["o"]["a"]
    assert edge.n_persistence_segments >= 2 and not edge.pf_fallback
    m.predict("o", DAY_SECONDS + 2 * H)
    summary = m.fallback_summary()
    assert summary[0]["n_fallback_edge_beliefs"] == summary[0]["n_edge_beliefs"]
    assert summary[1]["n_fallback_edge_beliefs"] < summary[1]["n_edge_beliefs"]
    rows = m.edge_summary()
    assert {r["receptacle_id"] for r in rows} == {"a", "b"}


def test_perpetua_records_reset_events() -> None:
    m = _perpetua(fallback_median_h=1.0)
    for k in range(12):
        m.update(_obs("a" if k % 2 == 0 else "b", k * 3 * H))
    events = m.reset_events
    assert events and {e["direction"] for e in events} <= {"to_emergence",
                                                           "to_persistence"}
    assert all(e["object_id"] == "o" for e in events)


def test_perpetua_star_literal_variant_never_resets() -> None:
    m = _star(reset_mode="none", fallback_median_h=1.0)
    for k in range(12):
        m.update(_obs("a" if k % 2 == 0 else "b", k * 3 * H))
    assert m.reset_events == []
    assert "reset=none" in m.name
    m2 = _star(fallback_median_h=1.0)
    for k in range(12):
        m2.update(_obs("a" if k % 2 == 0 else "b", k * 3 * H))
    # the default rule resets at every observed flip of each edge
    assert len(m2.reset_events) >= 10
    assert "reset=" not in m2.name


def test_argmax_ties_prefer_last_sighted_then_lexicographic(monkeypatch) -> None:
    m = _star(switching_prior="flat")
    m.update(_obs("c", 0))
    m.update(_obs("b", H))
    m.update(_obs("a", H))
    monkeypatch.setattr(m, "_edge_belief", lambda edge, t: 0.3)   # exact tie
    pred = m.predict("o", 2 * H)
    assert all(p == pytest.approx(1 / 3) for p in pred.distribution.values())
    assert pred.argmax == "a"          # a and b share the newest sighting
    m._edges["o"]["b"].last_sighting_t = 2 * H - 1
    assert m.predict("o", 2 * H).argmax == "b"


# --------------------------------------------------- switching prior

def test_time_of_day_prior_is_the_timetable_share() -> None:
    m = _star()
    m.update(_obs("a", 8 * H))
    m.update(_obs("a", 8 * H + 600 + DAY_SECONDS))
    m.update(_obs("b", 8 * H + 1200 + 2 * DAY_SECONDS))
    m.update(_obs("b", 20 * H))
    t = 8 * H + 1800 + 2 * DAY_SECONDS            # 8h bin: a, a, b sightings
    counts = m._weighted_counts([(8 * H, "a"), (8 * H + 600 + DAY_SECONDS, "a"),
                                 (8 * H + 1200 + 2 * DAY_SECONDS, "b")], t, 24 * H)
    expected = (counts["a"] + 1) / (sum(counts.values()) + 2)
    assert m.switching_prior("o", "a", t) == pytest.approx(expected)
    assert m.switching_prior("o", "b", t) == pytest.approx(1 - expected)
    # empty bin: whole history
    t2 = 3 * H + 3 * DAY_SECONDS
    whole = m._weighted_counts(m._history["o"], t2, 24 * H)
    assert m.switching_prior("o", "a", t2) == pytest.approx(
        (whole["a"] + 1) / (sum(whole.values()) + 2))
    # a fresh edge's prior is not 1: the smoothing keeps it off the rails
    fresh = _star()
    fresh.update(_obs("a", 0))
    assert fresh.switching_prior("o", "a", 0) == pytest.approx(2 / 3)
    assert _star(switching_prior="flat").switching_prior("o", "a", 0) == 0.5


def test_fremen_prior_is_a_stub() -> None:
    with pytest.raises(NotImplementedError):
        PerpetuaStarConfig(switching_prior="fremen")


# --------------------------------------------------- registry

def test_registry_entries() -> None:
    for name in ("perpetua", "perpetua_star"):
        assert BELIEF_REGISTRY[name].panel == "candidate"
    names = [s["name"] for s in CANDIDATE_SLATE]
    assert names.count("perpetua") == 1 and names.count("perpetua_star") == 2
    built = [build_registered_belief(dict(s), random.Random(0))
             for s in CANDIDATE_SLATE if s["name"].startswith("perpetua")]
    display = [b.name.split("(")[0] for b in built]
    assert display == ["Perpetua", "PerpetuaStar", "PerpetuaStarFlat"]
    star = build_registered_belief({"name": "perpetua_star", "alpha0_per_h": 9.21,
                                    "family": "exponential"}, random.Random(0))
    assert "a0=9.21/h" in star.name and "exponential" in star.name


def test_config_validation() -> None:
    with pytest.raises(ValueError):
        PerpetuaConfig(p_m=0.0)
    with pytest.raises(ValueError):
        PerpetuaConfig(family="weibull")
    with pytest.raises(ValueError):
        PerpetuaBelief(random.Random(0), PerpetuaConfig(delta_low=0.9, delta_high=0.1))
    with pytest.raises(ValueError):
        PerpetuaStarConfig(gamma=1.5)
    assert math.isclose(pfl.single_component_prior("exponential", 3600.0)
                        .params["lambda_"][0], math.log(2) / 3600.0)


# --------------------------------------------------- analysis wiring

def test_diagnostics_reach_the_passive_evaluation_and_side_files(tmp_path) -> None:
    from baselines.bank import JsonlBank, write_gate_pass_bank
    from baselines.household_analysis import (_absence_rows, _perpetua_rows,
                                              ABSENCE_COLUMNS, EDGE_COLUMNS,
                                              FALLBACK_COLUMNS, RESET_COLUMNS,
                                              SIDE_FILES, truth_category)
    from baselines.household_report import perpetua_section
    from baselines.passive_eval import PassiveProtocolConfig, evaluate_continuous
    import csv
    import gzip

    path = tmp_path / "bank.jsonl"
    write_gate_pass_bank(path, seed=0)
    episode = next(iter(JsonlBank(path=path).episodes()))
    belief = PerpetuaStarBelief(random.Random(0), PerpetuaStarConfig(
        k_range=(1,), em_max_iter=10))
    scored = evaluate_continuous(episode, belief, PassiveProtocolConfig())
    assert scored and all(q.diagnostics is not None for q in scored)
    assert all(0.0 <= q.diagnostics["max_edge_belief"] <= 1.0 for q in scored)
    absence = _absence_rows(scored, episode, "hh", 0, "continuous")
    assert len(absence) == len(scored)
    assert all(len(r) == len(ABSENCE_COLUMNS) for r in absence)
    assert {r[10] for r in absence} <= {"ordinary receptacle", "out of house",
                                        "on a person"}
    assert truth_category("OUT_OF_HOUSE") == "out of house"
    assert truth_category("ON_PERSON_alice") == "on a person"
    side = _perpetua_rows(belief, "hh", 0)
    assert set(side) == {"resets", "edges", "fallback"}
    assert all(len(r) == len(RESET_COLUMNS) for r in side["resets"])
    assert all(len(r) == len(EDGE_COLUMNS) for r in side["edges"])
    assert all(len(r) == len(FALLBACK_COLUMNS) for r in side["fallback"])
    assert _perpetua_rows(object(), "hh", 0) == {}       # non-Perpetua model
    # the report section reads the side files back
    for key, rows in {"absence": absence, **side}.items():
        fname, columns = SIDE_FILES[key]
        with gzip.open(tmp_path / fname, "wt", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(columns)
            w.writerows(rows)
    section = perpetua_section(tmp_path)
    assert section is not None and "Absence signal" in section
    assert "PerpetuaStar" in section
    assert perpetua_section(tmp_path / "empty") is None


def test_perpetua_report_figures_render(tmp_path) -> None:
    """The two focused per-home figures draw from synthetic cells without
    touching a real run, and no-op when their models are absent."""
    from baselines.household_report import (AGE_ORDER, fig_perpetua_by_home,
                                            fig_perpetua_long_age_delta,
                                            models_in)

    models = ["LastObservation", "MostFrequentLocation(hl=24)", "Markov1(a=1)",
              "Perpetua(lognormal)", "PerpetuaStar(lognormal)",
              "PerpetuaStarFlat(lognormal)"]
    homes = {f"hh_{i:03d}": {"household_type": "working_professional_solo",
                             "residents": 1 + i % 3, "resident_group": "1",
                             "archetype": "a", "overlay": "o", "variant": "v",
                             "wave": 1, "tags": []} for i in range(1, 5)}
    rows = []
    for hh in homes:
        for seed in (0, 1):
            for model in models + ["routine_oracle"]:
                for i, age in enumerate(AGE_ORDER[:-1]):
                    rows.append({"household": hh, "seed": seed, "model": model,
                                 "mode": "continuous", "day": 7, "horizon": 0.0,
                                 "age_bin": age, "n": 40,
                                 "correct": 30 - i * 2 + len(model) % 5,
                                 "logloss": 1.0})
    ordered = models_in(rows)
    a = tmp_path / "by_home.png"
    b = tmp_path / "delta.png"
    fig_perpetua_by_home(rows, homes, ordered, a)
    fig_perpetua_long_age_delta(rows, homes, ordered, b)
    assert a.stat().st_size > 5000 and b.stat().st_size > 5000
    # without the survival models neither figure is drawn
    plain = [r for r in rows if "Perpetua" not in r["model"]]
    c = tmp_path / "none.png"
    fig_perpetua_by_home(plain, homes, models_in(plain), c)
    fig_perpetua_long_age_delta(plain, homes, models_in(plain), c)
    assert not c.exists()


def test_perpetua_cases_split_and_report(tmp_path, monkeypatch) -> None:
    """The four-case replay classifies every question, the tables guard
    small cells, and the figure and markdown are written."""
    import csv
    import gzip
    from baselines import perpetua_cases as pc
    from baselines.bank import write_gate_pass_bank

    path = tmp_path / "bank.jsonl"
    write_gate_pass_bank(path, seed=0)
    monkeypatch.setattr(pc, "bank_path", lambda h, s: path)
    rows = pc.replay_bank({"household": "hh_x", "seed": 0})
    assert rows and {r["age_bin"] for r in rows}
    assert all(r["answers"].keys() == {"last_observation", "most_frequent"}
               for r in rows)
    cases = {pc._case_of(r) for r in rows}
    assert cases <= {label for label, _, _ in pc.CASES}
    # fabricate a Perpetua correctness side file over the same questions
    with gzip.open(tmp_path / "absence_signal.csv.gz", "wt", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["household", "seed", "model", "mode", "question_id",
                    "age_bin", "correct"])
        for r in rows:
            w.writerow(["hh_x", 0, "PerpetuaStar(x)", "continuous", r["qid"],
                        r["age_bin"], int(r["answers"]["last_observation"] == r["truth"])])
    correct = pc.perpetua_correctness(tmp_path, [b for _, bins in pc.AGE_BLOCKS for b in bins])
    assert "PerpetuaStar" in correct
    meta = {"hh_x": {"residents": 1, "resident_group": "1"}}
    lines, cnt = pc.tabulate(rows, correct, meta, pc.LONG_AGES + ("[12h,24h)",))
    assert lines[0].startswith("| home |") and len(lines) == 3
    assert sum(c["n"] for c in cnt["hh_x"].values()) == sum(
        1 for r in rows if r["age_bin"] in pc.LONG_AGES + ("[12h,24h)",))
    pc.fig_cases_by_home(cnt, meta, tmp_path / "cases.png", "t")
    assert (tmp_path / "cases.png").stat().st_size > 5000
    # an empty counter set draws nothing
    pc.fig_cases_by_home({}, meta, tmp_path / "none.png", "t")
    assert not (tmp_path / "none.png").exists()
