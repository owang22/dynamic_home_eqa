"""Offline scan-to-map localizer (task 3): online tracking replay and global relocalization.

    python3 go2/localization/localizer.py online      # replay every session, every map  -> results/online_*.json
    python3 go2/localization/localizer.py global      # whole-map search from keyframes   -> results/global_*.json
    python3 go2/localization/localizer.py walls       # wall-direction heading test       -> results/walls.json

Reference maps (likelihood fields, sigma 0.1 m) and the cloud cells used against each:
  saved      the console's saved map.png (occupied pixels)               query: column top >= 0.4 m
  high       pooled cells whose column reaches >= 0.9 m in >= 40% of views query: column top >= 0.9 m
  static     cells classified static (column >= 0.25 m), persistence.py   query: column top >= 0.25 m
  consensus  pooled cells reaching >= 0.5 m in >= 50% of views            query: column top >= 0.5 m
high/static/consensus are built from the pose-graph poses (pgo.py) leaving out the test session's DAY, so a
session is never matched against a map that contains its own day.

Pseudo ground truth: pose-graph poses at keyframes (results/pgo_poses). They were fitted from cloud-to-cloud
revisit registrations + odom + a weak console prior; on held-out revisit pairs they are consistent to a median
0.05 m / 1.0 deg (85% within 0.3 m / 5 deg) vs the console's 0.21 m / 5.3 deg (44%).

Online mode, per snapshot (~0.5 Hz): predict map->odom unchanged (odom carries the motion), correlative search
+-0.3 m / +-4 deg (0.5 deg steps) around the prediction, accept the best pose only if it beats the prediction's
score by >= 0.01 and the runner-up (>= 0.15 m / 2 deg away) by >= 0.01. The small window is the jump gate: a
correction can never exceed 0.3 m / 4 deg per update. Start: the console pose at the first snapshot (lesson 1:
start from a known pose).
"""
from __future__ import annotations

import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import jumps  # noqa: E402
import matcher  # noqa: E402
import persistence as P  # noqa: E402
import revisits  # noqa: E402

OUT = common.HERE / "results"
QUERY_Z = {"saved": 0.4, "high": 0.9, "static": 0.25, "consensus": 0.5}
MAPS = ("saved", "high", "static", "consensus")


# ---------------------------------------------------------------- reference maps
def _counts():
    z = np.load(OUT / "persistence_counts_pgo.npz")
    return [str(s) for s in z["names"]], z["occ"], z["view"], float(z["res"]), z["origin"]


def reference(name, leave_day=None):
    """Field for map `name`, built without sessions of `leave_day` (None: all)."""
    if name == "saved":
        M = common.load_map()
        return matcher.Field((M == 0)[::-1], 0.05, common.MAP_ORIGIN, sigma=0.1)
    names, occ, view, res, origin = _counts()
    keep = [i for i, s in enumerate(names) if s[:10] != leave_day]
    o = occ[keep].sum(0)
    v = view[keep].sum(0)
    th = list(P.THRESH)
    if name == "high":
        f = np.where(v >= 5, o[th.index(0.9)] / np.maximum(v, 1), 0)
        grid = f >= 0.4
    elif name == "consensus":
        k = th.index(0.5)
        f = np.where(v >= 5, o[k] / np.maximum(v, 1), 0)
        grid = f >= 0.5
    elif name == "static":
        per = {names[i]: (occ[i], view[i]) for i in keep}
        cls = P.classify(per, [names[i] for i in keep])
        grid = cls[0] == 2
        if len({names[i][:10] for i in keep}) < 2:
            raise ValueError("static map needs >= 2 days")
    else:
        raise KeyError(name)
    return matcher.Field(grid, res, tuple(origin), sigma=0.1)


# ---------------------------------------------------------------- pose helpers
def pivot_pose(T, dog):
    p = common.transform_pts(T, np.asarray(dog, float)[None])[0]
    return np.array([p[0], p[1], T[2]])


def T_from_pivot(pp, dog):
    c, s = math.cos(pp[2]), math.sin(pp[2])
    return np.array([pp[0] - (c * dog[0] - s * dog[1]), pp[1] - (s * dog[0] + c * dog[1]), pp[2]])


