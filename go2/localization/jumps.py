"""Localizer-quality diagnostic over all event logs (task 1). Also the metric library for the other scripts.

    python3 go2/localization/jumps.py            # table per session -> results/jumps_sessions.csv, events csv, figs

Idea: odometry (the dog's own estimate) is smooth; the console's map pose = map->odom correction * odom.
For each 10 Hz step k->k+1 we predict the map pose by applying the odom step to the previous map pose:
    pred = m_k * (o_k^-1 * o_{k+1})       residual = pred^-1 * m_{k+1}   (in the robot frame, no lever arm)
The residual is what the localizer changed. Consecutive non-zero residuals within 1 s are merged into one event
(a correction can be smeared over 2-3 rows by the 0.1 s sampling and lag). Steps below 2 cm / 1 deg are
"creep" (continuous small corrections, as in SLAM mapping mode) and are summed separately per minute.

Motion state of an event (from odom, +-1 s around it): still (<2 cm/s and <3 deg/s), turning (>10 deg/s
and <10 cm/s), walking (otherwise). Event classes:
    twitch  : still, 0.03 m <= size < 0.3 m and < 10 deg
    jump    : >= 0.3 m or >= 10 deg, while moving or still
    hand?   : >= 0.5 m or >= 10 deg, while odom is frozen for >= 3 s around it, with no cheetah agent call in
              progress (calls.jsonl). Most likely a person placing the dog by hand on the console (or the
              console's own align); reported separately, not counted as localizer jumps.
    start   : first map pose after it was null (localization (re)started)
The lag between the map pose and odom is estimated per session (the lag that minimises residuals while turning)
and odom is interpolated at t - lag before differencing.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

OUT = common.HERE / "results"
FIGS = common.HERE / "figs"
STILL_V, STILL_W = 0.02, math.radians(3)
TURN_W = math.radians(10)
JUMP_M, JUMP_DEG = 0.3, 10.0
TWITCH_M = 0.03
SEED_M, SEED_DEG = 0.02, 1.0   # a step counts as a correction above this
MERGE_S, MAX_EVENT_S = 0.5, 2.0  # merge steps <0.5 s apart into one event, at most 2 s long


def agent_calls():
    """[(t_start, t_end, call)] of cheetah agent calls that move the dog (from calls.jsonl, t = end time)."""
    p = common.GO2 / "data" / "lab_agent" / "calls.jsonl"
    out = []
    for line in open(p):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        o = (e.get("out") or {}).get("out") or {}
        dur = o.get("dur_s") or 0.0
        out.append((e["t"] - max(dur, 0.0) - 1.0, e["t"] + 0.5, e.get("call")))
    st = common.HERE / "console_snapshot" / "state_2026-10-23.json"
    if st.exists():  # the console's own agent log (last 40 calls, includes the console page's calls)
        for e in json.load(open(st))["agents"]["log"]:
            dur = e.get("dur_s") or 0.0
            out.append((e["t"] - dur - 1.0, e["t"] + 0.5, e.get("call")))
    return out


def odom_at(d, tq):
    """Odom (x, y, yaw) interpolated at times tq, from de-duplicated odom samples timed at t - age.odom."""
    to = d["t"] - np.nan_to_num(d["age"][:, 0], nan=0.0)
    od = d["odom"][:, [0, 1, 3]]
    keep = np.r_[True, np.any(np.diff(od, axis=0) != 0, axis=1)] & np.r_[True, np.diff(to) > 1e-3]
    to, od = to[keep], od[keep]
    order = np.argsort(to, kind="stable")
    return common.interp_pose(to[order], tq, od[order])


def motion(d, lag=0.0):
    """Odom resampled at map-pose times (t - lag); speeds (m/s, rad/s) smoothed over +-1 s."""
    t = d["t"]
    # The map pose is refreshed at ~5 Hz (repeated on every other 10 Hz row); each row's value was computed at
    # t - age.map_pose. Evaluate odom at that same instant (from odom samples at their own t - age.odom).
    tm = t - np.nan_to_num(d["age"][:, 2], nan=0.0)
    o = odom_at(d, tm - lag)
    yaw_u = np.unwrap(d["odom"][:, 3])
    k = 10
    v = np.zeros(len(t))
    w = np.zeros(len(t))
    if len(t) > 2 * k:
        dx = np.hypot(d["odom"][2 * k:, 0] - d["odom"][:-2 * k, 0], d["odom"][2 * k:, 1] - d["odom"][:-2 * k, 1])
        dt = t[2 * k:] - t[:-2 * k]
        v[k:-k] = dx / dt
        w[k:-k] = np.abs(yaw_u[2 * k:] - yaw_u[:-2 * k]) / dt
    return o, v, w


def residuals(d, lag=0.0):
    """Per step k (k = 1..n-1): residual (dx, dy in robot frame, dyaw) of the map pose not explained by odom."""
    o, v, w = motion(d, lag)
    m = d["map"]
    ok = ~np.isnan(m[:, 0])
    step_o = common.compose(common.inverse(o[:-1]), o[1:])
    pred = common.compose(m[:-1], step_o)
    res = common.compose(common.inverse(pred), m[1:])
    valid = ok[:-1] & ok[1:] & (np.diff(d["t"]) < 0.5)
    res[~valid] = np.nan
    return res, valid, o, v, w


def estimate_lag(d):
    best = None
    for lag in np.arange(-0.3, 0.31, 0.05):
        res, valid, o, v, w = residuals(d, lag)
        turning = valid & (w[1:] > TURN_W)
        if turning.sum() < 50:
            return 0.0, None
        r = np.nanmedian(np.abs(res[turning, 2]))
        if best is None or r < best[1]:
            best = (lag, r)
    return best


def events(d, lag=0.0, calls=None):
    """Merge non-trivial residual steps into events. Returns list of dicts."""
    res, valid, o, v, w = residuals(d, lag)
    t = d["t"]
    mag = np.hypot(res[:, 0], res[:, 1])
    ang = np.abs(np.degrees(res[:, 2]))
    nz = valid & ((mag > SEED_M) | (ang > SEED_DEG))
    idx = np.flatnonzero(nz)
    evs = []
    group = []
    for i in idx:
        if group and (t[i + 1] - t[group[-1] + 1] > MERGE_S or t[i + 1] - t[group[0]] > MAX_EVENT_S):
            evs.append(group)
            group = []
        group.append(i)
    if group:
        evs.append(group)
    out = []
    m = d["map"]
    calls = calls or []
    for g in evs:
        a, b = g[0], g[-1] + 1  # map pose before a+... : from row a to row b
        # net correction over the event = m_b vs m_a * odom(a->b)
        pred = common.compose(m[a], common.compose(common.inverse(o[a]), o[b]))
        r = common.compose(common.inverse(pred), m[b])
        size = float(math.hypot(r[0], r[1]))
        deg = float(abs(math.degrees(r[2])))
        lo, hi = max(0, a - 10), min(len(t) - 1, b + 10)
        vv, ww = float(np.max(v[lo:hi + 1])), float(np.max(w[lo:hi + 1]))
        if vv < STILL_V and ww < STILL_W:
            state = "still"
        elif ww > TURN_W and vv < 0.1:
            state = "turning"
        else:
            state = "walking"
        # odom frozen for >= 3 s around it?
        lo3, hi3 = max(0, a - 30), min(len(t) - 1, b + 30)
        frozen = (np.max(v[lo3:hi3 + 1]) < STILL_V) and (np.max(w[lo3:hi3 + 1]) < STILL_W)
        in_call = any(s <= t[a] <= e for s, e, c in calls if c not in ("claim", "release", "status", "photo"))
        big = size >= JUMP_M or deg >= JUMP_DEG
        if big and frozen and not in_call and (deg >= JUMP_DEG or size >= 0.5):
            kind = "hand?"
        elif big:
            kind = "jump"
        elif state == "still" and size >= TWITCH_M:
            kind = "twitch"
        elif size >= TWITCH_M or deg >= 2:
            kind = "small"
        else:
            kind = "tiny"
        out.append(dict(t=float(t[a]), t_end=float(t[b]), a=int(a), b=int(b), size=size, deg=deg,
                        dx=float(r[0]), dy=float(r[1]), state=state, kind=kind, in_call=in_call,
                        map_before=[float(x) for x in m[a]], map_after=[float(x) for x in m[b]]))
    # localization (re)starts: map pose appears after being null
    ok = ~np.isnan(m[:, 0])
    starts = np.flatnonzero(ok[1:] & ~ok[:-1]) + 1
    for s in starts:
        out.append(dict(t=float(t[s]), t_end=float(t[s]), a=int(s), b=int(s), size=float("nan"), deg=float("nan"),
                        dx=0.0, dy=0.0, state="-", kind="start", in_call=False,
                        map_before=None, map_after=[float(x) for x in m[s]]))
    out.sort(key=lambda e: e["t"])
    return out


def calm_mask(d, evs, lag=0.0, quiet_s=5.0, max_v=0.3, max_w_deg=30.0, kinds=("jump", "hand?", "start")):
    """Rows where the console pose is trustworthy: no event of `kinds` within +-quiet_s, moving slowly,
    map pose present."""
    t = d["t"]
    o, v, w = motion(d, lag)
    ok = ~np.isnan(d["map"][:, 0]) & (v < max_v) & (w < math.radians(max_w_deg))
    for e in evs:
        if e["kind"] in kinds:
            ok &= ~((t > e["t"] - quiet_s) & (t < e["t_end"] + quiet_s))
    # also the first 5 s after a start of the log (map pose of an older run?)
    ok &= t > t[0] + quiet_s
    return ok


def windows(d, lag=0.0, W=10.0):
    """Net correction over consecutive W-second windows: (t0, size m, |deg|, state)."""
    t = d["t"]
    o, v, w = motion(d, lag)
    m = d["map"]
    ok = ~np.isnan(m[:, 0])
    out = []
    i = 0
    n = len(t)
    while i < n:
        j = np.searchsorted(t, t[i] + W)
        if j >= n:
            break
        if ok[i] and ok[j] and ok[i:j + 1].all() and np.all(np.diff(t[i:j + 1]) < 0.5):
            pred = common.compose(m[i], common.compose(common.inverse(o[i]), o[j]))
            r = common.compose(common.inverse(pred), m[j])
            vv, ww = v[i:j + 1].max(), w[i:j + 1].max()
            st = "still" if (vv < STILL_V and ww < STILL_W) else ("turning" if (vv < 0.1 and ww > TURN_W) else "walking")
            out.append((t[i], math.hypot(r[0], r[1]), abs(math.degrees(r[2])), st))
        i = j
    return out


def twitch_revert(d, evs, within=15.0):
    """Fraction of twitches whose correction is undone (back to within 3 cm of the pre-twitch pose) within 15 s."""
    tw = [e for e in evs if e["kind"] == "twitch"]
    m = d["map"]
    t = d["t"]
    n = 0
    for e in tw:
        a = e["a"]
        j = np.searchsorted(t, e["t_end"] + within)
        seg = m[e["b"] + 1:j]
        if len(seg) and np.min(np.hypot(seg[:, 0] - m[a, 0], seg[:, 1] - m[a, 1])) < 0.03:
            n += 1
    return n / len(tw) if tw else None


def still_yaw_drift(d):
    """Odom and map yaw change (deg/min) over 60 s windows with < 5 cm of odom path."""
    t, o, m = d["t"], d["odom"], d["map"]
    k, i, segs = 600, 0, []
    while i + k < len(t):
        path = np.sum(np.hypot(*np.diff(o[i:i + k + 1, :2], axis=0).T))
        if path < 0.05 and t[i + k] - t[i] < 62:
            yu = np.unwrap(o[i:i + k + 1, 3])
            dm = math.degrees(common.wrap(m[i + k, 2] - m[i, 2])) if not np.isnan(m[[i, i + k], 2]).any() else np.nan
            segs.append((math.degrees(yu[-1] - yu[0]) * 60 / (t[i + k] - t[i]), dm * 60 / (t[i + k] - t[i])))
            i += k
        else:
            i += 50
    return np.array(segs).reshape(-1, 2)


def session_stats(name, calls):
    d = common.load(name)
    t = d["t"]
    has_map = ~np.isnan(d["map"][:, 0])
    if has_map.sum() < 50:
        return None, []
    lag_r = estimate_lag(d)
    lag = lag_r[0] if lag_r else 0.0
    evs = events(d, lag, calls)
    o, v, w = motion(d, lag)
    dt = np.diff(t, prepend=t[0])
    dt[dt > 0.5] = 0
    still = (v < STILL_V) & (w < STILL_W) & has_map
    turning = (w > TURN_W) & (v < 0.1) & has_map
    yaw_u = np.unwrap(d["odom"][:, 3])
    turned_deg = float(np.degrees(np.sum(np.abs(np.diff(yaw_u))[has_map[1:]])))
    walked_m = float(np.sum(np.hypot(np.diff(d["odom"][:, 0]), np.diff(d["odom"][:, 1]))[has_map[1:]]))
    still_h = float(dt[still].sum() / 3600)
    k = {}
    for e in evs:
        k.setdefault(e["kind"], []).append(e)
    jumps = k.get("jump", [])
    tw = k.get("twitch", [])
    calm = calm_mask(d, evs, lag)
    yd = still_yaw_drift(d)
    res, valid, _, _, _ = residuals(d, lag)
    mag = np.hypot(res[:, 0], res[:, 1])
    small = valid & (mag <= SEED_M) & (np.abs(np.degrees(res[:, 2])) <= SEED_DEG)
    wins = windows(d, lag)
    ws = {st: np.array([(a, b) for _, a, b, s_ in wins if s_ == st]).reshape(-1, 2) for st in ("still", "turning", "walking")}
    slides = sum(1 for _, a, b, s_ in wins if a >= JUMP_M or b >= JUMP_DEG)
    creep_cm_per_min = float(100 * np.nansum(mag[small]) / max(valid.sum() / 600, 1e-9))
    row = dict(session=name, minutes=round((t[-1] - t[0]) / 60, 1),
               map_pose_pct=round(100 * has_map.mean()), lag_s=round(lag, 2),
               still_min=round(still_h * 60, 1), turned_deg=round(turned_deg), walked_m=round(walked_m, 1),
               twitches=len(tw), twitch_per_min_still=round(len(tw) / max(still_h * 60, 1e-9), 2) if still_h > 0 else None,
               twitch_med_m=round(float(np.median([e["size"] for e in tw])), 3) if tw else None,
               jumps=len(jumps), jumps_still=sum(e["state"] == "still" for e in jumps),
               jumps_turning=sum(e["state"] == "turning" for e in jumps),
               jumps_walking=sum(e["state"] == "walking" for e in jumps),
               jumps_per_360=round(sum(e["state"] == "turning" for e in jumps) / max(turned_deg / 360, 1e-9), 2)
               if turned_deg > 0 else None,
               jump_max_m=round(max([e["size"] for e in jumps], default=0), 2),
               jump_max_deg=round(max([e["deg"] for e in jumps], default=0), 1),
               hand=len(k.get("hand?", [])), starts=len(k.get("start", [])),
               turning_min=round(float(dt[turning].sum() / 60), 1),
               calm_pct=round(100 * calm.mean()), creep_cm_per_min=round(creep_cm_per_min, 1),
               win10_still_p95_m=round(float(np.percentile(ws["still"][:, 0], 95)), 3) if len(ws["still"]) else None,
               win10_walk_p50_m=round(float(np.percentile(ws["walking"][:, 0], 50)), 3) if len(ws["walking"]) else None,
               win10_walk_p95_m=round(float(np.percentile(ws["walking"][:, 0], 95)), 3) if len(ws["walking"]) else None,
               win10_walk_p95_deg=round(float(np.percentile(ws["walking"][:, 1], 95)), 1) if len(ws["walking"]) else None,
               win10_turn_p95_deg=round(float(np.percentile(ws["turning"][:, 1], 95)), 1) if len(ws["turning"]) else None,
               slides10=slides, n_win=len(wins),
               still_odom_yaw_deg_min=round(float(np.median(yd[:, 0])), 2) if len(yd) else None,
               still_map_yaw_deg_min=round(float(np.nanmedian(yd[:, 1])), 2) if len(yd) and np.isfinite(yd[:, 1]).any() else None,
               still_minutes_measured=len(yd),
               twitch_revert=round(twitch_revert(d, evs), 2) if twitch_revert(d, evs) is not None else None)
    for e in evs:
        e["session"] = name
    return row, evs


def main():
    OUT.mkdir(exist_ok=True)
    FIGS.mkdir(exist_ok=True)
    calls = agent_calls()
    rows, all_evs = [], []
    with open(OUT / "odom_yaw_drift.csv", "w") as f:
        f.write("session,still_minutes,odom_yaw_deg_per_min_median,p10,p90,map_yaw_deg_per_min_median\n")
        for s in common.sessions():
            yd = still_yaw_drift(common.load(s))
            if len(yd):
                f.write(f"{s},{len(yd)},{np.median(yd[:, 0]):.2f},{np.percentile(yd[:, 0], 10):.2f},"
                        f"{np.percentile(yd[:, 0], 90):.2f},{np.nanmedian(yd[:, 1]) if np.isfinite(yd[:, 1]).any() else float('nan'):.2f}\n")
    for s in common.sessions():
        row, evs = session_stats(s, calls)
        if row is None:
            print(f"{s}: no map pose, skipped")
            continue
        rows.append(row)
        all_evs += evs
    keys = list(rows[0].keys())
    with open(OUT / "jumps_sessions.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, keys)
        wr.writeheader()
        wr.writerows(rows)
    ek = ["session", "t", "kind", "state", "size", "deg", "dx", "dy", "in_call", "map_before", "map_after"]
    with open(OUT / "jumps_events.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(ek + ["hms"])
        for e in all_evs:
            if e["kind"] in ("tiny",):
                continue
            wr.writerow([e[k] for k in ek] + [common.hms(e["t"])])
    # print table
    cols = ["session", "minutes", "map_pose_pct", "lag_s", "still_min", "twitches", "twitch_per_min_still",
            "twitch_med_m", "turned_deg", "jumps", "jumps_still", "jumps_turning", "jumps_walking", "jumps_per_360",
            "jump_max_m", "jump_max_deg", "hand", "starts", "calm_pct", "win10_still_p95_m", "win10_walk_p50_m",
            "win10_walk_p95_m", "win10_walk_p95_deg", "win10_turn_p95_deg", "slides10", "n_win", "twitch_revert",
            "still_odom_yaw_deg_min", "still_map_yaw_deg_min"]
    print(" ".join(f"{c[:12]:>12}" for c in cols))
    for r in rows:
        print(" ".join(f"{str(r[c])[:12]:>12}" for c in cols))
    tot = {c: sum(r[c] for r in rows) for c in ["minutes", "still_min", "twitches", "turned_deg", "jumps", "jumps_still",
                                                "jumps_turning", "jumps_walking", "hand", "starts", "slides10", "n_win"]}
    print("TOTAL", tot, "twitch/min still", round(tot["twitches"] / tot["still_min"], 2),
          "turning jumps per 360", round(tot["jumps_turning"] / (tot["turned_deg"] / 360), 2))
    print("\nbig events:")
    for e in all_evs:
        if e["kind"] in ("jump", "hand?"):
            print(f"  {e['session']} {common.hms(e['t'])} {e['kind']:6s} {e['state']:8s} {e['size']:.2f} m {e['deg']:5.1f} deg"
                  f" call={e['in_call']}")
    json.dump(dict(rows=rows), open(OUT / "jumps_sessions.json", "w"), indent=1)
    return rows, all_evs


if __name__ == "__main__":
    main()
