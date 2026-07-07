#!/usr/bin/env python3
"""
qualify_scene.py — scene-qualification pre-flight CLI.

Runs embodied.reachability.check_reachability_invariant and exits non-zero
if any room centroid or anchor is unreachable from the agent's selected
start pose. On failure, also runs the D0 diagnostic render (see
diagnose_navmesh_islands.py) so the failure comes with the evidence needed
to decide whether it's a fixable navmesh setting or a genuine geometry
fragment (see the navmesh-connectivity phase's escalation rule). Run this
once per scene before generation or an experiment sweep.

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import argparse
import pathlib
import sys

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.config import NavMeshConfig
from dynamic_home_eqa.embodied.reachability import check_reachability_invariant


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", default="102343992")
    ap.add_argument("--render-on-failure", action="store_true", default=True)
    ap.add_argument("--out-dir", default=str(_DYNAMIC_EQA / "diagnostics"))
    args = ap.parse_args()

    result = check_reachability_invariant(args.scene, NavMeshConfig())
    print(result.summary())
    if result.excluded_small_fragment:
        print("Excluded sub-threshold fragments (not counted as failures):")
        for item in result.excluded_small_fragment:
            print(f"  - {item}")

    if result.ok:
        print(f"PASS: scene {args.scene} qualifies (start room '{result.start_room}', "
              f"island {result.start_island}).")
        return

    print(f"FAIL: {len(result.unreachable)} unreachable from start room "
          f"'{result.start_room}' (island {result.start_island}):")
    for item in result.unreachable:
        print(f"  - {item}")

    if args.render_on_failure:
        from dynamic_home_eqa.scripts.diagnose_navmesh_islands import (
            _make_sim, _island_vertices, collect_island_stats, nearest_pairs,
            print_table, print_near_touch, render,
        )
        out_dir = pathlib.Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        png_path = out_dir / f"navmesh_islands_{args.scene}_FAILED_qualify.png"

        sim = _make_sim(args.scene)
        try:
            pf = sim.pathfinder
            verts_by_island = {i: _island_vertices(pf, i) for i in range(pf.num_islands)}
            stats, outdoor_points = collect_island_stats(sim, args.scene, verts_by_island)
            print_table(stats)
            print_near_touch(nearest_pairs(verts_by_island, stats))
            render(args.scene, stats, verts_by_island, outdoor_points, png_path)
        finally:
            sim.close()
        print(f"\nEvidence render: {png_path}")

    sys.exit(1)


if __name__ == "__main__":
    main()