def pose_err(Ta, Tb, dog):
    pa, pb = pivot_pose(Ta, dog), pivot_pose(Tb, dog)
    return math.hypot(pa[0] - pb[0], pa[1] - pb[1]), abs(math.degrees(common.wrap(pa[2] - pb[2])))


def pgo_table():
    tab = {}
    for f in (OUT / "pgo_poses").glob("*.npz"):
        z = np.load(f)
        for c, T in zip(z["cloud"], z["T_map_odom"]):
            tab[(f.stem, int(c))] = np.array(T)
    return tab


# ---------------------------------------------------------------- online
LOST_SCORE = {"saved": 0.68, "high": 0.45, "static": 0.64, "consensus": 0.72}  # from results/online_metrics: between
# the median tracking score when the pose is right (0.82 / 0.64 / 0.71 / 0.81) and when lost (0.60 / 0.32 / 0.62 / 0.72)


def global_search(F, rel, top_k=8):
    yaws = np.radians(np.arange(-180, 180, 2.0))
    ranked = matcher.best_poses(F, matcher.search(F, rel, (0, 0), yaws, None), top_k=top_k, min_sep_deg=10, min_sep_m=0.5)
    ranked = [matcher.refine_pose(F, rel, r) for r in ranked[:4]] + ranked[4:]
    ranked.sort(key=lambda a: -a[0])
    best = ranked[0]
    second = next((r for r in ranked[1:] if math.hypot(r[1] - best[1], r[2] - best[2]) >= 0.5
                   or abs(math.degrees(common.wrap(r[3] - best[3]))) >= 10), (0, 0, 0, 0))
    return best, second[0] / best[0] if best[0] > 0 else 1.0


def run_online(args):
    """args: (session, map) or (session, map, init, reloc). init 'console' (default) or 'gt' (pseudo-GT pose of the
    first keyframe: tracking from a known start); reloc: relocalize by a gated whole-map search when lost."""
    session, mapname = args[:2]
    init = args[2] if len(args) > 2 else "console"
    reloc = args[3] if len(args) > 3 else False
    alpha = args[4] if len(args) > 4 else 1.0  # fraction of each accepted correction applied (1 = all)
    gt = pgo_table() if init == "gt" else None
    n_reloc = n_reloc_try = 0
    recent_scores, recent_edge, cooldown_t = [], [], -1e9
    F = reference(mapname, leave_day=None if mapname == "saved" else session[:10])
    d = common.load(session)
    o, v, w = jumps.motion(d, 0.0)
    m = d["map"]
    zq = QUERY_Z[mapname]
    T = None
    log = []
    for i, r in enumerate(d["c_row"]):
        if T is None:
            if init == "gt":
                if (session, i) not in gt:
                    continue
                T = gt[(session, i)].copy()
            else:
                if np.isnan(m[r, 0]):
                    continue
                T = common.compose(m[r], common.inverse(o[r]))  # anchor: console pose at start
        ob, _ = common.cloud(d, i)
        ob = ob[ob[:, 2] >= zq][:, :2].astype(float)
        dog = d["odom"][r, :2].astype(float)
        upd = (0.0, 0.0, False, 0.0)
        if len(ob) >= 30:
            rel = ob - dog
            pp = pivot_pose(T, dog)
            sc_pred = F.score(rel, pp)
            rk = matcher.match(F, rel, pp, 4, 0.5, 0.3, top_k=4)
            if rk:
                b = rk[0]
                alt = max([c[0] for c in rk[1:] if math.hypot(c[1] - b[1], c[2] - b[2]) >= 0.15
                           or abs(math.degrees(common.wrap(c[3] - b[3]))) >= 2] or [0.0])
                if b[0] - sc_pred >= 0.01 and b[0] - alt >= 0.01:
                    newp = np.array(b[1:])
                    if alpha < 1.0:
                        dlt = newp - pp
                        dlt[2] = common.wrap(dlt[2])
                        newp = pp + alpha * dlt
                    dxy = math.hypot(*(newp[:2] - pp[:2]))
                    ddeg = abs(math.degrees(common.wrap(newp[2] - pp[2])))
                    T = T_from_pivot(newp, dog)
                    upd = (dxy, ddeg, True, b[0])
                else:
                    upd = (0.0, 0.0, False, sc_pred)
                recent_scores = (recent_scores + [upd[3]])[-8:]
                recent_edge = (recent_edge + [upd[2] and (upd[0] >= 0.25 or upd[1] >= 3.5)])[-6:]
                lost = (len(recent_scores) == 8 and np.median(recent_scores) < LOST_SCORE[mapname]) or sum(recent_edge) >= 4
                if reloc and lost and d["c_t"][i] - cooldown_t > 20:
                    cooldown_t = d["c_t"][i]
                    n_reloc_try += 1
                    gb, ratio = global_search(F, rel)
                    if ratio <= 0.95 and gb[0] >= F.score(rel, pivot_pose(T, dog)) + 0.03:
                        T = T_from_pivot(np.array(gb[1:]), dog)
                        n_reloc += 1
                        recent_scores, recent_edge = [], []
                        upd = (0.0, 0.0, "reloc", gb[0])
        log.append(dict(cloud=i, t=float(d["c_t"][i]), T=T.tolist(), dog=dog.tolist(), still=bool(v[r] < 0.02 and w[r] < math.radians(3)),
                        dxy=upd[0], ddeg=upd[1], applied=upd[2], score=float(upd[3]),
                        console=(common.compose(m[r], common.inverse(o[r])).tolist() if not np.isnan(m[r, 0]) else None)))
    if log:
        log[-1]["n_reloc"] = n_reloc
        log[-1]["n_reloc_try"] = n_reloc_try
    return session, mapname, log


