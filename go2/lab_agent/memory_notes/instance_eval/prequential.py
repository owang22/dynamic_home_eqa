"""Prequential check of P(still there): for every instance and every later picture that covers its position,
predict from what was known before that picture (last sighting before it, misses before it), then compare with
whether that picture shows it (it is one of the instance's sightings, or its description names that kind).
Reports AUC and Brier score for the persistence model and simpler baselines.
    python3 go2/lab_agent/memory_notes/instance_eval/prequential.py"""
import sys, json, math
sys.path.insert(0, "/home/oliver/robot/dynamic_home_eqa/go2/lab_agent")
import memory as M, memory_instances as I

recs = M.load()
by = {r["id"]: r for r in recs}
described = sorted((r for r in recs if r.get("seen")), key=lambda r: r["t"])
G = I.grid()
insts = I.load_instances()
rows = []
for i in insts:
    own = set(i["pictures"])
    t_seen = sorted(by[p]["t"] for p in own)
    cov = [r for r in described if r["t"] > t_seen[0] and (r["id"] in own or I.covers(r, i["x"], i["y"], G, i["name"] in I.SMALL))]
    misses = later = 0
    last = t_seen[0]
    seen_visits = set()
    for r in cov:
        hit = r["id"] in own or I.lists(r, i["name"], I.colour_key(i["colour"]))
        h = (r["t"] - last) / 3600
        rows.append({"name": i["name"], "hours": h, "misses": misses, "later": later, "hit": hit,
                     "same_day": M.clock(r["t"])[:14] == M.clock(last)[:14]})
        if hit:
            last, misses, later = r["t"], 0, 0
            seen_visits = set()
        elif I.visit(r["t"]) not in seen_visits:     # misses in one visit count once (as in build)
            seen_visits.add(I.visit(r["t"]))
            misses += 1
            later += I.day(r["t"]) != I.day(last)


def auc(ps, ys):
    pos = [p for p, y in zip(ps, ys) if y]; neg = [p for p, y in zip(ps, ys) if not y]
    if not pos or not neg:
        return float("nan")
    s = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg)
    return s / (len(pos) * len(neg))


ys = [r["hit"] for r in rows]
base = sum(ys) / len(ys)
models = {
    "constant (base rate)": lambda r: base,
    "time decay only": lambda r: I.p_still(r["name"], r["hours"], 0),
    "misses only (no time)": lambda r: 1 / (1 + 1 / (I.miss_lr(r["name"]) ** r["misses"])),
    "persistence model (time + misses)": lambda r: I.p_still(r["name"], r["hours"], r["misses"], r["later"]),
}
out = [f"{len(rows)} (instance, covering picture) pairs from {len(insts)} instances; shown in {sum(ys)} ({base:.2f})"]
for name, f in models.items():
    ps = [f(r) for r in rows]
    brier = sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ys)
    out.append(f"  {name:36} AUC {auc(ps, ys):.3f}  Brier {brier:.3f}")
for sd in (True, False):
    sub = [r for r in rows if r["same_day"] == sd]
    if sub:
        out.append(f"  {'same day' if sd else 'later day'}: {len(sub)} pairs, shown {sum(r['hit'] for r in sub) / len(sub):.2f}; "
                   f"model AUC {auc([I.p_still(r['name'], r['hours'], r['misses'], r['later']) for r in sub], [r['hit'] for r in sub]):.3f}")
for m in range(4):
    sub = [r for r in rows if min(r["misses"], 3) == m]
    if sub:
        out.append(f"  after {m}{'+' if m == 3 else ''} misses: {len(sub)} pairs, shown next {sum(r['hit'] for r in sub) / len(sub):.2f}")
print("\n".join(out))

# static kinds: P(shown | covered) when they are surely still there -> COVER_TRUE * recall
STATIC = {"sofa", "fire extinguisher", "printer", "whiteboard", "television", "fridge", "bookshelf", "vacuum cleaner"}
print("static kinds, shown rate when covered (they do not move):")
for sd in (True, False):
    sub = [r for r in rows if r["name"] in STATIC and r["same_day"] == sd]
    if sub:
        sh = sum(r["hit"] for r in sub) / len(sub)
        rc = sum(I.DESCRIBE_RECALL.get(r["name"], I.DEFAULT_RECALL) for r in sub) / len(sub)
        print(f"  {'same day' if sd else 'later day'}: {len(sub)} pairs, shown {sh:.2f}, mean recall {rc:.2f} -> cover factor {sh / rc:.2f}")
ps = [I.p_still(r["name"], r["hours"], r["misses"], r["later"]) * I.COVER_TRUE * I.DESCRIBE_RECALL.get(r["name"], I.DEFAULT_RECALL) for r in rows]
print(f"predicting 'shown' as p_still * COVER_TRUE * recall: Brier {sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ys):.3f} "
      f"(constant {sum((base - y) ** 2 for y in ys) / len(ys):.3f}), AUC {auc(ps, ys):.3f}")

MOVABLE = {"backpack", "bag", "laptop", "jacket", "clothing", "bottle", "cup", "phone", "case", "camera", "tripod",
           "robot", "paper bag", "tote bag", "plastic bag", "key", "mouse", "keyboard", "tool", "tape", "storage bin"}
for label, keep in (("movable kinds", lambda r: r["name"] in MOVABLE), ("static kinds", lambda r: r["name"] in STATIC)):
    sub = [r for r in rows if keep(r)]
    yy = [r["hit"] for r in sub]
    print(f"{label}: {len(sub)} pairs, shown {sum(yy) / len(yy):.2f}; AUC " + ", ".join(
        f"{n} {auc([f(r) for r in sub], yy):.3f}" for n, f in models.items() if n != "constant (base rate)"))

fin = [i for i in insts if i["name"] in STATIC]
print(f"static instances at the end: {len(fin)}, p_still < 0.3 for {sum(i['p_still'] < 0.3 for i in fin)} "
      f"(these do not move, so every one is a false 'gone')")
