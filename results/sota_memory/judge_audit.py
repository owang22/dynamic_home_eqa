"""Audit the validity-window judge in facts_zep_mech runs: every closure (INVALIDATE) reconstructed from the revision
prompt and its decision. For each closure: did the night's rule-made facts for that object still put it at the SAME spot
(a false closure), (a) same spot at all, (b) same spot with hours overlapping >= 50% of the shorter interval?
And for facts whose spot really changed (no same-spot new fact, overlapping hours), how many nights until closed?
Usage: python3 judge_audit.py GLOB_OF_RUN_DIRS"""
import json, re, sys, glob, collections
def hrs(s):
    a, b = s.split('-'); return int(a[:2]), int(b[:2])
def overlap(x, y):
    (a1, b1), (a2, b2) = hrs(x), hrs(y); o = max(0, min(b1, b2) - max(a1, a2)); m = min(b1 - a1, b2 - a2) or 1
    return o / m
def stage(d): return 'lead-up (1-13)' if d < 14 else ('sick (14-23)' if d < 24 else 'back (24-31)')
for run in sorted(glob.glob(sys.argv[1])):
    hh = run.split('/')[-1].split('_t03')[0]
    tally = collections.defaultdict(lambda: collections.Counter())
    open_real = {}   # (obj, fact id) -> night first seen contradicted
    lags = []
    for l in open(f'{run}/calls.jsonl'):
        x = json.loads(l)
        if not x['where'].startswith('facts revise day'): continue
        day = int(x['where'].split()[-1]); m = x['messages'][1]['content']
        try: dec = json.loads(x['completion'])
        except Exception: continue
        olds, news, obj = {}, collections.defaultdict(list), None
        for line in m.splitlines():
            if re.match(r'^\S+:$', line): obj = line[:-1]; continue
            mo = re.match(r'^  old (f\d+): (\S+), (\d\d:\d\d-\d\d:\d\d)', line)
            if mo and obj: olds[mo.group(1)] = (obj, mo.group(2), mo.group(3))
            mn = re.match(r'^  new (n\d+): (\S+), (\d\d:\d\d-\d\d:\d\d)', line)
            if mn and obj: news[obj].append((mn.group(2), mn.group(3)))
        closed = {d['old'] for d in dec.get('old_facts', []) if d.get('op') == 'INVALIDATE'}
        for fid, (o, spot, h) in olds.items():
            same_any = any(s == spot for s, _ in news[o])
            same_ov = any(s == spot and overlap(h, hh2) >= 0.5 for s, hh2 in news[o])
            really_changed = not same_ov
            st = stage(day); t = tally[st]
            if fid in closed:
                t['closures'] += 1; t['false_same_spot'] += same_any; t['false_same_spot_overlap'] += same_ov
            if really_changed:
                t['contradicted'] += 1; t['contradicted_closed'] += fid in closed
                open_real.setdefault(fid, day)
                if fid in closed: lags.append((st, day - open_real[fid]))
            else:
                t['agreeing'] += 1; t['agreeing_closed'] += fid in closed
    print(hh)
    for st in ('lead-up (1-13)', 'sick (14-23)', 'back (24-31)'):
        t = tally[st]
        if not t: continue
        c = t['closures'] or 1
        print(f"  {st:15s} closures {t['closures']:4d} | false (same spot) {100*t['false_same_spot']/c:.0f}% | false (same spot, hours overlap) {100*t['false_same_spot_overlap']/c:.0f}%"
              f" | closed when really contradicted {t['contradicted_closed']}/{t['contradicted']} ({100*t['contradicted_closed']/max(1,t['contradicted']):.0f}%)"
              f" | closed when agreeing {t['agreeing_closed']}/{t['agreeing']} ({100*t['agreeing_closed']/max(1,t['agreeing']):.0f}%)")
    lg = collections.defaultdict(list)
    for st, d in lags: lg[st].append(d)
    print('  nights from first contradiction to closure:', {k: dict(collections.Counter(v)) for k, v in lg.items()})
