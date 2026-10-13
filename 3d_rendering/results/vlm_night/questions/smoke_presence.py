"""Smoke test on the six committed renders: yes/no 'is there a <type> in this picture?'
for things truly in view (>=300 px) and for other household types not on that spot."""
import json, random, sys, collections
import vlm
R = '/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/render_methods/habitat_hssd/'
v = json.load(open(R + 'views.json'))
snap = json.load(open('/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/lived_home/hssd_a/day_07/positions_1800.json'))
alltypes = sorted({o['type'] for o in snap['objects'].values()})
rng = random.Random(0)
think = len(sys.argv) > 1
res = collections.Counter()
for x in v['views']:
    if x['camera'] != 'high':
        continue
    here = {s['type'] for s in x['spot_things']}
    pos = sorted({s['type'] for s in x['spot_things'] if s['pixels'] >= 300})
    neg = rng.sample([t for t in alltypes if t not in here], 6)
    for t, truth in [(t, True) for t in pos] + [(t, False) for t in neg]:
        q = f"Is there a {t} anywhere in this picture? Answer yes or no."
        a, info = vlm.ask(q, [R + x['picture']], think=think, max_tokens=4000 if think else 10)
        said = 'yes' in a.lower()
        res[(truth, said)] += 1
        if said != truth:
            print(f"  wrong: {x['picture'].split('/')[-1]:<36} {t:<20} truth={truth} said={a.strip()[:30]}")
print('think' if think else 'no think', dict(res))
tp, fn, fp, tn = res[(True, True)], res[(True, False)], res[(False, True)], res[(False, False)]
print(f"seen when there: {tp}/{tp+fn}   said yes when absent: {fp}/{fp+tn}")
