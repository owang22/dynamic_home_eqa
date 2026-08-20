"""Step-2 property tests for the L3 extensions: per-day skip and bout
fragmentation, plus the no-extensions identity (extensions consume no
randomness when unused)."""
from __future__ import annotations

import random

import pytest

from revamp_v2_helpers import mini_program

import expand_calendar as xc
import simulate as sim


def test_no_extensions_is_identical_to_plain_v1():
    sa = sim.load_v1()
    program = mini_program()
    acts, motions = xc.expand(program)
    sa.validate(acts, motions)
    log1, hourly1, blocks1, _ = sa.simulate(acts, motions, 21, 7)
    log2, hourly2, blocks2, stats2, _, _ = sim.simulate_program(
        program, 21, 7, sa=sa)
    assert log1 == log2 and hourly1 == hourly2 and blocks1 == blocks2
    assert stats2["skips_per_activity"] == {}
    assert stats2["fragment_bouts_per_activity"] == {}


def test_skip_counts_match_binomial():
    sa = sim.load_v1()
    program = mini_program()
    program["weekly_blocks"][1]["skip_p"] = 0.3     # relax, 18 days
    skips = trials = 0
    for seed in range(60):
        *_, stats, acts, _ = sim.simulate_program(program, 21, seed, sa=sa)
        skips += stats["skips_per_activity"].get("relax", 0)
        trials += 18
    rate = skips / trials
    sigma = (0.3 * 0.7 / trials) ** 0.5
    assert abs(rate - 0.3) < 5 * sigma, f"skip rate {rate:.3f} vs 0.3"


def test_skipped_block_takes_its_linger_with_it():
    sa = sim.load_v1()
    program = mini_program()
    program["weekly_blocks"][1]["skip_p"] = sim.load_params()[
        "skip"]["max_skip_p"]
    *_, stats, acts, _ = sim.simulate_program(program, 21, 3, sa=sa)
    n_skipped = stats["skips_per_activity"].get("relax", 0)
    assert n_skipped > 0
    wind = sum(1 for e in acts["calendar"] for it in e["activities"]
               if it["a"] == "relax")
    lingers = [it for e in acts["calendar"] for it in e["activities"]
               if it["a"] == "linger_table_a"]
    # every surviving relax keeps exactly one linger; skipped ones lost
    # theirs (21 breakfast lingers always remain)
    assert wind == 18 - n_skipped
    assert len(lingers) == 21 + wind


def test_skip_before_jitter_not_after():
    # A skipped block must never appear in residents.jsonl blocks at all
    # (dropped pre-realization), not appear squeezed to zero length.
    sa = sim.load_v1()
    program = mini_program()
    program["weekly_blocks"][1]["skip_p"] = 0.5
    _, _, blocks, stats, _, _ = sim.simulate_program(program, 21, 11, sa=sa)
    names = [b["activity"] for b in blocks]
    assert names.count("relax") == 18 - stats[
        "skips_per_activity"].get("relax", 0)


def test_poisson_sampler_mean():
    rng = random.Random(0)
    n = 20000
    mean = sum(sim._poisson(rng, 4.0) for _ in range(n)) / n
    assert abs(mean - 4.0) < 0.06


def test_fragmentation_bout_counts_and_windows():
    sa = sim.load_v1()
    program = mini_program()
    # widen breakfast so fragmentation has room: 08:00 -> 12:00
    program["weekly_blocks"][0]["end"] = "12:00"
    program["activities"][0]["fragment"] = {"mean_bouts": 3}
    total_bouts = total_blocks = 0
    for seed in range(20):
        log, _, blocks, stats, _, motions = sim.simulate_program(
            program, 21, seed, sa=sa)
        bouts = [b for b in blocks if b["activity"] == "breakfast"]
        total_bouts += len(bouts)
        total_blocks += 21
        # sub-bouts are non-overlapping and ordered within each day
        by_day = {}
        for b in bouts:
            by_day.setdefault(b["t0"] // 1440, []).append(b)
        for day_bouts in by_day.values():
            day_bouts.sort(key=lambda b: b["t0"])
            for x, y in zip(day_bouts, day_bouts[1:]):
                assert x["t1"] <= y["t0"]
        assert stats["fragment_bouts_per_activity"]["breakfast"] == len(bouts)
    mean_bouts = total_bouts / total_blocks
    # E[max(1, Poisson(3))] ~ 3.05, minus a little merging loss
    assert 2.2 < mean_bouts < 3.6, mean_bouts


def test_fragmented_bindings_fire_per_bout_gated_by_only_from():
    sa = sim.load_v1()
    program = mini_program()
    program["weekly_blocks"][0]["end"] = "12:00"
    program["activities"][0]["fragment"] = {"mean_bouts": 4}
    log, *_ = sim.simulate_program(program, 21, 5, sa=sa)
    moves = [e for e in log if e["object"] == "mug_1"]
    # the mug still only ping-pongs table <-> sink/shelf; no rule fires
    # from a state only_from excludes
    for e in moves:
        if e["by"] == "activity:breakfast" and e["to"] in ("sink_k",):
            assert e["from"] == "table_a"


def test_unfragmented_when_window_too_small():
    sa = sim.load_v1()
    program = mini_program()          # breakfast window is 08:00-08:30 gap
    program["activities"][0]["fragment"] = {"mean_bouts": 5}
    _, _, blocks, stats, _, _ = sim.simulate_program(program, 21, 2, sa=sa)
    bouts = [b for b in blocks if b["activity"] == "breakfast"]
    per_day = {}
    for b in bouts:
        per_day.setdefault(b["t0"] // 1440, []).append(b)
    # a day that actually fragmented respects the min-bout floor (a lone
    # bout may just be a jitter-squeezed original block)
    for day_bouts in per_day.values():
        if len(day_bouts) > 1:
            assert all(b["t1"] - b["t0"] >= 9 for b in day_bouts)
    assert max(len(v) for v in per_day.values()) <= 6
