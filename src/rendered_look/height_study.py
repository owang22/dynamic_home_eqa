"""What a camera at each height can see of the same household at the same moments.

    python -m rendered_look.height_study

Reads the study renders (`render --every-position`), in which every place
with something on it was photographed from up to eight camera positions at
each height, and writes one JSON file. A thing is counted at two levels:

  in view    at least 200 of its pixels in a 960 by 720 picture, not cut by
             the edge, and at least half of what it shows at its best
  clear      in view, at least 600 pixels, and not dark on dark or close in
             brightness to what surrounds it

and from two sets of positions: the one position the picker chose, and the
best of all positions tried. The gap between those two is the picker, not
the height.
"""
from __future__ import annotations

import collections
import json

import numpy as np

from rendered_look.world import REPO

HOME = REPO / "results/rendered_look/hh_s151"
HEIGHTS = ["0.30", "0.45", "0.70", "1.00", "1.30"]
BANDS = [("on the floor", -1, 0.05), ("low, up to 50 cm", 0.05, 0.50),
         ("seat and bed height, 50 to 70 cm", 0.50, 0.70),
         ("table height, 70 to 85 cm", 0.70, 0.85), ("counter height, above 85 cm", 0.85, 9)]


def band_of(y: float) -> str:
    return next(name for name, low, high in BANDS if low < y <= high)


def main() -> None:
    runs = {}
    for h in HEIGHTS:
        path = HOME / f"every_position_eye{h}.json"
        if path.exists():
            runs[h] = json.load(path.open())
    shares = collections.defaultdict(list)
    for moments in runs.values():
        for m in moments:
            for v in m["views"]:
                for shown in v["from_each_position"]:
                    for p in shown:
                        if not p["is_person"] and p["seen"] and not p.get("cut_by_the_edge"):
                            shares[p["what"]].append(p["share_of_its_outline"])
    best = {k: float(np.percentile(v, 90)) for k, v in shares.items() if len(v) >= 5}

    def in_view(p) -> bool:
        return bool(p["seen"] and not p.get("cut_by_the_edge") and
                    (p["what"] not in best or p["share_of_its_outline"] >= 0.5 * best[p["what"]]))

    def clear(p) -> bool:
        return in_view(p) and p["pixels"] >= 600 and not p["hard_to_make_out"]

    out = {"heights": {}, "bands": [b[0] for b in BANDS],
           "levels": {"in view": "at least 200 of its pixels in a 960 by 720 picture, the edge of the picture does "
                                 "not cut it, and at least half of what it shows at its best is in view",
                      "clear": "in view, at least 600 pixels, and not dark on a dark ground or close in brightness "
                               "to what is around it"},
           "lens_degrees": 75,
           "positions": {"chosen": "the first camera position of every picture taken at that moment: the picker's "
                                   "choice for each place with something on it, and the whole-room positions",
                         "best": "any picture taken at that moment, from any of the up to eight positions tried "
                                 "for each place with something on it, and the whole-room positions. The run at "
                                 "0.30 m has no whole-room pictures."}}
    for height, moments in runs.items():
        tally = collections.Counter()
        tried = []
        for m in moments:
            got = collections.defaultdict(set)   # (level, positions) -> things
            for v in m["views"]:
                each = v["from_each_position"]
                tried.append(len(each))
                for n, shown in enumerate(each):
                    for p in shown:
                        if p["is_person"]:
                            continue
                        for level, test in (("in view", in_view), ("clear", clear)):
                            if test(p):
                                got[level, "best"].add(p["what"])
                                if n == 0:
                                    got[level, "chosen"].add(p["what"])
            for object_id, t in m["things"].items():
                if not t.get("shown"):
                    continue
                keys = [("band", band_of(t["y"])), ("place", t["place"]), ("class", t["class"]), ("all", "all"),
                        ("all but towels", "all") if t["class"] != "towel" else ("towels", "all")]
                for key in keys:
                    tally[key + ("placed",)] += 1
                    for (level, positions), things in got.items():
                        if object_id in things:
                            tally[key + (level, positions)] += 1

        def cell(kind, name):
            return {"placed": tally[kind, name, "placed"],
                    **{f"{level}, {positions} position": tally[kind, name, level, positions]
                       for level in ("in view", "clear") for positions in ("chosen", "best")}}

        out["heights"][height] = {
            "everything": cell("all", "all"), "everything but towels": cell("all but towels", "all"),
            "by_band": {b: cell("band", b) for b, _, _ in BANDS},
            "by_place": {k[1]: cell("place", k[1]) for k in tally if k[0] == "place" and k[2] == "placed"},
            "by_class": {k[1]: cell("class", k[1]) for k in tally if k[0] == "class" and k[2] == "placed"},
            "most_positions_tried_for_a_place": int(max(tried)) if tried else 0,
        }
    out["sensitivity"] = sensitivity(runs, best)
    out["go2"] = go2_camera(best)
    (HOME / "height_study.json").write_text(json.dumps(out, indent=1))
    if out["go2"]:
        print("\nGo2's own camera, 0.37 m, 100 degree lens; in view from the best position, by how far up it may tilt")
        for limit, cells in out["go2"]["by_tilt_limit"].items():
            print(f"  tilt up to {limit:>9}: " + "  ".join(
                f"{b.split(',')[0][:12]} {c['in view'] / max(1, c['placed']):.0%}" for b, c in cells["by_band"].items())
                + f"  | everything {cells['everything']['in view'] / cells['everything']['placed']:.0%}"
                + f"  | but towels {cells['everything but towels']['in view'] / cells['everything but towels']['placed']:.0%}")
    for column in ("in view, chosen position", "in view, best position", "clear, best position"):
        print(f"\n{column}")
        print(f"{'':38}" + "".join(f"{h + ' m':>9}" for h in runs))
        rows = [(b, lambda H, b=b: H["by_band"][b]) for b, _, _ in BANDS] + [
            ("everything", lambda H: H["everything"]), ("everything but towels", lambda H: H["everything but towels"])]
        for name, get in rows:
            n = get(next(iter(out["heights"].values())))["placed"]
            print(f"{name + f' ({n})':38}" + "".join(
                f"{get(out['heights'][h])[column] / max(1, get(out['heights'][h])['placed']):>9.0%}" for h in runs))


