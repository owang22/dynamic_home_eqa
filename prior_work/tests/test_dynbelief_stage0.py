"""Stage 0 cross-cutting tests (brief: ReplayWorld reconstruction, parent
invariant, belief-tier update math, oracle occlusion against proxies,
schedule/runner determinism)."""
from __future__ import annotations

import json
import math

import numpy as np
import pytest

from dynbelief import ELSEWHERE_ID, MIN_PER_DAY
from dynbelief.beliefs.base import object_class, shannon
from dynbelief.beliefs.fremen import SwitchingPrior, constant_prior, fremen_prior
from dynbelief.beliefs.perpetua import B3PerpetuaStar
from dynbelief.beliefs.zoo import B0LastSeen, B1LongMem, B2ClassDecay


# ── synthetic episode written through the real logger format ────────────────

@pytest.fixture()
def episode(tmp_path):
    """Hand-built 2-day episode in the exact log format: 2 objects, 3
    receptacles (+elsewhere), one within-day move, one day-boundary reset."""
    reg = {
        "scene_id": "synthetic", "n_days": 2, "folders": ["d0", "d1"],
        "objects": {"bowl_1": 0, "mia_phone": 1},
        "receptacles": {"elsewhere": 0, "kitchen.counter_1": 1,
                        "kitchen.table_1": 2, "bedroom_1.bed_1": 3},
        "receptacle_meta": {
            "0": {"label": "elsewhere", "room": None, "position": None},
            "1": {"label": "kitchen.counter_1", "room": "kitchen",
                  "position": [0.0, 0.0, 0.0]},
            "2": {"label": "kitchen.table_1", "room": "kitchen",
                  "position": [1.0, 0.0, 0.0]},
            "3": {"label": "bedroom_1.bed_1", "room": "bedroom_1",
                  "position": [5.0, 0.0, 0.0]},
        },
        "elsewhere_id": 0,
    }
    (tmp_path / "registry.json").write_text(json.dumps(reg))
    (tmp_path / "snapshot_day0.json").write_text(json.dumps(
        {"t_min": 0, "day": 0, "parents": {"0": 1, "1": 3}, "states": {}}))
    # day 0: bowl moves counter->table at 480; phone bed->table at 600
    # day 1 starts with both reset to day-0 start (independent days)
    (tmp_path / "snapshot_day1.json").write_text(json.dumps(
        {"t_min": MIN_PER_DAY, "day": 1, "parents": {"0": 1, "1": 3},
         "states": {}}))
    events = [
        {"t_min": 480, "object_id": 0, "parent_id": 2, "states": {}, "moved_by": "human"},
        {"t_min": 600, "object_id": 1, "parent_id": 2, "states": {}, "moved_by": "human"},
        {"t_min": MIN_PER_DAY, "object_id": 0, "parent_id": 1, "states": {}, "moved_by": "init"},
        {"t_min": MIN_PER_DAY, "object_id": 1, "parent_id": 3, "states": {}, "moved_by": "init"},
        {"t_min": MIN_PER_DAY + 500, "object_id": 0, "parent_id": 2, "states": {}, "moved_by": "human"},
    ]
    with open(tmp_path / "events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    return tmp_path


def test_replay_reconstruction_matches_snapshots(episode):
    """Event replay from day-0 must equal the day-1 snapshot at its boundary
    (the logger's init-event contract)."""
    from dynbelief.replay import ReplayWorld
    w = ReplayWorld(episode)
    at_boundary = {o: p for o, (p, _) in w.state_at(MIN_PER_DAY).items()}
    snap = json.loads((episode / "snapshot_day1.json").read_text())
    assert at_boundary == {int(k): v for k, v in snap["parents"].items()}


def test_replay_state_and_parent_invariant(episode):
    from dynbelief.replay import ReplayWorld
    w = ReplayWorld(episode)
    assert w.true_parent(0, 0) == 1
    assert w.true_parent(0, 480) == 2       # inclusive of the event minute
    assert w.true_parent(0, 479) == 1
    assert w.true_parent(1, 700) == 2
    assert w.true_parent(0, MIN_PER_DAY + 600) == 2
    for t in (0, 100, 480, 900, MIN_PER_DAY + 10):
        state = w.state_at(t)
        assert set(state) == {0, 1}          # exactly one parent per object
        for _, (p, _s) in state.items():
            assert isinstance(p, int)


# ── belief tiers ─────────────────────────────────────────────────────────────

def _mk(model):
    model.reset([0], [0, 1, 2, 3], t0=0)
    return model


def test_b0_last_seen():
    b = _mk(B0LastSeen())
    assert np.allclose(b.predict(0)[0], 0.25)  # uniform before any obs
    b.observe(10, {0: (2, {})})
    assert b.predict(500)[0][2] == 1.0


def test_b1_longmem_frequency():
    b = _mk(B1LongMem())
    for t, p in [(0, 1), (10, 1), (20, 2)]:
        b.observe(t, {0: (p, {})})
    d = b.predict(30)[0]
    assert d[1] > d[2] > d[3]


def test_b2_decays_toward_class_prior():
    b = _mk(B2ClassDecay({0: "bowl"}))
    # training: object seen at 1 then 2 (a change over 100 min) -> lambda > 0
    b.observe(0, {0: (1, {})})
    b.observe(100, {0: (2, {})})
    d_soon = b.predict(101)[0]
    d_late = b.predict(2000)[0]
    assert d_soon[2] > d_late[2]             # confidence in last-seen decays
    assert d_late[1] > 0.1                   # mass flows to class prior


def test_b3_pure_persistence_special_case():
    """f = 0 (single component, no switching): posterior frozen at the last
    observation forever."""
    zero_f = SwitchingPrior(np.full(MIN_PER_DAY, 1e-4))  # floor -> ~0
    zero_f.per_min = np.zeros(MIN_PER_DAY)
    zero_f._cum = np.zeros(MIN_PER_DAY + 1)
    b = B3PerpetuaStar({0: "bowl"}, zero_f)
    b.reset([0], [0, 1, 2, 3], 0)
    b.observe(10, {0: (2, {})})
    d = b.predict(10 + 3 * MIN_PER_DAY)[0]
    assert d[2] == pytest.approx(1.0)
    assert d[0] == pytest.approx(0.0)


def test_b3_two_observation_hand_case():
    """Constant f=1; rates learned from one on->off pair, then closed form
    p(t) = p_eq + (p0 - p_eq) e^{-(mu+eta) dt} checked by hand."""
    b = B3PerpetuaStar({0: "bowl"}, constant_prior())
    b.reset([0], [0, 1, 2], 0)
    b.observe(0, {0: (1, {})})
    b.observe(100, {0: (2, {})})   # left receptacle 1, entered 2
    mu, eta = b._edge_rates(0, 1)
    p_eq = eta / (mu + eta)
    dt = 50
    expect = p_eq + (0.0 - p_eq) * math.exp(-(mu + eta) * dt)  # anchored at 0
    d = b.predict(150)[0]
    assert d[1] == pytest.approx(expect, rel=1e-6)
    assert 0.0 <= d[0] <= 1.0 and abs(d.sum() - 1.0) < 1e-9


def test_b3_elsewhere_mass_reserved():
    b = B3PerpetuaStar({0: "bowl"}, constant_prior())
    b.reset([0], [0, 1, 2], 0)
    b.observe(0, {0: (1, {})})
    d = b.predict(0)[0]
    assert d[1] == pytest.approx(1.0) and d[0] == pytest.approx(0.0)
    d2 = b.predict(5000)[0]
    assert abs(d2.sum() - 1.0) < 1e-9 and d2[0] > 0.0  # leaked mass -> elsewhere


def test_fremen_recovers_periodicity():
    times = [d * MIN_PER_DAY + m for d in range(5) for m in (480, 481, 900)]
    f = fremen_prior(times, top_k=3)
    assert f(480) > f(200)
    assert abs(np.mean([f(t) for t in range(0, MIN_PER_DAY, 7)]) - 1.0) < 0.05
    assert f.cumulative(0, MIN_PER_DAY) == pytest.approx(MIN_PER_DAY, rel=0.02)


def test_object_class():
    assert object_class("bowl_3") == "bowl"
    assert object_class("mia_phone") == "phone"
    assert object_class("laundry_basket_1") == "laundry_basket"


# ── oracle occlusion against the collision proxy grid ───────────────────────

def test_oracle_occlusion_grid(episode, monkeypatch):
    """A wall (non-navigable run) blocks the ray; the tail allowance keeps
    on-furniture targets visible."""
    from dynbelief.perception.oracle import OraclePerceiver
    from dynbelief.replay import ReplayWorld

    class TD:
        meters_per_pixel = 0.05
        grid = np.ones((200, 200), dtype=bool)
        bounds_min = np.array([-5.0, 0.0, -5.0])

        def world_to_pixel(self, x, z):
            return (int((z - self.bounds_min[2]) / self.meters_per_pixel),
                    int((x - self.bounds_min[0]) / self.meters_per_pixel))

        def is_in_bounds(self, r, c):
            return 0 <= r < 200 and 0 <= c < 200

    td = TD()
    td.grid[:, 140:160] = False  # a 1m wall at x = [2, 3]
    monkeypatch.setattr("dynamic_home_eqa.topdown_map.load_topdown_map",
                        lambda scene_id, **k: td)
    w = ReplayWorld(episode)
    p = OraclePerceiver(w, d_max=50.0)
    assert p.ray_unobstructed(0.0, 0.0, 1.5, 0.0)          # open floor
    assert not p.ray_unobstructed(0.0, 0.0, 4.0, 0.0)      # crosses the wall
    assert p.ray_unobstructed(0.0, 0.0, 2.6, 0.0)          # target ON the wall
    # region: the tail allowance treats the last 0.8 m as the
    # supporting furniture's own footprint


def test_runner_determinism(episode, monkeypatch):
    import numpy as np

    class TD:  # fully open floor
        meters_per_pixel = 0.05
        grid = np.ones((400, 400), dtype=bool)
        bounds_min = np.array([-10.0, 0.0, -10.0])

        def world_to_pixel(self, x, z):
            return (int((z + 10.0) / 0.05), int((x + 10.0) / 0.05))

        def is_in_bounds(self, r, c):
            return 0 <= r < 400 and 0 <= c < 400

    monkeypatch.setattr("dynamic_home_eqa.topdown_map.load_topdown_map",
                        lambda scene_id, **k: TD())
    from dynbelief.perception.oracle import OraclePerceiver
    from dynbelief.replay import ReplayWorld
    from dynbelief.replay.runner import run_schedule
    from dynbelief.replay.viewpoints import Viewpoints

    w = ReplayWorld(episode)
    vps = Viewpoints([{ "vp_id": "vp_a", "position": [0.5, 0, 0.2], "yaw": 0.0,
                        "visible_slots": [1, 2], "travel_min": {"vp_a": 0.0}}])
    def go():
        b = B0LastSeen()
        return run_schedule(w, vps, OraclePerceiver(w), b,
                            [(60, "vp_a"), (700, "vp_a")], 0, MIN_PER_DAY, 60)
    a, bdf = go(), go()
    assert a.equals(bdf)
    # the visit at 700 sees the bowl on the table -> prediction updates
    row = a[(a.t == 720) & (a.obj_id == 0)].iloc[0]
    assert row.pred_argmax == 2 and row.last_seen_age == 20
