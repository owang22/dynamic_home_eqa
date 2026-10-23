"""Which focal length makes the image-estimated rotation agree with odom over 1-4 s? (calibration sanity check)"""
import numpy as np, math, cv2, json
import vcommon as V, geo
R = V.load_records()
T = [r for r in R if r["source"] == "trail" and r["session"]]
S = V._sessions()
pairs = []
for a, b in zip(T[:-1], T[1:]):
    if a["session"] != b["session"] or b["t"] - a["t"] > 4: continue
    tt, od, mp = S[a["session"]]
    ia, ib = np.searchsorted(tt, [a["t"], b["t"]])
    dodom = math.degrees((od[ib, 3] - od[ia, 3] + math.pi) % (2 * math.pi) - math.pi)
    if 4 < abs(dodom) < 40:
        A, B = geo.raw_matches(a, b)
        if len(A) >= 40: pairs.append((dodom, A, B, a["day"]))
    if len(pairs) >= 250: break
K0 = V.K_for(640, 360, eff=False)   # calibrated K (the sweep is what set FX_SCALE)
out = {}
for dist_on in (True, False):
    for s in (0.80, 0.85, 0.87, 0.90, 0.95, 1.0):
        K = K0.copy(); K[0, 0] *= s; K[1, 1] *= s
        dd = V.DIST720 if dist_on else np.zeros(5)
        est, ref = [], []
        for dodom, A, B, day in pairs:
            na = cv2.undistortPoints(A.reshape(-1, 1, 2).astype(np.float64), K, dd).reshape(-1, 2)
            nb = cv2.undistortPoints(B.reshape(-1, 1, 2).astype(np.float64), K, dd).reshape(-1, 2)
            E, m = cv2.findEssentialMat(na, nb, np.eye(3), method=cv2.RANSAC, prob=0.999, threshold=1.5 / K[0, 0])
            if E is None or E.shape != (3, 3): continue
            _, Rm, t, _ = cv2.recoverPose(E, na, nb, np.eye(3), mask=m.copy())
            est.append(math.degrees(math.atan2(Rm[0, 2], Rm[2, 2]))); ref.append(dodom)
        est, ref = np.array(est), np.array(ref)
        sl = float(np.sum(ref * est) / np.sum(ref ** 2))
        out[f"dist={dist_on} s={s}"] = {"n": len(est), "slope": round(sl, 3), "med_abs": round(float(np.median(np.abs(est - ref))), 2)}
        print(f"dist={dist_on} fx scale {s}: n={len(est)} slope={sl:.3f} med|est-odom|={np.median(np.abs(est-ref)):.2f}", flush=True)
json.dump(out, open("results/fx_sweep.json", "w"), indent=1)
