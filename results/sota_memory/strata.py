"""Split questions into MOVED vs UNMOVED by the shift, from the run logs' own truth column (no hidden state needed):
for each question, the object's usual spot at this hour = the most frequent true location among that household's
lead-up questions (days 0-13) about the same object within +-1 h of clock time. MOVED = truth now != usual spot.
Usage: python3 strata.py BASE_GLOB ARM_GLOB   (paired per household on the question ids both answered)
Source of the classification: the BASE arm's `truth` column only, over the full-run lead-up. `truth` is the bank's true
location at question time, identical in every arm's log, so every arm gets the same moved/unmoved label for the same
question; no arm's answers are used. The base must be a full 32-day run (for example the recent-sightings list).
Each line also prints a POOLED figure (all households' questions together, with the total n). It is marked pooled and is NOT
comparable to the paired mean beside it; use it as a direction for thin cells (the unmoved questions in the spell)."""
import json, glob, sys, collections, statistics as st
W = [("lead", 9, 13), ("sick1", 14, 16), ("sick", 17, 23), ("ret1", 24, 26), ("ret", 27, 31)]
def win(d):
    for n, a, b in W:
        if a <= d <= b: return n
def usual(rows):
    lead = [r for r in rows if r['day_index'] < 14]
    def f(r):
        c = collections.Counter(x['truth'] for x in lead if x['object_id'] == r['object_id']
                                and min(abs(x['t_query'] % 86400 - r['t_query'] % 86400), 86400 - abs(x['t_query'] % 86400 - r['t_query'] % 86400)) <= 3600)
        return c.most_common(1)[0][0] if c else None
    return f
def load(p): return {json.loads(l)['question_id']: json.loads(l) for l in open(p)}
base = {p.split('/')[-2].split('_t03')[0]: load(p) for p in glob.glob(sys.argv[1])}
arm = {p.split('/')[-2].split('_t03')[0]: load(p) for p in glob.glob(sys.argv[2])}
out = collections.defaultdict(list)
for hh in sorted(set(base) & set(arm)):
    B, A = base[hh], arm[hh]
    u = usual(list(B.values()))
    cells = collections.defaultdict(lambda: [0, 0, 0])
    for qid in set(B) & set(A):
        r = B[qid]; w = win(r['day_index'])
        if not w: continue
        s = 'moved' if r['truth'] != u(r) else 'unmoved'
        c = cells[(w, s)]; c[0] += B[qid]['correct']; c[1] += A[qid]['correct']; c[2] += 1
    for (w, s), (b, a, n) in sorted(cells.items()):
        out[(w, s)].append((hh, 100 * b / n, 100 * a / n, n))
for (w, s) in sorted(out, key=lambda k: ([x[0] for x in W].index(k[0]), k[1])):
    v = out[(w, s)]; d = [a - b for _, b, a, _ in v]
    sd = st.stdev(d) if len(d) > 1 else float('nan')
    N = sum(n for *_, n in v)
    pb = sum(b * n for _, b, _, n in v) / N; pa = sum(a * n for _, _, a, n in v) / N
    print(f"{w:6s} {s:8s} " + "  ".join(f"{hh}: {b:.0f}->{a:.0f} (n{n})" for hh, b, a, n in v)
          + f"   paired mean diff {st.mean(d):+.1f}, spread {sd:.1f} | POOLED {pb:.0f}->{pa:.0f} (n{N})")
