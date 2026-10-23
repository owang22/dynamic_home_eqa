"""Shared loading for the offline localization study (2026-10-23).

Parses go2/data/event_logs/*.jsonl.gz once into localization/cache/<session>.npz:
  rows  (10 Hz): t, odom x/y/z/yaw, map x/y/yaw (nan when null), ages (odom, cloud, map_pose, map)
  clouds (~0.5 Hz): row index, t, n_total, floor_z, age_cloud, and the obs [x,y,z] / flat [x,y] cells
                    (odom frame), concatenated with offsets.
Map helpers for the saved console map (localization/console_snapshot/map_2026-10-23.png).
"""
from __future__ import annotations

import gzip
import json
import math
from pathlib import Path

import numpy as np

GO2 = Path(__file__).resolve().parents[1]
LOGS = GO2 / "data" / "event_logs"
HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
MAP_PNG = HERE / "console_snapshot" / "map_2026-10-23.png"
MAP_RES, MAP_ORIGIN = 0.05, (-6.85, -5.4)


def wrap(a):
    return (np.asarray(a) + np.pi) % (2 * np.pi) - np.pi


def sessions():
    return sorted(p.name[:-9] for p in LOGS.glob("*.jsonl.gz"))


def _parse(name):
    t, od, mp, ag = [], [], [], []
    c_row, c_t, c_n, c_fz, c_age, obs, flat, obs_off, flat_off = [], [], [], [], [], [], [], [0], [0]
    with gzip.open(LOGS / f"{name}.jsonl.gz", "rt") as f:
        for line in f:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            o = e.get("odom")
            if not o:
                continue
            m = e.get("map_pose") or {}
            a = e.get("age") or {}
            t.append(e["t"])
            od.append(o["pos"][:3] + [o["yaw"]])
            mp.append([m.get("x", np.nan) if m.get("x") is not None else np.nan,
                       m.get("y", np.nan) if m.get("y") is not None else np.nan,
                       m.get("yaw", np.nan) if m.get("yaw") is not None else np.nan])
            ag.append([a.get(k, np.nan) if a.get(k) is not None else np.nan
                       for k in ("odom", "cloud", "map_pose", "map")])
            c = e.get("cloud")
            if c and c.get("obs") is not None:
                c_row.append(len(t) - 1)
                c_t.append(e["t"])
                c_n.append(c.get("n_total", 0))
                c_fz.append(c.get("floor_z", np.nan))
                c_age.append(a.get("cloud", np.nan) if a.get("cloud") is not None else np.nan)
                ob = np.asarray(c["obs"], dtype=np.float32).reshape(-1, 3)
                fl = np.asarray(c.get("flat") or [], dtype=np.float32).reshape(-1, 2)
                obs.append(ob)
                flat.append(fl)
                obs_off.append(obs_off[-1] + len(ob))
                flat_off.append(flat_off[-1] + len(fl))
    d = dict(t=np.array(t), odom=np.array(od, dtype=np.float64).reshape(-1, 4),
             map=np.array(mp, dtype=np.float64).reshape(-1, 3), age=np.array(ag, dtype=np.float64).reshape(-1, 4),
             c_row=np.array(c_row, dtype=np.int64), c_t=np.array(c_t), c_n=np.array(c_n),
             c_fz=np.array(c_fz, dtype=np.float64), c_age=np.array(c_age, dtype=np.float64),
             obs=np.concatenate(obs) if obs else np.zeros((0, 3), np.float32),
             flat=np.concatenate(flat) if flat else np.zeros((0, 2), np.float32),
             obs_off=np.array(obs_off), flat_off=np.array(flat_off))
    return d


def load(name):
    CACHE.mkdir(exist_ok=True)
    p = CACHE / f"{name}.npz"
    if not p.exists():
        np.savez_compressed(p, **_parse(name))
    z = np.load(p)
    return {k: z[k] for k in z.files}


def cloud(d, i):
    """obs (N,3) and flat (M,2) of cloud i, odom frame."""
    return d["obs"][d["obs_off"][i]:d["obs_off"][i + 1]], d["flat"][d["flat_off"][i]:d["flat_off"][i + 1]]


def interp_pose(t, tq, xyyaw):
    """Interpolate an (N,3) x,y,yaw track at times tq (yaw unwrapped)."""
    yaw = np.unwrap(xyyaw[:, 2])
    return np.stack([np.interp(tq, t, xyyaw[:, 0]), np.interp(tq, t, xyyaw[:, 1]),
                     wrap(np.interp(tq, t, yaw))], -1)


def compose(a, b):
    """SE2 a*b for (...,3) arrays."""
    c, s = np.cos(a[..., 2]), np.sin(a[..., 2])
    return np.stack([a[..., 0] + c * b[..., 0] - s * b[..., 1], a[..., 1] + s * b[..., 0] + c * b[..., 1],
                     wrap(a[..., 2] + b[..., 2])], -1)


def inverse(a):
    c, s = np.cos(a[..., 2]), np.sin(a[..., 2])
    return np.stack([-c * a[..., 0] - s * a[..., 1], s * a[..., 0] - c * a[..., 1], wrap(-a[..., 2])], -1)


def transform_pts(T, pts):
    """Apply SE2 T=(x,y,yaw) to (N,2+) points (xy only)."""
    c, s = math.cos(T[2]), math.sin(T[2])
    out = np.array(pts, dtype=np.float64, copy=True)
    out[:, 0] = T[0] + c * pts[:, 0] - s * pts[:, 1]
    out[:, 1] = T[1] + s * pts[:, 0] + c * pts[:, 1]
    return out


def load_map():
    import cv2
    m = cv2.imread(str(MAP_PNG), cv2.IMREAD_GRAYSCALE)
    return m  # 0 occupied, 254 free, 205 unknown; row 0 = top = max y


def world_to_px(x, y, h=289):
    col = (np.asarray(x) - MAP_ORIGIN[0]) / MAP_RES
    row = h - 1 - (np.asarray(y) - MAP_ORIGIN[1]) / MAP_RES
    return col, row


def hms(t):
    import time
    return time.strftime("%H:%M:%S", time.localtime(t))
