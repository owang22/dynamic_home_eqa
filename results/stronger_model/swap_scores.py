"""Two-by-two: who READS (the model choosing the first room) by whose RECORD it reads (which model's looking built
the record). First room right, %, per household and window, then paired means over households.
Own-record cells use the cell's actual first room; swapped cells use stronger_model/swap_records answers.
    python3 results/stronger_model/swap_scores.py"""
import json, pathlib, statistics as st
S = pathlib.Path("results/stronger_model/swap")
HH = ["hh_s2_t03", "hh_s19_t03", "hh_s20_t03"]
W = {"all 1-31": range(1, 32), "settled 8-13": range(8, 14), "illness 14-23": range(14, 24),
     "15-17": range(15, 18), "return 24-31": range(24, 32)}

def rows(record, reader, hh):
    if record == reader:
        rs = [json.loads(l) for l in open(S / f"prompts_from_{record}_{hh}.jsonl")]
        return [{**r, "room": r["own_first_room"]} for r in rs]
    f = S / f"answers_from_{record}_by_{reader}_{hh}.jsonl"
    return [json.loads(l) for l in open(f)] if f.exists() else []

def pct(rs, days, movers=False):
    xs = [r["room"] == r["true_room"] for r in rs if r["day"] in days and (r["is_a_mover"] or not movers)]
    return 100 * sum(xs) / len(xs) if xs else None

CELLS = [("qwen", "qwen"), ("qwen", "sonnet"), ("qwen2", "qwen2"), ("qwen2", "sonnet"), ("sonnet", "qwen"), ("sonnet", "sonnet")]
for movers in (False, True):
    print(f"\n## first room right, {'movers only' if movers else 'all questions'}; record built by X, read by Y")
    for hh in HH:
        print(f"  {hh}")
        for rec, rd in CELLS:
            rs = rows(rec, rd, hh)
            n = len(rs)
            print(f"    record {rec:6s} read by {rd:6s} (n={n:3d}) " + "  ".join(
                f"{w} {('%5.1f' % v) if (v := pct(rs, d, movers)) is not None else '  -  '}" for w, d in W.items()))
    print("  paired over households (mean, se, n households):")
    for label, (a, b) in {"reader effect on Qwen's record (sonnet - qwen)": (("qwen", "sonnet"), ("qwen", "qwen")),
                          "reader effect on Qwen's FRESH record (sonnet - qwen)": (("qwen2", "sonnet"), ("qwen2", "qwen2")),
                          "record effect, Sonnet reading (sonnet rec - qwen FRESH rec)": (("sonnet", "sonnet"), ("qwen2", "sonnet")),
                          "record effect, Qwen reading (sonnet rec - qwen FRESH rec)": (("sonnet", "qwen"), ("qwen2", "qwen2")),
                          "reader effect on Sonnet's record (sonnet - qwen)": (("sonnet", "sonnet"), ("sonnet", "qwen")),
                          "record effect, Qwen reading (sonnet rec - qwen rec)": (("sonnet", "qwen"), ("qwen", "qwen")),
                          "record effect, Sonnet reading (sonnet rec - qwen rec)": (("sonnet", "sonnet"), ("qwen", "sonnet"))}.items():
        cols = []
        for w, d in W.items():
            ds = []
            for hh in HH:
                ra, rb = rows(*a, hh), rows(*b, hh)
                if len(ra) == 248 and len(rb) == 248:
                    ds.append(pct(ra, d, movers) - pct(rb, d, movers))
            if ds:
                se = st.stdev(ds) / len(ds) ** .5 if len(ds) > 1 else float("nan")
                cols.append(f"{w} {st.mean(ds):+5.1f} (se {se:3.1f}, {sum(x > 0 for x in ds)}/{len(ds)}+)")
            else:
                cols.append(f"{w}   -  ")
        print(f"    {label:62s} " + "  ".join(cols))