def online_metrics(logs, gt):
    """logs: {(session, map): [entries]}. Returns per map: agreement with pseudo-GT at keyframes, twitches, jumps."""
    res = {}
    for mapname in sorted({k[1] for k in logs}):
        errs, cerrs, still_n, still_tw, n_app, big = [], [], 0, 0, 0, 0
        still_minutes = 0.0
        for (s, mn), log in logs.items():
            if mn != mapname:
                continue
            prev_t = None
            for e in log:
                g = gt.get((s, e["cloud"]))
                if g is not None:
                    errs.append(pose_err(np.array(e["T"]), g, e["dog"]))
                    if e["console"] is not None:
                        cerrs.append(pose_err(np.array(e["console"]), g, e["dog"]))
                if e["still"]:
                    still_n += 1
                    if prev_t is not None:
                        still_minutes += min(e["t"] - prev_t, 5.0) / 60
                    if e["applied"] is True and e["dxy"] >= 0.05:
                        still_tw += 1
                n_app += e["applied"] is True
                big += e["applied"] is True and (e["dxy"] >= 0.25 or e["ddeg"] >= 3.5)
                prev_t = e["t"]
        E, C = np.array(errs), np.array(cerrs)
        res[mapname] = dict(
            n_kf=len(E), med_m=float(np.median(E[:, 0])), med_deg=float(np.median(E[:, 1])),
            p90_m=float(np.percentile(E[:, 0], 90)), p90_deg=float(np.percentile(E[:, 1], 90)),
            ok=float(np.mean((E[:, 0] < 0.3) & (E[:, 1] < 5))),
            console_med_m=float(np.median(C[:, 0])), console_med_deg=float(np.median(C[:, 1])),
            console_p90_m=float(np.percentile(C[:, 0], 90)), console_p90_deg=float(np.percentile(C[:, 1], 90)),
            console_ok=float(np.mean((C[:, 0] < 0.3) & (C[:, 1] < 5))),
            twitch_ge5cm_per_still_min=still_tw / max(still_minutes, 1e-9), still_minutes=still_minutes,
            updates_applied=int(n_app), updates_at_gate_edge=int(big))
    return res


