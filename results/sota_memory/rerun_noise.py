"""Rerun noise floor: the SAME arm (the recent-sightings list), same data, same days, generated twice — the workshop
session's run1 (older server load) vs a fresh run tonight (nottold_rerun). Per household and window: accuracy of each,
the difference, and the share of questions whose answer changed. Also flags which fresh answers were cache hits shared
with another arm (prompts byte-identical to the corrected-card arm before day 14 on hh_s0-2)."""
import json, glob, statistics as st
FMR = '/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/run1'
W = [("lead 11-13", 11, 13), ("sick 14-16", 14, 16), ("sick 17,21,22", 17, 23), ("ret 24-26", 24, 26), ("ret 27-28", 27, 28), ("ALL", 0, 99)]
rows = {}
for f in sorted(glob.glob('nottold_rerun/hh_s*_t03_naive_nottold_lookoff/run_log.jsonl')):
    hh = f.split('/')[-2].split('_t03')[0]
    A = {json.loads(l)['question_id']: json.loads(l) for l in open(f)}
    B = {json.loads(l)['question_id']: json.loads(l) for l in open(f'{FMR}/{hh}_t03_naive_nottold_lookoff/run_log.jsonl')}
    rows[hh] = (A, B)
for w, a, b in W:
    d, ch, line = [], [], []
    for hh, (A, B) in rows.items():
        q = [k for k, r in A.items() if a <= r['day_index'] <= b]
        if not q: continue
        acc_a = 100 * sum(A[k]['correct'] for k in q) / len(q); acc_b = 100 * sum(B[k]['correct'] for k in q) / len(q)
        chg = 100 * sum(A[k]['answer'] != B[k]['answer'] for k in q) / len(q)
        d.append(acc_a - acc_b); ch.append(chg); line.append(f"{hh}:{acc_b:.0f}->{acc_a:.0f} chg{chg:.0f}%(n{len(q)})")
    if d:
        sd = st.stdev(d) if len(d) > 1 else float('nan')
        print(f"{w:14s} " + "  ".join(line) + f"  | acc diff mean {st.mean(d):+.1f}, mean |diff| {st.mean(map(abs, d)):.1f}, spread {sd:.1f} | answers changed {st.mean(ch):.0f}%")
