"""
M3 smoke test: all eight policies run end-to-end on one scene, one day, ten
MCQ questions, producing a replay log and a results CSV. Smoke only — this
checks the whole pipeline executes and produces sane-shaped output, not
that any policy is "good" (that's the experiment sweep, M4+).

Requires habitat_sim — skipped when unavailable.
"""
from __future__ import annotations

import csv
import json
import pathlib

import pytest

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"
_REAL_SCENE = "102343992"
_N_QUESTIONS = 10


def _has_habitat_sim() -> bool:
    try:
        import habitat_sim  # noqa: F401
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(
    not _has_habitat_sim(), reason="habitat_sim not installed in this environment"
)


def _dynamic_labels(manifest: dict) -> list[str]:
    """Labels that actually moved at least once (have a real change event)
    — world.current_instances() also returns never-moved Tier 1/2a
    furniture-adjacent objects (e.g. potted plants), and dict iteration
    order happening to front-load one such category swamped an earlier
    version of this test's signal entirely."""
    return sorted({c["label"] for c in manifest["changes"]})


@pytest.fixture(scope="module")
def real_day():
    result = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    return result, manifest


@pytest.fixture(scope="module")
def decay_models(real_day):
    from dynamic_home_eqa.embodied.belief import fit_decay_models
    from dynamic_home_eqa.generation.exports import category_location_change_stats

    _, manifest = real_day
    stats = category_location_change_stats(manifest["changes"])
    return fit_decay_models(stats)


def _all_policies():
    from dynamic_home_eqa.embodied.policy import (
        AlwaysResense,
        AnswerImmediately,
        CoverageStop,
        DecayThreshold,
        DecayVoi,
        DecayVoiRouting,
        RandomResense,
        RandomResenseConfig,
        TimeOnlyThreshold,
    )
    return {
        "answer_immediately":    AnswerImmediately(),
        "always_resense":        AlwaysResense(),
        "coverage_stop":         CoverageStop(),
        "decay_threshold":       DecayThreshold(),
        "decay_voi":             DecayVoi(),
        "decay_voi_routing":     DecayVoiRouting(),
        "budget_matched_random": RandomResense(RandomResenseConfig(p_resense=0.12, seed=0)),
        "time_only_threshold":   TimeOnlyThreshold(),
    }


def test_all_eight_policies_run_end_to_end_and_produce_a_results_csv(real_day, decay_models, tmp_path):
    from dynamic_home_eqa.embodied.belief import BeliefStore
    from dynamic_home_eqa.embodied.question import (
        categories_ever_outdoor,
        category_anchor_history,
        generate_mcq_question,
    )
    from dynamic_home_eqa.embodied.runner import EpisodeConfig, QuestionEpisodeRunner
    from dynamic_home_eqa.embodied.world import EmbodiedWorld

    result, manifest = real_day
    csv_rows: list[dict] = []

    policies = _all_policies()
    assert len(policies) == 8

    anchor_history = category_anchor_history([manifest])
    outdoor_categories = categories_ever_outdoor([manifest])
    dynamic_labels = _dynamic_labels(manifest)[:_N_QUESTIONS]

    for policy_name, policy in policies.items():
        world = EmbodiedWorld(_REAL_SCENE, result, manifest)
        belief = BeliefStore(decay_models=decay_models)
        try:
            runner = QuestionEpisodeRunner(world, belief, policy, EpisodeConfig(patrol_start=6.0, wait_hours=0.5))
            runner.patrol()

            instances = world.current_instances()
            labels = [l for l in dynamic_labels if l in instances]
            assert labels, "fixture scene must have at least one trackable dynamic instance after patrol"

            for label in labels:
                category, _slot = instances[label]

                runner.dock_and_wait()
                question = generate_mcq_question(
                    label=label, category=category, asked_t=world.t,
                    initial_state=world.initial_state, changes=world.changes,
                    anchor_history=anchor_history, outdoor_categories=outdoor_categories,
                    decay_models=decay_models,
                )
                episode = runner.run_question(question)

                assert episode.correct in (True, False, None)
                assert isinstance(episode.abstained, bool)
                assert 0.0 <= episode.brier <= 1.0
                assert episode.answer_latency_s >= 0.0
                assert episode.distance_traveled_m >= 0.0
                assert episode.policy_invocations >= 1
                assert episode.log  # non-empty replay log

                csv_rows.append({
                    "policy": policy_name,
                    "label": label,
                    "category": category,
                    "hazard_class": question.hazard_class,
                    "n_options": len(question.options),
                    "correct": episode.correct,
                    "abstained": episode.abstained,
                    "confidence": episode.confidence,
                    "brier": episode.brier,
                    "answer_latency_s": episode.answer_latency_s,
                    "distance_traveled_m": episode.distance_traveled_m,
                    "policy_invocations": episode.policy_invocations,
                })
        finally:
            world.close()

    assert len(csv_rows) > 0
    assert len(csv_rows) % 8 == 0  # same question count asked under every policy

    out_csv = tmp_path / "results.csv"
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    assert out_csv.exists()
    written = list(csv.DictReader(open(out_csv)))
    assert len(written) == len(csv_rows)
    assert {row["policy"] for row in written} == set(policies.keys())
