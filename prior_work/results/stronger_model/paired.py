"""Paired within-household differences, first room right (and found within 3), over the households where both
cells have finished all 31 days. Mean difference, its standard error over households, and how many households
share the sign. One cell per household per arm, so the per-household rerun spread (up to ~6 points) applies.
    PYTHONPATH=src python3 results/stronger_model/paired.py"""
import json, pathlib, statistics as st
R = pathlib.Path("results")
C = {
    "qwen log only": R / "self_improve/wave_log_only/cells/log_only_no_notes",
    "qwen log only rerun2 (fresh cache)": R / "stronger_model/qwen38_plain_rerun2/cells/log_only_no_notes",
    "qwen log+notes T1 (old schema)": R / "self_improve/overnight_wave/cells/the_log_and_notes_about_the_routine",
    "qwen log+notes rerun": R / "stronger_model/qwen38_plain/cells/the_log_and_notes_about_the_routine",
    "qwen think4000 log only": R / "stronger_model/qwen38_think4000/cells/log_only_no_notes",
    "qwen think4000 log+notes": R / "stronger_model/qwen38_think4000/cells/the_log_and_notes_about_the_routine",
    "sonnet log only": R / "stronger_model/claude_sonnet/cells/log_only_no_notes",
    "sonnet log+notes": R / "stronger_model/claude_sonnet/cells/the_log_and_notes_about_the_routine",
}
HH = ["hh_s2_t03", "hh_s19_t03", "hh_s20_t03"]
W = {"all 1-31": range(1, 32), "settled 8-13": range(8, 14), "illness 14-23": range(14, 24),
     "15-17": range(15, 18), "return 24-31": range(24, 32), "25-27": range(25, 28)}

def score(cell, hh, days, key, movers):
    f = C[cell] / hh / "searches.jsonl"
    if not f.exists():
        return None
    rs = [r for r in map(json.loads, open(f)) if r.get("kind") == "search"]
    if max((r["day"] for r in rs), default=0) < 31:
        return None
    rs = [r for r in rs if r["day"] in days and (r["is_a_mover"] or not movers)]
    if not rs:
        return None
    ok = (lambda r: r["rooms_opened"][:1] == [r["true_room"]]) if key == "first" else (lambda r: r["found_it"])
    return 100 * sum(map(ok, rs)) / len(rs)

PAIRS = [("qwen log only rerun2 (fresh cache)", "qwen log only"), ("sonnet log only", "qwen log only rerun2 (fresh cache)"),
         ("sonnet log only", "qwen log only"), ("sonnet log+notes", "sonnet log only"),
         ("sonnet log+notes", "qwen log+notes rerun"), ("sonnet log+notes", "qwen log+notes T1 (old schema)"),
         ("qwen log+notes rerun", "qwen log only"), ("qwen think4000 log only", "qwen log only"),
         ("qwen think4000 log+notes", "qwen log+notes rerun")]
for key in ("first", "found"):
    for movers in (False, True):
        print(f"\n### {'first room right' if key == 'first' else 'found within 3'}, {'movers only' if movers else 'all questions'}")
        print(f"{'A - B':62s}" + "".join(f"{w:>22s}" for w in W))
        for a, b in PAIRS:
            cols = []
            for w, days in W.items():
                ds = [(sa - sb) for hh in HH if (sa := score(a, hh, days, key, movers)) is not None
                      and (sb := score(b, hh, days, key, movers)) is not None]
                if not ds:
                    cols.append(f"{'-':>22s}")
                    continue
                se = st.stdev(ds) / len(ds) ** 0.5 if len(ds) > 1 else float("nan")
                pos = sum(d > 0 for d in ds)
                cols.append(f"{st.mean(ds):+6.1f} se{se:4.1f} {pos}/{len(ds)}+".rjust(22))
            print(f"{a + ' - ' + b:62s}" + "".join(cols))
