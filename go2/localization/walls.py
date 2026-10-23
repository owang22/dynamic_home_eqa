"""Dominant wall direction (mod 90 deg) of an occupancy image or of a cloud snapshot (Roomba lesson 3).

Gradient-orientation histogram, doubled-angle trick for mod-180 and quadrupled for mod-90:
    theta = angle(sum_i w_i * exp(4j * phi_i)) / 4, strength = |sum| / sum w
"""
from __future__ import annotations

import math

import numpy as np
from scipy import ndimage


def grid_from_points(xy, res=0.05, pad=0.5):
    x0, y0 = xy[:, 0].min() - pad, xy[:, 1].min() - pad
    Wd = int((xy[:, 0].max() + pad - x0) / res) + 1
    Hd = int((xy[:, 1].max() + pad - y0) / res) + 1
    g = np.zeros((Hd, Wd), np.float32)
    g[((xy[:, 1] - y0) / res).astype(int), ((xy[:, 0] - x0) / res).astype(int)] = 1.0
    return g


def dominant_dir(img, sigma=1.5, weight_power=1.0):
    """img: (H,W) float occupancy, row 0 = min y. Returns (theta mod 90 in rad within [-45,45) deg, strength 0..1)."""
    g = ndimage.gaussian_filter(img.astype(np.float32), sigma)
    gy = ndimage.sobel(g, axis=0)
    gx = ndimage.sobel(g, axis=1)
    mag = np.hypot(gx, gy) ** weight_power
    phi = np.arctan2(gy, gx)  # edge normal direction
    z = np.sum(mag * np.exp(4j * phi))
    s = np.abs(z) / max(np.sum(mag), 1e-9)
    theta = np.angle(z) / 4.0  # normal direction mod 90 == wall direction mod 90
    return theta, s


def histogram(img, sigma=1.5, bins=90):
    g = ndimage.gaussian_filter(img.astype(np.float32), sigma)
    gy = ndimage.sobel(g, axis=0)
    gx = ndimage.sobel(g, axis=1)
    mag = np.hypot(gx, gy)
    phi = np.degrees(np.arctan2(gy, gx)) % 90.0
    h, e = np.histogram(phi, bins=bins, range=(0, 90), weights=mag)
    return h / max(h.sum(), 1e-9), e


def cloud_dir(xy, res=0.05, sigma=1.5):
    if len(xy) < 30:
        return float("nan"), 0.0
    return dominant_dir(grid_from_points(xy, res), sigma)


def wrap90(a_deg):
    return (np.asarray(a_deg) + 45.0) % 90.0 - 45.0


def projection_score(xy, angles_deg, bin_m=0.1, rng=None, jitter=0.05):
    """Peakiness of the projection of points onto the normal of each candidate line direction.
    Points from a 0.1 m grid are jittered within their cell so the grid's own rows/columns do not look like walls.
    Returns score per angle (direction of the line, degrees, 0..180)."""
    rng = rng or np.random.default_rng(0)
    p = xy + rng.uniform(-jitter, jitter, xy.shape)
    out = np.zeros(len(angles_deg))
    for k, a in enumerate(np.radians(angles_deg)):
        rho = -p[:, 0] * math.sin(a) + p[:, 1] * math.cos(a)  # distance along the line's normal
        h = np.bincount(np.floor((rho - rho.min()) / bin_m).astype(int))
        out[k] = np.sum(h.astype(float) ** 2) / max(len(p), 1) ** 2
    return out


def manhattan_dir(xy, step=0.5, **kw):
    """Dominant direction mod 90 (deg in [0,90)) of a point set, and a contrast (peak / median)."""
    ang = np.arange(0, 180, step)
    sc = projection_score(xy, ang, **kw)
    n = len(ang) // 2
    m90 = sc[:n] + sc[n:]
    k = int(np.argmax(m90))
    contrast = m90[k] / max(np.median(m90), 1e-12)
    # second peak at least 10 deg away (mod 90)
    d = np.abs(((ang[:n] - ang[k]) + 45) % 90 - 45)
    k2 = int(np.argmax(np.where(d >= 10, m90, -1)))
    return float(ang[k]), float(contrast), float(m90[k2] / m90[k]), m90
