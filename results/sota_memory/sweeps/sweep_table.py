"""Tables for the two counting-method sweeps. Per config dir: per household accuracy in each window, then mean and standard
error across households (n=10). Windows from the config: settled = last 5 lead-up days; break = first 3 sick days (or the
whole spell if shorter); relearn = last 3 sick days; return break = first 3 days back. Also mean questions per day.
Cold = first question about an object that day. Usage: python3 sweep_table.py DIR [DIR ...]"""
import json, glob, sys, statistics as st, yaml, collections
AG = {'TimetableLookup(bin=2h,days=all)': 'timetable, never forgets', 'TimetableLookup(bin=2h,days=all,hl=72h)': 'timetable, 3-day memory',
      'MostFrequentLocation': 'most frequent, never forgets', 'PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)': 'survival-time (Perpetua*)'}
def windows(cfg):
    cal = {c['name']: c['days'] for c in cfg['calendar']}
    s0, s1 = cal['sick']; r0 = cal['return'][0]; L = s1 - s0 + 1
    return [('settled', 9, 13), ('break', s0, s0 + min(2, L - 1)), ('relearn', max(s0, s1 - 2), s1), ('return break', r0, r0 + 2)]
for d in sys.argv[1:]:
    cfg = yaml.safe_load(open(f'{d}/config.yaml')); W = windows(cfg)
    logs = sorted(glob.glob(f'{d}/classical/*.jsonl'))
    per = collections.defaultdict(lambda: collections.defaultdict(list)); qpd = []
    for f in logs:
        rows = [json.loads(l) for l in open(f)]
        byag = collections.defaultdict(list)
        for r in rows: byag[r['belief']].append(r)
        any_ag = next(iter(byag.values())); qpd.append(len(any_ag) / cfg['days'])
        for ag, name in AG.items():
            rs = sorted(byag.get(ag, []), key=lambda r: r['t_query']); seen = set()
            for r in rs:
                k = (r['day_index'], r['object_id']); r['_cold'] = k not in seen; seen.add(k)
            for w, a, b in W:
                for tag, sel in (('all', lambda r: True), ('cold', lambda r: r['_cold'])):
                    x = [r['correct'] for r in rs if a <= r['day_index'] <= b and sel(r)]
                    if x: per[(name, tag)][w].append(100 * sum(x) / len(x))
    print(f"\n== {d}  (n={len(logs)} households, {st.mean(qpd):.1f} questions/day, gap {cfg.get('question_min_gap_min')} min, days {cfg['days']})")
    print("method".ljust(34) + "".join(f"{w:>18s}" for w, *_ in W) + f"{'break size':>13s}{'return drop':>13s}")
    for tag in ('all', 'cold'):
        for name in AG.values():
            m = per[(name, tag)]
            if not m: continue
            cells = "".join(f"{st.mean(m[w]):>11.0f} ±{st.stdev(m[w]) / len(m[w]) ** .5:>3.0f}  " for w, *_ in W)
            brk = [a - b for a, b in zip(m['settled'], m['break'])]; ret = [a - b for a, b in zip(m['relearn'], m['return break'])]
            print(f"{(name + ' [' + tag + ']'):34s}{cells}{st.mean(brk):>9.0f} ±{st.stdev(brk) / len(brk) ** .5:.0f}{st.mean(ret):>9.0f} ±{st.stdev(ret) / len(ret) ** .5:.0f}")
