"""Migrate hypothesis files from the retired ``after`` enum to per-move
``duration_h``.

``after`` selected where a move's displacement window closed:
``returned`` at the activity's ``duration_h``, ``left`` at midnight.
The converter now closes every window at ``start + move duration``
(defaulting to the activity's) and clamps to midnight, so the exact
equivalent is: ``returned`` -> drop the field; ``left`` ->
``duration_h = 24 - start_hour`` on the move.

Idempotent; rewrites in place and prints what it touched. Logs and
diagnostics (records of what the LLM wrote) are left alone.

Usage:
  python -m baselines.llm_hypotheses.migrate_after results/llm_hypotheses/hypotheses
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Dict, Tuple


def migrate_hypothesis(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """One hypothesis (or leaf) body; returns (migrated copy, moves changed)."""
    out = dict(raw)
    changed = 0
    activities = []
    for act in raw.get("activities", ()):
        act = dict(act)
        start = float(act.get("start_hour", 0.0))
        moves = []
        for move in act.get("moves", ()):
            move = dict(move)
            after = move.pop("after", None)
            if after is not None:
                changed += 1
                if after == "left" and "duration_h" not in move:
                    move["duration_h"] = round(24.0 - start, 3)
            moves.append(move)
        act["moves"] = moves
        activities.append(act)
    out["activities"] = activities
    return out, changed


def migrate_file(path: pathlib.Path) -> int:
    payload = json.loads(path.read_text())
    changed = 0
    for key in ("hypotheses", "leaves"):
        if isinstance(payload, dict) and key in payload:
            rows = []
            for h in payload[key]:
                h2, n = migrate_hypothesis(h)
                changed += n
                rows.append(h2)
            payload[key] = rows
    if changed:
        path.write_text(json.dumps(payload, indent=1))
    return changed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=pathlib.Path)
    args = ap.parse_args()
    total = 0
    for path in sorted(args.root.rglob("*.json")):
        n = migrate_file(path)
        if n:
            print(f"{path}: {n} moves migrated")
        total += n
    print(f"total moves migrated: {total}")


if __name__ == "__main__":
    main()
