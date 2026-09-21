"""Progress of the running hypothesis-mixture arms, from their live.jsonl streams.

    python3 results/confidence_shift_2026-09-20/live_progress.py [--tail 8] [--hh hh_s10]

Per household and day: answers so far, accuracy of told / not told / most frequent / naive LLM
on the SAME questions, the mixture's probability on its answer, the library agreement, the
effective number of documents, and revisions made. Then the latest answers with clock time.
"""
import argparse
import glob
import json
import pathlib
import re
import sys
from collections import defaultdict

R = pathlib.Path(__file__).resolve().parent / "heldout"
sys.path.insert(0, str(R.parents[2] / "src"))
from baselines.patrol.run import spots_only  # noqa: E402

DAYS = {}


def clock(t):
    m = (t % 86400) // 60
    return f"{m // 60:02d}:{m % 60:02d}"


def load_live(p):
    rows = []
    for l in open(p):
        try:
            rows.append(json.loads(l))
        except ValueError:
            pass
    return rows


def answer_of(r):
    dist, _ = spots_only({k: float(v) for k, v in r["dist"].items()})
    a = max(dist, key=lambda k: (dist[k], k)) if dist else r["argmax"]
    return a, dist.get(a, 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tail", type=int, default=6)
    ap.add_argument("--hh", default=None)
    a = ap.parse_args()
    for study in sorted(glob.glob(str(R / "hyp/study/*__bank0"))):
        hh = pathlib.Path(study).name.split("_p2")[0]
        if a.hh and hh != a.hh:
            continue
        bank = [json.loads(l) for l in open(R / "banks" / f"{hh}_p2.jsonl")]
        hdr = bank[0]
        qs = {q["question_id"]: q for q in bank if q["kind"] == "question"}
        names = {int(k): v[:3] for k, v in hdr["day_names"].items()}
        truth, ref = {}, defaultdict(dict)
        for l in open(R / "classical" / f"{hh}_p2.jsonl"):
            r = json.loads(l)
            truth[r["question_id"]] = r["truth"]
            if r["belief"].startswith("MostFrequent"):
                ref["mf"][r["question_id"]] = r["correct"]
        for arm, lab in (("told", "nv_t"), ("nottold", "nv_n")):
            p = R / "llm" / f"{hh}_p2_naive_{arm}_lookoff" / "run_log.jsonl"
            if p.exists():
                for l in open(p):
                    r = json.loads(l)
                    ref[lab][r["question_id"]] = r["correct"]
        arms = {}
        for arm in ("told", "nottold"):
            p = pathlib.Path(study) / "arms/passive" / f"passive__longleaf__longleaf_named__{arm}" / "live.jsonl"
            if p.exists():
                arms[arm] = load_live(p)
        revs = {arm: sorted(glob.glob(f"{study}/arms/passive/passive__longleaf__longleaf_named__{arm}/revisions/*.json"))
                for arm in ("told", "nottold")}
        print(f"\n=== {hh}  shift days {[names[d] for d in hdr['shift_days']]}  events "
              f"{ {names[int(d)]: [c.split(':')[0] for c in v if c.split(':')[0] in ('sick_day', 'guest_visit')] for d, v in hdr['day_causes'].items() if any(c.split(':')[0] in ('sick_day', 'guest_visit') for c in v)} }"
              f"  answered: told {len(arms.get('told', []))}, not told {len(arms.get('nottold', []))} of {len(qs)}")
        print(f"  {'day':4s} {'n':>3s} | {'told':>5s} {'ntold':>5s} {'mostf':>5s} {'naive':>5s} | {'p_top':>5s} {'agree':>5s} {'ess':>4s} | {'p_top':>5s} {'agree':>5s} {'ess':>4s} | revisions told / not told")
        by = {arm: defaultdict(list) for arm in arms}
        for arm, rows in arms.items():
            for r in rows:
                by[arm][r["day"]].append(r)
        for d in sorted(set().union(*[set(b) for b in by.values()]) if by else []):
            cells = {}
            for arm in ("told", "nottold"):
                rows = by.get(arm, {}).get(d, [])
                if not rows:
                    cells[arm] = None
                    continue
                acc = sum(answer_of(r)[0] == truth[r["question_id"]] for r in rows) / len(rows)
                ptop = sum(answer_of(r)[1] for r in rows) / len(rows)
                agree = 0.0
                for r in rows:
                    ans = answer_of(r)[0]
                    own = r.get("own") or {}
                    if own:
                        agree += sum(r["weights"].get(n, 0.0) for n, (sp, _) in own.items()
                                     if sp not in ("ON_PERSON", "OUT_OF_HOUSE") and sp == ans)
                    else:
                        agree += answer_of(r)[1]
                agree /= len(rows)
                ess = sum(r["ess"] or 0 for r in rows) / len(rows)
                cells[arm] = (acc, ptop, agree, ess, [r["question_id"] for r in rows])
            base = cells.get("told") or cells.get("nottold")
            qids = base[4]
            mf = sum(ref["mf"].get(q, 0) for q in qids) / len(qids)
            nv = sum(ref["nv_t"].get(q, 0) for q in qids) / len(qids) if ref["nv_t"] else float("nan")
            t, n = cells.get("told"), cells.get("nottold")
            f = lambda c, i: f"{100 * c[i]:5.0f}" if c else "    -"
            g = lambda c, i: f"{c[i]:5.2f}" if c else "    -"
            rt = sum(1 for p in revs["told"] if json.load(open(p))["day"] == d)
            rn = sum(1 for p in revs["nottold"] if json.load(open(p))["day"] == d)
            print(f"  {names[d]:4s} {len(qids):3d} | {f(t, 0)} {f(n, 0)} {100 * mf:5.0f} {100 * nv:5.0f} | {f(t, 1)} {f(t, 2)} {(t[3] if t else 0):4.1f} | {f(n, 1)} {f(n, 2)} {(n[3] if n else 0):4.1f} | {rt} / {rn}")
        for arm, rows in arms.items():
            print(f"  latest {arm}:")
            for r in rows[-a.tail:]:
                ans, p = answer_of(r)
                q = qs[r["question_id"]]
                ok = "ok " if ans == truth[r["question_id"]] else "NO "
                top = max(r["weights"], key=lambda k: r["weights"][k]) if r.get("weights") else "?"
                print(f"    {names[r['day']]} {clock(r['t_query'])} {q['object_id']:22s} {q.get('moment', ''):16s} -> {ans:22s} p={p:4.2f} {ok} truth {truth[r['question_id']]:22s} top-doc {re.sub(r'.*\\((p_\\w+)\\).*', r'\\1', top)} ({100 * r['weights'].get(top, 0):.0f}%)")


if __name__ == "__main__":
    main()
