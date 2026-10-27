"""Where the printed ArUco markers are on the map, for marker re-anchoring (go2_mapper.Mapper.marker_fix).

Sources, by priority:
  1. objects with an aruco_id in <maps>/<map>_objects.json, hand-placed ones (source "hand") first: yaw (rad) is the
     direction the printed face looks out;
  2. survey files <maps>/<map>_markers_survey/<mark>.json (nav-planner's survey from fix_ok sightings: id, x, y,
     facing_deg = direction the front looks, degrees CCW from +x).
Reloaded when either changes. When an id has both a hand placement and a survey entry, the difference is logged
(neither is assumed right; the log is how we learn which to trust).
"""
import glob
import json
import math
import os
import time


class MarkerTable:
    def __init__(self, maps_dir, name, log=print):
        self.objects_path = os.path.join(maps_dir, f"{name}_objects.json")
        self.survey_dir = os.path.join(maps_dir, f"{name}_markers_survey")
        self.log = log
        self._stamp = None
        self.table = {}          # aruco id -> {"x", "y", "facing_deg", "source", "name"}
        self.disagree = {}       # aruco id -> {"dist_m", "facing_diff_deg"} hand vs survey

    def _mtimes(self):
        files = [self.objects_path] + sorted(glob.glob(os.path.join(self.survey_dir, "*.json")))
        return tuple((f, os.path.getmtime(f)) for f in files if os.path.exists(f))

    def get(self):
        st = self._mtimes()
        if st != self._stamp:
            self._stamp = st
            self._load()
        return self.table

    def _load(self):
        hand, other, survey = {}, {}, {}
        try:
            with open(self.objects_path) as f:
                objs = json.load(f).get("objects", [])
        except (OSError, ValueError):
            objs = []
        for o in objs:
            a = o.get("aruco_id")
            if a is None or "x" not in o or "y" not in o:
                continue
            e = {"x": float(o["x"]), "y": float(o["y"]), "facing_deg": math.degrees(float(o.get("yaw") or 0.0)),
                 "source": "hand" if o.get("source") == "hand" else f"object:{o.get('source')}", "name": o.get("name")}
            (hand if o.get("source") == "hand" else other).setdefault(int(a), e)
        for f in sorted(glob.glob(os.path.join(self.survey_dir, "*.json"))):
            try:
                d = json.load(open(f))
                survey[int(d["id"])] = {"x": float(d["x"]), "y": float(d["y"]), "facing_deg": float(d["facing_deg"]),
                                        "source": "survey:" + os.path.basename(f), "name": d.get("mark")}
            except (OSError, ValueError, KeyError, TypeError):
                continue
        table = dict(survey)
        table.update(other)
        table.update(hand)
        self.disagree = {}
        for a in set(hand) & set(survey):
            h, s = hand[a], survey[a]
            self.disagree[a] = {"dist_m": round(math.hypot(h["x"] - s["x"], h["y"] - s["y"]), 3),
                                "facing_diff_deg": round((h["facing_deg"] - s["facing_deg"] + 180) % 360 - 180, 1)}
        self.table = table
        self.log(f"[markers] table reloaded {time.strftime('%H:%M:%S')}: "
                 + ", ".join(f"{a}={e['name']} ({e['x']:.2f},{e['y']:.2f}) {e['facing_deg']:.0f}deg from {e['source']}"
                             for a, e in sorted(table.items()))
                 + ("; hand vs survey: " + json.dumps(self.disagree) if self.disagree else ""))
