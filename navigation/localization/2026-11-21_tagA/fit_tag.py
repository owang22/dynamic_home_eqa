"""Where is tag A on the map, according to today's lidar poses? Runs go2_markers on patrol shots (1280x720) and trail
frames (640 px) that have a map pose, and puts each tag-A sighting on the map: lens = pose + 0.30 m forward, then the
tag's camera-frame position (z ahead, x right). Read-only. Usage: python3 fit_tag.py [tag_id]"""
import glob, json, math, os, sys, threading
import cv2, numpy as np
sys.path.insert(0, "/root")
import go2_markers as GM
TAG = int(sys.argv[1]) if len(sys.argv) > 1 else 0
VIEW_MAX = float(sys.argv[2]) if len(sys.argv) > 2 else 30
HAND, SURVEY = (1.41, 0.48), (1.305, 0.679)
frames = []
for vj in glob.glob("/maps/lab_patrols/p_*/views/*/view.json"):
    v = json.load(open(vj))
    for s in v.get("shots", []):
        if s.get("pose") and (s.get("files") or {}).get("dog"):
            frames.append((s["t"], os.path.join(os.path.dirname(vj), s["files"]["dog"]), s["pose"]["x"], s["pose"]["y"],
                           math.radians(s["pose"]["yaw_deg"]), (s.get("loc") or {}).get("track_fit"), "patrol"))
for d in sorted(glob.glob("/maps/lab_trail/2026112*")):
    for l in open(os.path.join(d, "index.jsonl")):
        p = json.loads(l)
        frames.append((p["t"], os.path.join(d, p["f"]), p["x"], p["y"], p["yaw"], (p.get("loc") or {}).get("track_fit"), "trail"))
out = {}
for model in ("pinhole79", "calibrated"):
    GM.CAMERA_MODEL = model
    m = GM.Markers({"img": None, "t": 0.0}, threading.Lock())
    rows = []
    for t, f, x, y, yaw, fit, src in frames:
        img = cv2.imread(f)
        if img is None:
            continue
        for k in (m.detect(img, t) or {}).get("list", []):
            if k.get("id") != TAG or k.get("view_deg", 99) > VIEW_MAX or k.get("reproj_px", 9) > 3.0:
                continue
            cx, cy = x + 0.30 * math.cos(yaw), y + 0.30 * math.sin(yaw)
            tx = cx + k["z"] * math.cos(yaw) + k["x"] * math.sin(yaw)
            ty = cy + k["z"] * math.sin(yaw) - k["x"] * math.cos(yaw)
            rows.append({"t": t, "src": src, "w": img.shape[1], "dog": [round(x, 2), round(y, 2)], "dist": round(k.get("dist") or k["z"], 2),
                         "view": round(k.get("view_deg", 0), 1), "fit": fit, "tag": [round(tx, 3), round(ty, 3)]})
    out[model] = rows
    if rows:
        a = np.array([r["tag"] for r in rows]); dd = np.array([r["dist"] for r in rows])
        med = np.median(a, 0)
        print(f"{model}: n={len(rows)} median tag at ({med[0]:.3f}, {med[1]:.3f}); spread p50 "
              f"{np.median(np.hypot(*(a - med).T)):.3f} m; dist {dd.min():.2f}-{dd.max():.2f} m")
        print(f"   vs hand {math.hypot(med[0]-HAND[0], med[1]-HAND[1]):.3f} m, vs survey {math.hypot(med[0]-SURVEY[0], med[1]-SURVEY[1]):.3f} m")
        for lo, hi in ((0, 1.3), (1.3, 2.0), (2.0, 9)):
            sel = (dd >= lo) & (dd < hi)
            if sel.sum():
                mm = np.median(a[sel], 0); print(f"   dist {lo}-{hi} m: n={sel.sum()} tag ({mm[0]:.3f}, {mm[1]:.3f})")
json.dump(out, open("/tmp/tagfit.json", "w"))
