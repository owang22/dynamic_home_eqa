"""Oliver's in-place turns (human driving, recorded lidar), for the AUT (Oliver 11-22: margins too strict; the agent may
reduce them where he has turned before). Read-only. Inputs: exits/cache/*.npz (odom, 1 Hz history, per-cloud clearance
and 36-bin surround, same band 0.18-0.60 m as the console), remap_1121 per-node correction (old map -> 19:29 map).
Output: human_turns.json, one record per spin (|v| <= 0.04 m/s, |w| > 0.15 rad/s, >= 0.5 s, human, standing)."""
import glob, json, math, os, sys, time
import numpy as np
R = "/home/nesl/go2_overnight/remap_1121"
sys.path.insert(0, R); sys.path.insert(0, "/home/nesl/go2_overnight/exits")
from common import HERE as RH, wrap
from rebuild_1121 import frame, poses
from episodes import resample
run = "r2"; F = frame(os.path.join(RH, "out", run, "frame.json"))
I, X = [], []
for s in json.load(open(os.path.join(RH, "out", run, "sessions.json"))):
    if os.path.exists(os.path.join(RH, "track", f"fix_{s}.npz")):
        continue
    T = np.load(os.path.join(RH, "track", f"old_{s}.npz")); P = poses(run, s, F)["node"]
    ok = (T["src"] == 1) & np.isfinite(T["X"][:, 0]); I.append(T["X"][ok]); X.append(P[ok])
I, X = np.vstack(I), np.vstack(X)

def to_new(x, y, yaw):
    p = np.array([x, y]); d = np.hypot(I[:, 0] - x, I[:, 1] - y)
    near = np.nonzero(d < max(0.75, d.min() + 0.05))[0]
    q, th = [], []
    for k in near:
        t = wrap(X[k, 2] - I[k, 2]); c, s = math.cos(t), math.sin(t); dd = p - I[k, :2]
        q.append(X[k, :2] + np.array([c * dd[0] - s * dd[1], s * dd[0] + c * dd[1]])); th.append(t)
    q = np.median(q, 0); t = float(np.median(th))
    return float(q[0]), float(q[1]), float(wrap(yaw + t)), float(d.min())

HL, HW = 0.35, 0.155                       # body half length / half width (0.70 x 0.31 m)
def sweep_margin(sur, turn_rad):
    """Smallest gap (m) between the body outline and the nearest obstacle per 10-deg bin over the turn actually made
    (bin centres; negative = that bin's nearest cell would be inside the swept outline)."""
    best = None
    sgn = 1 if turn_rad >= 0 else -1
    phis = np.linspace(0, abs(turn_rad), max(2, int(abs(math.degrees(turn_rad)) / 3) + 1)) * sgn
    for b, r in enumerate(sur):
        if not np.isfinite(r) or r > 1.0:
            continue
        a = math.radians(-180 + 10 * b + 5)
        px, py = r * math.cos(a), r * math.sin(a)
        for ph in phis:                    # body rotated by ph: the point in the rotated body frame
            c, s = math.cos(ph), math.sin(ph)
            bx, by = c * px + s * py, -s * px + c * py
            gap = math.hypot(max(abs(bx) - HL, 0), max(abs(by) - HW, 0)) if (abs(bx) > HL or abs(by) > HW) else -min(HL - abs(bx), HW - abs(by))
            best = gap if best is None or gap < best else best
    return best

out = []
for f in sorted(glob.glob("/home/nesl/go2_overnight/exits/cache/*.npz")):
    sess = os.path.basename(f)[:-4]; d = np.load(f)
    if not len(d["cl"]):
        continue
    od, ht, hk, hc, hb, hm = d["od"], d["ht"], d["hk"], d["hc"], d["hb"], d["hm"]
    ct, cl, sur = d["ct"][:, 1], d["cl"], d["sur"]
    ok_h = (hk == "human") & (hc == "") & ~(hb < 0.20)
    if not ok_h.any():
        continue
    g, gx, gy, gw, v, w = resample(od, od[0, 0], od[-1, 0])
    k = np.clip(np.searchsorted(ht, g), 0, len(ht) - 1)
    good = ok_h[k] & (np.abs(ht[k] - g) < 1.5)
    spin = good & (np.abs(v) <= 0.04) & (np.abs(w) > 0.15)
    i = 0; n = len(g)
    while i < n:
        if not spin[i]:
            i += 1; continue
        j = i
        while j + 1 < n and (spin[j + 1] or (j + 2 < n and spin[j + 2])):
            j += 1
        if j - i + 1 >= 5:
            t0, t1 = g[i], g[j]; turn = float(gw[j] - gw[i])
            cm = (ct >= t0 - 0.5) & (ct <= t1 + 0.2)
            pre = np.nonzero(ct <= t0)[0]
            idx = np.nonzero(cm)[0]
            if not len(idx) and len(pre) and t0 - ct[pre[-1]] < 5:
                idx = pre[-1:]
            kk = int(np.argmin(np.abs(ht - t0)))
            mx, my, myaw = hm[kk]
            rec = {"session": sess, "t": round(float(t0), 2), "t_pt": time.strftime("%m-%d %H:%M:%S", time.localtime(t0)),
                   "duration_s": round(float(t1 - t0), 1), "turn_deg": round(math.degrees(turn), 0),
                   "drift_m": round(float(math.hypot(gx[j] - gx[i], gy[j] - gy[i])), 2)}
            if np.isfinite(mx):
                nx_, ny_, nyaw, dn = to_new(mx, my, myaw)
                rec["map"] = {"x": round(nx_, 2), "y": round(ny_, 2), "yaw_deg": round(math.degrees(nyaw), 0),
                              "frame": "19:29 map (converted from the old map, nearest track node %.2f m)" % dn}
            if len(idx):
                rec["min_clearance_m"] = round(float(np.nanmin(cl[idx])), 2)
                q = idx[int(np.nanargmin(cl[idx]))]
                rec["min_body_gap_m"] = None if sweep_margin(sur[q], turn) is None else round(sweep_margin(sur[q], turn), 2)
            out.append(rec)
        i = j + 1
json.dump({"made": time.strftime("%Y-%m-%d %H:%M"), "n": len(out), "note": __doc__, "turns": out},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "human_turns.json"), "w"), indent=1)
a = [t for t in out if "min_clearance_m" in t]
cl_ = np.array([t["min_clearance_m"] for t in a]); big = np.array([abs(t["turn_deg"]) >= 90 for t in a])
print("spins", len(out), "with lidar", len(a), "with map pose", sum("map" in t for t in out))
for lab, m in (("all", np.ones(len(a), bool)), (">=90deg", big)):
    print(lab, "n", m.sum(), "clearance p5/p10/p50", np.round(np.percentile(cl_[m], [5, 10, 50]), 2), "below 0.42:", int((cl_[m] < 0.42).sum()))
