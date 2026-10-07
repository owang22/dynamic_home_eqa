"""Phase 1 — HOMER+ raw routines -> one canonical trace format.

No method reads the raw dataset; everything downstream consumes the rows
this module emits (or the artifacts derived from them).

Raw encoding, and the state-vs-transition decision
--------------------------------------------------
A HOMER+ ``routines_*/<day>.json`` holds ~200 FULL-STATE graph snapshots
per day, one per simulated atomic action, each timestamped in minutes from
midnight (floats; the simulator day spans 06:00-24:00, ``common_data.json``
start_time=360, end_time=1440). The raw data therefore encodes STATE, not
transitions. The canonical stream reduces each object's snapshot sequence
to CHANGE-POINTS: one row at the day's first snapshot (the day-initial
state) and one row whenever the resolved receptacle differs from the
previous snapshot. Location holds piecewise-constant until the next row —
so `state_at(object, t)` is the last row at or before ``t``, and no
information in the snapshots is lost (between snapshots the simulator, and
hence the dataset, asserts nothing moved).

Timestamps are minutes from MIDNIGHT of the day's own script — HOMER+
days are self-contained scripts with no cross-day night continuity, so
midnight (the dataset's native anchor) is the declared day boundary.
Fractional minutes are kept.

Receptacle resolution
---------------------
A VirtualHome snapshot gives most objects SEVERAL location edges at once —
typically INSIDE the containing room AND ON/INSIDE a piece of furniture
(and possibly inside another movable object: food INSIDE a pot ON the
stove). The room edge is redundant with the furniture edge, so the direct
parent is chosen by SPECIFICITY, not edge order: a movable container
first (nesting), then props/appliances/furniture, and the room only when
nothing more specific exists (an object on the floor). Among equally
specific targets, INSIDE beats ON, then lowest id — deterministic. The
canonical receptacle is then the nearest ancestor in the parent chain that
is not itself a movable object. Choosing by the old lowest-id rule instead
silently resolved every object to its ROOM (rooms have the lowest ids),
collapsing 20+ real receptacles to 5 — the inventory's receptacle count is
the regression check against that.

Held-out masks are a separate artifact (heldout_masks.json), never row
deletion.
"""

from __future__ import annotations

import collections
import dataclasses
import json
import pathlib
import random
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

HOMER_ROOT = pathlib.Path("third_party/HOMER_PLUS")
HOUSEHOLDS = ("HouseholdA", "HouseholdB", "HouseholdC")
PLACABLE = "placable_objects"
DAY_END_MIN = 1440.0
TRACE_FIELDS = ("object_id", "timestamp", "receptacle_id", "household_id",
                "day_index", "split")


@dataclasses.dataclass(frozen=True)
class TraceRow:
    """One canonical observation: object seen at receptacle at time t."""

    object_id: str          # "<class_name>#<node_id>" — stable per household
    timestamp: float        # minutes from midnight of the day
    receptacle_id: str
    household_id: str       # "A" | "B" | "C"
    day_index: int          # within-split day number (file name)
    split: str              # "train" | "test"


@dataclasses.dataclass
class Inventory:
    """Phase 0 dataset facts, computed from the raw snapshots."""

    household_id: str
    n_objects: int = 0
    n_receptacles: int = 0
    days_train: int = 0
    days_test: int = 0
    rows_train: int = 0
    rows_test: int = 0
    moves_per_day: float = 0.0
    frac_objects_ever_move: float = 0.0
    per_object_moves: Dict[str, int] = dataclasses.field(default_factory=dict)
    multi_parent_snapshots: int = 0
    objects: List[str] = dataclasses.field(default_factory=list)
    receptacles: List[str] = dataclasses.field(default_factory=list)


def _resolve(node_cat: Dict[int, str], parents: Dict[int, Tuple[str, int]],
             obj: int) -> Optional[int]:
    """Nearest non-placable ancestor of ``obj`` (None if orphaned)."""
    seen = set()
    cur = obj
    while cur in parents:
        if cur in seen:
            return None                      # defensive: parent cycle
        seen.add(cur)
        cur = parents[cur][1]
        if node_cat.get(cur) != PLACABLE:
            return cur
    return None


