"""
experiment_config.py — the frozen E0 configuration every post-E0 milestone
reruns identically, so their effects can be attributed to the milestone's
own change and nothing else (a different question set, day split, seed, or
navmesh setting between reruns would confound the comparison the
attribution table exists to make).

FROZEN_LABELS is a literal list, not "the first N dynamic labels recomputed
from the eval manifest" — freezing the computation instead of the result
would silently change the question set if the eval manifest is ever
regenerated (a different model, a different seed), defeating the point of
freezing anything.

Superseded (2nd) generation, post navmesh-connectivity phase: the original
FROZEN_LABELS (10 labels, "moved at least once in day4") was invalidated by
the M1 gate's 80% abstain rate, traced to two sampling defects it never
screened for — 5 of 10 labels didn't exist yet at patrol_start, and 4 of
the remaining 5 sat on navmesh islands unreachable from the start pose (see
world.py's and config.NavMeshConfig's docstrings for the connectivity fix
itself). embodied/sampling.py's qualify_labels() now screens for both
properties; FROZEN_LABELS below is its output
(scripts/compute_frozen_labels.py), computed once and frozen the same way
the original 10 were — 9 of the original 22 candidate dynamic labels in
102343992_family_with_kids_day4/manifest.json qualify.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .config import NavMeshConfig

FROZEN_SCENE   = "102343992"
FROZEN_PROFILE = "family_with_kids"

FROZEN_TRAIN_FOLDERS: tuple[str, ...] = (
    "102343992_family_with_kids",
    "102343992_family_with_kids_day1",
    "102343992_family_with_kids_day2",
    "102343992_family_with_kids_day3",
)
FROZEN_EVAL_FOLDER = "102343992_family_with_kids_day4"

# Recomputed by scripts/compute_frozen_labels.py under embodied/sampling.py's
# two-property rule (exists at patrol_start AND every historical anchor
# slot reachable from the start pose). None of these 9 were disqualified by
# reachability alone — the navmesh-connectivity phase's D1 fix (climb=0.4)
# fully resolved reachability for this label set; the remaining 13
# candidates (of 22) fail purely on "doesn't exist yet at patrol_start=6.0"
# (an insert_new event later that day).
FROZEN_LABELS: tuple[str, ...] = (
    "book_1", "bowl_1", "candle_1", "cup_1", "keys_1",
    "phone_1", "potted_plant_1", "stool_1", "vase_1",
)

# M3 (state-change dynamics): a parallel, separate day-folder set
# (scripts/generate_state_stratum.py) — the state-change events derived
# from the SAME real activity traces as the location folders above, but
# never merged into them (see experiment_config.py's own module docstring
# note below and generate_state_stratum.py's docstring for why the frozen
# location folders are never regenerated in place). Adding these fields
# changes FrozenConfig.fingerprint()'s hash — see the standing rule this
# phase already documents: any config-affecting change rebuilds the whole
# attribution table, and E0/M1/M2 need one mechanical rerun (no logic
# change) purely to refresh their tag.
FROZEN_STATE_TRAIN_FOLDERS: tuple[str, ...] = (
    "102343992_family_with_kids_state",
    "102343992_family_with_kids_state_day1",
    "102343992_family_with_kids_state_day2",
    "102343992_family_with_kids_state_day3",
)
FROZEN_STATE_EVAL_FOLDER = "102343992_family_with_kids_state_day4"
# Real instance ids (not the "label::variable" synthetic belief-store key —
# see posterior.py's module docstring) with at least one state_change event
# in the state eval day — the state-axis analog of FROZEN_LABELS'
# "moved at least once" property. Computed by
# scripts/compute_frozen_state_labels.py. Unlike location labels, no
# existence-at-patrol_start filter is needed (the underlying furniture
# instance always exists from scene-init — no insert semantics for state,
# see env/inventory.py's STATEFUL_FURNITURE) — but the ANCHOR itself (not
# just its room) does need checking: "fridge_1" is excluded here despite
# fridge's room (kitchen) being reachable, because fridge's own real HSSD
# position in this scene fails navmesh-adjacency entirely (confirmed —
# see tests/test_topdown_map.py's check_anchor_sanity and
# tests/test_sensor.py's _NO_VIEWPOINT_WITHIN_RANGE) — no viewpoint exists
# from which to sense or resense it, so no policy could ever answer a
# fridge::door question on genuine information. Same category of
# real-scene geometry limitation the navmesh-connectivity phase already
# documented for the living_room furniture cluster (NavMeshConfig's
# docstring); excluded by the same kind of human decision, not silently
# left to fail every trial.
FROZEN_STATE_LABELS: tuple[str, ...] = ("wardrobe_1",)

FROZEN_WAIT_HOURS_SWEEP: tuple[float, ...] = (0.25, 0.5, 1.0, 2.0, 4.0)
FROZEN_LAMBDA_SWEEP: tuple[float, ...] = (0.0, 0.001, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0)
# Chosen fixed (not moved past the morning insert_new burst) — see
# embodied/sampling.py's module docstring for why: moving it would flatten
# the "patrol in the morning, get asked later" framing the whole phase is
# built on. The cost is a smaller eligible label pool (9 of 22), addressed
# at the M4 experiment-suite stage by drawing more eval days if needed.
FROZEN_PATROL_START = 6.0
FROZEN_SEED = 0
FROZEN_NAVMESH = NavMeshConfig()


@dataclass(frozen=True)
class FrozenConfig:
    """Identifies one rerun for the attribution table's consistency check —
    two rows with the same milestone but a different fingerprint indicate a
    rerun that didn't actually use the frozen setup. navmesh is part of the
    fingerprint: a different agent_max_climb/agent_radius/etc. changes which
    anchors are reachable and where the agent starts, exactly the class of
    bug the navmesh-connectivity phase exists to catch before it reaches an
    experiment's results."""
    scene:              str = FROZEN_SCENE
    profile:            str = FROZEN_PROFILE
    train_folders:      tuple[str, ...] = FROZEN_TRAIN_FOLDERS
    eval_folder:        str = FROZEN_EVAL_FOLDER
    labels:             tuple[str, ...] = FROZEN_LABELS
    wait_hours_sweep:   tuple[float, ...] = FROZEN_WAIT_HOURS_SWEEP
    patrol_start:       float = FROZEN_PATROL_START
    seed:               int = FROZEN_SEED
    navmesh:            NavMeshConfig = FROZEN_NAVMESH
    # M3 (state-change dynamics) — see this module's own comments above.
    state_train_folders: tuple[str, ...] = FROZEN_STATE_TRAIN_FOLDERS
    state_eval_folder:   str = FROZEN_STATE_EVAL_FOLDER
    state_labels:        tuple[str, ...] = FROZEN_STATE_LABELS

    def fingerprint(self) -> str:
        import hashlib
        payload = repr((
            self.scene, self.profile, self.train_folders, self.eval_folder,
            self.labels, self.wait_hours_sweep, self.patrol_start, self.seed,
            self.state_train_folders, self.state_eval_folder, self.state_labels,
            self.navmesh,
        ))
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


FROZEN = FrozenConfig()
