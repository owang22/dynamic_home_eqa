"""Image embeddings for the picture memory (SigLIP ViT-SO400M-14-384), so a search can find what the descriptions
missed ("blue roll of tape" was never written down, but it is in the picture).

    python3 go2/lab_agent/embeddings.py update            # embed every picture not embedded yet
    python3 go2/lab_agent/embeddings.py search "blue roll of tape"
    python3 go2/lab_agent/embeddings.py serve             # keep the model loaded for text queries (127.0.0.1:8311)

Each picture is embedded three times: the whole picture squashed to a square (SigLIP was trained that way), and a
square crop of its left and right part (a 16:9 frame holds a lot; a small thing is easier to match in a crop).
A text query is scored against all three and the best one counts. Stored in go2/data/lab_agent/embeddings/:
views.npy (pictures x 3 x 1152, float16, unit length) and ids.json (the picture id of each row). Rows are only
appended, so a picture is embedded once.

The weights come from the HF cache (timm/ViT-SO400M-14-SigLIP-384); the text tokenizer (timm/ViT-B-16-SigLIP,
fetched once on 2026-10-23) is kept in go2/data/models/siglip_tokenizer. It runs on the GPU when about 3 GB are
free there (vLLM takes most of it), else on the CPU (slower: about 1 s per picture, 0.2 s per query).
"""
from __future__ import annotations

import argparse
import json
import os
import threading
from pathlib import Path

import numpy as np

import memory as M

EMB = M.DATA / "embeddings"
VIEWS, IDS = EMB / "views.npy", EMB / "ids.json"
WEIGHTS = (Path.home() / ".cache/huggingface/hub/models--timm--ViT-SO400M-14-SigLIP-384/snapshots/"
           "ac16108d567c4389e6cd2b11c9b8585f7474435b/open_clip_model.safetensors")
TOKENIZER = M.ROOT / "data" / "models" / "siglip_tokenizer"
_MODEL, _LOCK = {}, threading.Lock()


def model():
    """(model, preprocess, tokenizer, device), loaded once."""
    with _LOCK:
        if not _MODEL:
            import open_clip
            import torch
            from open_clip.tokenizer import HFTokenizer
            free = torch.cuda.mem_get_info()[0] if torch.cuda.is_available() else 0
            dev = "cuda" if free > 3e9 else "cpu"
            m, _, pre = open_clip.create_model_and_transforms(
                "ViT-SO400M-14-SigLIP-384", pretrained=str(WEIGHTS), image_mean=(0.5,) * 3, image_std=(0.5,) * 3,
                image_interpolation="bicubic", image_resize_mode="squash")
            m = (m.half() if dev == "cuda" else m).to(dev).eval()
            tok = HFTokenizer(str(TOKENIZER), context_length=64, clean="canonicalize")
            _MODEL.update(m=m, pre=pre, tok=tok, dev=dev)
    return _MODEL["m"], _MODEL["pre"], _MODEL["tok"], _MODEL["dev"]


def views(im):
    """The whole picture, and square crops of its left and right part."""
    w, h = im.size
    return [im, im.crop((0, 0, h, h)), im.crop((w - h, 0, w, h))] if w > h else [im, im, im]


def embed_images(paths, batch=8):
    """-> pictures x 3 x 1152 float16 (unit length)."""
    import torch
    from PIL import Image
    m, pre, _, dev = model()
    out = []
    for i in range(0, len(paths), batch):
        ims = [v for p in paths[i:i + batch] for v in views(Image.open(p).convert("RGB"))]
        x = torch.stack([pre(v) for v in ims]).to(dev, next(m.parameters()).dtype)
        with torch.no_grad():
            e = m.encode_image(x, normalize=True).float().cpu().numpy()
        out.append(e.reshape(-1, 3, e.shape[-1]))
    return np.concatenate(out).astype(np.float16) if out else np.zeros((0, 3, 1152), np.float16)


def crop_at(im, across, frac=0.45):
    """A square crop around a point `across` the picture (0 = left, 1 = right), `frac` of the picture's width."""
    w, h = im.size
    side = min(h, int(w * frac))
    x0 = min(max(0, int(across * w - side / 2)), w - side)
    y0 = (h - side) // 2 + side // 4 if side < h else 0       # things sit low in a 0.4 m high camera's picture
    return im.crop((x0, min(y0, h - side), x0 + side, min(y0, h - side) + side))


def embed_crops(items, batch=16):
    """[(picture path, across)] -> N x 1152 float16, one embedding of the crop around each object."""
    import torch
    from PIL import Image
    m, pre, _, dev = model()
    out, cache = [], {}
    for i in range(0, len(items), batch):
        ims = []
        for path, across in items[i:i + batch]:
            if path not in cache:
                cache.clear()
                cache[path] = Image.open(path).convert("RGB")
            ims.append(crop_at(cache[path], across))
        x = torch.stack([pre(v) for v in ims]).to(dev, next(m.parameters()).dtype)
        with torch.no_grad():
            out.append(m.encode_image(x, normalize=True).float().cpu().numpy())
    return np.concatenate(out).astype(np.float16) if out else np.zeros((0, 1152), np.float16)