def _day_rows(path: pathlib.Path, household: str, day: int, split: str,
              inv: Inventory) -> Iterator[TraceRow]:
    d = json.loads(path.read_text())
    graphs, times = d["graphs"], d["times"]
    nodes = {n["id"]: n for n in graphs[0]["nodes"]}
    node_cat = {i: n["category"] for i, n in nodes.items()}
    name = {i: f"{n['class_name']}#{i}" for i, n in nodes.items()}
    objects = [i for i, n in nodes.items() if n["category"] == PLACABLE]

    cat_rank = {PLACABLE: 0, "Props": 1, "Appliances": 2, "Furniture": 3,
                "Decor": 4, "Rooms": 5, "Home": 6}

    last: Dict[int, Optional[int]] = {}
    for g, t in zip(graphs, times):
        # Most-specific parent wins (module docstring); ties: INSIDE < ON,
        # then id. Sorting stably and keeping the first per from_id makes
        # the whole choice deterministic.
        edges = sorted(
            (e for e in g["edges"]
             if e["relation_type"] in ("INSIDE", "ON")
             and e["to_id"] in node_cat),
            key=lambda e: (e["from_id"],
                           cat_rank.get(node_cat[e["to_id"]], 9),
                           0 if e["relation_type"] == "INSIDE" else 1,
                           e["to_id"]))
        parents: Dict[int, Tuple[str, int]] = {}
        for e in edges:
            if e["from_id"] in parents:
                inv.multi_parent_snapshots += 1
                continue
            parents[e["from_id"]] = (e["relation_type"], e["to_id"])
        for obj in objects:
            rec = _resolve(node_cat, parents, obj)
            if rec is None:
                continue                      # no resolvable location: skip
            if last.get(obj) != rec:
                last[obj] = rec
                yield TraceRow(object_id=name[obj], timestamp=float(t),
                               receptacle_id=name[rec],
                               household_id=household[-1], day_index=day,
                               split=split)


def build_household(household: str,
                    root: pathlib.Path = HOMER_ROOT
                    ) -> Tuple[List[TraceRow], Inventory]:
    """All canonical rows plus the inventory for one household."""
    inv = Inventory(household_id=household[-1])
    rows: List[TraceRow] = []
    objects: set = set()
    receptacles: set = set()
    moves = 0
    move_days = 0
    per_obj: collections.Counter = collections.Counter()

    for split in ("train", "test"):
        days = sorted((root / household / f"routines_{split}").glob("*.json"))
        for path in days:
            day = int(path.stem)
            day_rows = list(_day_rows(path, household, day, split, inv))
            rows.extend(day_rows)
            first_ts = min(r.timestamp for r in day_rows)
            day_initial = sum(1 for r in day_rows if r.timestamp == first_ts)
            moves += len(day_rows) - day_initial
            move_days += 1
            for r in day_rows:
                objects.add(r.object_id)
                receptacles.add(r.receptacle_id)
                if r.timestamp != first_ts:
                    per_obj[r.object_id] += 1
        if split == "train":
            inv.days_train = len(days)
            inv.rows_train = len(rows)
        else:
            inv.days_test = len(days)
            inv.rows_test = len(rows) - inv.rows_train

    inv.n_objects = len(objects)
    inv.n_receptacles = len(receptacles)
    inv.moves_per_day = moves / move_days if move_days else 0.0
    inv.frac_objects_ever_move = (sum(1 for o in objects if per_obj[o] > 0)
                                  / len(objects) if objects else 0.0)
    inv.per_object_moves = dict(per_obj)
    inv.objects = sorted(objects)
    inv.receptacles = sorted(receptacles)
    return rows, inv


def write_traces(out_dir: pathlib.Path,
                 root: pathlib.Path = HOMER_ROOT,
                 seed: int = 0, heldout_k: int = 2,
                 heldout_draws: int = 5) -> Dict[str, Inventory]:
    """Write canonical CSVs, inventories, and held-out masks."""
    import csv
    import gzip
    out_dir.mkdir(parents=True, exist_ok=True)
    inventories: Dict[str, Inventory] = {}
    masks: Dict[str, List[List[str]]] = {}
    rng = random.Random(seed)
    for household in HOUSEHOLDS:
        rows, inv = build_household(household, root)
        inventories[household[-1]] = inv
        with gzip.open(out_dir / f"{household}.csv.gz", "wt", newline="") as f:
            w = csv.writer(f)
            w.writerow(TRACE_FIELDS)
            for r in rows:
                w.writerow([r.object_id, r.timestamp, r.receptacle_id,
                            r.household_id, r.day_index, r.split])
        # Held-out draws favour objects that move non-trivially (>= 1 move
        # per 5 training days on average): holding out a never-mover tests
        # nothing but the initial-placement fallback.
        movers = sorted(o for o, n in inv.per_object_moves.items()
                        if n >= inv.days_train / 5)
        draws: List[List[str]] = []
        for _ in range(heldout_draws):
            draws.append(sorted(rng.sample(movers, min(heldout_k,
                                                       len(movers)))))
        masks[household[-1]] = draws
    (out_dir / "heldout_masks.json").write_text(json.dumps(
        {"seed": seed, "k": heldout_k, "draws": masks}, indent=2))
    (out_dir / "inventory.json").write_text(json.dumps(
        {h: dataclasses.asdict(inv) for h, inv in inventories.items()},
        indent=2))
    return inventories


def read_traces(out_dir: pathlib.Path, household: str) -> List[TraceRow]:
    """Reload one household's canonical rows (loader test asserts counts)."""
    import csv
    import gzip
    rows: List[TraceRow] = []
    with gzip.open(out_dir / f"Household{household}.csv.gz", "rt",
                   newline="") as f:
        for r in csv.DictReader(f):
            rows.append(TraceRow(
                object_id=r["object_id"], timestamp=float(r["timestamp"]),
                receptacle_id=r["receptacle_id"],
                household_id=r["household_id"],
                day_index=int(r["day_index"]), split=r["split"]))
    return rows
