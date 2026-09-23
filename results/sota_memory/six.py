"""Six-household paired contrasts against the SAME-SESSION baseline (the recent-sightings list re-run tonight,
nottold_rerun), with the per-window noise floor (that baseline vs the workshop's older run of the same arm).
Per window: per-household differences, mean, standard error, spread, and |mean| / floor, where floor = mean absolute
per-household rerun difference in that window. Usage: python3 six.py ARM [ARM2 ...]  (arm = nocard, truecard, pinned)"""
import json, sys, statistics as st, os
FMR = '/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/run1'
W = [("lead 11-13", 11, 13), ("sick 14-16", 14, 16), ("sick 17,21,22", 17, 23), ("back 24-26", 24, 26), ("back 27-28", 27, 28)]
HH = [f"hh_s{i}" for i in range(6)]
def load(p): return {json.loads(l)['question_id']: json.loads(l) for l in open(p)} if os.path.exists(p) else None
def cold_ids(rows):
    seen, out = set(), set()
    for r in sorted(rows.values(), key=lambda r: r['t_query']):
        k = (r['day_index'], r['object_id'])
        if k not in seen: out.add(r['question_id'])
        seen.add(k)
    return out
base = {h: load(f'nottold_rerun/{h}_t03_naive_nottold_lookoff/run_log.jsonl') for h in HH}
old = {h: load(f'{FMR}/{h}_t03_naive_nottold_lookoff/run_log.jsonl') for h in HH}
cold = {h: cold_ids(old[h]) for h in HH}          # cold defined on the full 32-day run, same for every arm
def acc(R, ids): return 100 * sum(R[i]['correct'] for i in ids) / len(ids)
def window(h, a, b, arm_rows, cold_only):
    ids = [i for i, r in base[h].items() if a <= r['day_index'] <= b and i in arm_rows and (i in cold[h] or not cold_only)]
    return ids
for cold_only in (False, True):
    floors = {}
    for w, a, b in W:
        d = [abs(acc(base[h], ids) - acc(old[h], ids)) for h in HH if base[h] and (ids := window(h, a, b, base[h], cold_only))]
        floors[w] = st.mean(d) if d else float('nan')
    for arm in sys.argv[1:]:
        print(f"\n{arm} minus same-session recent-sightings list — {'COLD (first question about an object that day)' if cold_only else 'ALL questions'}")
        for w, a, b in W:
            per = []
            for h in HH:
                A = load(f'nottold/{h}_t03_{arm}_nottold_lookoff/run_log.jsonl')
                if not A or not base[h]: continue
                ids = window(h, a, b, A, cold_only)
                if ids: per.append((h, acc(base[h], ids), acc(A, ids), len(ids)))
            d = [x[2] - x[1] for x in per]
            if len(d) < 2: continue
            m, sd = st.mean(d), st.stdev(d); se = sd / len(d) ** 0.5
            bar = ("IDENTICAL (byte-identical prompts, shared cache)" if se == 0 and m == 0 else "detected (>=2 se)" if abs(m) >= 2 * se else "not detected")
            print(f"  {w:14s} n={len(d)}  " + " ".join(f"{b0:.0f}->{b1:.0f}" for _, b0, b1, _ in per)
                  + f" | mean {m:+.1f}, se {se:.1f}, spread {sd:.1f} -> {bar}; floor {floors[w]:.1f} -> {abs(m) / floors[w] if floors[w] else float('inf'):.0f}x floor")
