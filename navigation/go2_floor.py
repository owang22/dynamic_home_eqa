"""Clean a lidar map with the front camera, offline, from a recording of a mapping drive (Oliver, 10-23).

The lidar map smears where the dog's heading drifted and where clutter (chair legs, cables, bags, the
dog's own scatter) sits in the 0.2-0.6 m bump band, so open floor around desks reads as a grey cloud.
In the camera images the open floor is obvious. Three stages, each run in the image that has its tools:

  extract  (rosrobot image, needs rosbag2_py): every FRAME_DT s of drive time a camera frame (jpg), plus
           /odom, /imu rpy, /go2_states body_height and /camera/camera_info  ->  <work>/frames, <work>/meta.npz
  segment  (vllm image, GPU): ADE20K semantic segmentation (SegFormer-B5) of every frame -> <work>/seg.npz
  fuse     (numpy + cv2, any image): corrected pose per frame (go2_straighten's heading correction),
           floor pixels -> floor plane -> map cells; evidence grids; fusion into a cleaner map; pictures

  W=/path/to/work; B=/home/nesl/oliver/go2_recordings/<rec>
  docker run --rm --entrypoint bash -v /home/nesl/oliver:/src -v $B:/bag:ro -v $W:/w rosrobot -c \\
    'source /opt/ros/humble/setup.bash; source /ros2_ws/install/setup.bash; python3 /src/go2_floor.py extract --bag /bag --work /w'
  docker run --rm --gpus '"device=0"' -e NVIDIA_DISABLE_REQUIRE=1 --mount type=tmpfs,destination=/usr/local/cuda/compat \\
    -v /home/nesl/.cache/huggingface:/root/.cache/huggingface -v /home/nesl/oliver:/src -v $W:/w \\
    --entrypoint python3 vllm/vllm-openai:v0.11.0 /src/go2_floor.py segment --work /w
  docker run --rm --entrypoint bash -v /home/nesl/oliver:/src -v $W:/w -v <straighten cache dir>:/cache:ro rosrobot -c \\
    'python3 /src/go2_floor.py fuse --work /w --base /src/go2_maps/lab.grid.npz --out /src/go2_maps/lab_clean.grid.npz \\
     --straighten-cache /cache/cache.npz --straighten-info /src/go2_maps/lab_straightened.info.json --pics /w/pics'

For an extension drive: straighten it first (go2_straighten.py --cache ...), then run the three stages on
its recording with --base = the current map and --out = a new file; the camera evidence only clears cells.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

RES, SIZE, OCC_SCORE = 0.05, 1000, 2     # go2_mapper.py grid
HOST_UID = 1000
FRAME_DT = 0.30            # s of drive time between frames used (~3.3 Hz)
SEG_W, SEG_H = 640, 360    # segmentation is run and kept at half resolution
# camera on the dog (base_link frame: x forward, y left, z up): 0.33 m ahead, 0.04 m above the pose point
CAM_XYZ = (0.33, 0.0, 0.04)
# ADE20K (150 classes, 0-based ids as in the HF config)
FLOOR_CLS = {3: "floor", 28: "rug", 6: "road", 11: "sidewalk", 52: "path", 91: "dirt track"}
PERSON_CLS = {12: "person"}
DESK_CLS = {15: "table", 33: "desk", 45: "counter", 64: "coffee table", 70: "countertop", 77: "bar", 99: "buffet",
            56: "pool table", 73: "kitchen island"}
# floor boundary: a floor pixel with any other class (not a person) just above it = the foot of an object


# ---------------------------------------------------------------- stage 1: read the bag (ROS image only)
def extract(bag, work):
    """Camera frames every FRAME_DT s (jpg, full size) and the small topics, all on bag receive time
    (the same clock go2_straighten.py uses for /odom)."""
    import cv2
    import rosbag2_py
    from rclpy.serialization import deserialize_message
    from rosidl_runtime_py.utilities import get_message
    os.makedirs(os.path.join(work, "frames"), exist_ok=True)
    r = rosbag2_py.SequentialReader()
    r.open(rosbag2_py.StorageOptions(uri=bag, storage_id="sqlite3"), rosbag2_py.ConverterOptions("cdr", "cdr"))
    types = {t.name: t.type for t in r.get_all_topics_and_types()}
    want = ["/camera/image_raw", "/camera/camera_info", "/odom", "/imu", "/go2_states"]
    r.set_filter(rosbag2_py.StorageFilter(topics=[w for w in want if w in types]))
    msg = {k: get_message(types[k]) for k in want if k in types}
    od, imu, st, ft, fs, cam = [], [], [], [], [], None
    last_f = -1e9
    while r.has_next():
        topic, data, t = r.read_next()
        t = t * 1e-9
        if topic == "/camera/image_raw":
            if t - last_f < FRAME_DT:
                continue                                  # skip before deserializing (2.7 MB each)
            m = deserialize_message(data, msg[topic])
            img = np.frombuffer(m.data, np.uint8).reshape(m.height, m.width, -1)
            if m.encoding == "rgb8":
                img = img[:, :, ::-1]
            cv2.imwrite(os.path.join(work, "frames", f"{len(ft):05d}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 93])
            ft.append(t)
            fs.append(m.header.stamp.sec + m.header.stamp.nanosec * 1e-9)
            last_f = t
            continue
        m = deserialize_message(data, msg[topic])
        if topic == "/odom":
            p, q = m.pose.pose.position, m.pose.pose.orientation
            od.append((t, p.x, p.y, p.z, math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))))
        elif topic == "/imu":
            imu.append((t, *[float(v) for v in m.rpy]))
        elif topic == "/go2_states":
            st.append((t, float(m.body_height)))
        elif topic == "/camera/camera_info" and cam is None:
            cam = {"K": np.array(m.k, float).reshape(3, 3), "D": np.array(m.d, float), "wh": (m.width, m.height)}
    np.savez(os.path.join(work, "meta.npz"), ft=np.array(ft), fstamp=np.array(fs), odom=np.array(od),
             imu=np.array(imu), state=np.array(st), K=cam["K"] if cam else np.zeros((3, 3)),
             D=cam["D"] if cam else np.zeros(5), wh=np.array(cam["wh"] if cam else (1280, 720)))
    print(f"{len(ft)} frames, {len(od)} odom, {len(imu)} imu, {len(st)} states; camera_info", cam)


# ---------------------------------------------------------------- stage 2: segmentation (torch image, GPU)
def segment(work, model_id, batch=8, long_side=1024):
    """ADE20K class id per pixel (SEG_W x SEG_H, uint8) for every frame -> <work>/seg.npz (labels, model, s/frame)."""
    import cv2
    import torch
    from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation, Mask2FormerForUniversalSegmentation
    names = sorted(f for f in os.listdir(os.path.join(work, "frames")) if f.endswith(".jpg"))
    proc = AutoImageProcessor.from_pretrained(model_id)
    m2f = "mask2former" in model_id.lower()
    model = (Mask2FormerForUniversalSegmentation if m2f else AutoModelForSemanticSegmentation).from_pretrained(model_id)
    model = model.cuda().eval().half()
    out = np.zeros((len(names), SEG_H, SEG_W), np.uint8)
    t0 = time.time()
    for k in range(0, len(names), batch):
        imgs = []
        for n in names[k:k + batch]:
            im = cv2.imread(os.path.join(work, "frames", n))[:, :, ::-1]
            s = long_side / max(im.shape[:2])
            imgs.append(cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA))
        kw = {"do_resize": False} if not m2f else {"size": {"height": imgs[0].shape[0], "width": imgs[0].shape[1]}}
        x = proc(images=imgs, return_tensors="pt", **kw)
        with torch.no_grad():
            o = model(pixel_values=x["pixel_values"].cuda().half())
            if m2f:
                seg = proc.post_process_semantic_segmentation(o, target_sizes=[(SEG_H, SEG_W)] * len(imgs))
                lab = torch.stack(seg)
            else:
                lab = torch.nn.functional.interpolate(o.logits.float(), size=(SEG_H, SEG_W), mode="bilinear",
                                                      align_corners=False).argmax(1)
        out[k:k + len(imgs)] = lab.cpu().numpy().astype(np.uint8)
        if k % (batch * 25) == 0:
            print(f"{k + len(imgs)}/{len(names)}  {(time.time() - t0) / (k + len(imgs)):.3f} s/frame", flush=True)
    spf = (time.time() - t0) / max(len(names), 1)
    np.savez_compressed(os.path.join(work, "seg.npz"), labels=out, model=model_id, s_per_frame=spf, long_side=long_side)
    print(f"{len(names)} frames, {spf:.3f} s/frame ({model_id}, input long side {long_side})")


# ---------------------------------------------------------------- stage 3: geometry
# parameters of the fuse stage (defaults; all on the command line too)
P = dict(
    R_MAX=4.0,        # m: floor pixels up to this far from the camera vote "floor seen"
    R_CLEAR=2.5,      # m: only votes this close count towards clearing (range error ~ r^2/h per deg of pitch: 0.18 m at 2.5 m)
    MAX_TURN=0.5,     # rad/s: frames taken while turning faster are skipped (blur, timing)
    HORIZON_DEG=1.5,  # rays less than this far below the horizon are ignored (range blows up there)
    PERSON_PAD=24,    # px (half-res): floor this close to a person is ignored (feet, shadows)
    ERODE=2,          # px (half-res): floor mask eroded by this much first (floor/object seam)
    PASS_S=20.0,      # s: votes in different windows of this length count as separate passes
    CLEAR_FRAMES=4,   # a lidar-occupied cell is cleared after this many frames saw floor there (r <= R_CLEAR)
    CLEAR_PASSES=2,   # ...in at least this many separate passes,
    CLEAR_FOOT=0.20,  # ...and object-foot votes are under this share of (floor + foot) votes. Lidar-free floor has a
                      #    median share of ~0.13, lidar-occupied cells ~0.40 (feet scatter with range/pose error)
    DESK_H=0.72,      # m: assumed height of desk/table tops, to place their front edge (lowest desk pixel per column)
    DESK_KEEP=3,      # cells with >= this many frames (2+ passes) of "under a desk/table top" (dilated 1 cell)...
    DESK_SHARE=0.25,  # ...and at least this share of the cell's floor votes are never cleared
    MID_KEEP=3,       # never cleared: desk/table tops (mid layer >= this), high structure (high >= this),
    BND_KEEP=3,       # and cells next to (1 cell) an object foot: >= this many foot votes
    FOOT_SHARE=0.35,  #    making up >= this share of the cell's votes
    NEW_FRAMES=6,     # unseen cells become open floor after this many frames (r <= R_CLEAR) in >= NEW_PASSES passes
    NEW_PASSES=2,
)


def pixel_rays(K, D, w=SEG_W, h=SEG_H, full=(1280, 720)):
    """Undistorted normalized camera coords (x right, y down) of the centre of every segmentation pixel."""
    import cv2
    sx, sy = full[0] / w, full[1] / h
    u, v = np.meshgrid((np.arange(w) + 0.5) * sx - 0.5, (np.arange(h) + 0.5) * sy - 0.5)
    pts = np.c_[u.ravel(), v.ravel()].astype(np.float64)[:, None]
    if np.any(D):
        n = cv2.undistortPointsIter(pts, K, D, None, None, (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 100, 1e-9))[:, 0]
    else:
        n = np.c_[(pts[:, 0, 0] - K[0, 2]) / K[0, 0], (pts[:, 0, 1] - K[1, 2]) / K[1, 1]]
    return n[:, 0].reshape(h, w), n[:, 1].reshape(h, w)


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ground(xn, yn, pose, cam, z0=0.0):
    """Floor points (map frame) of camera rays. xn, yn: normalized coords (1-D); pose: (x, y, yaw, roll, pitch,
    body_height) of base_link in the map frame (roll/pitch from the IMU, + pitch = nose down as in ROS);
    cam: dict(alpha = camera pitch down on the body, rad; imu = 1 to apply the IMU attitude, 0 to ignore).
    z0: height of the plane to hit instead of the floor (desk-top undersides). Returns (gx, gy, range from the
    camera, ray depression below the horizon in rad, negative = above it); rays that never reach the plane get
    range inf."""
    x, y, yaw, roll, pitch, hb = pose
    att = rot_y(cam["imu"] * pitch) @ rot_x(cam["imu"] * roll)       # body attitude, yaw removed
    d = np.stack([np.ones_like(xn), -xn, -yn]) / np.sqrt(1 + xn ** 2 + yn ** 2)   # optical -> body (x fwd, y left, z up)
    d = att @ rot_y(cam["alpha"]) @ d
    c = att @ np.array(CAM_XYZ)                                       # camera relative to base_link, level frame
    cz = hb + c[2]
    dep = -np.arcsin(np.clip(d[2], -1, 1))
    with np.errstate(divide="ignore", invalid="ignore"):
        s = (z0 - cz) / d[2]
    s = np.where(np.isfinite(s) & (s > 0), s, np.inf)
    lx, ly = c[0] + s * d[0], c[1] + s * d[1]
    rng = s * np.hypot(d[0], d[1])
    cs, sn = math.cos(yaw), math.sin(yaw)
    return x + cs * lx - sn * ly, y + sn * lx + cs * ly, rng, dep


def frame_masks(lab, pad, erode):
    """floor pixels to use (largest floor regions touching the image bottom, eroded, away from people) and
    boundary pixels (top edge of that floor with an object, not a person, directly above)."""
    import cv2
    fl = np.isin(lab, list(FLOOR_CLS)).astype(np.uint8)
    n, cc = cv2.connectedComponents(fl, connectivity=4)
    bottom = np.unique(cc[-SEG_H // 8:][fl[-SEG_H // 8:] > 0])
    fl = np.isin(cc, bottom[bottom > 0]).astype(np.uint8)
    person = (lab == 12).astype(np.uint8)
    near_p = cv2.dilate(person, np.ones((2 * pad + 1, 2 * pad + 1), np.uint8)) > 0 if person.any() else np.zeros_like(fl, bool)
    core = cv2.erode(fl, np.ones((2 * erode + 1, 2 * erode + 1), np.uint8)) > 0
    above = np.r_[np.zeros((2, SEG_W), np.uint8), fl[:-2]]       # floor 2 px up?
    lab_up = np.r_[np.full((2, SEG_W), 255, np.uint8), lab[:-2]]
    bnd = (fl > 0) & (above == 0) & (lab_up != 255) & ~np.isin(lab_up, list(FLOOR_CLS) + [12, 2, 5]) & ~near_p
    return core & ~near_p, bnd, near_p


# ---------------------------------------------------------------- stage 3: poses
def frame_poses(meta, a):
    """Map-frame pose of base_link at every frame time: go2_straighten's heading correction delta(t) applied to
    /odom (exactly recomputed from its cache, or interpolated from its info.json), then the map <- odom
    transform T. Plus IMU roll/pitch, body height and the odom yaw rate."""
    T = None
    info = json.load(open(a.straighten_info)) if a.straighten_info else None
    if a.T:
        T = np.array([float(v) for v in a.T.split(",")])
    elif info:
        T = np.array(info["T"])
    if a.straighten_cache:
        import go2_straighten as S
        d = np.load(a.straighten_cache)
        pts, off, ct, od = d["pts"], d["off"], d["ct"], d["odom"]
    else:
        od = meta["odom"]
    ot, ox, oy, oyaw = od[:, 0], od[:, 1], od[:, 2], np.unwrap(od[:, 4])
    k = np.r_[True, np.diff(ot) > 1e-4]
    ot, ox, oy, oyaw = ot[k], ox[k], oy[k], oyaw[k]
    src = "none (raw odom)"
    if a.straighten_cache:
        n = len(off) - 1
        floor = np.array([np.percentile(pts[off[i]:off[i + 1], 2], 20) if off[i + 1] > off[i] else np.nan for i in range(n)])
        floor = np.where(np.isnan(floor), np.nanmedian(floor), floor)
        _, birth = S.voxel_births(pts, off)
        info_, ll = S.heading_evidence(pts, off, ct, birth, np.interp(ct, ot, ox), np.interp(ct, ot, oy), floor, ot, oyaw)
        tg, phi, _ = S.track_residual(info_, ll, S.fit_drift(info_, ot, oyaw), ot, oyaw)
        del pts, birth
        src = "go2_straighten, recomputed from " + a.straighten_cache
    elif info:
        tg = ot[0] + np.array(info["delta_deg"]["t"])
        phi = np.array(info["delta_deg"]["delta"])
        src = "go2_straighten info.json delta(t) (every ~4 s)"
    else:
        tg, phi = ot[[0, -1]], np.zeros(2)
    delta = np.radians(np.interp(ot, tg, phi - phi[0]))
    dm = 0.5 * (delta[1:] + delta[:-1])
    dx, dy = np.diff(ox), np.diff(oy)
    cx = ox[0] + np.r_[0, np.cumsum(np.cos(-dm) * dx - np.sin(-dm) * dy)]
    cy = oy[0] + np.r_[0, np.cumsum(np.sin(-dm) * dx + np.cos(-dm) * dy)]
    cyaw = oyaw - delta
    if T is None:
        T = np.zeros(3)
    ft = meta["ft"]
    c, s = math.cos(T[2]), math.sin(T[2])
    fx, fy = np.interp(ft, ot, cx), np.interp(ft, ot, cy)
    mx, my = T[0] + c * fx - s * fy, T[1] + s * fx + c * fy
    myaw = np.interp(ft, ot, cyaw) + T[2]
    rate = (np.interp(ft + 0.25, ot, oyaw) - np.interp(ft - 0.25, ot, oyaw)) / 0.5
    imu, st = meta["imu"], meta["state"]
    roll, pitch = np.interp(ft, imu[:, 0], imu[:, 1]), np.interp(ft, imu[:, 0], imu[:, 2])
    hb = np.interp(ft, st[:, 0], st[:, 1])
    traj = (T[0] + c * cx - s * cy, T[1] + s * cx + c * cy)
    return np.c_[mx, my, myaw, roll, pitch, hb], rate, src, T, traj


# ---------------------------------------------------------------- stage 3: calibration check against the lidar
def ray_offsets(gx, gy, camx, camy, occ, origin, rmax=6.0, step=0.025):
    """Signed range error of projected object feet: (camera range to the foot) - (range along the same bearing
    to the first lidar-occupied cell). nan where the lidar has nothing within rmax."""
    dx, dy = gx - camx, gy - camy
    r = np.hypot(dx, dy)
    ux, uy = dx / np.maximum(r, 1e-9), dy / np.maximum(r, 1e-9)
    hit = np.full(len(r), np.nan)
    for k in np.arange(0.15, rmax, step):
        c = np.floor((camx + k * ux - origin[0]) / RES).astype(np.int64)
        rr = np.floor((camy + k * uy - origin[1]) / RES).astype(np.int64)
        ok = (c >= 0) & (c < SIZE) & (rr >= 0) & (rr < SIZE) & np.isnan(hit)
        on = np.zeros(len(r), bool)
        on[ok] = occ[rr[ok], c[ok]]
        hit[on] = k
        if not np.isnan(hit).any():
            break
    return r - hit


def calibrate(labels, poses, rate, models, occ, origin, a, nframes=240):
    """Grid search of the camera pitch on the body (alpha) for each intrinsics model and IMU use, scored by how
    many projected object feet land within 15 cm (along the ray) of the first lidar-occupied cell."""
    use = np.nonzero(np.abs(rate) < a.MAX_TURN)[0]
    use = use[np.linspace(0, len(use) - 1, min(nframes, len(use))).astype(int)]
    rng = np.random.default_rng(0)
    pix = []
    for i in use:
        _, bnd, _ = frame_masks(labels[i], a.PERSON_PAD, a.ERODE)
        v, u = np.nonzero(bnd)
        if len(v) > 150:
            k = rng.choice(len(v), 150, replace=False)
            v, u = v[k], u[k]
        pix.append((i, v, u))
    res = []
    for name, (xn, yn) in models.items():
        for imu in (1, 0, -1):
            for al in np.arange(-6.0, 10.01, 0.5):
                cam = {"alpha": math.radians(al), "imu": imu}
                offs, rr = [], []
                for i, v, u in pix:
                    gx, gy, r, dep = ground(xn[v, u], yn[v, u], poses[i], cam)
                    ok = (r < a.R_MAX) & (dep > math.radians(a.HORIZON_DEG))
                    if not ok.any():
                        continue
                    yaw = poses[i, 2]
                    camx, camy = poses[i, 0] + CAM_XYZ[0] * math.cos(yaw), poses[i, 1] + CAM_XYZ[0] * math.sin(yaw)
                    offs.append(ray_offsets(gx[ok], gy[ok], camx, camy, occ, origin))
                    rr.append(r[ok])
                o, r = np.concatenate(offs), np.concatenate(rr)
                f = np.isfinite(o)
                inl = float((np.abs(o[f]) < 0.15).sum() / max(len(o), 1))
                near = f & (np.abs(o) < 0.75)
                res.append({"model": name, "imu": imu, "alpha_deg": round(float(al), 1), "within_15cm": round(inl, 4),
                            "median_offset_m": round(float(np.median(o[near])), 3) if near.any() else None, "n": int(len(o))})
    return res, pix


# ---------------------------------------------------------------- stage 3: evidence grids
def evidence(labels, poses, rate, xn, yn, cam, origin, a):
    """Per cell: frames / passes that saw floor (all within R_MAX, and close within R_CLEAR), frames / passes that
    saw an object's foot, frames / passes that saw floor under a desk/table top (or its front edge). Each frame
    votes once per cell."""
    G = {k: np.zeros((SIZE, SIZE), np.int32) for k in ("floor", "floor_near", "bnd", "desk", "floor_pass", "near_pass", "bnd_pass", "desk_pass")}
    last = {k: np.full((SIZE, SIZE), -1, np.int32) for k in ("floor_pass", "near_pass", "bnd_pass", "desk_pass")}
    used, t0 = 0, None
    ft = a._ft
    for i in range(len(labels)):
        if abs(rate[i]) >= a.MAX_TURN:
            continue
        core, bnd, _ = frame_masks(labels[i], a.PERSON_PAD, a.ERODE)
        pid = int((ft[i] - ft[0]) // a.PASS_S)
        # desk/table tops: in each column, the lowest desk/table pixel above the horizon is the top's front edge
        # (seen from 0.35 m we look at its underside); floor seen beyond that edge in that column is under the top
        desk = np.isin(labels[i], list(DESK_CLS))
        dv, du = np.nonzero(desk)
        ex, ey, er, edep = ground(xn[dv, du], yn[dv, du], poses[i], cam, a.DESK_H)
        k = (er < a.R_CLEAR) & (edep < -math.radians(a.HORIZON_DEG))
        edge_v = np.full(SEG_W, -1)
        np.maximum.at(edge_v, du[k], dv[k])
        edge_r = np.full(SEG_W, np.inf)
        ke = k & (dv == edge_v[du])
        edge_r[du[ke]] = er[ke]
        sets = {}
        for key, m, rmax in (("floor", core, a.R_MAX), ("bnd", bnd, a.R_CLEAR)):
            v, u = np.nonzero(m)
            gx, gy, r, dep = ground(xn[v, u], yn[v, u], poses[i], cam)
            ok = (r < rmax) & (dep > math.radians(a.HORIZON_DEG))
            if key == "floor":
                under = r > edge_r[u] - 0.10
                sets["desk"] = (np.r_[gx[ok & under], ex[ke]], np.r_[gy[ok & under], ey[ke]])
                ok &= ~under
                sets["floor_near"] = (gx[ok & (r < a.R_CLEAR)], gy[ok & (r < a.R_CLEAR)])
            sets[key] = (gx[ok], gy[ok])
        for key, (X, Y) in sets.items():
            c = np.floor((X - origin[0]) / RES).astype(np.int64)
            rr = np.floor((Y - origin[1]) / RES).astype(np.int64)
            ib = (c >= 0) & (c < SIZE) & (rr >= 0) & (rr < SIZE)
            cell = np.unique(rr[ib] * SIZE + c[ib])
            G[key].flat[cell] += 1
            pk = {"floor": "floor_pass", "floor_near": "near_pass", "bnd": "bnd_pass", "desk": "desk_pass"}[key]
            new = cell[last[pk].flat[cell] != pid]
            G[pk].flat[new] += 1
            last[pk].flat[new] = pid
        used += 1
    return G, used


def desk_top(G, a):
    return (G["desk"] >= a.DESK_KEEP) & (G["desk_pass"] >= 2) & (G["desk"] >= a.DESK_SHARE * G["floor_near"])


def fuse(base, G, a):
    """The cleaner map: lidar-occupied cells that the camera repeatedly saw as floor become free, except desk and
    table tops (mid layer), high structure, and cells next to where objects meet the floor; unseen cells that the
    camera saw as floor many times become open floor."""
    import cv2
    score, seen = base["score"].copy(), base["seen"].copy()
    occ = score >= OCC_SCORE
    k3 = np.ones((3, 3), np.uint8)
    top = cv2.dilate(((base["mid"] >= a.MID_KEEP) | (base["high"] >= a.MID_KEEP)
                      | desk_top(G, a)).astype(np.uint8), k3) > 0
    share = G["bnd"] / np.maximum(G["floor_near"] + G["bnd"], 1)
    foot = cv2.dilate(((G["bnd"] >= a.BND_KEEP) & (share >= a.FOOT_SHARE)).astype(np.uint8), k3) > 0
    camfree = (G["floor_near"] >= a.CLEAR_FRAMES) & (G["near_pass"] >= a.CLEAR_PASSES) & (share < a.CLEAR_FOOT)
    clear = occ & camfree & ~top & ~foot
    blocked = {"desk/table/high top": int((occ & camfree & top).sum()),
               "object foot nearby": int((occ & camfree & ~top & foot).sum())}
    new = ~seen & (G["floor_near"] >= a.NEW_FRAMES) & (G["near_pass"] >= a.NEW_PASSES) & (share < a.CLEAR_FOOT) & ~foot & ~top
    score[clear] = -1
    score[new] = -1
    seen = seen | new
    return score, seen, clear, new, blocked


# ---------------------------------------------------------------- stage 3: validation
def validate(base, score, clear, G, labels, poses, rate, xn, yn, cam, places, a):
    """(1) feet of walls/cabinets/doors seen by the camera vs the first lidar-occupied cell along the same ray
    (signed, + = camera farther), median and histogram mode, by range; (2) distance from camera foot cells to the
    nearest lidar-occupied cell; (3) cleared clusters and where; (4) the known objects' cells before/after."""
    import cv2
    org = base["origin"]
    occ0 = base["score"] >= OCC_SCORE
    out = {}
    O, R = [], []
    for i in range(0, len(labels), 3):
        if abs(rate[i]) > 0.3:
            continue
        lab = labels[i]
        _, bnd, _ = frame_masks(lab, a.PERSON_PAD, a.ERODE)
        up = np.r_[np.full((2, SEG_W), 255, np.uint8), lab[:-2]]
        v, u = np.nonzero(bnd & np.isin(up, [0, 10, 14, 35, 44]))     # wall, cabinet, door, wardrobe, drawers
        if not len(v):
            continue
        p = poses[i]
        gx, gy, r, dep = ground(xn[v, u], yn[v, u], p, cam)
        ok = (r < a.R_MAX) & (dep > math.radians(a.HORIZON_DEG))
        O.append(ray_offsets(gx[ok], gy[ok], p[0] + CAM_XYZ[0] * math.cos(p[2]), p[1] + CAM_XYZ[0] * math.sin(p[2]), occ0, org))
        R.append(r[ok])
    O, R = np.concatenate(O), np.concatenate(R)
    f = np.isfinite(O) & (np.abs(O) < 0.6)

    def mode(o):
        h, e = np.histogram(o, bins=np.arange(-0.6, 0.6001, 0.025))
        h = np.convolve(h, [1, 2, 3, 2, 1], "same")
        return round(float(e[h.argmax()] + 0.0125), 3)
    out["wall_feet_vs_lidar"] = {
        "n": int(f.sum()), "median_m": round(float(np.median(O[f])), 3), "mode_m": mode(O[f]),
        "within_15cm": round(float((np.abs(O[np.isfinite(O)]) < 0.15).mean()), 3),
        "by_range": {f"{lo}-{hi} m": {"median": round(float(np.median(O[f & (R >= lo) & (R < hi)])), 3),
                                      "mode": mode(O[f & (R >= lo) & (R < hi)]), "n": int((f & (R >= lo) & (R < hi)).sum())}
                     for lo, hi in ((0.4, 1.2), (1.2, 2.0), (2.0, 3.0), (3.0, 4.0))},
        "note": "+ = the camera puts the wall's foot farther than the first lidar-occupied cell along the ray; the "
                "lidar map's scattered cells on open floor bias the median positive, the mode is the cleaner number"}
    feet = (G["bnd"] >= a.BND_KEEP) & (G["bnd"] >= a.FOOT_SHARE * (G["floor_near"] + G["bnd"]))
    for nm, sc in (("before", base["score"]), ("after", score)):
        dt = cv2.distanceTransform((sc < OCC_SCORE).astype(np.uint8), cv2.DIST_L2, 5) * RES
        out[f"foot_cells_to_lidar_{nm}_m"] = {"median": round(float(np.median(dt[feet])), 3),
                                              "within_10cm": round(float((dt[feet] <= 0.10).mean()), 3)}
    # cleared clusters
    n, cc, st, cen = cv2.connectedComponentsWithStats(clear.astype(np.uint8), connectivity=8)
    pl = {k: (v["x"], v["y"]) for k, v in places.items()}
    clusters = []
    for k in np.argsort(-st[1:, cv2.CC_STAT_AREA])[:15] + 1:
        x, y = org[0] + (cen[k][0] + 0.5) * RES, org[1] + (cen[k][1] + 0.5) * RES
        near = min(pl, key=lambda q: math.hypot(pl[q][0] - x, pl[q][1] - y)) if pl else None
        clusters.append({"cells": int(st[k, cv2.CC_STAT_AREA]), "x": round(x, 2), "y": round(y, 2), "near": near,
                         "dist_m": round(math.hypot(pl[near][0] - x, pl[near][1] - y), 2) if near else None})
    out["cleared_clusters"] = clusters
    out["cleared_near_places_1.5m"] = {}
    rr, cc_ = np.nonzero(clear)
    X, Y = org[0] + (cc_ + 0.5) * RES, org[1] + (rr + 0.5) * RES
    for k, (x, y) in pl.items():
        out["cleared_near_places_1.5m"][k] = int((np.hypot(X - x, Y - y) < 1.5).sum())
    # known objects: occupied cells within 0.4 m of each place's target (the thing itself), before / after
    objs = {}
    for k, v in places.items():
        t = v.get("target")
        if not t:
            continue
        c0, r0 = int((t["x"] - org[0]) / RES), int((t["y"] - org[1]) / RES)
        rad = int(0.4 / RES)
        yy, xx = np.mgrid[-rad:rad + 1, -rad:rad + 1]
        disk = (xx ** 2 + yy ** 2) <= rad ** 2
        sl = (slice(r0 - rad, r0 + rad + 1), slice(c0 - rad, c0 + rad + 1))
        objs[k] = {"occ_before": int(((base["score"][sl] >= OCC_SCORE) & disk).sum()),
                   "occ_after": int(((score[sl] >= OCC_SCORE) & disk).sum()),
                   "mid_cells": int(((base["mid"][sl] >= a.MID_KEEP) & disk).sum())}
    out["known_objects_0.4m"] = objs
    out["known_objects_note"] = ("place targets were set by hand on older maps and several sit on open floor (sofa: 1 "
                                 "occupied cell before); see crop_places.png")
    camobj = occ0 & (feet | desk_top(G, a))
    out["lidar_cells_with_camera_object_kept"] = {"cells": int(camobj.sum()),
                                                  "kept": round(float((score[camobj] >= OCC_SCORE).mean()), 3)}
    return out


