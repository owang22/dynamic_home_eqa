"""Printed ArUco markers (DICT_4X4_50, 18 cm black square) seen by the front camera.

A background thread runs the detector on the newest full-size camera frame, up to RATE_HZ, and keeps
the latest result: for each marker its distance along the camera axis (z), sideways offset (x, + = right),
bearing (+ = right of straight ahead) and size in pixels. Camera model: pinhole, ~79 deg horizontal
field of view; tape-checked at 1.2 m to within 1 cm (10-23). No lens distortion model yet, so readings
near the image edges are less exact.

Markers by the lab's line-up marks: 0 = A, 1 = B, 2 = C, 3 = D; 4 and 5 are spares (Oliver, 10-23).
"""
import math
import threading
import time

import cv2
import numpy as np

SIZE_M = 0.18
HFOV_DEG = 79.0
RATE_HZ = 10.0
KNOWN = {0: "A", 1: "B", 2: "C", 3: "D", 4: "spare 4", 5: "spare 5"}


class Markers:
    def __init__(self, full, lock):
        self.full, self.lock = full, lock          # the console's latest full-size frame {"img", "t"}
        self.latest = {"t": 0.0, "frame_t": 0.0, "list": [], "ms": None}
        self.det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50),
                                           cv2.aruco.DetectorParameters())
        h = SIZE_M / 2
        self.obj = np.array([[-h, h, 0], [h, h, 0], [h, -h, 0], [-h, -h, 0]], np.float32)
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        last = 0.0
        while True:
            time.sleep(1.0 / RATE_HZ)
            with self.lock:
                img, t = self.full["img"], self.full["t"]
            if img is None or t == last:
                continue
            last = t
            try:
                self.latest = self.detect(img, t)
            except cv2.error:
                pass

    def detect(self, img, frame_t):
        t0 = time.time()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
        h, w = gray.shape
        f = (w / 2) / math.tan(math.radians(HFOV_DEG / 2))
        K = np.array([[f, 0, w / 2], [0, f, h / 2], [0, 0, 1]], float)
        corners, ids, _ = self.det.detectMarkers(gray)
        out = []
        for c, i in zip(corners or [], [] if ids is None else ids.ravel()):
            i = int(i)
            if i not in KNOWN:           # stray patterns sometimes decode as other ids at a distance
                continue
            ok, rv, tv = cv2.solvePnP(self.obj, c.reshape(4, 2), K, None, flags=cv2.SOLVEPNP_IPPE_SQUARE)
            if not ok:
                continue
            x, y, z = (float(v) for v in tv.ravel())
            out.append({"id": i, "mark": KNOWN[i], "z": round(z, 3), "x": round(x, 3), "up": round(-y, 3),
                        "bearing_deg": round(math.degrees(math.atan2(x, z)), 1),
                        "side_px": round(float(np.hypot(*(c[0][0] - c[0][1]))))})
        return {"t": round(time.time(), 3), "frame_t": round(frame_t, 3), "list": out,
                "ms": round((time.time() - t0) * 1000, 1)}

    def snapshot(self, max_age=1.0):
        """The latest detections if they're from a recent frame, else an empty list (with the age)."""
        m = dict(self.latest)
        m["age_s"] = round(time.time() - m["frame_t"], 2) if m["frame_t"] else None
        if m["age_s"] is None or m["age_s"] > max_age:
            m["list"] = []
        return m