def sensitivity(runs: dict, best: dict) -> dict:
    """The headline under other ways of counting, from the best position. An
    independent recount on 2026-09-30 found the low-height numbers turn on the
    'half of its best' rule and on a few things that sit in one place for many
    moments; these rows show how far they move."""
    def passes(p, half: bool, pixels: int, clear: bool) -> bool:
        if p["pixels"] < pixels or p.get("cut_by_the_edge"):
            return False
        if half and p["what"] in best and p["share_of_its_outline"] < 0.5 * best[p["what"]]:
            return False
        return not clear or (p["pixels"] >= 600 and not p["hard_to_make_out"])

    rules = {"as published": dict(half=True, pixels=200, clear=False),
             "without the half-of-its-best rule": dict(half=False, pixels=200, clear=False),
             "400 pixels, not 200": dict(half=True, pixels=400, clear=False),
             "clear (600 pixels, not dark on dark)": dict(half=True, pixels=200, clear=True)}
    groups = {"everything": lambda t: True, "table height": lambda t: 0.70 < t["y"] <= 0.85,
              "counter height": lambda t: t["y"] > 0.85}
    out = {"rows": {}, "pairs": {}}
    for name, rule in list(rules.items()) + [("as published, counted per distinct thing and place", rules["as published"])]:
        per_pair = name.endswith("place")
        out["rows"][name] = {}
        for height, moments in runs.items():
            seen_by_pair = collections.defaultdict(list)
            for m in moments:
                got = {p["what"] for v in m["views"] for shown in v["from_each_position"] for p in shown
                       if not p["is_person"] and passes(p, **rule)}
                for object_id, t in m["things"].items():
                    if t.get("shown"):
                        seen_by_pair[object_id, t["place"], round(t["y"], 2)].append(object_id in got)
            cell = {}
            for group, test in groups.items():
                pairs = {k: v for k, v in seen_by_pair.items() if test({"y": k[2]})}
                if per_pair:
                    cell[group] = round(float(np.mean([np.mean(v) for v in pairs.values()])), 5)
                    out["pairs"][group] = len({(k[0], k[1]) for k in pairs})
                else:
                    cell[group] = round(sum(sum(v) for v in pairs.values()) / sum(len(v) for v in pairs.values()), 5)
            out["rows"][name][height] = cell
    return out


def go2_camera(best: dict) -> dict:
    """The study at the Go2's own camera: 0.37 m, a 100 degree lens, and a limit on
    how far up the body can tilt. The render is 960 pixels across and the real
    camera 1280, so pixel counts are scaled by (1280 / 960) squared before the
    200 and 600 pixel rules are applied."""
    path = HOME / "every_position_eye0.37_lens100.json"
    if not path.exists():
        return {}
    moments = json.load(path.open())
    scale = (1280 / 960) ** 2

    def in_view(p) -> bool:
        return bool(p["pixels"] * scale >= 200 and not p.get("cut_by_the_edge") and
                    (p["what"] not in best or p["share_of_its_outline"] >= 0.5 * best[p["what"]]))

    def clear(p) -> bool:
        return in_view(p) and p["pixels"] * scale >= 600 and not p["hard_to_make_out"]

    result = {"height_m": 0.37, "lens_degrees": 100, "picture": "960 by 540, counted as if 1280 by 720",
              "by_tilt_limit": {}}
    for label, limit in (("any tilt", 90.0), ("30 degrees", 30.0), ("15 degrees", 15.0), ("level", 3.0)):
        tally = collections.Counter()
        for m in moments:
            got = collections.defaultdict(set)
            for v in m["views"]:
                for shown, up in zip(v["from_each_position"], v["degrees_up"]):
                    if up > limit:
                        continue
                    for p in shown:
                        if not p["is_person"]:
                            if in_view(p):
                                got["in view"].add(p["what"])
                            if clear(p):
                                got["clear"].add(p["what"])
            for object_id, t in m["things"].items():
                if not t.get("shown"):
                    continue
                for key in [("band", band_of(t["y"])), ("all", "everything"),
                            ("all", "everything but towels") if t["class"] != "towel" else ("skip", "")]:
                    tally[key + ("placed",)] += 1
                    for level in ("in view", "clear"):
                        tally[key + (level,)] += object_id in got[level]
        cell = lambda kind, name: {"placed": tally[kind, name, "placed"], "in view": tally[kind, name, "in view"],
                                   "clear": tally[kind, name, "clear"]}
        result["by_tilt_limit"][label] = {"by_band": {b: cell("band", b) for b, _, _ in BANDS},
                                          "everything": cell("all", "everything"),
                                          "everything but towels": cell("all", "everything but towels")}
    return result


if __name__ == "__main__":
    main()
