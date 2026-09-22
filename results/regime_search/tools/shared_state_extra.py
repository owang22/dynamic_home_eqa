#!/usr/bin/env python3
"""Merge the global-vs-per-person shared-state comparison into story_extra.json under "shared_state" — does not
touch "affected_windows" or any other key.

    python3 tools/shared_state_extra.py  (run from results/regime_search)
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UQ = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq")

WINDOWS = ["last5lead", "first3sick", "restsick", "first3return", "restreturn"]
WINDOW_LABEL = {"last5lead": "before", "first3sick": "sick, days 1–3", "restsick": "sick, later",
                "first3return": "back, days 1–3", "restreturn": "back, later"}
METHOD_INFO = {
    "hedge": ("Hedge over memory lengths", "one weight vector for the household", "one per person", "confidence", "--s5"),
    "conformal": ("Honest sets (conformal)", "one size bar for the household", "one per person", "set size (places)", "--s13"),
    "reset": ("Change alarm + reset", "one alarm for the household", "one per person", "confidence", "--s3"),
}


def main():
    ss = json.load(open(f"{UQ}/shared_state.json"))
    out_methods = {}
    for key, (name, global_name, person_name, metric_label, color) in METHOD_INFO.items():
        if key not in ss:
            continue
        d = ss[key]
        out_methods[key] = {"name": name, "global_name": global_name, "person_name": person_name,
                             "metric_label": metric_label, "color": color, "n_households": d["n_households"],
                             "windows": d["windows"], "pairs": d["pairs"]}

    block = {"window_order": WINDOWS, "window_label": WINDOW_LABEL, "methods": out_methods}
    path = f"{ROOT}/story_extra.json"
    data = json.load(open(path)) if os.path.exists(path) else {}
    data["shared_state"] = block
    json.dump(data, open(path, "w"), separators=(",", ":"))
    print(f"merged shared_state into {path}: {len(out_methods)} methods, other keys kept: {[k for k in data if k != 'shared_state']}")


if __name__ == "__main__":
    main()
