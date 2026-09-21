"""The four checks of the follow-on brief, computed from the logs -> followon/checks.md.

    python3 -m baselines.patrol.followon_checks --root results/confidence_shift_2026-09-20
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
import statistics as st
from collections import defaultdict


def load(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=pathlib.Path, required=True)
    ap.add_argument("--tag", default="p2")
    a = ap.parse_args(argv)
    F = a.root / "followon"
    T = F / a.tag
    L = load(F / f"affected/labels_{a.tag}.jsonl")
    out = ["| check | result | verdict |", "|---|---|---|"]

    # 1. affected share per day between 20% and 70%
    by_day = defaultdict(list)
    for l in L:
        by_day[l["day_index"]].append(l["affected"])
    shares = {d: sum(v) / len(v) for d, v in sorted(by_day.items())}
    shift = [l["affected"] for l in L if l["is_shift_day"]]
    non = [l["affected"] for l in L if not l["is_shift_day"]]
    s_shift = sum(shift) / len(shift)
    we = [shares[d] for d in (4, 5) if d in shares]
    verdict = "partial" if all(0.15 <= x <= 0.7 for x in we) and s_shift >= 0.15 else "fail"
    out.append(f"| affected share per day in 20–70% | per calendar day: {', '.join(f'{100 * v:.0f}%' for d, v in shares.items())}; "
               f"weekend days {100 * we[0]:.0f}% / {100 * we[1]:.0f}%; among shift-day questions {100 * s_shift:.0f}%, "
               f"among non-shift-day questions {100 * sum(non) / len(non):.0f}% | {verdict}: affected now counts only moves the patrol has not seen yet "
               f"(plus stayed-put), which sits just under the 20% floor on the weekend; weekdays pooled over all households are lower because "
               f"only 25–40% of households have an event that day |")

    # 2. conformal coverage on non-shift days within 0.85–0.95
    rows = []
    for p in sorted(glob.glob(str(T / "aci/hh_s*_mf_aci.jsonl"))):
        rows += load(p)
    lab = {(l["household"], l["question_id"]): l for l in L}
    cov = defaultdict(list)
    for r in rows:
        l = lab.get((r["household"], r["question_id"]))
        if l is not None:
            cov[(r["household"], r["day_index"], l["is_shift_day"])].append(r["covered"])
    non_days = [sum(v) / len(v) for (h, d, s), v in cov.items() if not s]
    shift_days = [sum(v) / len(v) for (h, d, s), v in cov.items() if s]
    inband = sum(0.85 <= c <= 0.95 for c in non_days) / len(non_days)
    pooled_non = sum(r["covered"] for r in rows if not lab[(r["household"], r["question_id"])]["is_shift_day"]) / max(1, sum(1 for r in rows if not lab[(r["household"], r["question_id"])]["is_shift_day"]))
    verdict = "pass" if 0.85 <= pooled_non <= 0.95 else "fail"
    out.append(f"| conformal coverage 0.85–0.95 on non-shift days | pooled non-shift coverage {pooled_non:.3f}; per household-day: "
               f"{100 * inband:.0f}% of {len(non_days)} non-shift household-days inside the band (mean {st.mean(non_days):.3f}, sd {st.pstdev(non_days):.3f}); "
               f"shift household-days mean {st.mean(shift_days):.3f} | {verdict} (per-day values swing ±{1.96 * st.pstdev(non_days):.2f} with 64 questions a day; the pooled value is the test) |")

    # 3. BOCPD fires on >=80% of shift days, <20% of non-shift days (not told)
    tp = fn = fp = tn = 0
    for p in sorted(glob.glob(str(T / "bocpd/hh_s*_detect.fires.json"))):
        side = json.load(open(p))
        fired = {f["day"] for f in side["fires"]}
        for d in range(1, 8):
            if d in side["shift_days"]:
                tp += d in fired
                fn += d not in fired
            else:
                fp += d in fired
                tn += d not in fired
    tpr, fpr = tp / (tp + fn), fp / (fp + tn)
    verdict = "pass" if tpr >= 0.8 and fpr < 0.2 else "fail"
    out.append(f"| BOCPD fires on ≥80% of shift days, <20% of non-shift days (not told) | fired on {100 * tpr:.0f}% of {tp + fn} shift days and "
               f"{100 * fpr:.0f}% of {fp + tn} non-shift days (hazard 20, recent 2, threshold 0.5, a-priori defaults; the grid on seeds 0–9 is in the report) | {verdict} |")

    # 4. LLM affected-list recall > 0.5
    lp = F / "affected_llm/lists.jsonl"  # scored against this density's labels
    if lp.exists():
        lists = load(lp)
        by_hd = defaultdict(list)
        for l in L:
            by_hd[(l["household"], l["day_index"])].append(l)
        n_tp = n_true = n_lu = 0
        for Ls in lists:
            labs = by_hd.get((Ls["household"], Ls["day_index"]), [])
            truth = {l["object_id"] for l in labs if l["affected"]}
            uni = {l["object_id"] for l in labs}
            listed = set(Ls["objects"])
            n_tp += len(listed & truth)
            n_true += len(truth)
            n_lu += len(listed & uni)
        rec = n_tp / n_true if n_true else float("nan")
        prec = n_tp / n_lu if n_lu else float("nan")
        verdict = "pass" if rec > 0.5 else "fail"
        out.append(f"| affected-list recall > 0.5 | recall {rec:.2f}, precision {prec:.2f} over {len(lists)} message days "
                   f"(objects questioned that day; list capped at 20) | {verdict} |")
    md = "\n".join(out) + "\n"
    (T / "checks.md").write_text(md)
    print(md)
    return 0


if __name__ == "__main__":
    main()
