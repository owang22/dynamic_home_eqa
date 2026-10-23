"""SuperPoint + LightGlue matching (cvg/LightGlue, installed with --no-deps into visual/.pylib together with kornia;
weights in visual/cache/torch). Same outputs as geo.rel_pose. SuperPoint features are cached in memory per picture.
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".pylib"))
os.environ.setdefault("TORCH_HOME", str(HERE / "cache" / "torch"))

import cv2  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from lightglue import LightGlue, SuperPoint  # noqa: E402

import geo  # noqa: E402

_ex = _lg = None
_feat = {}


def _models():
    global _ex, _lg
    if _ex is None:
        _ex = SuperPoint(max_num_keypoints=2048, detection_threshold=0.003).eval().cuda()
        _lg = LightGlue(features="superpoint", depth_confidence=-1, width_confidence=-1).eval().cuda()
    return _ex, _lg


@torch.no_grad()
def feats(rec):
    if rec["id"] in _feat:
        return _feat[rec["id"]]
    ex, _ = _models()
    im = cv2.imread(rec["path"], cv2.IMREAD_GRAYSCALE)
    im = cv2.resize(im, (640, 360), interpolation=cv2.INTER_AREA)
    t = torch.from_numpy(im).float().cuda()[None, None] / 255.0
    f = ex.extract(t)
    _feat[rec["id"]] = {k: v for k, v in f.items()}
    return _feat[rec["id"]]


def _sub(f, keep):
    idx = torch.from_numpy(np.where(keep)[0]).cuda()
    return {"keypoints": f["keypoints"][:, idx], "keypoint_scores": f["keypoint_scores"][:, idx],
            "descriptors": f["descriptors"][:, idx], "image_size": f["image_size"]}


@torch.no_grad()
def raw_matches(a, b, row_max=None, mask_a=None, mask_b=None):
    _, lg = _models()
    fa, fb = feats(a), feats(b)
    ka = fa["keypoints"][0].cpu().numpy(); kb = fb["keypoints"][0].cpu().numpy()
    sa = np.ones(len(ka), bool); sb = np.ones(len(kb), bool)
    if row_max is not None:
        sa &= ka[:, 1] < row_max; sb &= kb[:, 1] < row_max
    if mask_a is not None:
        sa &= mask_a[ka[:, 1].astype(int).clip(0, 359), ka[:, 0].astype(int).clip(0, 639)]
    if mask_b is not None:
        sb &= mask_b[kb[:, 1].astype(int).clip(0, 359), kb[:, 0].astype(int).clip(0, 639)]
    if sa.sum() < 8 or sb.sum() < 8:
        return np.zeros((0, 2)), np.zeros((0, 2))
    fa2, fb2 = _sub(fa, sa), _sub(fb, sb)
    m = lg({"image0": fa2, "image1": fb2})["matches"][0].cpu().numpy()
    A = fa2["keypoints"][0].cpu().numpy()[m[:, 0]]; B = fb2["keypoints"][0].cpu().numpy()[m[:, 1]]
    return A, B


def rel_pose(a, b, row_max=None, mask_a=None, mask_b=None, thr_px=1.5):
    orig = geo.raw_matches
    try:
        geo.raw_matches = raw_matches
        return geo.rel_pose(a, b, row_max, mask_a, mask_b, thr_px)
    finally:
        geo.raw_matches = orig
