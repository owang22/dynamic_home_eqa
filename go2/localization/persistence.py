"""Which cells of the lab stay put? Per-cell occupancy frequency per session and across days (task 2).

    python3 go2/localization/persistence.py [--pose console|refined]

Every cloud snapshot (dog's voxel cells, odom frame, column-top height z above floor) taken during a calm
period (jumps.calm_mask: no jump / hand placement / restart within +-5 s, < 0.3 m/s, < 30 deg/s) is put into the
saved map's frame with the console's map->odom at that moment. Grid 0.1 m aligned to the saved map origin.

Per snapshot a cell is
  in view  : inside the dog's voxel window (+-3.2 m square around the dog, odom axes), and within 3.0 m of the
             dog (ray-free approximation: occluded cells count as seen-free)
  occupied : some cloud cell lands in it whose column top reaches the threshold h
Thresholds h (column reaches at least): 0.25 m (anything above floor noise), 0.5 m, 0.9 m, 1.2 m.
Frequencies f = occupied / in-view. Snapshots are ~0.5 Hz and strongly correlated, so a session counts as one
vote per cell: occupied in session s if f_s >= 0.5 (and >= 3 in-view snapshots), free if f_s <= 0.1.
Only "fresh" snapshots are used (dog moved >= 0.3 m or turned >= 20 deg in the previous 30 s, >= 3 s apart);
see snapshot_poses.

Classes (per threshold h), using days (2026-10-19, -20, -22) as the unit across sessions:
  static      : occupied in every day it was in view, in view on >= 2 days, and within each day never seen
                free in a session
  semi-static : occupied on some day(s) and free on another day (moved between days: chairs, bags, boxes)
  dynamic     : within one day/session it flips: f_s between 0.1 and 0.5 in some session, or occupied in one
                session and free in another session of the same day (people, chairs pushed around)
  free        : free in every session it was in view
  rare/unknown: otherwise

Outputs: results/persistence_<h>.npz (per-session counts), figs/persistence_*.png, results/persistence_summary.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import jumps  # noqa: E402

RES = 0.1
OX, OY = common.MAP_ORIGIN
W = int(round(283 * 0.05 / RES)) + 1
H = int(round(289 * 0.05 / RES)) + 1
THRESH = (0.25, 0.5, 0.9, 1.2)
VIEW_R = 3.0
# sessions whose console poses are in the saved map's frame (scratch/session_frame_check.py: hit ratio >= 1.1)
MAP_SESSIONS = ["2026-10-19_155256", "2026-10-19_163531", "2026-10-19_164038", "2026-10-19_170641",
                "2026-10-19_170813", "2026-10-20_111931", "2026-10-20_153827", "2026-10-20_191336",
                "2026-10-20_192619", "2026-10-20_193751", "2026-10-22_153454", "2026-10-22_155604",
                "2026-10-22_155728", "2026-10-22_160051", "2026-10-22_161641"]
OUT = common.HERE / "results"
FIGS = common.HERE / "figs"
OCC_F, FREE_F, MIN_VIEW = 0.5, 0.1, 3
FRESH_ONLY, FRESH_S, MIN_GAP_S = True, 30.0, 3.0
TOL_CELLS = 1  # a cell counts as occupied in a snapshot if a cloud cell lands within 1 cell (0.1 m)


def day(s):
    return s[:10]


def cell_idx(xy):
    return np.floor((xy[:, 0] - OX) / RES).astype(int), np.floor((xy[:, 1] - OY) / RES).astype(int)


def snapshot_poses(name, calls, pose_source="console"):
    """[(cloud index, map->odom T)] for calm snapshots of a session."""
    d = common.load(name)
    lag_r = jumps.estimate_lag(d)
    lag = lag_r[0] if lag_r else 0.0
    evs = jumps.events(d, lag, calls)
    calm = jumps.calm_mask(d, evs, lag)
    o, v, w = jumps.motion(d, lag)
    out = []
    # "fresh" snapshots only: the dog moved >= 0.3 m or turned >= 20 deg within the last FRESH_S seconds (its voxel
    # window was recently refilled and the console pose recently re-matched), at most one per MIN_GAP_S seconds.
    # Long still periods otherwise dominate the counts and carry the yaw-drift smear (problems_found.md #1).
    t = d["t"]
    cum_d = np.r_[0, np.cumsum(np.hypot(*np.diff(d["odom"][:, :2], axis=0).T))]
    cum_a = np.r_[0, np.cumsum(np.abs(np.diff(np.unwrap(d["odom"][:, 3]))))]
    last_t = -1e9
    if pose_source in ("refined", "pgo"):
        ref = np.load(OUT / ("refined_poses" if pose_source == "refined" else "pgo_poses") / f"{name}.npz")
        rmap = {int(i): T for i, T in zip(ref["cloud"], ref["T_map_odom"])}
    for i, r in enumerate(d["c_row"]):
        if not calm[r]:
            continue
        if FRESH_ONLY:
            r0 = max(0, np.searchsorted(t, t[r] - FRESH_S))
            if cum_d[r] - cum_d[r0] < 0.3 and cum_a[r] - cum_a[r0] < math.radians(20):
                continue
            if t[r] - last_t < MIN_GAP_S:
                continue
            last_t = t[r]
        if pose_source in ("refined", "pgo"):
            if i not in rmap:
                continue
            T = rmap[i]
        else:
            T = common.compose(d["map"][r], common.inverse(o[r]))
        out.append((i, T, d["odom"][r, :2]))
    return d, out


def accumulate(name, calls, pose_source="console"):
    d, snaps = snapshot_poses(name, calls, pose_source)
    occ = np.zeros((len(THRESH), H, W), np.int32)
    view = np.zeros((H, W), np.int32)
    gx, gy = np.meshgrid(OX + (np.arange(W) + 0.5) * RES, OY + (np.arange(H) + 0.5) * RES)
    for i, T, dog_odom in snaps:
        ob, _ = common.cloud(d, i)
        ob = ob[ob[:, 2] >= THRESH[0]]
        dog_map = common.transform_pts(T, dog_odom[None, :].astype(float))[0]
        # in view: within VIEW_R of the dog and inside the +-3.2 m odom-aligned square
        dx, dy = gx - dog_map[0], gy - dog_map[1]
        c, s = math.cos(-T[2]), math.sin(-T[2])
        ux, uy = c * dx - s * dy, s * dx + c * dy  # cell offset in odom axes
        inv = (dx ** 2 + dy ** 2 <= VIEW_R ** 2) & (np.abs(ux) <= 3.15) & (np.abs(uy) <= 3.15)
        view += inv
        if len(ob) == 0:
            continue
        q = common.transform_pts(T, ob.astype(float))
        ci, cj = cell_idx(q)
        ok = (ci >= 0) & (ci < W) & (cj >= 0) & (cj < H)
        ci, cj, z = ci[ok], cj[ok], ob[ok, 2]
        for k, h in enumerate(THRESH):
            sel = z >= h
            m = np.zeros((H, W), bool)
            m[cj[sel], ci[sel]] = True
            if TOL_CELLS:  # occupied if any cell within TOL_CELLS (pose noise tolerance)
                m = ndimage.binary_dilation(m, iterations=TOL_CELLS)
            occ[k] += m & inv
    return occ, view, len(snaps)


def classify_v1(per_session, names):
    """First version: any session with an intermediate frequency made a cell "dynamic". With the ray-free view
    approximation and residual pose noise that labelled most of the lab dynamic. Kept for the record."""
    """per_session: dict name -> (occ[k], view). Returns class maps per threshold: codes
    0 unknown, 1 free, 2 static, 3 semi-static, 4 dynamic, 5 rare."""
    days = sorted({day(s) for s in names})
    out = []
    for k in range(len(THRESH)):
        occ_s = {}
        free_s = {}
        mid_s = {}
        for s in names:
            o, v = per_session[s][0][k], per_session[s][1]
            f = np.where(v >= MIN_VIEW, o / np.maximum(v, 1), np.nan)
            occ_s[s] = f >= OCC_F
            free_s[s] = f <= FREE_F
            mid_s[s] = (f > FREE_F) & (f < OCC_F)
        occ_d = {dd: np.zeros((H, W), bool) for dd in days}
        free_d = {dd: np.zeros((H, W), bool) for dd in days}
        mixed_within = np.zeros((H, W), bool)
        for dd in days:
            ss = [s for s in names if day(s) == dd]
            any_occ = np.zeros((H, W), bool)
            any_free = np.zeros((H, W), bool)
            for s in ss:
                any_occ |= occ_s[s]
                any_free |= free_s[s]
                mixed_within |= mid_s[s]
            mixed_within |= any_occ & any_free
            occ_d[dd] = any_occ & ~any_free
            free_d[dd] = any_free & ~any_occ
        n_occ_days = sum(occ_d[dd].astype(int) for dd in days)
        n_free_days = sum(free_d[dd].astype(int) for dd in days)
        cls = np.zeros((H, W), np.uint8)
        seen = np.zeros((H, W), bool)
        for s in names:
            seen |= per_session[s][1] >= MIN_VIEW
        cls[seen] = 5
        cls[(n_free_days > 0) & (n_occ_days == 0) & ~mixed_within] = 1
        cls[(n_occ_days >= 2) & (n_free_days == 0) & ~mixed_within] = 2
        cls[(n_occ_days >= 1) & (n_free_days >= 1)] = 3
        cls[mixed_within & (cls != 3) & (cls != 1)] = 4
        cls[mixed_within & (cls == 1)] = 4
        out.append(cls)
    return out


def classify(per_session, names, occ_f=0.5, free_f=0.15, min_view_day=10):
    """Day-pooled classes (v2). Per day d: f_d = sum occ / sum view over that day's sessions (>= 10 views).
    Per session s also f_s (>= MIN_VIEW views).
      static      : f_d >= 0.5 on every viewed day, viewed on >= 2 days
      semi-static : f_d >= 0.5 on some day and f_d <= 0.15 on another (moved between days)
      dynamic     : not semi-static, and within one day it changes: f_d strictly between 0.15 and 0.5, or one session
                    of the day has f_s >= 0.5 and another f_s <= 0.1
      free        : f_d <= 0.15 on every viewed day and no within-day change
      rare/one-day: occupied but viewed on one day only"""
    days = sorted({day(s) for s in names})
    out = []
    for k in range(len(THRESH)):
        fd = []
        within = np.zeros((H, W), bool)
        for dd in days:
            ss = [s for s in names if day(s) == dd]
            o = sum(per_session[s][0][k] for s in ss)
            v = sum(per_session[s][1] for s in ss)
            fd.append(np.where(v >= min_view_day, o / np.maximum(v, 1), np.nan))
            occ_any = np.zeros((H, W), bool)
            free_any = np.zeros((H, W), bool)
            for s in ss:
                f = np.where(per_session[s][1] >= MIN_VIEW, per_session[s][0][k] / np.maximum(per_session[s][1], 1), np.nan)
                occ_any |= f >= occ_f
                free_any |= f <= 0.1
            within |= occ_any & free_any
        fd = np.stack(fd)
        nview = np.sum(~np.isnan(fd), 0)
        fmax = np.nanmax(np.where(np.isnan(fd), -1, fd), 0)
        fmin = np.nanmin(np.where(np.isnan(fd), 9, fd), 0)
        mid_day = np.any((fd > free_f) & (fd < occ_f), 0)
        cls = np.zeros((H, W), np.uint8)
        seen = nview >= 1
        cls[seen] = 5
        cls[seen & (fmax <= free_f) & ~within] = 1
        cls[(nview >= 2) & (fmin >= occ_f)] = 2
        semi = (nview >= 2) & (fmax >= occ_f) & (fmin <= free_f)
        cls[semi] = 3
        cls[seen & ~semi & (cls != 2) & (mid_day | within)] = 4
        cls[(nview == 1) & (fmax >= occ_f) & ~within] = 5
        out.append(cls)
    return out


CLASS_NAMES = {0: "unknown", 1: "free", 2: "static", 3: "semi-static", 4: "dynamic", 5: "rare/one-day"}
CLASS_COLORS = {0: (0.8, 0.8, 0.8, 0), 1: (1, 1, 1, 0), 2: (0.1, 0.2, 0.8, 1), 3: (1.0, 0.55, 0.0, 1),
                4: (0.85, 0.1, 0.1, 1), 5: (0.6, 0.6, 0.6, 0.6)}


def render(cls_maps, freq_all, names, tag):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    M = common.load_map()
    places = json.load(open(common.GO2 / "data" / "lab_agent" / "places.json"))
    ext_map = [OX, OX + 283 * 0.05, OY, OY + 289 * 0.05]
    ext = [OX, OX + W * RES, OY, OY + H * RES]
    fig, axs = plt.subplots(2, len(THRESH), figsize=(7 * len(THRESH), 14))
    for k, h in enumerate(THRESH):
        ax = axs[0, k]
        ax.imshow(M, cmap="gray", extent=ext_map, vmin=-150, vmax=300, interpolation="nearest")
        rgba = np.zeros((H, W, 4))
        for c, col in CLASS_COLORS.items():
            rgba[cls_maps[k] == c] = col
        ax.imshow(rgba, origin="lower", extent=ext, interpolation="nearest")
        ax.set_title(f"[{tag}] column reaches >= {h} m: class")
        ax2 = axs[1, k]
        ax2.imshow(M, cmap="gray", extent=ext_map, vmin=-150, vmax=300, interpolation="nearest")
        f = freq_all[k]
        im = ax2.imshow(np.ma.masked_invalid(np.where(f > 0.02, f, np.nan)), origin="lower", extent=ext,
                        cmap="viridis", vmin=0, vmax=1, interpolation="nearest", alpha=0.85)
        ax2.set_title(f"occupancy frequency, all sessions pooled (>= {h} m)")
        plt.colorbar(im, ax=ax2, fraction=0.04)
        for a in (ax, ax2):
            for pid, p in places.items():
                a.plot(p["x"], p["y"], "m^", ms=5)
                a.text(p["x"], p["y"], pid, fontsize=7, color="m")
            a.set_xlim(-5.5, 6.5)
            a.set_ylim(-5.0, 6.5)
    axs[0, 0].legend(handles=[Patch(color=CLASS_COLORS[c][:3], label=n) for c, n in CLASS_NAMES.items() if c >= 2],
                     loc="lower left", fontsize=9)
    plt.tight_layout()
    p = FIGS / f"persistence_{tag}.png"
    plt.savefig(p, dpi=60)
    plt.close()
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pose", default="console", choices=["console", "refined", "pgo"])
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    FIGS.mkdir(exist_ok=True)
    calls = jumps.agent_calls()
    per = {}
    nsnap = {}
    names = []
    for s in MAP_SESSIONS:
        folder = {"refined": "refined_poses", "pgo": "pgo_poses"}.get(a.pose)
        if folder and not (OUT / folder / f"{s}.npz").exists():
            continue
        occ, view, n = accumulate(s, calls, a.pose)
        per[s] = (occ, view)
        nsnap[s] = n
        names.append(s)
        print(f"{s}: {n} calm snapshots, cells in view >= {MIN_VIEW}: {(view >= MIN_VIEW).sum()}")
    np.savez_compressed(OUT / f"persistence_counts_{a.pose}.npz", names=np.array(names),
                        occ=np.stack([per[s][0] for s in names]), view=np.stack([per[s][1] for s in names]),
                        thresh=np.array(THRESH), res=RES, origin=np.array([OX, OY]))
    cls = classify(per, names)
    occ_all = sum(per[s][0] for s in names)
    view_all = sum(per[s][1] for s in names)
    freq_all = [np.where(view_all >= MIN_VIEW, occ_all[k] / np.maximum(view_all, 1), np.nan) for k in range(len(THRESH))]
    summary = dict(pose=a.pose, sessions=nsnap, classes={})
    for k, h in enumerate(THRESH):
        cnt = {CLASS_NAMES[c]: int((cls[k] == c).sum()) for c in CLASS_NAMES}
        summary["classes"][str(h)] = cnt
        print(f"h >= {h}: " + ", ".join(f"{n} {v}" for n, v in cnt.items()))
    np.savez_compressed(OUT / f"persistence_classes_{a.pose}.npz", cls=np.stack(cls), thresh=np.array(THRESH),
                        res=RES, origin=np.array([OX, OY]), freq=np.stack(freq_all))
    json.dump(summary, open(OUT / f"persistence_summary_{a.pose}.json", "w"), indent=1)
    p = render(cls, freq_all, names, a.pose)
    print("figure:", p)


if __name__ == "__main__":
    main()
