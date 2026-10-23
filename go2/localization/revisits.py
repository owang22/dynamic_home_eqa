"""Revisit consistency without ground truth: register snapshots of the same place directly to each other.

    python3 go2/localization/revisits.py            # builds results/revisit_pairs.npz (slow part, cached)

Two keyframes (persistence.py's calm "fresh" snapshots, any session in the saved map's frame) taken >= 60 s apart
whose console positions are within 1.5 m are registered cloud-to-cloud (cells with column top >= 0.4 m, both in
their own odom frames): correlative search +-0.8 m, +-25 deg around the console-implied relative pose, then
refined. A pair is kept only if the registration is confident: score >= 0.55, margin >= 0.05 over the best pose
>= 0.3 m / 10 deg away, and the reverse registration (i onto j) agrees within 0.1 m / 2 deg.

The registration R maps odom_j -> odom_i. A pose source with map->odom transforms T_i, T_j is consistent at this
revisit if T_i * R == T_j. Error = distance between T_i(R(dog_j)) and T_j(dog_j) and the yaw difference.
evaluate(pairs, poses) returns those errors for any pose source (console, refined, our localizer).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import jumps  # noqa: E402
import matcher  # noqa: E402
import persistence as P  # noqa: E402

OUT = common.HERE / "results"
ZMIN = 0.4


def field_from(pts, res=0.05, pad=1.5, sigma=0.07):
    x0, y0 = pts[:, 0].min() - pad - res / 2, pts[:, 1].min() - pad - res / 2
    Wd = int((pts[:, 0].max() + pad - x0) / res) + 1
    Hd = int((pts[:, 1].max() + pad - y0) / res) + 1
    occ = np.zeros((Hd, Wd), bool)
    occ[np.floor((pts[:, 1] - y0) / res).astype(int), np.floor((pts[:, 0] - x0) / res).astype(int)] = True
    return matcher.Field(occ, res, (x0, y0), sigma=sigma)


def keyframes():
    calls = jumps.agent_calls()
    kf = []
    for s in P.MAP_SESSIONS:
        d, snaps = P.snapshot_poses(s, calls, "console")
        for i, T, dog in snaps:
            ob, _ = common.cloud(d, i)
            ob = ob[ob[:, 2] >= ZMIN][:, :2].astype(float)
            if len(ob) < 100:
                continue
            kf.append(dict(session=s, cloud=i, t=float(d["c_t"][i]), pts=ob, dog=dog.astype(float), T=np.array(T)))
    return kf


def register(A, B, dogB, guess_R, yaw_win=25, xy_win=0.8):
    """Find R (odom_B -> odom_A) maximising the fit of B's cells onto A's. Returns (score, margin, R)."""
    F = field_from(A)
    rel = B - dogB
    pB = common.transform_pts(guess_R, dogB[None])[0]
    guess = (pB[0], pB[1], guess_R[2])
    rk = matcher.match(F, rel, guess, yaw_win, 1.0, xy_win, top_k=4)
    if not rk:
        return 0, 0, None
    b = rk[0]
    alt = 0.0
    for c in rk[1:]:
        if math.hypot(c[1] - b[1], c[2] - b[2]) >= 0.3 or abs(math.degrees(common.wrap(c[3] - b[3]))) >= 10:
            alt = max(alt, c[0])
    # pivot pose -> R
    cth, sth = math.cos(b[3]), math.sin(b[3])
    R = np.array([b[1] - (cth * dogB[0] - sth * dogB[1]), b[2] - (sth * dogB[0] + cth * dogB[1]), b[3]])
    return b[0], b[0] - alt, R


def build_pairs(max_pairs_per_kf=8, seed=0):
    kf = keyframes()
    rng = np.random.default_rng(seed)
    pos = np.array([common.transform_pts(k["T"], k["dog"][None])[0] for k in kf])
    pairs = []
    tried = 0
    order = rng.permutation(len(kf))
    for a in order:
        cand = [b for b in range(len(kf)) if b != a and abs(kf[b]["t"] - kf[a]["t"]) >= 60
                and np.hypot(*(pos[b] - pos[a])) <= 1.5]
        rng.shuffle(cand)
        for b in cand[:max_pairs_per_kf]:
            if a > b and any(p[0] == b and p[1] == a for p in pairs):
                continue
            tried += 1
            ka, kb = kf[a], kf[b]
            guess = common.compose(common.inverse(ka["T"]), kb["T"])  # odom_b -> odom_a implied by console
            sc, mg, R = register(ka["pts"], kb["pts"], kb["dog"], guess)
            if R is None or sc < 0.55 or mg < 0.05:
                continue
            sc2, mg2, R2 = register(kb["pts"], ka["pts"], ka["dog"], common.inverse(R), yaw_win=4, xy_win=0.2)
            if R2 is None:
                continue
            chk = common.compose(R, R2)
            if math.hypot(chk[0], chk[1]) > 0.1 or abs(math.degrees(chk[2])) > 2:
                continue
            pairs.append((a, b, sc, mg, *R))
    print(f"{len(kf)} keyframes, {tried} pairs tried, {len(pairs)} confident")
    np.savez(OUT / "revisit_pairs.npz", pairs=np.array(pairs),
             kf_session=np.array([k["session"] for k in kf]), kf_cloud=np.array([k["cloud"] for k in kf]),
             kf_t=np.array([k["t"] for k in kf]), kf_dog=np.array([k["dog"] for k in kf]),
             kf_T=np.array([k["T"] for k in kf]))


def load_pairs():
    z = np.load(OUT / "revisit_pairs.npz")
    return {k: z[k] for k in z.files}


def evaluate(pr, T_of):
    """T_of(session, cloud) -> map->odom (3,) or None. Returns array of (err_m, err_deg, same_session, dt_s)."""
    out = []
    for a, b, sc, mg, rx, ry, ryaw in pr["pairs"]:
        a, b = int(a), int(b)
        Ta = T_of(str(pr["kf_session"][a]), int(pr["kf_cloud"][a]))
        Tb = T_of(str(pr["kf_session"][b]), int(pr["kf_cloud"][b]))
        if Ta is None or Tb is None:
            continue
        R = np.array([rx, ry, ryaw])
        dog = pr["kf_dog"][b]
        p1 = common.transform_pts(common.compose(Ta, R), dog[None])[0]
        p2 = common.transform_pts(Tb, dog[None])[0]
        dyaw = abs(math.degrees(common.wrap(common.compose(Ta, R)[2] - Tb[2])))
        out.append((math.hypot(*(p1 - p2)), dyaw, pr["kf_session"][a] == pr["kf_session"][b],
                    abs(pr["kf_t"][a] - pr["kf_t"][b])))
    return np.array(out, dtype=float).reshape(-1, 4)


def summarize(e, label):
    if not len(e):
        return f"{label}: no pairs"
    s = e[:, 2] > 0.5
    parts = []
    for name, m in (("all", np.ones(len(e), bool)), ("same session", s), ("cross session", ~s)):
        if m.sum():
            parts.append(f"{name} n={m.sum()}: med {np.median(e[m, 0]):.2f} m / {np.median(e[m, 1]):.1f} deg, "
                         f"p90 {np.percentile(e[m, 0], 90):.2f} m / {np.percentile(e[m, 1], 90):.1f} deg, "
                         f"ok(<0.3 m & <5 deg) {np.mean((e[m, 0] < 0.3) & (e[m, 1] < 5)):.2f}")
    return f"{label}: " + " | ".join(parts)


def console_T(pr):
    tab = {(str(s), int(c)): T for s, c, T in zip(pr["kf_session"], pr["kf_cloud"], pr["kf_T"])}
    return lambda s, c: tab.get((s, c))


def refined_T(folder=OUT / "refined_poses"):
    tab = {}
    for f in folder.glob("*.npz"):
        z = np.load(f)
        for c, T in zip(z["cloud"], z["T_map_odom"]):
            tab[(f.stem, int(c))] = T
    return lambda s, c: tab.get((s, c))


if __name__ == "__main__":
    if not (OUT / "revisit_pairs.npz").exists() or "--rebuild" in sys.argv:
        build_pairs()
    pr = load_pairs()
    print(summarize(evaluate(pr, console_T(pr)), "console"))
    if (OUT / "refined_poses").exists():
        print(summarize(evaluate(pr, refined_T()), "refined (consensus)"))
