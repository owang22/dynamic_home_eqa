"""Pieces shared by the position recorder and the patrol."""
from __future__ import annotations

import datetime
import json
import math
import os
from pathlib import Path

import yaml
from rclpy.duration import Duration
from rclpy.time import Time

SPORT_TOPIC = "rt/api/sport/request"
BALANCE_STAND, EULER = 1002, 1007  # Unitree sport-mode command numbers


def now_iso() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def yaw_from_quaternion(q) -> float:
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def lookup_pose(tf_buffer, map_frame: str, base_frame: str):
    """(x, y, yaw in radians) of the robot in the map, or None if the map is not localised yet."""
    try:
        t = tf_buffer.lookup_transform(map_frame, base_frame, Time(), timeout=Duration(seconds=0.5))
    except Exception:  # noqa: BLE001 - tf2 raises several kinds
        return None
    tr = t.transform.translation
    return tr.x, tr.y, yaw_from_quaternion(t.transform.rotation)


def load_positions(path: str | Path) -> list[dict]:
    data = yaml.safe_load(Path(path).read_text()) or {}
    positions = data.get("positions", [])
    ids = [p["id"] for p in positions]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path}: position ids repeat: {ids}")
    return positions


def save_positions(path: str | Path, positions: list[dict], note: str = "") -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {"note": note or "positions in the map frame; yaw and pitch in degrees", "positions": positions}
    tmp = path.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(body, sort_keys=False))
    os.replace(tmp, path)


def write_json_atomic(path: Path, obj) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1))
    os.replace(tmp, path)


def save_image(bridge, msg, path: Path, quality: int = 92) -> tuple[int, int]:
    import cv2
    img = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), img, [cv2.IMWRITE_JPEG_QUALITY, quality]):
        raise OSError(f"could not write {path}")
    return img.shape[1], img.shape[0]
