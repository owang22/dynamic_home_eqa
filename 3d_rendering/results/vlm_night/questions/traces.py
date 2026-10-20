"""Full thinking traces for a few where-is questions, following two things over the days.

For each question the model, with thinking on,
  1. sees up to 40 pictures from its recent patrols (newest first, as search.py 'pics') and
     ranks up to 8 pieces of furniture to look at;
  2. looks at them in that order (filled up with nearest furniture), seeing the pictures of
     each piece at the question time, and says yes or no; it stops at the first yes.
The full reasoning is kept (vlm.py keeps only the first 4000 characters).

    python traces.py            writes traces/traces.json
"""
from __future__ import annotations

import collections
import concurrent.futures as cf
import hashlib
import json
import pathlib
import time
import urllib.request

import search
import vlm
from world import NOTE_PX, World

HERE = pathlib.Path(__file__).parent
OUT = HERE / "traces"
CACHE = OUT / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

ASK = [("tote bag", 5, "2200"), ("tote bag", 6, "1400"), ("tote bag", 10, "1000"),
       ("tote bag", 12, "2200"), ("tote bag", 13, "1800"), ("tote bag", 14, "2200"),
       ("dish towel", 5, "1000"), ("dish towel", 6, "1400"), ("dish towel", 7, "1400"),
       ("dish towel", 8, "1000"), ("dish towel", 10, "2200"), ("dish towel", 13, "1400"),
       ("lounge pants", 4, "2200"), ("lounge pants", 5, "1800"), ("lounge pants", 6, "2200"),
       ("lounge pants", 8, "2200"), ("lounge pants", 9, "2200"), ("lounge pants", 10, "1400")]


