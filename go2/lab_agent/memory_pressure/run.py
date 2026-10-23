"""Memory pressure, offline (2026-10-23): replay the lab agent's stored pictures in time order, keep only a budget of
them with each retention policy, and score what each policy kept.

    CUDA_VISIBLE_DEVICES= python3 go2/lab_agent/memory_pressure/run.py            # all policies x budgets
    CUDA_VISIBLE_DEVICES= python3 go2/lab_agent/memory_pressure/run.py --selftest # small checks, about 1 min

Read-only on go2/data/lab_agent/ (index, embeddings, instances, search labels). Never talks to the console or a vision
server. The SigLIP picture embeddings already exist; only the 40 query texts are embedded, on the CPU, once (cached).

Tiers:  L1 = the picture, its description and embedding (what search and Opus see today)
        L2 = embedding + one-line summary, no image (cheap; search can still find it, Opus can't look at it)
        gone = discarded
A policy sees one picture at a time (observe) and must stay within its L1 budget after each one.

Writes go2/data/memory_pressure/: results_offline.json, features.jsonl (per-picture features for a learned retention
scorer later), recall_coverage.png.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB))
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")      # cheetah's GPU belongs to another user today: CPU only
import embeddings as E  # noqa: E402
import memory as M  # noqa: E402

OUT = M.ROOT / "data" / "memory_pressure"
LABELS = LAB / "memory_notes" / "search_eval" / "labels.json"
INST = M.DATA / "instances" / "instances.json"
BUDGETS = [25, 50, 100, 200, None]       # None = no limit
CELL_M, CELL_DEG = 1.5, 45.0
DUP = 0.95                               # mean-view SigLIP cosine at or above this = the same view
CHANGE_J = 0.5                           # object-set Jaccard below this = the cell changed
EMB_BYTES = 3 * 1152 * 2                 # SigLIP, 3 views, float16
L2_BYTES = EMB_BYTES + 150               # + a one-line summary
L1_BYTES = []                            # per picture: jpg + description JSON + embedding (filled by load)


# ---- data ----

def load():
    recs = sorted(M.load(), key=lambda r: r["t"])
    sid, V = E.load_store()
    row = {i: n for n, i in enumerate(sid)}
    recs = [r for r in recs if r["id"] in row]
    Vr = V[[row[r["id"]] for r in recs]].astype(np.float32)
    mean = Vr.mean(axis=1)
    mean /= np.linalg.norm(mean, axis=1, keepdims=True)
    L1_BYTES[:] = [Path(r["path"]).stat().st_size + len(json.dumps(r.get("seen"))) + EMB_BYTES for r in recs]
    return recs, Vr, mean @ mean.T


def cell(r):
    return (math.floor(r["x"] / CELL_M), math.floor(r["y"] / CELL_M), math.floor((r["yaw_deg"] % 360) / CELL_DEG))


def objset(r):
    """The movable things in a picture (canonical names, clutter like walls and desks left out)."""
    return {M.canon(o["name"]) for o in (r.get("seen") or {}).get("objects", [])} - M.CLUTTER


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def people(r):
    return (r.get("seen") or {}).get("people") or 0


# ---- policies: observe(i) for each picture index in time order; .l1 / .l2 are sets of indices ----

class Policy:
    name = "?"
    uses_description = False     # True: deciding needs every picture described first (change_aware compares objects)

    def __init__(self, recs, S, budget):
        self.recs, self.S, self.B = recs, S, budget
        self.l1, self.l2, self.entered = set(), set(), set()

    def admit(self, i):
        self.l1.add(i)
        self.entered.add(i)

    def over(self):
        return self.B is not None and len(self.l1) > self.B


class KeepAll(Policy):
    name = "keep_all"

    def observe(self, i):
        self.admit(i)


class Fifo(Policy):
    name = "recency_fifo"

    def observe(self, i):
        self.admit(i)
        if self.over():
            self.l1.discard(min(self.l1))


class Uniform(Policy):
    """Thin the kept set so it stays evenly spread in time: drop the picture whose neighbours are closest together."""
    name = "uniform_time"

    def observe(self, i):
        self.admit(i)
        if self.over():
            k = sorted(self.l1)
            t = [self.recs[j]["t"] for j in k]
            gap = [(t[n + 1] - t[n - 1], k[n]) for n in range(1, len(k) - 1)]
            self.l1.discard(min(gap)[1])


class Grid(Policy):
    """Newest picture per place x heading cell; with more cells than budget, the cell refreshed longest ago goes."""
    name = "place_heading_grid"

    def __init__(self, *a):
        super().__init__(*a)
        self.by = {}

    def observe(self, i):
        c = cell(self.recs[i])
        if c in self.by:
            self.l1.discard(self.by[c])
        self.by[c] = i
        self.admit(i)
        if self.over():
            j = min(self.l1)
            self.l1.discard(j)
            self.by = {c: k for c, k in self.by.items() if k != j}


class Novelty(Policy):
    """Keep a picture if it looks unlike everything kept (max cosine < tau); over budget, drop the most redundant."""
    name = "novelty"

    def __init__(self, recs, S, budget, tau=0.9):
        super().__init__(recs, S, budget)
        self.tau = tau

    def observe(self, i):
        if self.l1 and self.S[i, list(self.l1)].max() >= self.tau:
            return
        self.admit(i)
        if self.over():
            k = sorted(self.l1)
            sub = self.S[np.ix_(k, k)].copy()
            np.fill_diagonal(sub, -1)
            red = sub.max(axis=1)
            self.l1.discard(k[int(np.argmax(red))])          # argmax takes the oldest among ties


class ChangeAware(Policy):
    """One L1 view per cell. A new view replaces it only when the cell changed (movable objects' Jaccard < CHANGE_J,
    or the number of people changed); the replaced view goes to L2. Unchanged views are dropped (tiered: kept in L2).
    Over budget: the cell whose L1 view is oldest is demoted to L2."""
    name = "change_aware"
    to_l2_unchanged = False
    uses_description = True

    def __init__(self, *a):
        super().__init__(*a)
        self.by = {}

    def observe(self, i):
        r = self.recs[i]
        c = cell(r)
        j = self.by.get(c)
        if j is not None:
            old = self.recs[j]
            changed = jaccard(objset(r), objset(old)) < CHANGE_J or people(r) != people(old)
            if not changed:
                if self.to_l2_unchanged:
                    self.l2.add(i)
                return
            self.l1.discard(j)
            self.l2.add(j)
        self.by[c] = i
        self.admit(i)
        if self.over():
            j = min(self.l1)
            self.l1.discard(j)
            self.l2.add(j)
            self.by = {c: k for c, k in self.by.items() if k != j}


class Tiered(ChangeAware):
    name = "tiered"
    to_l2_unchanged = True


def run_policy(cls, recs, S, budget, **kw):
    p = cls(recs, S, budget, **kw)
    lazy = not p.uses_description
    for i in range(len(recs)):
        p.observe(i)
        assert not p.over(), (p.name, i)
    p.l2 -= p.l1
    if lazy:                     # a policy that decides from time, pose or embedding describes only what it kept
        p.entered = set(p.l1)
    return p


def tune_tau(recs, S, budget):
    """The novelty threshold whose admitted count is closest to the budget (so eviction rarely has to step in)."""
    if budget is None:
        return 1.01
    if not _SWEEP:
        for tau in np.arange(0.70, 0.995, 0.01):
            _SWEEP[round(float(tau), 2)] = len(run_policy(Novelty, recs, S, None, tau=float(tau)).l1)
    return min(_SWEEP, key=lambda tau: (abs(_SWEEP[tau] - budget), tau))


_SWEEP = {}     # tau -> pictures admitted with no budget (the same for every budget)


# ---- metrics ----

class QueryScores:
    """M.search with the picture scores taken from cached query embeddings (no picture is re-embedded)."""

    def __init__(self, queries, recs, Vr):
        OUT.mkdir(parents=True, exist_ok=True)
        cache = OUT / "query_emb.json"
        have = json.loads(cache.read_text()) if cache.exists() else {}
        need = [q for q in queries if q not in have]
        if need:
            Q = E.embed_text([f"a photo of {q}." for q in need]).astype(np.float32)
            have.update({q: v.tolist() for q, v in zip(need, Q)})
            cache.write_text(json.dumps(have))
        self.s = {q: dict(zip([r["id"] for r in recs], (Vr @ np.array(have[q], np.float32)).max(axis=1).tolist()))
                  for q in queries}
        E.update = lambda recs=None: 0
        E.scores = lambda query, ids=None: {i: self.s[query][i] for i in (ids or self.s[query])}


def l2_view(r):
    """What an L2 record still has: the embedding (scores unchanged) and the one-line summary, no object list."""
    s = r.get("seen") or {}
    return dict(r, seen={"summary": s.get("summary", ""), "objects": [], "states": [], "people": s.get("people", 0),
                         "people_notes": ""})


def recall(recs, S, keep, labels, mode, k=5, l2=frozenset()):
    """Per query: did the top k of a search over only `keep` contain a relevant picture (strict), or a picture that
    is the same view (cos >= DUP) as some relevant picture (dup-tolerant)? Also whether any relevant picture is kept."""
    idx = {r["id"]: n for n, r in enumerate(recs)}
    pool = [l2_view(recs[i]) if i in l2 else dict(recs[i]) for i in sorted(keep)]
    strict = tol = ceil = 0
    for q, lab in labels.items():
        rel = {idx[i] for i in (lab["relevant"] if isinstance(lab, dict) else lab) if i in idx}
        if not rel:
            continue
        hits = [idx[h["id"]] for h in M.search(q, k=k, recs=pool, mode=mode)]
        relv = sorted(rel)
        strict += any(h in rel for h in hits)
        tol += any(h in rel or S[h, relv].max() >= DUP for h in hits)
        ceil += bool(rel & keep)
    n = sum(1 for lab in labels.values() if (lab["relevant"] if isinstance(lab, dict) else lab))
    return {"strict": round(strict / n, 3), "dup_tolerant": round(tol / n, 3), "any_relevant_kept": round(ceil / n, 3)}


def coverage(recs, keep1, keep12, inst):
    idx = {r["id"]: n for n, r in enumerate(recs)}
    pics = {i["key"]: {idx[p] for p in i["pictures"] if p in idx} for i in inst}
    seen = sum(bool(pics[i["key"]] & keep1) for i in inst) / len(inst)
    moves = [(pics[i["key"]], pics.get(i["later"], set())) for i in inst if i.get("later") in pics]
    gone = [(pics[i["key"]], {idx[p] for p in i.get("missed_after_last_seen") or [] if p in idx}) for i in inst
            if i.get("missed_after_last_seen")]
    out = {"instances_seen_L1": round(seen, 3), "n_instances": len(inst), "n_moves": len(moves),
           "n_disappear": len(gone)}
    for tag, keep in (("L1", keep1), ("L1+L2", keep12)):
        out[f"moves_{tag}"] = round(sum(bool(a & keep) and bool(b & keep) for a, b in moves) / max(1, len(moves)), 3)
        out[f"disappear_{tag}"] = round(sum(bool(a & keep) and bool(b & keep) for a, b in gone) / max(1, len(gone)), 3)
    return out


def features(recs, S, inst, labels):
    idx = {r["id"]: n for n, r in enumerate(recs)}
    n_inst = [0] * len(recs)
    for i in inst:
        for p in i["pictures"]:
            if p in idx:
                n_inst[idx[p]] += 1
    trans = set()
    for i in inst:
        if i.get("later") or i.get("missed_after_last_seen"):
            trans |= {idx[p] for p in i["pictures"] if p in idx}
            trans |= {idx[p] for p in i.get("missed_after_last_seen") or [] if p in idx}
    rel = {idx[p] for lab in labels.values() for p in (lab["relevant"] if isinstance(lab, dict) else lab) if p in idx}
    last, count, rows = {}, {}, []
    for n, r in enumerate(recs):
        c = cell(r)
        prev = last.get(c)
        rows.append({"id": r["id"], "t": r["t"], "source": r["source"], "cell": list(c),
                     "novelty": round(1 - float(S[n, :n].max()), 4) if n else 1.0,
                     "change_vs_cell": None if prev is None else round(1 - jaccard(objset(r), objset(recs[prev])), 3),
                     "people_change": None if prev is None else people(r) != people(recs[prev]),
                     "n_objects": len((r.get("seen") or {}).get("objects", [])), "n_movable": len(objset(r)),
                     "people": people(r), "cell_views_before": count.get(c, 0),
                     "label_relevant": n in rel, "n_instances": n_inst[n], "transition_view": n in trans})
        last[c] = n
        count[c] = count.get(c, 0) + 1
    return rows


POLICIES = [KeepAll, Uniform, Fifo, Grid, Novelty, ChangeAware, Tiered]


def evaluate(recs, Vr, S, budgets=BUDGETS, policies=POLICIES, labels=None):
    labels = labels or json.loads(LABELS.read_text())
    inst = json.loads(INST.read_text())["instances"]
    QueryScores(list(labels), recs, Vr)
    res = []
    for cls in policies:
        for b in budgets:
            if cls is KeepAll and b is not None:
                continue
            kw = {"tau": tune_tau(recs, S, b)} if cls is Novelty else {}
            p = run_policy(cls, recs, S, b, **kw)
            row = {"policy": cls.name, "budget": b, **kw, "L1": len(p.l1), "L2": len(p.l2),
                   "described": len(recs) if p.uses_description else len(p.entered),
                   "bytes_MB": round(sum(L1_BYTES[i] for i in p.l1) / 1e6 + len(p.l2) * L2_BYTES / 1e6, 1)}
            for mode in ("fused", "words"):
                row[f"recall5_{mode}"] = recall(recs, S, p.l1, labels, mode)
                if p.l2:
                    row[f"recall5_{mode}_L1+L2"] = recall(recs, S, p.l1 | p.l2, labels, mode, l2=p.l2)
            row["coverage"] = coverage(recs, p.l1, p.l1 | p.l2, inst)
            res.append(row)
            print(f"{cls.name:20s} B={b}: L1 {row['L1']} L2 {row['L2']} fused {row['recall5_fused']} "
                  f"inst {row['coverage']['instances_seen_L1']} moves {row['coverage']['moves_L1']}", flush=True)
    return res, inst, labels


def plot(res, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker  # noqa: F401
    pols = [p.name for p in POLICIES if p not in (KeepAll, Tiered)]     # tiered has the same L1 as change_aware
    colors = dict(zip(pols, ["#8a8f98", "#d9822b", "#4c78a8", "#b279a2", "#e45756"]))
    names = dict(zip(pols, pols), change_aware="change_aware / tiered (same L1)")
    xs = [b for b in BUDGETS if b is not None]
    ref = next(r for r in res if r["policy"] == "keep_all")
    panels = [("Labelled queries: hit in top 5 (fused, dup-tolerant)", lambda r: r["recall5_fused"]["dup_tolerant"],
               ref["recall5_fused"]["dup_tolerant"]),
              ("Object instances with a kept picture", lambda r: r["coverage"]["instances_seen_L1"],
               ref["coverage"]["instances_seen_L1"]),
              ("Object moves with before + after kept (L1)", lambda r: r["coverage"]["moves_L1"],
               ref["coverage"]["moves_L1"])]
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.4))
    for ax, (title, f, top) in zip(axs, panels):
        for p in pols:
            ys = [f(next(r for r in res if r["policy"] == p and r["budget"] == b)) for b in xs]
            ax.plot(xs, ys, marker="o", lw=2, color=colors[p], label=names[p])
        ax.axhline(top, color="#333", ls=":", lw=1)
        ax.text(xs[0], top + 0.01, f"keep all {len(recs_global)}", fontsize=8, color="#333", va="bottom")
        ax.set_xscale("log")
        ax.set_xticks(xs)
        ax.set_xticklabels([str(x) for x in xs])
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("L1 budget (pictures kept)")
        ax.set_title(title, fontsize=10)
        ax.grid(alpha=0.25)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axs[0].legend(fontsize=8, frameon=False, loc="lower right")
    fig.text(0.5, 0.005, "Grid and change_aware fill only 146 cells (1.5 m x 45 deg), so their 200 point keeps 146.",
             ha="center", fontsize=8, color="#555")
    fig.suptitle(f"Memory pressure, offline replay of {len(recs_global)} lab pictures (10-19 to 10-22)", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=130)


def selftest(recs, Vr, S):
    sub = list(range(0, len(recs), 4))
    r2, S2 = [recs[i] for i in sub], S[np.ix_(sub, sub)]
    for cls in POLICIES:
        for b in (10, 40, None):
            if cls is KeepAll and b is not None:
                continue
            p = run_policy(cls, r2, S2, b, **({"tau": 0.9} if cls is Novelty else {}))
            assert b is None or len(p.l1) <= b
            assert not (p.l1 & p.l2)
    f = run_policy(Fifo, r2, S2, 10)
    assert f.l1 == set(range(len(r2) - 10, len(r2))), "fifo keeps the newest"
    g = run_policy(Grid, r2, S2, None)
    assert len(g.l1) == len({cell(r) for r in r2}), "grid keeps one per cell"
    t = run_policy(Tiered, r2, S2, None)
    c = run_policy(ChangeAware, r2, S2, None)
    assert t.l1 == c.l1 and len(t.l1 | t.l2) == len(r2), "tiered = change_aware + the rest in L2"
    labels = dict(list(json.loads(LABELS.read_text()).items())[:5])
    res, _, _ = evaluate(recs, Vr, S, budgets=[50, None], policies=[KeepAll, Fifo], labels=labels)
    assert res[0]["L1"] == len(recs)
    print("selftest ok:", [(r["policy"], r["budget"], r["recall5_fused"]) for r in res])


recs_global = []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    recs, Vr, S = load()
    recs_global[:] = recs
    print(f"{len(recs)} pictures, {recs[0]['time']} .. {recs[-1]['time']}", flush=True)
    if a.selftest:
        return selftest(recs, Vr, S)
    res, inst, labels = evaluate(recs, Vr, S)
    OUT.mkdir(parents=True, exist_ok=True)
    feats = features(recs, S, inst, labels)
    with (OUT / "features.jsonl").open("w") as f:
        for row in feats:
            f.write(json.dumps(row) + "\n")
    (OUT / "results_offline.json").write_text(json.dumps(
        {"n_pictures": len(recs), "cell": [CELL_M, CELL_DEG], "dup": DUP, "change_jaccard": CHANGE_J,
         "n_queries": len(labels), "results": res}, indent=1))
    plot(res, OUT / "recall_coverage.png")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
