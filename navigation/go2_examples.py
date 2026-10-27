"""Labelling by example: a person picks camera frames that show an object, and the box around it in each,
and gives it a name. From those examples the console works out where the object is on the map and its
outline, and can save a place to stand and look at it (Oliver, 10-23: easier than placing and rotating
shapes on the top-down map).

- Each example is a trail frame (stored with the map pose it was taken from) plus a box in it.
- One example: the box's centre direction is cast over the map; the first obstacle is the object.
- Two or more from different spots: the sight lines are intersected (least squares), which is much better.
- The outline: obstacle cells hit by rays across each box, near the estimated centre, as a rotated rectangle.
- Examples are kept (lab_examples.json), so objects can be recomputed when the map or poses change.

Boxes from the vision model (Qwen3-VL on this PC, port 8000) are offered as suggestions; a person can also
draw their own. Camera: pinhole, 79 deg horizontal field of view, 0.33 m ahead of the pose point.
"""
import base64
import json
import math
import os
import re
import threading
import time
import urllib.request

import cv2
import numpy as np

from go2_agent import check_name

HFOV_DEG = 79.0
CAM_AHEAD_M = 0.33
MAX_RANGE_M = 6.0
NEAR_M = 1.5             # outline cells must be this close to the estimated centre
VLM_URL = "http://localhost:8000/v1/chat/completions"
VLM_MODEL = "qwen3-vl-8b"
VOCAB = ["desk", "office chair", "sofa", "conference table", "table", "cabinet", "shelf", "door", "box",
         "printer", "water cooler", "trash bin", "monitor", "person", "other"]
