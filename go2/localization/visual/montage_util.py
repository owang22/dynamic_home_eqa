"""Small montage helper: grid of pictures with a caption bar and optional horizon/crop lines."""
from __future__ import annotations

import cv2
import numpy as np


def tile(path, caption, w=640, h=360, lines=(), color=(255, 255, 255), border=None):
    im = cv2.imread(str(path))
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
    for (row, c) in lines:
        cv2.line(im, (0, int(row * h / 360)), (w, int(row * h / 360)), c, 1)
    bar = np.zeros((22, w, 3), np.uint8)
    cv2.putText(bar, caption[:90], (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
    out = np.vstack([bar, im])
    if border is not None:
        out = cv2.copyMakeBorder(out, 3, 3, 3, 3, cv2.BORDER_CONSTANT, value=border)
    return out


def grid(tiles, cols):
    h = max(t.shape[0] for t in tiles); w = max(t.shape[1] for t in tiles)
    tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, w - t.shape[1], cv2.BORDER_CONSTANT) for t in tiles]
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    return np.vstack(rows)
