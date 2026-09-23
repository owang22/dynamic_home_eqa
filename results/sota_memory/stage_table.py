"""Per-household accuracy (all | cold) by window for arms in results dirs. cold = first question about an object that day.
Windows: lead 9-13, sick1 14-16, sick 17-23, ret1 24-26, ret 27-31."""
import json, glob, sys, collections
W = [("lead", 9, 13), ("sick1", 14, 16), ("sick", 17, 23), ("ret1", 24, 26), ("ret", 27, 31)]
def win(d):
    for n, a, b in W:
        if a <= d <= b: return n
def table(path):
    rows = [json.loads(l) for l in open(path)]
    seen, agg = set(), collections.defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        k = (r['day_index'], r['object_id']); cold = k not in seen; seen.add(k)
        w = win(r['day_index'])
        if not w: continue
        a = agg[w]; a[0] += r['correct']; a[1] += 1
        if cold: a[2] += r['correct']; a[3] += 1
    return {w: (100 * a[0] / a[1], 100 * a[2] / a[3] if a[3] else float('nan'), a[1]) for w, a in agg.items()}, len(rows)
if __name__ == "__main__":
    for pat in sys.argv[1:]:
        for f in sorted(glob.glob(pat)):
            t, n = table(f)
            print(f.split('/')[-2][:40].ljust(40), n, "  ".join(f"{w}:{t[w][0]:.0f}|{t[w][1]:.0f}" for w, *_ in W if w in t))
