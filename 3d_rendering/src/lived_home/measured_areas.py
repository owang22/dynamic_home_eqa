"""Surface areas measured in the rendered empty home, used for how much a spot holds.

A spot's area in the layout ("assumed") comes from the HSSD receptacle mesh or the
room's floor polygon when the household was made. The renderer's empty-home scan
(3d_rendering/results/vlm_night/render/choose_views.py, Home.grid_for) measured the
part of each open spot a thing could actually rest on: 2 cm cells of the spot's own
furniture at the spot's height, seen from above. The dining table is assumed 2.55 m²
and measures 1.34 m².

The scan only reaches spots it chose a view for (surfaces and open basins, not
drawers), and only household A's scene (107734254_176000121) so far. A scan that
finds under a quarter of the assumed area is not used: those are lower shelves seen
through the shelf above (0.002 m² for a bed's middle shelf), cushioned seats that
are not flat within 3 cm, and floors whose rugs are a separate object. Those keep
the assumed area and are listed as doubtful.

    python -m lived_home.measured_areas build     copy the scan into measured_areas.json
    python -m lived_home.measured_areas show [scene]
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
TABLE = HERE / "measured_areas.json"
SCANS = [HERE.parents[1] / "results" / "vlm_night" / "render" / n
         for n in ("spot_views.json", "spot_views_1p4.json")]
MIN_SCAN_SHARE = 0.25          # a scan under this share of the assumed area is doubtful


def build(scans=SCANS, out: pathlib.Path = TABLE) -> dict:
    """{scene: {place: {"scanned", "assumed", "from"}}} from the renderer's view files
    (the first file that has a spot wins)."""
    table = json.loads(out.read_text()) if out.exists() else {}
    for path in scans:
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        rows = table.setdefault(data["scene"], {})
        for v in data["views"]:
            if v["spot"] in rows or v.get("scanned_area_m2") is None:
                continue
            rows[v["spot"]] = {"scanned": v["scanned_area_m2"], "assumed": v["snapshot_area_m2"],
                               "from": f"{path.parent.name}/{path.name}"}
    out.write_text(json.dumps(table, indent=1, sort_keys=True))
    return table


def load(scene: str | None) -> dict:
    if not scene or not TABLE.exists():
        return {}
    return json.loads(TABLE.read_text()).get(scene, {})


def capacity_area(geometry: dict, row: dict | None) -> tuple[float | None, str]:
    """(area to use, where it came from): 'scanned', 'assumed (scan doubtful)' or
    'assumed'."""
    assumed = (geometry or {}).get("area_assumed", (geometry or {}).get("area"))
    if not row:
        return assumed, "assumed"
    if assumed and row["scanned"] < MIN_SCAN_SHARE * assumed:
        return assumed, "assumed (scan doubtful)"
    return row["scanned"], "scanned"


def apply(layout, scene: str | None) -> dict:
    """Sets each place's geometry["area"] to the measured area where there is a good
    one, keeping the old value as geometry["area_assumed"] and the choice as
    geometry["area_from"]. Returns {source: count}. Idempotent."""
    rows = load(scene)
    counts: dict = {}
    for pid, p in layout.places.items():
        g = p.geometry
        if not g or g.get("area") is None:
            continue
        g.setdefault("area_assumed", g["area"])
        area, src = capacity_area(g, rows.get(pid))
        g["area"], g["area_from"] = area, src
        counts[src] = counts.get(src, 0) + 1
    return counts


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "build":
        t = build()
        print({s: len(r) for s, r in t.items()})
        return
    scene = sys.argv[2] if len(sys.argv) > 2 else None
    for s, rows in json.loads(TABLE.read_text()).items():
        if scene and s != scene:
            continue
        for pid, r in sorted(rows.items(), key=lambda x: x[1]["scanned"] / max(x[1]["assumed"], 1e-9)):
            area, src = capacity_area({"area": r["assumed"]}, r)
            print(f"{r['scanned']:7.3f} {r['assumed']:7.3f}  {src:24s} {pid}")


if __name__ == "__main__":
    main()
