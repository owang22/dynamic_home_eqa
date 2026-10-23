"""Fusion variants on labelled queries: python3 variants.py [query-subset: dev|test|all]"""
import sys, json
sys.path.insert(0, "/home/oliver/robot/dynamic_home_eqa/go2/lab_agent")
import memory as M, embeddings as E
def ranks(scored):
    out, i = {}, 0
    while i < len(scored):
        j = i
        while j < len(scored) and scored[j][0] == scored[i][0]:
            j += 1
        for _, pid in scored[i:j]:
            out[pid] = (i + j - 1) / 2 + 1
        i = j
    return out
L = json.load(open("labels.json"))
sub = sys.argv[1] if len(sys.argv) > 1 else "all"
DEV = list(L)[:15]
qs = [q for q in L if L[q]["relevant"] and (sub == "all" or (q in DEV) == (sub == "dev"))]
R = M.load()
cache = {}
def parts(q):
    if q not in cache:
        wh = M.word_hits(q, R, True)
        img = E.scores(q)
        cache[q] = (wh, img)
    return cache[q]
def rrf(q, wi=1.0, wt=1.0, depth=100, K=60):
    wh, img = parts(q)
    wr = ranks([(s, r["id"]) for s, _, r, _ in wh])
    top = sorted(img.items(), key=lambda z: -z[1])[:depth]
    ir = ranks([(s, i) for i, s in top])
    f = {i: wt * (1 / (K + wr[i]) if i in wr else 0) + wi * (1 / (K + ir[i]) if i in ir else 0) for i in set(wr) | set(ir)}
    return sorted(f, key=lambda i: -f[i])
def boost(q, beta=0.02, full_only=False):
    """image cosine + beta * (word score / best word score)."""
    wh, img = parts(q)
    best = max((s for s, *_ in wh), default=1)
    ws = {r["id"]: s / best for s, _, r, _ in wh if not full_only or s == best}
    f = {i: v + beta * ws.get(i, 0) for i, v in img.items()}
    return sorted(f, key=lambda i: -f[i])
V = {"b.03": lambda q: boost(q, .03), "b.05": lambda q: boost(q, .05), "b.06": lambda q: boost(q, .06), "b.08": lambda q: boost(q, .08), "b.12": lambda q: boost(q, .12), "rrf": lambda q: rrf(q), "rrf_img2": lambda q: rrf(q, wi=2), "rrf_img3": lambda q: rrf(q, wi=3),
     "rrf_k10": lambda q: rrf(q, K=10), "boost.01": lambda q: boost(q, .01), "boost.02": lambda q: boost(q, .02),
     "boost.04": lambda q: boost(q, .04), "boost.02full": lambda q: boost(q, .02, True),
     "images": lambda q: boost(q, 0)}
res = {v: [0, 0] for v in V}
for q in qs:
    rel = set(L[q]["relevant"])
    for v, fn in V.items():
        ids = fn(q)[:10]
        res[v][0] += len(rel & set(ids[:5])) / min(5, len(rel)); res[v][1] += len(rel & set(ids)) / min(10, len(rel))
print(sub, len(qs), " ".join(f"{v}={a/len(qs):.2f}/{b/len(qs):.2f}" for v, (a, b) in res.items()))