HOST_UID = 1000


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class Examples:
    def __init__(self, maps_dir, name, mapper, trail):
        self.dir, self.name, self.mapper, self.trail = maps_dir, name, mapper, trail
        self.lock = threading.Lock()
        self.path = os.path.join(maps_dir, f"{name}_examples.json")
        self.cache_path = os.path.join(maps_dir, f"{name}_detect_cache.jsonl")
        self.cache = {}
        try:
            with open(self.cache_path) as f:
                for line in f:
                    d = json.loads(line)
                    self.cache[d["f"]] = d["boxes"]
        except (OSError, ValueError):
            pass

    # ---------- storage ----------
    def load(self):
        try:
            with open(self.path) as f:
                return json.load(f)
        except (OSError, ValueError):
            return {"examples": []}

    def _write(self, path, data):
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=1)
        os.chown(tmp, HOST_UID, HOST_UID)
        os.replace(tmp, path)

    def frame(self, url):
        """(trail record [t, x, y, yaw, rel], local file) for a /trail/<day>/<ms>.jpg URL."""
        rel = str(url).split("/trail/", 1)[-1]
        f = self.trail.path(rel)
        if f is None:
            raise ValueError("that camera frame doesn't exist")
        with self.trail.lock:
            rec = next((p for p in self.trail.points if p[4] == rel), None)
        if rec is None:
            raise ValueError("no map pose stored for that frame")
        return rec, f

    # ---------- suggestions from the vision model ----------
    def detect(self, url):
        """Boxes the vision model sees in a frame: [{label, box: [x1, y1, x2, y2] as 0-1 fractions}]. Cached."""
        rec, f = self.frame(url)
        if rec[4] in self.cache:
            return self.cache[rec[4]]
        b64 = base64.b64encode(open(f, "rb").read()).decode()
        prompt = ("List the furniture and objects in this photo from a robot dog's camera, about 30 cm above the floor. "
                  f"Use only these labels: {', '.join(VOCAB)}. Give each object once, as JSON only: "
                  '[{"bbox_2d": [x1, y1, x2, y2], "label": "..."}]')
        body = {"model": VLM_MODEL, "max_tokens": 700, "temperature": 0, "repetition_penalty": 1.05,
                "messages": [{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}},
                    {"type": "text", "text": prompt}]}]}
        req = urllib.request.Request(VLM_URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
        text = json.load(urllib.request.urlopen(req, timeout=60))["choices"][0]["message"]["content"]
        boxes, seen = [], set()
        for m in re.finditer(r'"bbox_2d"\s*:\s*\[([^\]]+)\]\s*,\s*"label"\s*:\s*"([^"]+)"', text):
            try:
                x1, y1, x2, y2 = (float(v) / 1000 for v in m.group(1).split(",")[:4])
            except ValueError:
                continue
            key = (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2))
            if key in seen or x2 <= x1 or y2 <= y1:
                continue
            seen.add(key)
            boxes.append({"label": m.group(2).strip().lower(), "box": [round(v, 4) for v in (x1, y1, x2, y2)]})
        self.cache[rec[4]] = boxes
        with open(self.cache_path, "a") as fh:
            fh.write(json.dumps({"f": rec[4], "boxes": boxes}) + "\n")
        return boxes

    # ---------- geometry ----------
    def _cam(self, rec):
        _, x, y, yaw, _ = rec
        return x + CAM_AHEAD_M * math.cos(yaw), y + CAM_AHEAD_M * math.sin(yaw), yaw

    @staticmethod
    def _bearing(u):
        """Direction (rad, + = left) of horizontal image position u (0..1, left to right)."""
        f = 0.5 / math.tan(math.radians(HFOV_DEG / 2))
        return math.atan2(0.5 - u, f)

    def _ray(self, x, y, a):
        """First obstacle cell along a ray on the saved map: ((x, y), distance) or None."""
        from go2_mapper import OCC_SCORE, RES, SIZE
        m = self.mapper
        for i in range(int(0.2 / RES), int(MAX_RANGE_M / RES)):
            px, py = x + math.cos(a) * i * RES, y + math.sin(a) * i * RES
            c, r = int((px - m.origin[0]) / RES), int((py - m.origin[1]) / RES)
            if not (0 <= r < SIZE and 0 <= c < SIZE):
                return None
            if m.score[r, c] >= OCC_SCORE:
                return (px, py), i * RES
        return None

    def estimate(self, exs):
        """Object centre, outline and stand spot from a list of examples, or None."""
        rays, hits = [], []
        for e in exs:
            cx, cy, yaw = self._cam(e["pose"])
            x1, _, x2, _ = e["box"]
            a = wrap(yaw + self._bearing((x1 + x2) / 2))
            rays.append((cx, cy, a))
            h = self._ray(cx, cy, a)
            if h:
                hits.append(h[0])
        if not rays:
            return None
        # centre: intersect the sight lines when they come from different directions, else the ray hits
        spread = max(abs(wrap(r[2] - rays[0][2])) for r in rays)
        if len(rays) >= 2 and spread > math.radians(15):
            A, b = np.zeros((2, 2)), np.zeros(2)
            for cx, cy, a in rays:
                n = np.array([-math.sin(a), math.cos(a)])        # normal of the line
                A += np.outer(n, n)
                b += np.outer(n, n) @ np.array([cx, cy])
            centre, how = np.linalg.solve(A, b), "intersection"
        elif hits:
            centre, how = np.mean(hits, axis=0), "ray hit"
        else:
            return None
        # outline: obstacle cells hit by rays across each box, near the centre
        cells = []
        for e in exs:
            cx, cy, yaw = self._cam(e["pose"])
            x1, _, x2, _ = e["box"]
            for u in np.linspace(x1, x2, max(3, int((x2 - x1) * HFOV_DEG))):
                h = self._ray(cx, cy, wrap(yaw + self._bearing(u)))
                if h and math.dist(h[0], centre) < NEAR_M:
                    cells.append(h[0])
        if len(cells) >= 3:
            (rx, ry), (w, hgt), ang = cv2.minAreaRect(np.array(cells, np.float32))
            outline = {"x": round(float(rx), 2), "y": round(float(ry), 2), "w": round(max(float(w), 0.3), 2),
                       "h": round(max(float(hgt), 0.3), 2), "yaw": round(math.radians(ang), 3)}
        else:
            outline = {"x": round(float(centre[0]), 2), "y": round(float(centre[1]), 2), "w": 0.4, "h": 0.4, "yaw": 0.0}
        # stand spot: the example taken most straight-on (box nearest the image centre), facing the centre
        best = min(exs, key=lambda e: abs((e["box"][0] + e["box"][2]) / 2 - 0.5))
        _, sx, sy, _, _ = best["pose"]
        stand = {"x": sx, "y": sy, "yaw": math.atan2(centre[1] - sy, centre[0] - sx), "frame": best["url"]}
        return {"centre": [round(float(centre[0]), 2), round(float(centre[1]), 2)], "how": how,
                "outline": outline, "stand": stand, "examples": len(exs), "cells": len(cells)}

    # ---------- people's examples ----------
    def add(self, url, box, name, label, by):
        name = check_name(name)
        x1, y1, x2, y2 = (float(v) for v in box)
        if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
            raise ValueError("box must be [x1, y1, x2, y2] as fractions of the image, x1 < x2, y1 < y2")
        rec, _ = self.frame(url)
        ex = {"id": f"ex{int(time.time() * 1000)}", "name": name, "label": str(label or "").lower()[:40],
              "url": f"/trail/{rec[4]}", "pose": [rec[0], rec[1], rec[2], rec[3], rec[4]],
              "box": [round(v, 4) for v in (x1, y1, x2, y2)], "by": by, "t": round(time.time(), 1)}
        with self.lock:
            data = self.load()
            data["examples"].append(ex)
            self._write(self.path, data)
        return ex

    def remove(self, ex_id):
        with self.lock:
            data = self.load()
            n = len(data["examples"])
            data["examples"] = [e for e in data["examples"] if e["id"] != ex_id]
            self._write(self.path, data)
        return n != len(data["examples"])

    def for_name(self, name):
        return [e for e in self.load()["examples"] if e["name"] == name]

    def upsert_object(self, objects_path, name, by):
        """Recompute the object called name from its examples and write it into the objects file."""
        exs = self.for_name(name)
        est = self.estimate(exs) if exs else None
        try:
            with open(objects_path) as f:
                data = json.load(f)
        except (OSError, ValueError):
            data = {"objects": []}
        data["objects"] = [o for o in data["objects"] if o.get("id") != f"named_{name}"]
        obj = None
        if est:
            labels = [e["label"] for e in exs if e["label"]]
            obj = dict(est["outline"], id=f"named_{name}", name=name,
                       label=max(set(labels), key=labels.count) if labels else "",
                       votes=len(exs), source="examples", how=est["how"], confirmed_by=by,
                       confirmed_t=round(time.time(), 1), stand=est["stand"], centre=est["centre"])
            data["objects"].append(obj)
        self._write(objects_path, data)
        return obj, est
