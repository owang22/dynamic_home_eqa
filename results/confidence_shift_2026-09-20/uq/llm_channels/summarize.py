"""summarize.py <rows.jsonl>: per-day accuracy and channel means, correct-vs-wrong separation per channel, E9 checks."""
import json, sys, collections
rows = [json.loads(l) for l in open(sys.argv[1])]
by = collections.defaultdict(list)
for r in rows:
    by[r["day_index"]].append(r)
def m(rs, k): return sum(r[k] for r in rs) / len(rs) if rs else float("nan")
print(f"{len(rows)} rows; days {sorted(by)}")
print("day  n  acc(greedy)  acc(mcq)  verbalized  agreement  token")
for d in sorted(by):
    rs = by[d]
    print(f"{d:3d} {len(rs):3d}  {100*m(rs,'correct'):5.0f}%      {100*m(rs,'mcq_correct'):5.0f}%    {m(rs,'top_prob'):.3f}      {m(rs,'conf_agree'):.3f}     {m(rs,'conf_token'):.3f}")
print("\nchannel: mean on correct vs wrong greedy answers (separation); token channel scored on the mcq answer too")
for k, ok in (("top_prob", "correct"), ("conf_agree", "correct"), ("conf_token", "correct"), ("conf_token", "mcq_correct")):
    c = [r for r in rows if r[ok]]; w = [r for r in rows if not r[ok]]
    print(f"  {k:10s} vs {ok:11s}: correct {m(c,k):.3f} (n={len(c)})  wrong {m(w,k):.3f} (n={len(w)})  sep {m(c,k)-m(w,k):+.3f}")
print("\nreliability bins (share) per channel")
for k in ("top_prob", "conf_agree", "conf_token"):
    cells = []
    for lo in (0, .2, .4, .6, .8):
        sub = [r for r in rows if lo <= r[k] < lo + 0.2 + (1e-9 if lo == .8 else 0)]
        cells.append(f"{100*m(sub,'correct'):.0f}% ({len(sub)})" if sub else "-")
    print(f"  {k:10s} " + " | ".join(cells))
if len(by) >= 2:
    d0, d1 = sorted(by)[:2]
    print(f"\nE9: verbalized day {d0} {m(by[d0],'top_prob'):.3f} vs day {d1} {m(by[d1],'top_prob'):.3f}; agreement {m(by[d0],'conf_agree'):.3f} vs {m(by[d1],'conf_agree'):.3f}; token {m(by[d0],'conf_token'):.3f} vs {m(by[d1],'conf_token'):.3f}; accuracy {100*m(by[d0],'correct'):.0f}% vs {100*m(by[d1],'correct'):.0f}%")