# ---------------------------------------------------------------- stage 3: pictures
def pictures(pics, base, score, seen, clear, new, G, places, traj, labels, poses, rate, xn, yn, cam, a):
    import cv2
    os.makedirs(pics, exist_ok=True)
    org = base["origin"]
    known = np.argwhere(base["seen"] | seen)
    (R0, C0), (R1, C1) = known.min(0) - 10, known.max(0) + 11

    def to_px(x, y, r0, r1, c0, s):
        return int(((x - org[0]) / RES - c0) * s), int(((r1 - r0) - ((y - org[1]) / RES - r0)) * s)

    def map_img(sc, sn, r0, r1, c0, c1, s, cl=None, nw=None):
        img = np.full((SIZE, SIZE, 3), 205, np.uint8)
        img[sn] = 254
        img[sc >= OCC_SCORE] = 0
        if cl is not None:
            img[cl] = (60, 200, 60)        # cleared by the camera
        if nw is not None:
            img[nw] = (240, 210, 150)      # newly seen open floor
        img = img[r0:r1, c0:c1][::-1]
        return cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)

    def ev_img(r0, r1, c0, c1, s):
        f = G["floor_near"].astype(np.float32)
        v = np.clip(np.log1p(f) / np.log1p(300), 0, 1)
        img = cv2.applyColorMap((v * 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS)
        img[f == 0] = (255, 255, 255)
        img[(base["score"] >= OCC_SCORE) & (f == 0)] = (150, 150, 150)
        img[desk_top(G, a)] = (255, 150, 0)
        img[(G["bnd"] >= a.BND_KEEP) & (G["bnd"] >= a.FOOT_SHARE * (G["floor_near"] + G["bnd"]))] = (0, 0, 255)
        img = img[r0:r1, c0:c1][::-1]
        return cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)

    def mark(img, r0, r1, c0, s, names=None, fs=0.45):
        for k, v in places.items():
            if names and k not in names:
                continue
            p = to_px(v["x"], v["y"], r0, r1, c0, s)
            cv2.circle(img, p, max(3, s), (0, 0, 220), -1)
            cv2.putText(img, k, (p[0] + 5, p[1] - 4), cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 0, 180), 1, cv2.LINE_AA)

    def title(img, txt):
        cv2.putText(img, txt, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
        return img
    sep = lambda h: np.full((h, 8, 3), 255, np.uint8)
    s = 3
    b = map_img(base["score"], base["seen"], R0, R1, C0, C1, s)
    c = map_img(score, seen, R0, R1, C0, C1, s, clear, new)
    for im in (b, c):
        mark(im, R0, R1, C0, s)
    px = np.array([to_px(x, y, R0, R1, C0, s) for x, y in zip(traj[0][::20], traj[1][::20])])
    cv2.polylines(b, [px.astype(np.int32)], False, (255, 140, 0), 1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(pics, "maps_before_after.png"),
                np.hstack([title(b, "before (lidar, straightened)"), sep(b.shape[0]),
                           title(c, "after: green = cleared by camera, blue = new open floor")]))
    e = ev_img(R0, R1, C0, C1, s)
    mark(e, R0, R1, C0, s)
    cv2.imwrite(os.path.join(pics, "camera_floor_evidence.png"),
                title(e, f"camera floor votes (r<={a.R_CLEAR} m, log, dark=few); red = object feet; blue = desk/table top; grey = lidar occ, no floor"))

    # zoomed crops: the desk area and the corridor to door_outside
    def bbox(names, m):
        xs = [places[k]["x"] for k in names if k in places] + [places[k]["target"]["x"] for k in names if k in places and places[k].get("target")]
        ys = [places[k]["y"] for k in names if k in places] + [places[k]["target"]["y"] for k in names if k in places and places[k].get("target")]
        c0, c1 = int((min(xs) - m - org[0]) / RES), int((max(xs) + m - org[0]) / RES)
        r0, r1 = int((min(ys) - m - org[1]) / RES), int((max(ys) + m - org[1]) / RES)
        return r0, r1, c0, c1
    for nm, names, m in (("crop_desks", ["desk_brian", "desk_oliver", "desk_pragya"], 1.5),
                         ("crop_corridor", ["desk_brian", "desk_oliver", "door_outside"], 1.0)):
        r0, r1, c0, c1 = bbox(names, m)
        s2 = 10
        ims = [map_img(base["score"], base["seen"], r0, r1, c0, c1, s2), ev_img(r0, r1, c0, c1, s2),
               map_img(score, seen, r0, r1, c0, c1, s2, clear, new)]
        for im in ims:
            mark(im, r0, r1, c0, s2, fs=0.5)
            for k in range(0, (c1 - c0) * s2, 20 * s2):          # 1 m grid ticks
                cv2.line(im, (k, 0), (k, 6), (0, 0, 0), 1)
        ims = [title(ims[0], "before"), title(ims[1], "camera: floor / feet (red) / desk tops (blue)"), title(ims[2], "after")]
        cv2.imwrite(os.path.join(pics, nm + ".png"), np.hstack([ims[0], sep(ims[0].shape[0]), ims[1], sep(ims[0].shape[0]), ims[2]]))

    # every place's target (the thing itself): 3 x 3 m before / camera / after, target ringed
    tiles = []
    for k, v in places.items():
        t = v.get("target")
        if not t:
            continue
        c0, r0 = int((t["x"] - 1.5 - org[0]) / RES), int((t["y"] - 1.5 - org[1]) / RES)
        r1, c1 = r0 + 60, c0 + 60
        ims = [map_img(base["score"], base["seen"], r0, r1, c0, c1, 4), ev_img(r0, r1, c0, c1, 4),
               map_img(score, seen, r0, r1, c0, c1, 4, clear, new)]
        for im in ims:
            cv2.circle(im, (120, 120), int(0.4 / RES * 4), (0, 0, 255), 1)
        row = np.hstack([ims[0], sep(240), ims[1], sep(240), ims[2]])
        cv2.putText(row, k, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        tiles.append(np.vstack([row, np.full((8, row.shape[1], 3), 255, np.uint8)]))
    if tiles:
        half = (len(tiles) + 1) // 2
        colL, colR = np.vstack(tiles[:half]), np.vstack(tiles[half:] or [np.zeros_like(tiles[0])])
        colR = np.vstack([colR, np.full((colL.shape[0] - colR.shape[0], colR.shape[1], 3), 255, np.uint8)])
        cv2.imwrite(os.path.join(pics, "crop_places.png"), np.hstack([colL, np.full((colL.shape[0], 16, 3), 255, np.uint8), colR]))

    # sample frames: floor mask and its projection
    ok = np.nonzero(np.abs(rate) < 0.2)[0]
    pick = ok[np.linspace(len(ok) * 0.05, len(ok) * 0.95, 6).astype(int)]
    rows = []
    for i in pick:
        im = cv2.resize(cv2.imread(os.path.join(a.work, "frames", f"{i:05d}.jpg")), (SEG_W, SEG_H))
        core, bnd, near_p = frame_masks(labels[i], a.PERSON_PAD, a.ERODE)
        ov = im.copy()
        ov[core] = (0, 200, 0)
        ov[near_p] = (200, 0, 200)
        ov = cv2.addWeighted(im, 0.55, ov, 0.45, 0)
        ov[cv2.dilate(bnd.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0] = (0, 0, 255)
        p = poses[i]
        cv2.putText(ov, f"frame {i}  t={a._ft[i] - a._ft[0]:.0f}s", (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        half = int(4.5 / RES)
        cr, cc_ = int((p[1] - org[1]) / RES), int((p[0] - org[0]) / RES)
        r0, r1, c0, c1 = cr - half, cr + half, cc_ - half, cc_ + half
        s3 = SEG_H / (2 * half)
        mp = map_img(base["score"], base["seen"], r0, r1, c0, c1, 1)
        mp = cv2.resize(mp, (SEG_H, SEG_H), interpolation=cv2.INTER_NEAREST)
        for m, col, step in ((core, (0, 170, 0), 4), (bnd, (0, 0, 255), 1)):
            v, u = np.nonzero(m)
            v, u = v[::step], u[::step]
            gx, gy, r, dep = ground(xn[v, u], yn[v, u], p, cam)
            k = (r < a.R_MAX) & (dep > math.radians(a.HORIZON_DEG))
            for x, y in zip(gx[k], gy[k]):
                q = (int(((x - org[0]) / RES - c0) * s3), int((r1 - r0 - ((y - org[1]) / RES - r0)) * s3))
                cv2.circle(mp, q, 1, col, -1)
        q = (int(((p[0] - org[0]) / RES - c0) * s3), int((r1 - r0 - ((p[1] - org[1]) / RES - r0)) * s3))
        cv2.arrowedLine(mp, q, (int(q[0] + 25 * math.cos(p[2])), int(q[1] - 25 * math.sin(p[2]))), (255, 0, 0), 2)
        rows.append(np.hstack([ov, sep(SEG_H), mp]))
    grid = [np.hstack([rows[k], sep(SEG_H), rows[k + 1]]) for k in range(0, len(rows) - 1, 2)]
    cv2.imwrite(os.path.join(pics, "sample_frames.jpg"), np.vstack([np.vstack([g, np.full((8, g.shape[1], 3), 255, np.uint8)]) for g in grid]))


# ---------------------------------------------------------------- main
def run_fuse(a):
    meta = dict(np.load(os.path.join(a.work, "meta.npz")))
    seg = np.load(os.path.join(a.work, "seg.npz"))
    labels = seg["labels"]
    a._ft = meta["ft"]
    t0 = time.time()
    poses, rate, src, T, traj = frame_poses(meta, a)
    print(f"poses: {src}; T = {np.round(T, 4).tolist()}  ({time.time() - t0:.0f} s)")
    base = dict(np.load(a.base))
    K, D = meta["K"], meta["D"]
    if a.intrinsics == "pinhole":       # 79 deg horizontal FOV, centred, no distortion
        f = 640 / math.tan(math.radians(39.5))
        K, D = np.array([[f, 0, 639.5], [0, f, 359.5], [0, 0, 1]]), np.zeros(5)
    xn, yn = pixel_rays(K, D)
    cam = {"alpha": math.radians(a.alpha), "imu": 1}
    calib = None
    if a.calibrate:
        res, _ = calibrate(labels, poses, rate, {a.intrinsics: (xn, yn)}, base["score"] >= OCC_SCORE, base["origin"], a)
        calib = max(res, key=lambda r: r["within_15cm"])
        print("lidar-based pitch search (biased by lidar smear; for reference):", calib)
    G, used = evidence(labels, poses, rate, xn, yn, cam, base["origin"], a)
    print(f"evidence from {used} frames ({time.time() - t0:.0f} s)")
    score, seen, clear, new, blocked = fuse(base, G, a)
    occ0 = base["score"] >= OCC_SCORE
    places = json.load(open(a.places)) if a.places and os.path.exists(a.places) else {}
    val = validate(base, score, clear, G, labels, poses, rate, xn, yn, cam, places, a)
    out = {k: v for k, v in base.items()}
    out["score"], out["seen"] = score.astype(base["score"].dtype), seen
    np.savez_compressed(a.out, **out)
    info_path = a.out.replace(".grid.npz", "") + ".info.json"
    stats = {"occupied_before": int(occ0.sum()), "occupied_after": int((score >= OCC_SCORE).sum()),
             "cleared": int(clear.sum()), "cleared_share": round(float(clear.sum() / max(occ0.sum(), 1)), 3),
             "kept_although_camera_saw_floor": blocked, "new_open_cells": int(new.sum()),
             "seen_before": int(base["seen"].sum()), "seen_after": int(seen.sum()),
             "camera_floor_cells": int((G["floor"] > 0).sum()),
             "camera_floor_cells_clear_grade": int(((G["floor_near"] >= a.CLEAR_FRAMES) & (G["near_pass"] >= a.CLEAR_PASSES)).sum()),
             "camera_foot_cells": int(((G["bnd"] >= a.BND_KEEP) & (G["bnd"] >= a.FOOT_SHARE * (G["floor_near"] + G["bnd"]))).sum()), "frames_used": used, "frames": int(len(labels))}
    info = {"base": a.base, "out": a.out, "work": a.work, "poses": src, "T": [float(v) for v in T],
            "segmentation": {"model": str(seg["model"]), "s_per_frame": round(float(seg["s_per_frame"]), 3),
                             "input_long_side": int(seg["long_side"]), "kept_at": [SEG_W, SEG_H]},
            "camera": {"intrinsics": a.intrinsics, "K": K.round(3).tolist(), "D": D.round(5).tolist(),
                       "alpha_deg_down_on_body": a.alpha, "imu_attitude": "applied (rpy, + pitch = nose down)",
                       "xyz_on_base_link": CAM_XYZ, "height": "body_height + 0.04 (+ attitude)",
                       "lidar_pitch_search": calib},
            "params": {k: getattr(a, k) for k in P}, "stats": stats, "validation": val,
            "made": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(info_path, "w") as fh:
        json.dump(info, fh, indent=1)
    np.savez_compressed(os.path.join(a.work, "evidence.npz"), clear=clear, new=new, **G)
    for p in (a.out, info_path):
        try:
            os.chown(p, HOST_UID, HOST_UID)
        except PermissionError:
            pass
    print(json.dumps(stats))
    print(json.dumps(val["wall_feet_vs_lidar"]))
    if a.pics:
        pictures(a.pics, base, score, seen, clear, new, G, places, traj, labels, poses, rate, xn, yn, cam, a)
        print("pictures in", a.pics)
    print(f"wrote {a.out} and {info_path} ({time.time() - t0:.0f} s)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract", help="frames + small topics from the bag (rosrobot image)")
    e.add_argument("--bag", required=True)
    e.add_argument("--work", required=True)
    s = sub.add_parser("segment", help="ADE20K segmentation of the frames (GPU)")
    s.add_argument("--work", required=True)
    s.add_argument("--model", default="facebook/mask2former-swin-large-ade-semantic",
                   help="or nvidia/segformer-b5-finetuned-ade-640-640")
    s.add_argument("--batch", type=int, default=8)
    s.add_argument("--long-side", type=int, default=1024)
    f = sub.add_parser("fuse", help="project floor onto the map and write the cleaned map")
    f.add_argument("--work", required=True)
    f.add_argument("--base", required=True, help="map to clean (grid.npz)")
    f.add_argument("--out", required=True, help="new grid.npz (never the live map)")
    f.add_argument("--places", default=None, help="places.json for crops/validation (default: <base dir>/lab.places.json)")
    f.add_argument("--straighten-cache", default=None, help="go2_straighten.py cache.npz: exact heading correction")
    f.add_argument("--straighten-info", default=None, help="go2_straighten.py info.json: T and delta(t) (fallback)")
    f.add_argument("--T", default=None, help="map <- odom transform x,y,yaw (default: from --straighten-info)")
    f.add_argument("--intrinsics", default="caminfo", choices=["caminfo", "pinhole"])
    f.add_argument("--alpha", type=float, default=1.1, help="camera pitch down on the body, deg (vanishing points)")
    f.add_argument("--calibrate", action="store_true", help="also run the lidar-based pitch search (slow)")
    f.add_argument("--pics", default=None)
    for k, v in P.items():
        f.add_argument("--" + k, type=type(v), default=v)
    a = ap.parse_args()
    if a.cmd == "extract":
        extract(a.bag, a.work)
    elif a.cmd == "segment":
        segment(a.work, a.model, a.batch, a.long_side)
    else:
        if a.places is None:
            a.places = os.path.join(os.path.dirname(a.base), "lab.places.json")
        if os.path.realpath(a.out) == os.path.realpath(a.base) or os.path.basename(a.out) == "lab.grid.npz":
            sys.exit("refusing to overwrite the base / live map; write a new file")
        run_fuse(a)


if __name__ == "__main__":
    main()
