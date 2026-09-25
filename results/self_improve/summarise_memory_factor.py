#!/usr/bin/env python3
"""The memory factor across households: does how you write the notes change what the notes contain?

Two ways of writing, same model, same household, same look stream, same words describing
what was seen. Only the instruction differs. We report paired within-household differences
with their standard error and n, because a pooled figure across a changing household set is
how this project has misled itself before.

    python3 results/self_improve/summarise_memory_factor.py results/self_improve/memory_factor_illness_v1
"""
import json, pathlib, sys, statistics, difflib

WHOLESALE, INCREMENTAL = "wholesale rewrite", "incremental edits"


def text_of(s):
    v = s.get("summary") or s.get("text") or ""
    return "\n".join(v) if isinstance(v, list) else str(v)


def one_household(d: pathlib.Path):
    diff = d / "diff.json"
    if not diff.exists():
        return None
    try:
        j = json.loads(diff.read_text())
    except json.JSONDecodeError:
        return None          # still being written
    row = {"household": j.get("household", d.name)}
    for arm, r in (j.get("runs") or {}).items():
        n = r.get("nightly") or []
        if not n:
            continue
        key = "w" if "wholesale" in arm else "i"
        row[f"{key}_nights"] = len(n)
        row[f"{key}_identical"] = sum(1 for x in n if x.get("identical_to_last_night"))
        row[f"{key}_failed"] = sum(1 for x in n if x.get("model_call_failed"))
        row[f"{key}_share_identical"] = row[f"{key}_identical"] / len(n)
    for key, sub in (("w", "wholesale_rewrite"), ("i", "incremental_edits")):
        p = d / sub / "notes.json"
        if p.exists():
            try:
                nd = json.loads(p.read_text())
            except json.JSONDecodeError:
                continue
            row[f"{key}_claims"] = len(nd.get("claims") or [])
            row[f"{key}_summaries"] = len(nd.get("nightly_summaries") or [])
    c = (j.get("comparison") or {})
    for k in ("share_of_edits_that_carried_something_new", "share_of_words_in_common",
              "the_ordinary_routine_claim_survives_in_wholesale",
              "the_ordinary_routine_claim_survives_in_incremental"):
        if k in c:
            row[k] = c[k]
    row["concerns"] = c.get("concerns") or j.get("concerns") or []
    return row


def paired(rows, a, b):
    """Within-household difference a - b, mean, standard error, n. Clustered on household
    because that is the unit that was randomised; per-question errors here run about four
    times too narrow."""
    ds = [r[a] - r[b] for r in rows if a in r and b in r]
    if len(ds) < 2:
        return None
    m = statistics.mean(ds)
    se = statistics.stdev(ds) / len(ds) ** 0.5
    return m, se, len(ds), ds


def main(root):
    root = pathlib.Path(root)
    rows = [r for r in (one_household(d) for d in sorted(root.iterdir()) if d.is_dir()) if r]
    if not rows:
        print(f"nothing finished yet under {root}")
        return 1
    print(f"{len(rows)} household(s) complete under {root}\n")
    hdr = (f"{'household':12s} {'nights':>6} {'copied verbatim':>16} {'':>6} {'claims held':>12} "
           f"{'failed calls':>13}")
    print(hdr); print("-" * len(hdr))
    print(f"{'':12s} {'':>6} {'wholesale':>9} {'incr':>6} {'wholesale/incr':>12} {'w / i':>13}")
    for r in rows:
        print(f"{r['household']:12s} {r.get('w_nights','-'):>6} "
              f"{r.get('w_identical','-'):>9} {r.get('i_identical','-'):>6} "
              f"{str(r.get('w_summaries','-'))+'/'+str(r.get('i_claims','-')):>12} "
              f"{str(r.get('w_failed','-'))+' / '+str(r.get('i_failed','-')):>13}")

    print("\nPAIRED WITHIN-HOUSEHOLD DIFFERENCES (mean, standard error, n)")
    p = paired(rows, "w_share_identical", "i_share_identical")
    if p:
        m, se, n, ds = p
        bar = "2 standard errors" if n >= 6 else "bigger than the spread"
        det = abs(m) > 2 * se if n >= 6 else abs(m) > statistics.stdev(ds)
        print(f"  share of nights that repeat the previous night, wholesale minus incremental:")
        print(f"    {m*100:+.1f} points  (standard error {se*100:.1f}, n={n})  "
              f"{'DETECTED' if det else 'not detected'} at the {bar} bar")
        print(f"    per household: {', '.join(f'{d*100:+.0f}' for d in ds)}")

    fails = sum(r.get("w_failed", 0) + r.get("i_failed", 0) for r in rows)
    print(f"\n  failed model calls across every arm and household: {fails}"
          f"{'  (so the repetition is the model, not a broken write path)' if fails == 0 else '  <-- INVESTIGATE'}")

    shares = [r["share_of_edits_that_carried_something_new"] for r in rows
              if "share_of_edits_that_carried_something_new" in r]
    if shares:
        print(f"\n  share of incremental edits carrying something new: "
              f"mean {statistics.mean(shares)*100:.0f}%, range {min(shares)*100:.0f}-{max(shares)*100:.0f}%, "
              f"n={len(shares)}")
        low = sum(1 for s in shares if s < 0.60)
        if low:
            print(f"    {low} of {len(shares)} households below 60%: the forced-edit rule is producing "
                  f"re-wordings rather than revision in those")

    allc = [c for r in rows for c in r["concerns"]]
    if allc:
        print("\n  concerns raised by the runs themselves:")
        for c in sorted(set(allc)):
            print(f"    - {c}  [{sum(1 for x in allc if x == c)} household(s)]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "results/self_improve/memory_factor_illness_v1"))
