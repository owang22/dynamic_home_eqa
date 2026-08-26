"""Tests for the viewer's belief traces.

The viewer draws "belief vs truth" straight from belief_trace.json, so the
file must agree with the belief models and with the bank exactly — a
plausible-looking but wrong trace would show a human a comparison the
harness never made.
"""
from __future__ import annotations

import json
import random

import pytest

from baselines.bank import (write_gate_pass_bank, write_periodic_probe_bank,
                            write_two_regime_bank)
from baselines.belief_trace import (DEFAULT_GRID_MINUTES, build_trace, _rle,
                                    resolve_specs, trace_one_model)
from baselines.cli import _derived_rng
from baselines.registry import build_registered_belief
from baselines.bank import JsonlBank
from baselines.types import DAY_SECONDS


def _seg_at(segments, minute):
    """The viewer's lookup rule (beliefs.js segAt), reimplemented here so
    the test checks what the page will actually read."""
    for segment in reversed(segments):
        if minute >= segment[0]:
            return segment
    return segments[0]


def test_rle_collapses_stable_runs_and_covers_the_timeline():
    samples = [(0, "a", 1.0), (15, "a", 0.9), (30, "b", 0.8), (45, "a", 0.7)]
    segments = _rle(samples, end_minute=60)
    assert segments == [[0, 30, "a", 1.0], [30, 45, "b", 0.8],
                        [45, 60, "a", 0.7]]
    # gapless and covering: every minute resolves to exactly one segment
    for minute in range(0, 60):
        assert _seg_at(segments, minute)[0] <= minute < _seg_at(segments, minute)[1]


def test_trace_matches_live_beliefs_at_every_grid_point(tmp_path):
    """The whole point: at every sampled moment, the traced argmax is what
    the model itself predicts under the same passive diet."""
    bank = write_gate_pass_bank(tmp_path / "bank.jsonl")
    episode = next(JsonlBank(path=bank.path).episodes())
    grid = DEFAULT_GRID_MINUTES
    for spec in resolve_specs(include_candidates=True):
        traced = trace_one_model(episode, dict(spec), seed=0,
                                 grid_minutes=grid)
        live = build_registered_belief(
            dict(spec),
            _derived_rng(0, "belief_trace", str(spec["name"]),
                         episode.episode_id))
        live.reset(episode.agent_view())
        for observation in episode.initial_observations:
            live.update(observation)
        cursor = 0
        scripted = episode.scripted_observations
        for minute in range(0, episode.n_days * 1440 + 1, grid):
            t = minute * 60
            while cursor < len(scripted) and scripted[cursor].t <= t:
                live.update(scripted[cursor])
                cursor += 1
            for object_id in episode.object_classes:
                assert (_seg_at(traced[object_id], minute)[2]
                        == live.predict_readonly(object_id, t).argmax), (
                    spec["name"], object_id, minute)


def test_trace_truth_matches_the_bank_exactly(tmp_path):
    bank = write_two_regime_bank(tmp_path / "regime.jsonl")
    episode = next(JsonlBank(path=bank.path).episodes())
    payload = build_trace(bank.path, seed=0, grid_minutes=60,
                          specs=resolve_specs(False))
    for object_id in payload["objects"]:
        for minute in range(0, payload["days"] * 1440, 60):
            assert (_seg_at(payload["truth"][object_id], minute)[2]
                    == episode.true_location(object_id, minute * 60))


def test_trace_is_passive_and_deterministic(tmp_path):
    """No sensing anywhere (a sense would add receptacles the passive diet
    never reveals), and two builds from one seed are byte-identical."""
    bank = write_periodic_probe_bank(tmp_path / "probe.jsonl")
    first = build_trace(bank.path, 0, 30, resolve_specs(True))
    second = build_trace(bank.path, 0, 30, resolve_specs(True))
    assert json.dumps(first, sort_keys=True) == json.dumps(second,
                                                           sort_keys=True)
    episode = next(JsonlBank(path=bank.path).episodes())
    sighted = {o.receptacle_id for o in
               (*episode.initial_observations, *episode.scripted_observations)}
    model = first["models"][0]          # last_observation: argmax IS a sighting
    seen = {segment[2] for segments in model["objects"].values()
            for segment in segments}
    assert seen <= sighted | set(episode.receptacle_ids)
    assert first["models"][0]["panel"] == "frozen"
    assert any(m["panel"] == "candidate" for m in first["models"])


def test_trace_payload_carries_what_the_viewer_needs(tmp_path):
    bank = write_gate_pass_bank(tmp_path / "bank.jsonl")
    payload = build_trace(bank.path, 0, DEFAULT_GRID_MINUTES,
                          resolve_specs(False))
    for key in ("household", "days", "grid_minutes", "objects",
                "receptacles", "truth", "models", "bank_manifest_hash",
                "seed", "object_classes"):
        assert key in payload, key
    assert set(payload["truth"]) == set(payload["objects"])
    for model in payload["models"]:
        assert set(model["objects"]) == set(payload["objects"])
        assert model["display"] and model["panel"] in ("frozen", "candidate")
        # every segment names a receptacle the viewer can place on the map
        for segments in model["objects"].values():
            for segment in segments:
                assert segment[2] in payload["receptacles"]


def test_multi_episode_bank_is_refused(tmp_path):
    """One household per trace: the viewer maps one floor plan."""
    bank = write_gate_pass_bank(tmp_path / "one.jsonl")
    doubled = tmp_path / "two.jsonl"
    text = bank.path.read_text()
    doubled.write_text(text + text.replace("gate_pass_ep0", "gate_pass_ep1"))
    with pytest.raises(ValueError, match="exactly one episode"):
        build_trace(doubled, 0, 60, resolve_specs(False))