TEXT_SERVER = "http://127.0.0.1:8311/text"     # `embeddings.py serve`: each agent turn starts a new server.py, and
                                               # loading the model on the CPU takes about 20 s there


def server_up():
    """Is `embeddings.py serve` running? It then also embeds new pictures, so agent processes need not."""
    try:
        import urllib.request
        with urllib.request.urlopen(TEXT_SERVER.rsplit("/", 1)[0] + "/ping", timeout=0.5) as r:
            return r.status == 200
    except Exception:  # noqa: BLE001
        return False


def embed_text(texts):
    try:
        import urllib.request
        req = urllib.request.Request(TEXT_SERVER, json.dumps({"texts": list(texts)}).encode(),
                                     {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return np.array(json.loads(r.read())["vecs"], dtype=np.float32)
    except Exception:  # noqa: BLE001 - no server: load the model here
        pass
    import torch
    m, _, tok, dev = model()
    with torch.no_grad():
        return m.encode_text(tok(texts).to(dev), normalize=True).float().cpu().numpy()


def load_store():
    if not IDS.exists():
        return [], np.zeros((0, 3, 1152), np.float16)
    ids, V = json.loads(IDS.read_text()), np.load(VIEWS)
    n = min(len(ids), len(V))          # another process may be between its two renames: use the common part
    return ids[:n], V[:n]


_STORE_LOCK = threading.Lock()


def update(recs=None):
    """Embed every picture in the memory that has no embedding yet. Returns how many were added."""
    with _STORE_LOCK:
        ids, V = load_store()
        have = set(ids)
        new = [r for r in (recs if recs is not None else M.load())
               if r["id"] not in have and Path(r["path"]).exists()]
        if not new:
            return 0
        E = embed_images([r["path"] for r in new])
        EMB.mkdir(parents=True, exist_ok=True)
        ids, V = ids + [r["id"] for r in new], np.concatenate([V, E])
        tv, ti = EMB / f"views.{os.getpid()}.tmp.npy", EMB / f"ids.{os.getpid()}.tmp"
        np.save(tv, V)                                       # write whole new files, then rename (no half files)
        tv.replace(VIEWS)
        ti.write_text(json.dumps(ids))
        ti.replace(IDS)
        return len(new)


def scores(query, ids=None):
    """{picture id: SigLIP score of the query} (cosine similarity, best of the three views)."""
    sid, V = load_store()
    if not sid:
        return {}
    q = embed_text([f"a photo of {query}."])[0].astype(np.float32)
    s = (V.astype(np.float32) @ q).max(axis=1)
    keep = None if ids is None else set(ids)
    return {i: float(v) for i, v in zip(sid, s) if keep is None or i in keep}


def search(query, k=12, recs=None):
    """[(id, score)] best first, over the pictures in recs (default: all)."""
    s = scores(query, None if recs is None else [r["id"] for r in recs])
    return sorted(s.items(), key=lambda z: -z[1])[:k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["update", "search", "serve"])
    ap.add_argument("query", nargs="?")
    a = ap.parse_args()
    if a.cmd == "serve":
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        global TEXT_SERVER
        TEXT_SERVER = ""                        # this process embeds itself
        import time
        import torch
        torch.set_num_threads(6)                # the CPU is shared with the agent and other users
        model()
        SERVE_LOCK = threading.Lock()

        def keep_up():                          # embed new pictures here, once, instead of in every agent process
            while True:
                try:
                    n = update()
                    if n:
                        print(f"{time.strftime('%H:%M')} embedded {n} new pictures", flush=True)
                except Exception as e:  # noqa: BLE001
                    print("update failed:", e, flush=True)
                time.sleep(60)
        threading.Thread(target=keep_up, daemon=True).start()

        class H(BaseHTTPRequestHandler):
            def log_message(self, *x):
                pass

            def do_GET(self):
                self.send_response(200 if self.path == "/ping" else 404)
                self.end_headers()

            def do_POST(self):
                texts = json.loads(self.rfile.read(int(self.headers["Content-Length"])))["texts"][:64]
                with SERVE_LOCK:                 # model() takes _LOCK itself
                    v = embed_text(texts)
                body = json.dumps({"vecs": v.tolist()}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)
        print(f"text embeddings on {model()[3]}, http://127.0.0.1:8311/text", flush=True)
        ThreadingHTTPServer(("127.0.0.1", 8311), H).serve_forever()
    elif a.cmd == "update":
        import time
        t0 = time.time()
        n = update()
        print(f"embedded {n} new pictures in {time.time() - t0:.0f} s on {model()[3] if n else '-'}; "
              f"store has {len(load_store()[0])}")
    else:
        by = {r["id"]: r for r in M.load()}
        for i, s in search(a.query):
            print(f"{s:.3f} [{i}] {by[i]['time'] if i in by else ''}")


if __name__ == "__main__":
    main()