def online(variant="console"):
    """variant: 'console' (start at console pose, no reloc), 'gt' (start at pseudo-GT), 'reloc' (console start +
    gated relocalization when lost), 'smooth' / 'smooth_reloc' (apply only 30% of each accepted correction)."""
    init = "gt" if variant == "gt" else "console"
    rel = variant in ("reloc", "smooth_reloc")
    alpha = 0.3 if variant.startswith("smooth") else 1.0
    tasks = [(s, mname, init, rel, alpha) for s in P.MAP_SESSIONS for mname in MAPS]
    logs = {}
    with ProcessPoolExecutor(16) as ex:
        for s, mn, log in ex.map(run_online, tasks):
            logs[(s, mn)] = log
    sfx = "" if variant == "console" else f"_{variant}"
    (OUT / f"online_logs{sfx}").mkdir(exist_ok=True)
    for (s, mn), log in logs.items():
        json.dump(log, open(OUT / f"online_logs{sfx}" / f"{s}_{mn}.json", "w"))
    gt = pgo_table()
    met = online_metrics(logs, gt)
    # revisit consistency on the (independent) registration pairs
    pr = revisits.load_pairs()
    for mn in MAPS:
        tab = {}
        for (s, m2), log in logs.items():
            if m2 == mn:
                for e in log:
                    tab[(s, e["cloud"])] = np.array(e["T"])
        ev = revisits.evaluate(pr, lambda s, c: tab.get((s, c)))
        met[mn]["revisit_med_m"] = float(np.median(ev[:, 0]))
        met[mn]["revisit_med_deg"] = float(np.median(ev[:, 1]))
        met[mn]["revisit_ok"] = float(np.mean((ev[:, 0] < 0.3) & (ev[:, 1] < 5)))
        print(revisits.summarize(ev, f"online[{mn}] revisits"))
    ev = revisits.evaluate(pr, revisits.console_T(pr))
    met["console_revisit"] = dict(med_m=float(np.median(ev[:, 0])), med_deg=float(np.median(ev[:, 1])),
                                  ok=float(np.mean((ev[:, 0] < 0.3) & (ev[:, 1] < 5))))
    for mn in MAPS:
        met[mn]["reloc_accepted"] = sum(log[-1].get("n_reloc", 0) for (s, m2), log in logs.items() if m2 == mn and log)
        met[mn]["reloc_tried"] = sum(log[-1].get("n_reloc_try", 0) for (s, m2), log in logs.items() if m2 == mn and log)
    json.dump(met, open(OUT / f"online_metrics{sfx}.json", "w"), indent=1)
    for k, v in met.items():
        print(k, json.dumps(v))


# ---------------------------------------------------------------- global
def global_one(args):
    """Whole-map search for one query. args: (session, cloud indices to pool, mapname, gt T, last cloud dog)."""
    session, clouds, mapname, gtT = args
    F = reference(mapname, leave_day=None if mapname == "saved" else session[:10])
    d = common.load(session)
    zq = QUERY_Z[mapname]
    # pool the clouds into the frame of the last one using odom (cells are already in odom frame)
    pts = []
    for i in clouds:
        ob, _ = common.cloud(d, i)
        pts.append(ob[ob[:, 2] >= zq][:, :2].astype(float))
    pts = np.unique(np.round(np.concatenate(pts) / 0.1).astype(int), axis=0) * 0.1
    dog = d["odom"][d["c_row"][clouds[-1]], :2].astype(float)
    if len(pts) < 30:
        return None
    rel = pts - dog
    yaws = np.radians(np.arange(-180, 180, 2.0))
    resl = matcher.search(F, rel, (0, 0), yaws, None)
    ranked = matcher.best_poses(F, resl, top_k=8, min_sep_deg=10, min_sep_m=0.5)
    ranked = [matcher.refine_pose(F, rel, r) for r in ranked[:4]] + ranked[4:]
    ranked.sort(key=lambda a: -a[0])
    best = ranked[0]
    second = next((r for r in ranked[1:] if math.hypot(r[1] - best[1], r[2] - best[2]) >= 0.5
                   or abs(math.degrees(common.wrap(r[3] - best[3]))) >= 10), (0, 0, 0, 0))
    gp = pivot_pose(gtT, dog)
    e = (math.hypot(best[1] - gp[0], best[2] - gp[1]), abs(math.degrees(common.wrap(best[3] - gp[2]))))
    # is the right answer among the candidates at all?
    rank_ok = next((k for k, r in enumerate(ranked) if math.hypot(r[1] - gp[0], r[2] - gp[1]) < 0.3
                    and abs(math.degrees(common.wrap(r[3] - gp[2]))) < 10), -1)
    # also against the console's own pose at that moment (its frame = the saved map's frame, locally)
    r_last = d["c_row"][clouds[-1]]
    o_, _, _ = jumps.motion(d, 0.0)
    ok_con = None
    if not np.isnan(d["map"][r_last, 0]):
        Tc = common.compose(d["map"][r_last], common.inverse(o_[r_last]))
        cp = pivot_pose(Tc, dog)
        ok_con = bool(math.hypot(best[1] - cp[0], best[2] - cp[1]) < 0.3 and abs(math.degrees(common.wrap(best[3] - cp[2]))) < 10)
    Tbest = T_from_pivot(np.array(best[1:]), dog)
    return dict(session=session, cloud=int(clouds[-1]), ok_vs_console=ok_con, T_best=Tbest.tolist(), n_clouds=len(clouds), n_pts=int(len(pts)), map=mapname,
                err_m=e[0], err_deg=e[1], ok=bool(e[0] < 0.3 and e[1] < 10), best=best[0], second=second[0],
                ratio=second[0] / best[0] if best[0] > 0 else 1.0, rank_of_truth=rank_ok)


