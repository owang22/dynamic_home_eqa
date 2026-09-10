

# ---------------------------------------------------------- forgetting

def test_half_life_ages_every_factor() -> None:
    model = OracleProgramPosterior(random.Random(0), _ensemble(), eps=0.5,
                                   half_life_h=2.0, floor_mass=0.0)
    model.reset(_context())
    model.update(Observation(object_id="o", object_class="mug",
                             receptacle_id="b", t=11 * H, source="scripted"))
    # Seeds 0, 1 disagree: log-weight log(0.5); one half-life later, half.
    model.predict("o", 13 * H)
    w = model.weights()
    assert w[0] / w[2] == pytest.approx(0.5 ** 0.5)
    # An earlier query never un-ages the weights.
    model.predict("o", 12 * H)
    w = model.weights()
    assert w[0] / w[2] == pytest.approx(0.5 ** 0.5)
    # Many half-lives on, the factor is gone: ESS back to the seed count.
    model.predict("o", 40 * H)
    assert model.effective_sample_size() == pytest.approx(3.0, abs=1e-3)
    # Aging happens at observations too: a second disagreement a
    # half-life after the first counts log(0.5) * (1 + 1/2).
    fresh = OracleProgramPosterior(random.Random(0), _ensemble(), eps=0.5,
                                   half_life_h=2.0, floor_mass=0.0)
    fresh.reset(_context())
    for t in (11 * H, 13 * H):
        fresh.update(Observation(object_id="o", object_class="mug",
                                 receptacle_id="b", t=t, source="scripted"))
    w = fresh.weights()
    assert w[0] / w[2] == pytest.approx(0.5 ** 1.5)


def test_no_half_life_never_forgets() -> None:
    model = _model(eps=0.5)
    model.update(Observation(object_id="o", object_class="mug",
                             receptacle_id="b", t=11 * H, source="scripted"))
    model.predict("o", 40 * H)
    w = model.weights()
    assert w[0] / w[2] == pytest.approx(0.5)
    assert model.half_life_h is None


def test_half_life_in_name_and_validated() -> None:
    assert _model().name == "OracleBelief(eps=0.05)"
    model = OracleProgramPosterior(random.Random(0), _ensemble(), eps=0.3,
                                   half_life_h=24.0)
    assert model.name == "OracleBelief(eps=0.3,hl=24h)"
    assert model.half_life_h == 24.0
    with pytest.raises(ValueError, match="half_life_h"):
        OracleProgramPosterior(random.Random(0), _ensemble(), half_life_h=0.0)


def test_registry_passes_the_knobs() -> None:
    from baselines.registry import build_registered_belief

    model = build_registered_belief(
        {"name": "oracle_program_posterior", "ensemble": _ensemble(),
         "eps": 0.3, "half_life_h": 24}, random.Random(0))
    assert isinstance(model, OracleProgramPosterior)
    assert model.eps == 0.3 and model.half_life_h == 24.0
    plain = build_registered_belief(
        {"name": "oracle_program_posterior", "ensemble": _ensemble()},
        random.Random(0))
    assert isinstance(plain, OracleProgramPosterior)
    assert plain.eps == DEFAULT_EPS and plain.half_life_h is None


def test_study_config_and_selection() -> None:
    from baselines.oracle_posterior_study import (ESS_STOP, OracleConfig,
                                                  select_config)

    cfg = OracleConfig(0.3, 24.0)
    assert cfg.slug == "eps0.3__hl24h"
    assert OracleConfig.from_json(cfg.to_json()) == cfg
    assert OracleConfig(0.05, None).slug == "eps0.05__hlnone"
    assert cfg.spec()["half_life_h"] == 24.0
    assert cfg.spec()["name"] == "oracle_program_posterior"

    def row(config: str, subset: str, ess: float, acc: float) -> dict:
        return {"config": config, "subset": subset, "median_ess": ess,
                "accuracy": acc, "eligible": int(ess >= ESS_STOP)}

    table = [row("a", "calibration", 1.0, 0.9), row("a", "test", 1.0, 0.9),
             row("b", "calibration", 6.0, 0.7), row("b", "test", 6.0, 0.95),
             row("c", "calibration", 9.0, 0.7), row("c", "test", 9.0, 0.5)]
    # Degenerate 'a' is out however accurate; the tie between b and c on
    # calibration accuracy goes to the larger ESS; test rows never count.
    chosen = select_config(table)
    assert chosen is not None and chosen["config"] == "c"
    assert select_config([row("a", "calibration", 1.0, 0.9)]) is None
