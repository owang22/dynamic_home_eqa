import json, math, sys, collections
import numpy as np
sys.path.insert(0, sys.argv[3]); from snaplib import snap, CAM
sys.path.insert(0, "/home/nesl/oliver")
from go2_marker_table import MarkerTable
tab = MarkerTable("/home/nesl/oliver/go2_maps", "lab", log=lambda m: None).get()
MODE, DEV = sys.argv[4], (None if sys.argv[5] == "none" else float(sys.argv[5]))
S = json.load(open(sys.argv[1])); P = np.load(sys.argv[2])
w = lambda d: (d + 180) % 360 - 180
rows = collections.defaultdict(list); why = collections.defaultdict(collections.Counter)
for i, s in enumerate(S):
    m, mp = s["m"], s["map_pose"]
    if f"p{i}" not in P.files or not mp or not m.get("fix_ok") or s.get("lost"): continue
    if m["view_deg"] > 30 or m["dist"] > 2.5 or (m.get("ambig") or 0) >= 0.5: continue
    r = snap(m, P[f"p{i}"], mode=MODE, max_dev=DEV)
    if not r["ok"]:
        why[m["mark"]][r["why"].split(" (")[0]] += 1
    psi = mp["yaw"]; c, sn = math.cos(psi), math.sin(psi)
    def to_map(q): return (mp["x"] + c * q["x"] - sn * q["y"], mp["y"] + sn * q["x"] + c * q["y"], w(math.degrees(psi) + q["facing"]))
    raw = to_map(r["raw"]); snp = to_map({**r["snap"], "facing": r["snap"]["facing"] if r.get("facing_ok") else r["raw"]["facing"]}) if r["ok"] else None
    rows[(m["id"], m["mark"])].append({"raw": raw, "snap": snp, "fit": r.get("fit"), "dist": m["dist"], "view": m["view_deg"], "track_fit": s.get("track_fit"),
                                       "facing_ok": r.get("facing_ok"), "dog": (mp["x"], mp["y"], psi), "m": m})
def spread(ps):
    a = np.array([p[:2] for p in ps]); med = np.median(a, 0); d = np.hypot(*(a - med).T)
    f = np.array([p[2] for p in ps]); fm = math.degrees(math.atan2(np.median(np.sin(np.radians(f))), np.median(np.cos(np.radians(f)))))
    fd = np.abs(w(f - fm))
    return med, np.median(d), np.percentile(d, 90), fm, np.median(fd), np.percentile(fd, 90)
def dogpose(tagpos, facing, m):      # dog map pose implied by a sighting with the tag at tagpos/facing (map) and dog-frame tag (fx, fy, fdeg)
    pass
out = {}
for k, rs in sorted(rows.items()):
    good = [r for r in rs if r["snap"]]
    print(f"\n=== detector id {k[0]} ('{k[1]}'): {len(rs)} usable sightings, snapped {len(good)}, failed: {dict(why[k[1]])}")
    if len(good) < 5: continue
    for lab, key in (("raw    ", "raw"), ("snapped", "snap")):
        med, md, p90, fm, fmd, fp90 = spread([r[key] for r in good])
        print(f"  implied tag map pos [{lab}] median ({med[0]:+.3f}, {med[1]:+.3f}) spread median {md*100:.1f} cm p90 {p90*100:.1f} cm | facing {fm:+.1f} deg spread median {fmd:.1f} p90 {fp90:.1f}")
        out.setdefault(k, {})[key] = (med, md, p90, fm, fmd, fp90)
    fo = [r for r in good if r["facing_ok"]]
    fits = np.array([[r["fit"]["rms"], r["fit"]["n"], r["fit"]["range_lidar"] - r["fit"]["range_det"]] for r in good])
    print(f"  fits: rms median {np.median(fits[:,0])*100:.1f} cm, inliers median {np.median(fits[:,1]):.0f}, facing_ok {len(fo)}/{len(good)}; lidar-detector range median {np.median(fits[:,2])*100:+.1f} cm (IQR {np.percentile(fits[:,2],25)*100:+.1f}..{np.percentile(fits[:,2],75)*100:+.1f})")
    # range bias vs distance
    for lo, hi in ((0, 1.2), (1.2, 1.8), (1.8, 2.6)):
        sel = [r["fit"]["range_lidar"] - r["fit"]["range_det"] for r in good if lo <= r["dist"] < hi]
        if sel: print(f"    dist {lo}-{hi} m: n {len(sel)}, lidar-detector {np.median(sel)*100:+.1f} cm")
    # table entry for this id
    sv = tab.get(k[0])
    if sv:
        for key in ("raw", "snap"):
            med, md, p90, fm, *_ = out[k][key]
            print(f"  vs table id {k[0]} '{sv.get('name')}' ({sv['x']:+.2f},{sv['y']:+.2f}) {sv['facing_deg']:+.0f}: [{key}] dx {med[0]-sv['x']:+.3f} dy {med[1]-sv['y']:+.3f} dfacing {w(fm-sv['facing_deg']):+.1f}")
    # marker-implied dog pose vs logged lidar map pose, using the table entry (as the line-up would)
    if sv:
        for key in ("raw", "snap"):
            e, eh = [], []
            for r in good:
                mm = r["m"]
                if key == "raw":
                    fx, fy, fd = CAM + mm["z"], -mm["x"], 180 - mm["yaw_deg"]
                else:
                    q = r["snap"]; psi = r["dog"][2]; c, sn = math.cos(psi), math.sin(psi)
                    # back to dog frame
                    dx, dy = q[0] - r["dog"][0], q[1] - r["dog"][1]
                    fx, fy, fd = c * dx + sn * dy, -sn * dx + c * dy, w(q[2] - math.degrees(psi))
                psi_m = math.radians(sv["facing_deg"] - fd)
                X = sv["x"] - (math.cos(psi_m) * fx - math.sin(psi_m) * fy); Y = sv["y"] - (math.sin(psi_m) * fx + math.cos(psi_m) * fy)
                e.append(math.hypot(X - r["dog"][0], Y - r["dog"][1])); eh.append(abs(w(math.degrees(psi_m - r["dog"][2]))))
            print(f"  marker dog pose vs lidar map pose [{key:4s}]: pos median {np.median(e)*100:.1f} cm p90 {np.percentile(e,90)*100:.1f} | heading median {np.median(eh):.1f} p90 {np.percentile(eh,90):.1f} deg")