def global_mode(n_per_session=12, seed=0):
    gt = pgo_table()
    rng = np.random.default_rng(seed)
    tasks = []
    for s in P.MAP_SESSIONS:
        d = common.load(s)
        kfs = sorted(c for (ss, c) in gt if ss == s)
        if not kfs:
            continue
        pick = rng.choice(kfs, size=min(n_per_session, len(kfs)), replace=False)
        for c in pick:
            # single snapshot, and a "short walk": all snapshots of the previous 60 s (pooled with odom)
            t_end = d["c_t"][c]
            walk = [int(i) for i in np.flatnonzero((d["c_t"] >= t_end - 60) & (d["c_t"] <= t_end))][::3] + [int(c)]
            walk = sorted(set(walk))
            for mn in MAPS:
                tasks.append((s, [int(c)], mn, gt[(s, int(c))]))
                tasks.append((s, walk, mn, gt[(s, int(c))]))
    print(len(tasks), "global queries")
    out = []
    with ProcessPoolExecutor(20) as ex:
        for r in ex.map(global_one, tasks, chunksize=4):
            if r:
                out.append(r)
    json.dump(out, open(OUT / "global_results.json", "w"), indent=1)
    summarize_global(out)


def summarize_global(out):
    rows = []
    for mn in MAPS:
        for kind, sel in (("single", lambda r: r["n_clouds"] == 1), ("60s walk", lambda r: r["n_clouds"] > 1)):
            rs = [r for r in out if r["map"] == mn and sel(r)]
            if not rs:
                continue
            ok = np.array([r["ok"] for r in rs])
            ratio = np.array([r["ratio"] for r in rs])
            inlist = np.array([r["rank_of_truth"] >= 0 for r in rs])
            # gate: accept only when the runner-up is clearly worse
            okc = [r["ok_vs_console"] for r in rs if r["ok_vs_console"] is not None]
            row = dict(map=mn, query=kind, n=len(rs), success=float(ok.mean()),
                       success_vs_console=float(np.mean(okc)) if okc else None, truth_in_top8=float(inlist.mean()),
                       ratio_med=float(np.median(ratio)))
            for g in (0.95, 0.9, 0.85):
                acc = ratio <= g
                row[f"accept@{g}"] = float(acc.mean())
                row[f"precision@{g}"] = float(ok[acc].mean()) if acc.any() else None
            rows.append(row)
            print(json.dumps(row))
    json.dump(rows, open(OUT / "global_summary.json", "w"), indent=1)


