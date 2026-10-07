"""Stage 0.4 — ReplayWorld: ground-truth parent/state of every object at any
t_min, reconstructed from an episode's snapshot + event logs. Lets belief
models be evaluated directly from logs, no simulator in the loop.
"""
from __future__ import annotations

import bisect
import json
import pathlib

from dynbelief import ELSEWHERE_ID, MIN_PER_DAY


class ReplayWorld:
    def __init__(self, episode_dir: str | pathlib.Path) -> None:
        d = pathlib.Path(episode_dir)
        self.episode_dir = d
        reg = json.loads((d / "registry.json").read_text())
        self.scene_id: str = reg["scene_id"]
        self.n_days: int = reg["n_days"]
        # days that actually exist in the episode (gaps = generation
        # failures); older registries lack the field -> all days present
        self.days: list[int] = reg.get("days", list(range(self.n_days)))
        self._obj_ids: dict[str, int] = reg["objects"]
        self._recep_ids: dict[str, int] = reg["receptacles"]
        self._recep_meta: dict[int, dict] = {int(k): v for k, v in reg["receptacle_meta"].items()}
        self.obj_label: dict[int, str] = {v: k for k, v in self._obj_ids.items()}
        self.recep_label: dict[int, str] = {v: k for k, v in self._recep_ids.items()}

        self._events: list[dict] = [json.loads(l) for l in (d / "events.jsonl").open()]
        self._events.sort(key=lambda e: e["t_min"])
        self._event_ts = [e["t_min"] for e in self._events]

        self._snapshots: dict[int, dict] = {}
        for p in sorted(d.glob("snapshot_day*.json")):
            s = json.loads(p.read_text())
            self._snapshots[s["day"]] = s

    # ── vocabulary ───────────────────────────────────────────────────────────
    def objects(self) -> list[int]:
        return sorted(self.obj_label)

    def receptacles(self, include_elsewhere: bool = True) -> list[int]:
        ids = sorted(self.recep_label)
        return ids if include_elsewhere else [r for r in ids if r != ELSEWHERE_ID]

    def rooms(self) -> list[str]:
        return sorted({m["room"] for m in self._recep_meta.values() if m.get("room")})

    def room_of(self, receptacle_id: int) -> str | None:
        return self._recep_meta.get(receptacle_id, {}).get("room")

    def position_of(self, receptacle_id: int) -> tuple[float, float, float] | None:
        pos = self._recep_meta.get(receptacle_id, {}).get("position")
        return tuple(pos) if pos else None

    def horizon_min(self) -> int:
        return self.n_days * MIN_PER_DAY

    # ── state reconstruction ─────────────────────────────────────────────────
    def state_at(self, t_min: int) -> dict[int, tuple[int, dict]]:
        """{object_id: (parent_id, states)} at time t_min, inclusive of
        events at exactly t_min. Replays forward from the nearest preceding
        day snapshot — the events.jsonl contract (gt_logger) guarantees the
        replay agrees with every later snapshot."""
        day = min(max(t_min // MIN_PER_DAY, 0), self.n_days - 1)
        if day not in self._snapshots:
            # gap day: replay proceeds from the latest existing snapshot —
            # with no events in the gap this is day-(k-1)'s end state
            day = max(d for d in self._snapshots if d <= day)
        snap = self._snapshots[day]
        parents = {int(k): v for k, v in snap["parents"].items()}
        states = {int(k): dict(v) for k, v in snap.get("states", {}).items()}
        lo = bisect.bisect_left(self._event_ts, snap["t_min"])
        hi = bisect.bisect_right(self._event_ts, t_min)
        for e in self._events[lo:hi]:
            parents[e["object_id"]] = e["parent_id"]
            if e.get("states"):
                states[e["object_id"]] = dict(e["states"])
        return {o: (p, states.get(o, {})) for o, p in parents.items()}

    def true_parent(self, object_id: int, t_min: int) -> int:
        return self.state_at(t_min).get(object_id, (ELSEWHERE_ID, {}))[0]

    # ── event access (belief training, FreMEn fitting, probe overlays) ──────
    def events(self, moved_by: str | None = None) -> list[dict]:
        if moved_by is None:
            return list(self._events)
        return [e for e in self._events if e["moved_by"] == moved_by]

    def change_times(self, object_id: int | None = None,
                     include_init: bool = False) -> list[int]:
        return [e["t_min"] for e in self._events
                if (object_id is None or e["object_id"] == object_id)
                and (include_init or e["moved_by"] != "init")]
