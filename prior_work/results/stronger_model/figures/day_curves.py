"""Per-day first-room-right (and found-within-3) for every stronger-model cell, per household, as JSON for the
figures page. One row per (cell, household, day): number of questions, number right.
    python3 results/stronger_model/figures/day_curves.py > results/stronger_model/figures/day_curves.json"""
import json, pathlib
R = pathlib.Path("results")
CELLS = {
    "qwen_plain_29sep": R / "self_improve/wave_log_only/cells/log_only_no_notes",
    "qwen_plain_fresh": R / "stronger_model/qwen38_plain_rerun2/cells/log_only_no_notes",
    "qwen_think": R / "stronger_model/qwen38_think4000/cells/log_only_no_notes",
    "qwen_think_rep2": R / "stronger_model/qwen38_think4000_rep2/cells/log_only_no_notes",
    "sonnet": R / "stronger_model/claude_sonnet/cells/log_only_no_notes",
    "sonnet_rep2": R / "stronger_model/claude_sonnet_rep2/cells/log_only_no_notes",
    "sonnet_notes": R / "stronger_model/claude_sonnet/cells/the_log_and_notes_about_the_routine",
    "qwen_plain_notes": R / "stronger_model/qwen38_plain/cells/the_log_and_notes_about_the_routine",
    "qwen_think_notes": R / "stronger_model/qwen38_think4000/cells/the_log_and_notes_about_the_routine",
}
out = {}
for name, d in CELLS.items():
    for hh in ["hh_s2_t03", "hh_s19_t03", "hh_s20_t03"]:
        f = d / hh / "searches.jsonl"
        if not f.exists():
            continue
        rs = [r for r in map(json.loads, open(f)) if r.get("kind") == "search"]
        if max(r["day"] for r in rs) < 31:
            continue
        days = {}
        for r in rs:
            x = days.setdefault(r["day"], [0, 0, 0, 0, 0])
            x[0] += 1
            x[1] += r["rooms_opened"][:1] == [r["true_room"]]
            x[2] += r["found_it"]
            if r["is_a_mover"]:
                x[3] += 1
                x[4] += r["rooms_opened"][:1] == [r["true_room"]]
        out.setdefault(name, {})[hh] = {str(k): v for k, v in sorted(days.items())}
print(json.dumps(out))