def ask_full(prompt, images=(), captions=None, schema=None, max_tokens=8000):
    content = []
    for i, p in enumerate(images):
        if captions:
            content.append({"type": "text", "text": captions[i]})
        content.append(vlm._img(p))
    content.append({"type": "text", "text": prompt})
    body = {"model": vlm.MODEL, "messages": [{"role": "user", "content": content}], "temperature": 0.0,
            "max_tokens": max_tokens, "chat_template_kwargs": {"enable_thinking": True}}
    if schema:
        body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
    key = hashlib.sha256(json.dumps([prompt, [str(p) for p in images], captions, schema, max_tokens]).encode()).hexdigest()[:24]
    f = CACHE / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text())
    t0 = time.time()
    req = urllib.request.Request(vlm.URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    out = json.loads(urllib.request.urlopen(req, timeout=3600).read())
    msg = out["choices"][0]["message"]
    r = {"text": msg.get("content") or "", "reasoning": msg.get("reasoning_content") or msg.get("reasoning") or "",
         "finish": out["choices"][0].get("finish_reason"), "seconds": round(time.time() - t0, 1),
         "usage": out.get("usage")}
    f.write_text(json.dumps(r))
    return r


def patrol_pictures(W, q, plan, caps, max_pics=40):
    """The same pictures and labels search.pics_order shows."""
    pics = []
    for day, t, rooms in sorted(plan, reverse=True):
        if (day, t) >= (q["day"], q["time"]) or not W.rendered(day, t):
            continue
        for f, spots in W.furniture.items():
            if W.places[spots[0]]["room"] not in rooms:
                continue
            for s in spots:
                if caps.get(f"{day}|{t}|{s}"):
                    shows = any(n >= NOTE_PX for o, n in W.raw_truth(day, t).get(s, {}).items() if o in q["accept"])
                    pics.append({"day": day, "time": t, "spot": s, "f": f,
                                 "label": f"Day {day} {t[:2]}:{t[2:]}, {W.fname(f)}:",
                                 "caption": caps[f"{day}|{t}|{s}"], "shows": shows})
        if len(pics) >= max_pics:
            break
    return pics[:max_pics]


def one(W, plan, caps, typ, day, t):
    ids = sorted(o for o, v in W.objects.items() if v["type"] == typ)
    q = {"type": typ, "day": day, "time": t, "accept": ids}
    names = {W.fname(f): f for f in W.furniture}
    seen = patrol_pictures(W, q, plan, caps)
    prompt = (
        "You are a home robot. Above are pictures from your most recent patrols, newest first, "
        "each labelled with when it was taken and which piece of furniture it shows. Pictures of "
        "empty furniture are left out.\n\n"
        f"It is now day {day}, {t[:2]}:{t[2:]}. Someone asks: \"{search.where_q(typ)}\"\n"
        "List up to 8 pieces of furniture to look at, most likely first. Use the names exactly "
        "as in this list:\n" + "\n".join(sorted(names)))
    schema = {"type": "object", "properties": {"order": {
        "type": "array", "items": {"type": "string", "enum": sorted(names)}, "maxItems": search.MAX_LOOKS}},
        "required": ["order"]}
    rank = ask_full(prompt, [W.picture(p["day"], p["time"], p["spot"]) for p in seen],
                    captions=[p["label"] for p in seen], schema=schema, max_tokens=30000)
    try:
        ranked = list(dict.fromkeys(names[x] for x in json.loads(rank["text"])["order"]))
    except Exception:  # noqa: BLE001
        ranked = []
    xz = W.furniture_xz()
    order = ranked + search.nearest_order(W, xz[ranked[-1]] if ranked else search.entry_xy(W), ranked)
    order = order[:search.MAX_LOOKS]
    looks, result = [], "not found"
    for f in order:
        spots = W.furniture[f]
        pics = [W.picture(day, t, s) for s in spots]
        lp = (f"You are a home robot looking for the {typ}. Is a {typ} visible in "
              f"{'this picture' if len(pics) == 1 else 'any of these pictures'}? End your reply "
              "with a last line that is exactly 'ANSWER: yes' or 'ANSWER: no'.")
        r = ask_full(lp, pics, captions=[f"Picture of the {W.views[s]['spot_name']}:" for s in spots])
        last = r["text"].strip().splitlines()[-1].lower() if r["text"].strip() else ""
        said = True if "answer: yes" in last else False if "answer: no" in last else None
        there = search.present(W, q, f)
        looks.append({"f": f, "name": W.fname(f), "from_ranking": f in ranked, "spots": spots,
                      "spot_names": [W.views[s]["spot_name"] for s in spots], "said": said, "there": there,
                      "text": r["text"], "reasoning": r["reasoning"], "seconds": r["seconds"],
                      "finish": r["finish"]})
        if said:
            result = "found" if there else "false find"
            break
    truth = W.raw_truth(day, t)
    where = sorted({W.fname(W.fkey(s)) for s, o in truth.items() if any(o.get(i, 0) >= NOTE_PX for i in ids)})
    print(f"{typ} day {day} {t}: {result} after {len(looks)} looks", flush=True)
    objs = W.states[(day, t)]["objects"]
    rests = sorted({W.fname(W.fkey(objs[i]["place"])) if objs[i].get("place") in W.places else str(objs[i].get("place"))
                    for i in ids})
    return {"type": typ, "day": day, "time": t, "where": where, "rests_on": rests, "seen": seen,
            "ranking": {"prompt": prompt, "order": [W.fname(f) for f in ranked], "text": rank["text"],
                        "reasoning": rank["reasoning"], "seconds": rank["seconds"], "finish": rank["finish"],
                        "usage": rank["usage"]},
            "order": [W.fname(f) for f in order], "looks": looks, "result": result}


def main():
    W = World()
    plan = W.patrol_plan()
    caps = json.loads((search.OUT / "captions.json").read_text())
    with cf.ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(lambda a: one(W, plan, caps, *a), ASK))
    (OUT / "traces.json").write_text(json.dumps(rows, indent=1))
    print(collections.Counter(r["result"] for r in rows))


if __name__ == "__main__":
    main()
