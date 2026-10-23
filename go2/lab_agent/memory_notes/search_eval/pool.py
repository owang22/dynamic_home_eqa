import sys, json
sys.path.insert(0, "/home/oliver/robot/dynamic_home_eqa/go2/lab_agent")
import memory as M
Q = json.load(open("queries.json"))
R = M.load()
pools = {}
for q in Q:
    runs = {"words_old": M.search(q, k=20, recs=R, mode="words", synonyms=False),
            "words_syn": M.search(q, k=20, recs=R, mode="words"),
            "images": M.search(q, k=20, recs=R, mode="images"),
            "fused": M.search(q, k=20, recs=R, mode="fused")}
    seen, items = set(), []
    for name, hits in runs.items():
        for b in hits:
            if b["id"] not in seen:
                seen.add(b["id"]); items.append([b["id"], (b.get("match") or {}).get("across")])
    pools[q] = items
    print(q, len(items))
json.dump(pools, open("pools.json", "w"))