def global_two_view(n_per_session=10, seed=2):
    """'Relocalize' behaviour check: two global searches from snapshots 20-90 s apart (dog moved >= 0.5 m or turned
    >= 30 deg in between). Accept only if the two answers agree through odometry (within 0.3 m / 5 deg) and each
    passes the ambiguity gate. Precision and acceptance vs pseudo-GT."""
    gt = pgo_table()
    rng = np.random.default_rng(seed)
    tasks, pairs = [], []
    for s in P.MAP_SESSIONS:
        kfs = sorted(c for (ss, c) in gt if ss == s)
        d = common.load(s)
        cand = []
        for a in kfs:
            for b in kfs:
                dt = d["c_t"][b] - d["c_t"][a]
                if 20 <= dt <= 90:
                    ra, rb = d["c_row"][a], d["c_row"][b]
                    moved = np.hypot(*(d["odom"][rb, :2] - d["odom"][ra, :2]))
                    turned = abs(math.degrees(common.wrap(d["odom"][rb, 3] - d["odom"][ra, 3])))
                    if moved >= 0.5 or turned >= 30:
                        cand.append((a, b))
        if not cand:
            continue
        for k in rng.choice(len(cand), min(n_per_session, len(cand)), replace=False):
            a, b = cand[k]
            pairs.append((s, a, b))
            for mn in ("consensus", "static", "saved"):
                tasks.append((s, [a], mn, gt[(s, a)]))
                tasks.append((s, [b], mn, gt[(s, b)]))
    res = {}
    with ProcessPoolExecutor(20) as ex:
        for r in ex.map(global_one, tasks, chunksize=2):
            if r:
                res[(r["session"], r["cloud"], r["map"])] = r
    rows = []
    for mn in ("consensus", "static", "saved"):
        n = acc = good = 0
        single_ok = []
        for s, a, b in pairs:
            ra, rb = res.get((s, a, mn)), res.get((s, b, mn))
            if not ra or not rb:
                continue
            n += 1
            single_ok.append(ra["ok"])
            # T is map->odom: if both answers are right they are the same transform
            Ta, Tb = np.array(ra["T_best"]), np.array(rb["T_best"])
            d = common.load(s)
            dog_b = d["odom"][d["c_row"][b], :2]
            e = pose_err(Ta, Tb, dog_b)
            agree = e[0] < 0.3 and e[1] < 5
            for gate in (1.0, 0.97, 0.95):
                pass
            if agree and max(ra["ratio"], rb["ratio"]) <= 0.97:
                acc += 1
                good += rb["ok"]
        rows.append(dict(map=mn, pairs=n, single_success=float(np.mean(single_ok)) if single_ok else None,
                         accept=acc / max(n, 1), precision=good / acc if acc else None))
        print(json.dumps(rows[-1]))
    json.dump(rows, open(OUT / "global_two_view.json", "w"), indent=1)


# ---------------------------------------------------------------- walls
def walls_mode():
    """Can wall directions fix heading? Dominant directions (mod 90) of the saved map and of the consensus map;
    per keyframe, the snapshot's dominant direction vs the pseudo-GT heading."""
    import walls
    gt = pgo_table()
    res = {}
    M = common.load_map()
    r, c = np.nonzero((M == 0)[::-1])
    xy = np.stack([common.MAP_ORIGIN[0] + (c + 0.5) * 0.05, common.MAP_ORIGIN[1] + (r + 0.5) * 0.05], -1)
    a, con, sec, prof_saved = walls.manhattan_dir(xy, step=0.5, jitter=0.025, bin_m=0.05)
    res["saved_map"] = dict(dir_deg=a, contrast=con, second_over_first=sec)
    F = reference("high")
    r, c = np.nonzero(F.occ)
    xy = np.stack([F.ox + (c + 0.5) * F.res, F.oy + (r + 0.5) * F.res], -1)
    a2, con2, sec2, prof_high = walls.manhattan_dir(xy, step=0.5)
    res["high_map"] = dict(dir_deg=a2, contrast=con2, second_over_first=sec2)
    print(res)
    errs = []
    for (s, cidx), T in list(gt.items())[::3]:
        d = common.load(s)
        ob, _ = common.cloud(d, cidx)
        for zq in (0.5, 0.9):
            p = ob[ob[:, 2] >= zq][:, :2].astype(float)
            if len(p) < 50:
                continue
            ad, cn, sc2, _ = walls.manhattan_dir(p, step=0.5)
            pred = a2 - ad
            e = float(walls.wrap90(pred - math.degrees(T[2])))
            errs.append((zq, e, cn, sc2))
    E = np.array(errs)
    for zq in (0.5, 0.9):
        k = E[:, 0] == zq
        for cmin in (0, 1.3, 1.6):
            kk = k & (E[:, 2] >= cmin)
            if kk.sum():
                res[f"snap_z{zq}_contrast{cmin}"] = dict(n=int(kk.sum()), med_abs_err=float(np.median(np.abs(E[kk, 1]))),
                                                         within3=float(np.mean(np.abs(E[kk, 1]) < 3)),
                                                         within5=float(np.mean(np.abs(E[kk, 1]) < 5)))
    print(json.dumps(res, indent=1))
    json.dump(res, open(OUT / "walls.json", "w"), indent=1)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "online"
    if mode == "online":
        online(sys.argv[2] if len(sys.argv) > 2 else "console")
    else:
        {"global": global_mode, "walls": walls_mode, "global2": global_two_view}[mode]()
