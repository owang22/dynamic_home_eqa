"""Streaming read of the runs in progress against the stated expectations.

    python3 results/confidence_shift_2026-09-20/live_affected.py [--dir heldout_p8]

Per household and day: accuracy and mean confidence on AFFECTED vs UNAFFECTED questions (the peer's
labels) for last seen (reference), the naive LLM (from calls.jsonl, partial), and the mixture arms
(from live.jsonl, partial). Flags: naive above last seen on affected; mixture confidence on affected not
below unaffected; a day with zero affected questions is left blank.
"""
import argparse
import glob
import json
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "src"))
from baselines.patrol.run import spots_only  # noqa: E402

NAMES = {1: "Wed", 2: "Thu", 3: "Fri", 4: "Sat", 5: "Sun", 6: "Mon", 7: "Tue"}


def load_labels(suffix="p8"):
    lab = {}
    path = next(q for q in (ROOT / f"followon/affected/labels_{suffix}.jsonl", ROOT / "followon/affected/labels.jsonl") if q.exists())
    for l in open(path):
        r = json.loads(l)
        lab[(r["household"], r["question_id"])] = r["affected"]
    return lab


def cell(c):
    return f"{100 * c['ok'] / c['n']:3.0f}% c{100 * c['conf'] / c['n']:3.0f} ({c['n']:2d})" if c["n"] else "      -       "


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="heldout_p8")
    ap.add_argument("--hh", default=None)
    a = ap.parse_args()
    D = ROOT / a.dir
    suffix = "p8" if "p8" in a.dir else "p2"
    lab = load_labels(suffix)
    flags = []
    for cl in sorted(D.glob("classical/hh_s1[0-4]_*.jsonl")):
        hh = cl.name.split("_")[0] + "_" + cl.name.split("_")[1]
        if a.hh and hh != a.hh:
            continue
        truth = {}
        agents = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"n": 0, "ok": 0, "conf": 0.0})))
        for l in open(cl):
            r = json.loads(l)
            truth[r["question_id"]] = r["truth"]
            if r["belief"].startswith("LastObs"):
                k = "aff" if lab.get((hh, r["question_id"])) else "un"
                c = agents["last seen"][r["day_index"]][k]
                c["n"] += 1; c["ok"] += r["correct"]; c["conf"] += r["top_prob"]
        for arm in ("told", "nottold"):
            p = D / "llm" / f"{hh}_{suffix}_naive_{arm}_lookoff" / "calls.jsonl"
            if p.exists():
                for l in open(p):
                    cr = json.loads(l)
                    try:
                        o = json.loads(cr["completion"])
                    except Exception:
                        continue
                    q = cr["where"]
                    if q not in truth:
                        continue
                    k = "aff" if lab.get((hh, q)) else "un"
                    c = agents[f"naive {arm}"][int(q[1])][k]
                    c["n"] += 1; c["ok"] += o["location"] == truth[q]; c["conf"] += float(o["confidence"])
            p = D / "hyp/study" / f"{hh}_{suffix}__bank0/arms/passive" / f"passive__longleaf__longleaf_named__{arm}" / "live.jsonl"
            if p.exists():
                for l in open(p):
                    try:
                        r = json.loads(l)
                    except ValueError:
                        continue
                    dist, _ = spots_only({k2: float(v) for k2, v in r["dist"].items()})
                    ans = max(dist, key=lambda k2: (dist[k2], k2)) if dist else r["argmax"]
                    k = "aff" if lab.get((hh, r["question_id"])) else "un"
                    c = agents[f"mixture {arm}"][r["day"]][k]
                    c["n"] += 1; c["ok"] += ans == truth[r["question_id"]]; c["conf"] += dist.get(ans, 0.0)
        print(f"\n=== {hh} ({a.dir})   cells: accuracy  c=mean confidence  (n)")
        print(f"  {'agent':16s}" + "".join(f"| {NAMES[d]:^30s}" for d in range(1, 8)))
        print(f"  {'':16s}" + "".join(f"| {'affected':^14s} {'unaffected':^14s} " for d in range(1, 8)))
        for ag in ["last seen", "naive told", "naive nottold", "mixture told", "mixture nottold"]:
            if ag not in agents:
                continue
            print(f"  {ag:16s}" + "".join(f"| {cell(agents[ag][d]['aff'])} {cell(agents[ag][d]['un'])} " for d in range(1, 8)))
        # flags
        for d in range(1, 8):
            ls = agents["last seen"][d]["aff"]
            for ag in ("naive told", "naive nottold"):
                c = agents.get(ag, {}).get(d, {}).get("aff")
                if c and c["n"] >= 8 and ls["n"] and c["ok"] / c["n"] > ls["ok"] / ls["n"] + 0.15:
                    flags.append(f"{hh} {NAMES[d]}: {ag} affected {100 * c['ok'] / c['n']:.0f}% >> last seen {100 * ls['ok'] / ls['n']:.0f}% (n={c['n']})")
            for ag in ("mixture told", "mixture nottold"):
                ca = agents.get(ag, {}).get(d, {}).get("aff"); cu = agents.get(ag, {}).get(d, {}).get("un")
                if ca and cu and ca["n"] >= 8 and cu["n"] >= 8 and ca["conf"] / ca["n"] >= cu["conf"] / cu["n"]:
                    flags.append(f"{hh} {NAMES[d]}: {ag} confidence on affected ({100 * ca['conf'] / ca['n']:.0f}) not below unaffected ({100 * cu['conf'] / cu['n']:.0f})")
    print("\nFLAGS:" if flags else "\nFLAGS: none")
    for f in flags:
        print("  !", f)


if __name__ == "__main__":
    main()
