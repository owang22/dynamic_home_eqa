"""Global descriptors for every picture, per crop (task 2). Cached to cache/<model>_<crop>.npz (ids, tokens or vecs).

    CUDA_VISIBLE_DEVICES=0 python3 desc.py dino     # DINOv2 ViT-L/14 reg4: CLS, GeM(patch), patch tokens for VLAD
    python3 desc.py siglip                           # SigLIP SO400M-14-384 image embedding (square windows averaged)

Crops are taken on the 640x360 picture BEFORE the network (so a crop's descriptor cannot see the rest of the
frame through attention). Rows (of 360): full 0-360, upper 0-162, top 0-108, lower 198-360.
A mask (bool HxW at 640x360, True = keep) can be applied by passing --mask masks.npz: masked pixels are set to
the ImageNet mean grey before the network and their patch tokens are dropped from pooling.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import torch

os.environ.setdefault("HF_HUB_OFFLINE", "1")
import vcommon as V  # noqa: E402

CROPS = {"full": (0, 360), "upper": (0, 162), "top": (0, 108), "lower": (198, 360)}
HERE = Path(__file__).resolve().parent
MEAN = np.array([0.485, 0.456, 0.406]); STD = np.array([0.229, 0.224, 0.225])


def load_rgb(path):
    im = cv2.imread(str(path))[:, :, ::-1]
    return cv2.resize(im, (640, 360), interpolation=cv2.INTER_AREA)


def dino(records, out_tag="", masks=None, crops=CROPS):
    import timm
    m = timm.create_model("vit_large_patch14_reg4_dinov2.lvd142m", pretrained=True, num_classes=0,
                          dynamic_img_size=True).cuda().half().eval()
    npre = m.num_prefix_tokens
    for crop, (r0, r1) in crops.items():
        W = 644; H = int(round((r1 - r0) * W / 640 / 14)) * 14
        cls, gem, toks, tok_keep = [], [], [], []
        for i in range(0, len(records), 8):
            batch = records[i:i + 8]
            ims, keeps = [], []
            for r in batch:
                im = load_rgb(r["path"])[r0:r1].astype(np.float32) / 255.0
                im = cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)
                keep = np.ones((H // 14, W // 14), bool)
                if masks is not None and r["id"] in masks:
                    mk = masks[r["id"]][r0:r1].astype(np.float32)
                    mk = cv2.resize(mk, (W, H), interpolation=cv2.INTER_AREA)
                    im[mk < 0.5] = MEAN
                    keep = cv2.resize(mk, (W // 14, H // 14), interpolation=cv2.INTER_AREA) > 0.5
                ims.append((im - MEAN) / STD); keeps.append(keep)
            x = torch.from_numpy(np.stack(ims).transpose(0, 3, 1, 2)).float().cuda().half()
            with torch.no_grad():
                f = m.forward_features(x).float()
            c = torch.nn.functional.normalize(f[:, 0], dim=-1)
            p = torch.nn.functional.normalize(f[:, npre:], dim=-1)          # B, N, D
            for b in range(len(batch)):
                kp = torch.from_numpy(keeps[b].reshape(-1)).cuda()
                pt = p[b][kp] if kp.sum() > 0 else p[b]
                g = pt.clamp(min=1e-6).pow(3).mean(0).pow(1 / 3)     # GeM on normalised tokens (positive part)
                gem.append(torch.nn.functional.normalize(torch.cat([g, (-pt).clamp(min=1e-6).pow(3).mean(0).pow(1 / 3)]), dim=0).cpu().numpy())
                cls.append(c[b].cpu().numpy())
                toks.append(pt.cpu().numpy().astype(np.float16))
        off = np.cumsum([0] + [len(t) for t in toks])
        np.savez(HERE / "cache" / f"dino{out_tag}_{crop}.npz", ids=np.array([r["id"] for r in records]),
                 cls=np.stack(cls), gem=np.stack(gem), tok=np.concatenate(toks), off=off)
        print("dino", crop, H, W, len(records), flush=True)


def siglip(records, out_tag="", masks=None, crops=CROPS):
    import open_clip
    path = Path.home() / ".cache/huggingface/hub/models--timm--ViT-SO400M-14-SigLIP-384"
    ckpt = next(path.glob("snapshots/*/open_clip_model.safetensors"))
    model, _, pre = open_clip.create_model_and_transforms("ViT-SO400M-14-SigLIP-384", pretrained=str(ckpt))
    model = model.cuda().half().eval()
    mean = np.array(pre.transforms[-1].mean); std = np.array(pre.transforms[-1].std)
    for crop, (r0, r1) in crops.items():
        vecs = []
        for r in records:
            im = load_rgb(r["path"])[r0:r1].astype(np.float32) / 255.0
            if masks is not None and r["id"] in masks:
                im[~masks[r["id"]][r0:r1]] = mean
            h, w = im.shape[:2]
            s = 384 / h
            im = cv2.resize(im, (max(384, int(round(w * s))), 384), interpolation=cv2.INTER_AREA)
            n = math.ceil(im.shape[1] / 384)
            xs = np.linspace(0, im.shape[1] - 384, n).astype(int) if n > 1 else [0]
            wins = np.stack([(im[:, x:x + 384] - mean) / std for x in xs]).transpose(0, 3, 1, 2)
            with torch.no_grad():
                e = model.encode_image(torch.from_numpy(wins).float().cuda().half()).float()
            e = torch.nn.functional.normalize(e, dim=-1).mean(0)
            vecs.append(torch.nn.functional.normalize(e, dim=0).cpu().numpy())
        np.savez(HERE / "cache" / f"siglip{out_tag}_{crop}.npz", ids=np.array([r["id"] for r in records]),
                 vec=np.stack(vecs))
        print("siglip", crop, len(records), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=["dino", "siglip"])
    ap.add_argument("--mask", default=None)
    ap.add_argument("--tag", default="")
    ap.add_argument("--crops", default=",".join(CROPS))
    a = ap.parse_args()
    R = V.load_records()
    masks = None
    if a.mask:
        z = np.load(a.mask)
        masks = {k: z[k] for k in z.files}
        R = [r for r in R if r["id"] in masks]
    crops = {k: CROPS[k] for k in a.crops.split(",")}
    (dino if a.model == "dino" else siglip)(R, a.tag, masks, crops)
