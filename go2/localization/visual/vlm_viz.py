"""Draw the VLM's permanence boxes (green fixed, blue rarely moved, red movable, magenta person) and the keep-mask."""
import json, sys
import cv2, numpy as np
import vcommon as V, montage_util as M, vlm_probe as P
model = sys.argv[1]; ids = json.load(open(sys.argv[2])); out = sys.argv[3]
R = {r["id"]: r for r in V.load_records()}
col = {"fixed": (0, 200, 0), "rarely_moved": (255, 150, 0), "movable": (0, 0, 255), "person": (255, 0, 255)}
tiles = []
for pid in ids:
    res = json.load(open(f"cache/vlm_{model}/{pid}.json"))
    im = cv2.resize(cv2.imread(R[pid]["path"]), (640, 360))
    m = P.keep_mask(res["items"])
    im[~m] = (0.35 * im[~m]).astype(np.uint8)
    for it in res["items"]:
        x1, y1, x2, y2 = [int(v * s / 1000) for v, s in zip(it["box"], (640, 360, 640, 360))]
        cv2.rectangle(im, (x1, y1), (x2, y2), col[it["permanence"]], 1)
        cv2.putText(im, it["name"][:22], (x1 + 2, max(10, y1 + 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.32, col[it["permanence"]], 1, cv2.LINE_AA)
    cv2.imwrite("/tmp/_t.jpg", im) if False else None
    bar = np.zeros((22, 640, 3), np.uint8)
    cv2.putText(bar, f"{pid} kept {m.mean():.0%} ({res['latency_s']:.0f} s)", (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
    tiles.append(np.vstack([bar, im]))
cv2.imwrite(out, M.grid(tiles, 2), [cv2.IMWRITE_JPEG_QUALITY, 80])
