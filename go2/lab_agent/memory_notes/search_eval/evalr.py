"""Recall@5/@10 of each search over the labelled queries. recall@k = relevant in top k / min(k, n relevant)."""
import sys, json
sys.path.insert(0, "/home/oliver/robot/dynamic_home_eqa/go2/lab_agent")
import memory as M
L = json.load(open("labels.json"))
R = M.load()
MODES = {"words_old": dict(mode="words", synonyms=False), "words_syn": dict(mode="words"),
         "images": dict(mode="images"), "fused": dict(mode="fused")}
extra = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
MODES.update(extra)
tot = {m: [0, 0, 0] for m in MODES}
rows = []
for q, lab in L.items():
    rel = set(lab["relevant"])
    if not rel:
        continue
    row = [q[:34], len(rel)]
    for m, kw in MODES.items():
        ids = [b["id"] for b in M.search(q, k=10, recs=R, **kw)]
        r5 = len(rel & set(ids[:5])) / min(5, len(rel)); r10 = len(rel & set(ids)) / min(10, len(rel))
        tot[m][0] += r5; tot[m][1] += r10; tot[m][2] += 1
        row += [f"{r5:.2f}/{r10:.2f}"]
    rows.append(row)
print(f"{'query':34} {'nrel':>4} " + " ".join(f"{m:>11}" for m in MODES))
for r in rows:
    print(f"{r[0]:34} {r[1]:>4} " + " ".join(f"{x:>11}" for x in r[2:]))
print(f"{'MEAN r@5/r@10':34} {len(rows):>4} " + " ".join(f"{t[0]/t[2]:.2f}/{t[1]/t[2]:.2f}".rjust(11) for t in tot.values()))
