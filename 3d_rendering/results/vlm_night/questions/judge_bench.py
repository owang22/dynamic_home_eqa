"""The look step alone: the robot stands at a piece of furniture and must say whether the thing
asked for is there. Built from the where-is questions (search/questions.json):

  there      the furniture where the thing is now (>= 500 px), one per question     (174)
  old spot   where the patrol notes last had it, for things that moved since      (77)
             (the hard negative: similar things live there)
  elsewhere  a random other furniture piece with things on it                      (100)

Ways of judging, all with the answer forced to yes/no by the output grammar:
  strict     "Is a <type> visible in this picture?"
  lenient    "Could any object be a <type>, even if it looks a bit different or is partly hidden?"
  think      strict, with the model's thinking on (slow)
  high       strict, on the 1.4 m camera pictures (questions at days 4-14, 10/14/18/22 h only)

    python judge_bench.py strict lenient think high
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import pathlib
import random
import sys

import vlm
from world import World

HERE = pathlib.Path(__file__).parent
OUT = HERE / "judge"
OUT.mkdir(exist_ok=True)
HIGH = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_1p4")


def items(W):
    rng = random.Random(1)
    qs = json.loads((HERE / "search/questions.json").read_text())
    out = []
    for q in qs:
        out.append(dict(q, f=q["where"][0], label="there"))
        if q["category"] == "moved since" and q["last_seen"]:
            out.append(dict(q, f=q["last_seen"], label="old spot"))
    busy = []
    for q in qs:
        tr = W.truth(q["day"], q["time"])
        for f, spots in W.furniture.items():
            if f in q["where"] or f == q["last_seen"]:
                continue
            if any(n >= 500 for s in spots for n in tr.get(s, {}).values()):
                busy.append(dict(q, f=f, label="elsewhere"))
    out += rng.sample(busy, 100)
    return out


def reference_crop(W, it, min_px=1500, seen_by=None):
    """A crop of the asked thing from an earlier picture, as the robot would have it from a
    past patrol: the largest view before the question time, on a different piece of furniture
    from the one being judged when possible. Returns (path, where it was) or (None, None)."""
    import numpy as np
    from PIL import Image
    best = None
    for (d, t) in sorted(W.states):
        if (d, t) >= (it["day"], it["time"]) or not W.rendered(d, t):
            continue
        tr = W.truth(d, t)
        for s, objs in tr.items():
            if seen_by is not None and (d, t, W.places[s]["room"]) not in seen_by:
                continue
            for o in it["accept"]:
                n = objs.get(o, 0)
                if n < min_px:
                    continue
                key = (W.fkey(s) != it["f"], n)
                if best is None or key > best[0]:
                    best = (key, d, t, s, o)
    if best is None:
        return None, None
    _, d, t, s, o = best
    crop_dir = OUT / "crops"
    crop_dir.mkdir(exist_ok=True)
    out = crop_dir / f"{o}_{d:02d}_{t}_{s}.jpg"   # same picture, same crop, whoever asks
    if not out.exists():
        raw = json.loads((W.picture(d, t, s).parent / "truth.json").read_text())
        sid = next(x["semantic_id"] for x in raw["pictures"][s]["objects"] if x["object"] == o)
        ids = np.array(Image.open(W.picture(d, t, s).with_name(f"{s}_ids.png")))
        ys, xs = np.nonzero(ids == sid)
        m = 12
        box = (max(0, xs.min() - m), max(0, ys.min() - m), min(639, xs.max() + m), min(479, ys.max() + m))
        im = Image.open(W.picture(d, t, s)).crop(box)
        scale = max(1, int(224 / max(im.size)))
        im = im.resize((im.size[0] * scale, im.size[1] * scale))
        im.save(out, quality=92)
    return out, W.fname(W.fkey(s))


def judge(W, it, how):
    spots = W.furniture[it["f"]]
    if how == "high":
        pics = [HIGH / f"day_{it['day']:02d}" / it["time"] / f"{s}.jpg" for s in spots]
        if not all(p.exists() for p in pics):
            return None
    else:
        pics = [W.picture(it["day"], it["time"], s) for s in spots]
    caps = [f"Picture of the {W.views[s]['spot_name']}:" for s in spots]
    t = it["type"]
    one = len(pics) == 1
    if how == "lenient":
        p = (f"You are a home robot looking for the {t}. Could any object in "
             f"{'this picture' if one else 'these pictures'} be the {t}, even if it looks a bit "
             "different from usual or is partly hidden?")
    else:
        p = (f"You are a home robot looking for the {t}. Is a {t} visible in "
             f"{'this picture' if one else 'any of these pictures'}?")
    if how == "ref":
        ref, _ = reference_crop(W, it)
        if ref is None:
            return None
        p = (f"You are a home robot looking for the {t}. The first picture is a close-up of this "
             f"exact {t}, taken earlier. Is this same {t} visible in "
             f"{'the next picture' if one else 'any of the next pictures'}? It may be seen from "
             "another side or partly hidden.")
        return vlm.yes_no(p, [ref] + pics, captions=["Close-up taken earlier:"] + caps)
    if how == "think":
        try:
            text, _ = vlm.ask(p + " End your reply with a last line that is exactly 'ANSWER: yes' or 'ANSWER: no'.",
                              pics, captions=caps, think=True, max_tokens=6000)
        except Exception:  # noqa: BLE001  (a timeout counts as unparsed, not a crash)
            return None
        last = text.strip().splitlines()[-1].lower() if text.strip() else ""
        return True if "answer: yes" in last else False if "answer: no" in last else None
    return vlm.yes_no(p, pics, captions=caps)


def main():
    W = World()
    its = items(W)
    res = {}
    for how in sys.argv[1:]:
        with cf.ThreadPoolExecutor(8) as ex:
            said = list(ex.map(lambda it: judge(W, it, how), its))
        rows = []
        for it, s in zip(its, said):
            rows.append({"id": it["id"], "label": it["label"], "type": it["type"], "f": it["f"],
                         "category": it["category"], "model": it["model"], "said": s})
        (OUT / f"{how}.json").write_text(json.dumps(rows, indent=1))
        line = []
        for lab in ["there", "old spot", "elsewhere"]:
            rs = [r for r in rows if r["label"] == lab and r["said"] is not None]
            unp = sum(r["said"] is None for r in rows if r["label"] == lab)
            line.append(f"{lab}: yes {sum(r['said'] for r in rs)}/{len(rs)}" + (f" ({unp} unparsed/missing)" if unp else ""))
        res[how] = line
        print(how, " | ".join(line), flush=True)
    old = json.loads((OUT / "summary.json").read_text()) if (OUT / "summary.json").exists() else {}
    old.update(res)
    (OUT / "summary.json").write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
