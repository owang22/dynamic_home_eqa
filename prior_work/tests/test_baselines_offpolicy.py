"""Tests for the confound-killing machinery: full-state scoring, off-policy
replay, offline metric reload, and the query-mode axis of the exporter."""

from __future__ import annotations

import json
import pathlib

import pytest

from baselines.bank import write_synthetic_bank
from baselines.cli import build_agent
from baselines.harness import run_episode
from baselines.metrics import aggregate, load_run_log
from baselines.replay import replay_stream


def test_full_state_snapshot_present_and_consistent(
        tmp_path: pathlib.Path) -> None:
    bank = write_synthetic_bank(tmp_path / "bank.jsonl")
    episode = next(bank.episodes())
    agent = build_agent({"name": "last_observation"},
                        {"name": "sequential_search"}, seed=0,
                        episode_id=episode.episode_id)
    for r in run_episode(agent, episode):
        # Snapshot covers every object, accuracy is its mean, and the
        # queried object's snapshot agrees with the recorded answer.
        assert set(r.belief_state) == set(episode.object_classes)
        oks = [ok for _, _, ok in r.belief_state.values()]
        assert r.belief_accuracy == pytest.approx(sum(oks) / len(oks))
        cls, guess, ok = r.belief_state[r.object_id]
        assert guess == r.answer_receptacle
        assert ok == r.correct
        assert cls == r.object_class


def test_replay_diagonal_reproduces_live_belief_accuracy(
        tmp_path: pathlib.Path) -> None:
    # Replaying an agent's own stream through its own belief spec (same
    # derived seed, same generator-consumption pattern) must reproduce the
    # live run's mean belief accuracy — the identity that certifies the
    # reconstruction is faithful.
    bank = write_synthetic_bank(tmp_path / "bank.jsonl")
    episode = next(bank.episodes())
    seed = 5
    spec = {"name": "last_observation"}
    agent = build_agent(spec, {"name": "sequential_search"}, seed=seed,
                        episode_id=episode.episode_id)
    records = [r.to_json_dict() for r in run_episode(agent, episode)]
    live = sum(float(str(r["belief_accuracy"])) for r in records) / len(records)
    replayed = replay_stream(episode, records, spec, seed, agent.name)
    assert replayed == pytest.approx(live)


def test_metrics_recompute_offline_from_run_log(
        tmp_path: pathlib.Path) -> None:
    # belief_accuracy is a post-hoc metric: reloading the JSONL run log
    # must aggregate to the exact numbers the live records gave.
    bank = write_synthetic_bank(tmp_path / "bank.jsonl")
    episode = next(bank.episodes())
    agent = build_agent({"name": "most_frequent"},
                        {"name": "sequential_search"}, seed=0,
                        episode_id=episode.episode_id)
    records = list(run_episode(agent, episode))
    log_path = tmp_path / "run_log.jsonl"
    with open(log_path, "w") as f:
        for r in records:
            f.write(json.dumps(r.to_json_dict()) + "\n")
    live = aggregate(records, budget_per_day=episode.budget_per_day)
    reloaded = aggregate(load_run_log(log_path),
                         budget_per_day=episode.budget_per_day)
    assert reloaded == live


def test_naturalistic_export_is_deterministic_and_biased(
        tmp_path: pathlib.Path) -> None:
    from baselines.export_bank import export

    # A tiny timeline stub: hourly.csv + events.jsonl in the shape the
    # exporter reads (times in minutes), plus a minimal spec/profile pair.
    timeline = tmp_path / "timeline"
    timeline.mkdir()
    (timeline / "hourly.csv").write_text(
        "t,stamp,obj_a,obj_b\n" + "\n".join(
            f"{h * 60},d{h // 24:02d} Mon {h % 24:02d}:00,rec_1,rec_2"
            for h in range(14 * 24)) + "\n")
    events = [{"t": d * 1440 + 600, "object": "obj_a", "from": "rec_1",
               "to": "rec_2", "by": "activity:x"} for d in range(14)]
    (timeline / "events.jsonl").write_text(
        "\n".join(json.dumps(e) for e in events) + "\n")
    spec = tmp_path / "spec.yaml"
    spec.write_text(
        "household: hh_test\n"
        "source_profile: profile.yaml\n"
        "receptacles:\n  - {id: rec_1, room: a}\n  - {id: rec_2, room: b}\n")
    (tmp_path / "profile.yaml").write_text(
        "object_inventory:\n"
        "  - {id: obj_a, class: mug}\n  - {id: obj_b, class: keys}\n")

    banks = [export(timeline, spec, tmp_path / f"bank{i}.jsonl", seed=3,
                    sightings_per_day=2, questions_per_day=30,
                    first_question_day=2, budget_per_day=2,
                    query_mode="naturalistic") for i in range(2)]
    # Determinism: same seed -> byte-identical banks.
    assert (tmp_path / "bank0.jsonl").read_bytes() == \
           (tmp_path / "bank1.jsonl").read_bytes()
    # Popularity bias: obj_a has truth weight 2 (it moves), obj_b weight 1,
    # so naturalistic questions target obj_a ~2/3 of the time (repeat bias
    # keeps the marginal near that). With n=360 draws, sigma ~ 0.025;
    # requiring > 0.55 leaves a ~4-sigma margin against flakiness while
    # cleanly rejecting the uniform 0.5 split.
    episode = next(banks[0].episodes())
    questions = [q for day in episode.questions_by_day for q in day]
    share_a = sum(q.object_id == "obj_a" for q in questions) / len(questions)
    assert share_a > 0.55

    # Uniform mode draws without replacement (daily pools): with 2 objects
    # and 30 questions/day every object is asked exactly 15 times per day —
    # the repeat lottery that plagued with-replacement draws cannot happen.
    uniform = export(timeline, spec, tmp_path / "bank_u.jsonl", seed=3,
                     sightings_per_day=2, questions_per_day=30,
                     first_question_day=2, budget_per_day=2,
                     query_mode="uniform")
    for day in next(uniform.episodes()).questions_by_day:
        if not day:
            continue
        counts = {"obj_a": 0, "obj_b": 0}
        for q in day:
            counts[q.object_id] += 1
        assert counts == {"obj_a": 15, "obj_b": 15}
