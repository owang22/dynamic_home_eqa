#!/usr/bin/env python3
"""Merge the windowed affected/unaffected analysis into story_extra.json under "affected_windows" — does not touch
the other keys ("sweep", "affected", "planning", ...) that story_extra.py or other scripts own.

    python3 tools/affected_windows_extra.py  (run from results/regime_search)

Reads ../confidence_shift_2026-09-20/uq/windows.json (written by src/baselines/patrol/uq_windows.py) and reshapes it
for the story page's renderAffected(): per-agent display name/color, the five windows in order, and the two paired
transitions (entry = first3sick vs last5lead, return = first3return vs restsick) each with the affected/unaffected
change, the gap, and how many of N households clear the gap bar.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UQ = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq")

WINDOWS = ["last5lead", "first3sick", "restsick", "first3return", "restreturn"]
WINDOW_LABEL = {"last5lead": "last 5 days before", "first3sick": "first 3 sick days", "restsick": "rest of the sick spell",
                "first3return": "first 3 days back", "restreturn": "rest of the return"}
# display name (plain language, no jargon) and legend color per agent key
AGENT_INFO = {
    "none_tt": ("the learner that never forgets", "--s2"),
    "none_tt72": ("the learner with a 3-day memory", "--s1"),
    "detperson_tt72": ("the 3-day learner + a change alarm for each person", "--s3"),
    "oracle_tt72": ("the 3-day learner, told in advance (best case)", "--s12"),
    "none_mf72": ("most-often-seen place, 3-day memory", "--s4"),
    "none_lastseen": ("last seen", "--sg"),
}
PAIRS = {"entry": ("first3sick", "last5lead"), "return": ("first3return", "restsick")}


def main():
    win = json.load(open(f"{UQ}/windows.json"))
    out_agents = {}
    for key, (name, color) in AGENT_INFO.items():
        if key not in win:
            continue
        a = win[key]
        w_out = {w: {"affected": a["windows"][w]["affected"], "unaffected": a["windows"][w]["unaffected"]} for w in WINDOWS}
        p_out = {}
        for label, (w, ref) in PAIRS.items():
            p = a["pairs"][f"{w}_vs_{ref}"]
            p_out[label] = {"window": w, "ref": ref, "affected_change": p["affected_change"], "unaffected_change": p["unaffected_change"],
                            "gap": p["gap"], "n_clear": p["n_clear_bar"], "n_total": p["n_total"], "gap_bar": p["gap_bar"]}
        out_agents[key] = {"name": name, "color": color, "n_households": a["n_households"], "windows": w_out, "pairs": p_out}

    block = {"window_order": WINDOWS, "window_label": WINDOW_LABEL, "agents": out_agents}

    path = f"{ROOT}/story_extra.json"
    data = json.load(open(path)) if os.path.exists(path) else {}
    data["affected_windows"] = block
    json.dump(data, open(path, "w"), separators=(",", ":"))
    print(f"merged affected_windows into {path}: {len(out_agents)} agents, {sum(1 for k in AGENT_INFO if k not in win)} missing, "
          f"other keys kept: {[k for k in data if k != 'affected_windows']}")


if __name__ == "__main__":
    main()
