"""Tests for the viewer's belief traces.

The viewer draws "belief vs truth" straight from belief_trace.json, so the
file must agree with the belief models and with the bank exactly — a
plausible-looking but wrong trace would show a human a comparison the
harness never made.
"""
from __future__ import annotations

import dataclasses
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


def test_sighting_stream_is_the_passive_evidence_in_time_order(tmp_path):
    """The viewer's "last seen" readout and its strip ticks read this, so
    it must be exactly the diet the models consumed — tour included, no
    sense results, sorted, and never missing an object."""
    bank = write_periodic_probe_bank(tmp_path / "probe.jsonl")
    episode = next(JsonlBank(path=bank.path).episodes())
    payload = build_trace(bank.path, 0, 60, resolve_specs(False))
    stream = payload["sightings"]

    assert set(stream) == set(episode.object_classes)
    expected = (len(episode.initial_observations)
                + len(episode.scripted_observations))
    assert sum(len(v) for v in stream.values()) == expected
    for object_id, entries in stream.items():
        assert [e[0] for e in entries] == sorted(e[0] for e in entries)
        for minute, receptacle in entries:
            # Every sighting is truthful: the bank never reports an object
            # anywhere but where it actually was.
            assert episode.true_location(object_id, minute * 60) == receptacle

    def last_seen(object_id, minute):
        seen = [e for e in stream[object_id] if e[0] <= minute]
        return seen[-1] if seen else None

    badge = "badge_shift"
    assert last_seen(badge, 0)[1] == "entry_e"          # the initial tour
    # Sighted at 10:00 (desk) and 20:00 (entry) daily, so at noon on day 5
    # the freshest sighting is that morning's desk look.
    assert last_seen(badge, 5 * 1440 + 12 * 60) == [5 * 1440 + 10 * 60,
                                                    "desk_d"]
    assert last_seen(badge, 5 * 1440 + 21 * 60) == [5 * 1440 + 20 * 60,
                                                    "entry_e"]


def test_last_seen_never_runs_ahead_of_the_belief(tmp_path):
    """LastObservation predicts precisely the last-sighted receptacle, so
    the viewer's "last seen" row and its belief ring must agree at EVERY
    grid point. This is the sharp end of rounding sighting seconds to
    minutes: flooring made the readout advertise a sighting one grid step
    before the models could act on it, and the page showed a "last seen"
    that contradicted the belief beside it.
    """
    bank = write_gate_pass_bank(tmp_path / "bank.jsonl")
    grid = DEFAULT_GRID_MINUTES
    payload = build_trace(bank.path, 0, grid, resolve_specs(False))
    last_obs = next(m for m in payload["models"]
                    if m["name"] == "last_observation")
    checked = 0
    for object_id in payload["objects"]:
        seen = payload["sightings"][object_id]
        for minute in range(0, payload["days"] * 1440 + 1, grid):
            before = [e for e in seen if e[0] <= minute]
            if not before:
                continue          # never-sighted: belief is the uniform fallback
            assert _seg_at(last_obs["objects"][object_id], minute)[2] == \
                before[-1][1], (object_id, minute)
            checked += 1
    assert checked > 1000, "fixture too small to be evidence"


def test_sighting_minutes_round_up_from_seconds(tmp_path):
    """The synthetic fixtures all sight on whole minutes, so the agreement
    test above cannot see the rounding direction — real banks draw
    sightings at arbitrary seconds. Pin it directly: a sighting at
    12 345 s must publish as minute 206 (ceil), not 205 (floor), because a
    belief sampled at minute 205 (t = 12 300 s) has NOT yet consumed it.
    """
    from baselines.belief_trace import sighting_stream
    from baselines.types import Observation

    bank = write_periodic_probe_bank(tmp_path / "probe.jsonl")
    episode = next(JsonlBank(path=bank.path).episodes())
    offset = Observation(object_id="mug_static", object_class="mug",
                         receptacle_id="desk_d", t=12_345, source="scripted")
    episode = dataclasses.replace(
        episode,
        scripted_observations=tuple(
            sorted((*episode.scripted_observations, offset),
                   key=lambda o: o.t)))
    minutes = [m for m, _ in sighting_stream(episode)["mug_static"]]
    assert 206 in minutes and 205 not in minutes


def test_sighting_stream_covers_every_object(tmp_path):
    """An object nobody ever sees still gets a key, so the viewer can say
    'never seen yet' without a missing-key check."""
    bank = write_gate_pass_bank(tmp_path / "bank.jsonl")
    payload = build_trace(bank.path, 0, 120, resolve_specs(False))
    assert set(payload["sightings"]) == set(payload["objects"])
    assert all(isinstance(v, list) for v in payload["sightings"].values())


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
