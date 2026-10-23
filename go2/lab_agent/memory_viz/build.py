"""Build the data for the memory explorer page (memory_explorer.html) from the lab agent's memory, 2026-10-23.

    python3 go2/lab_agent/memory_viz/build.py        # -> go2/data/lab_agent/memory_viz/

Reads only local files (index, pictures, embeddings, object instances, chats, search labels); never the console.
Writes:
  graph.json   pictures (pose, place, day, description, similar pictures), object instances, places, map, the word
               search tables (STOP, SAME, CANON, KIND), and a phrase bank: SigLIP picture scores for ~600 phrases,
               so the page can do picture-similarity search without running SigLIP in the browser
  traces.json  every logged conversation: Oliver's messages, each tool call with its arguments and the picture ids
               it returned, and the agent's answers
  evals.json   the 40 hand-labelled search queries with the top 10 of words / images / fused search and the labels
  thumbs.json  {id: data URI} 224 px wide
  full_N.json  {id: data URI} 640 px wide, in chunks
"""
from __future__ import annotations

import base64
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB))
import embeddings as E  # noqa: E402
import memory as M  # noqa: E402

OUT = M.DATA / "memory_viz"
CHATS = M.DATA / "chats"
EVAL = LAB / "memory_notes" / "search_eval"
INST = M.DATA / "instances"
ID_RE = re.compile(r"\[([tp]\d{9,}(?:_\d+)?)\]")


def jpg_uri(path, width, q):
    im = Image.open(path).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def pictures(recs, P):
    sid, V = E.load_store()
    row = {i: n for n, i in enumerate(sid)}
    mean = V.astype(np.float32).mean(axis=1)
    mean /= np.linalg.norm(mean, axis=1, keepdims=True)
    sim = mean @ mean.T
    out = []
    for r in recs:
        s = r.get("seen") or {}
        place, dist = M.nearest_place(r["x"], r["y"], P) if r.get("x") is not None else (None, None)
        nb = []
        if r["id"] in row:
            sc = sim[row[r["id"]]]
            nb = [[sid[j], round(float(sc[j]), 3)] for j in np.argsort(-sc)[1:7]]
        out.append({"id": r["id"], "t": r["t"], "time": r["time"], "day": r["time"][:14], "source": r["source"],
                    "x": r.get("x"), "y": r.get("y"), "yaw": r.get("yaw_deg"), "look": r.get("look_deg", 0),
                    "place": place, "place_m": dist, "summary": s.get("summary", ""),
                    "objects": [{"name": o["name"], "canon": M.canon(o["name"]), "colour": o.get("colour", ""),
                                 "on": o.get("on", ""), "across": o.get("across")} for o in s.get("objects", [])],
                    "people": s.get("people", 0), "people_notes": s.get("people_notes", ""),
                    "states": s.get("states", []), "similar": nb})
    return out


def instances():
    I = json.loads((INST / "instances.json").read_text())
    keep = ("key", "name", "colour", "on", "x", "y", "uncertainty_m", "how", "near_place", "near_place_m",
            "first_time", "last_time", "first_seen", "last_seen", "n_pictures", "pictures", "p_still", "chain",
            "chain_days", "pose_quality")
    out = []
    for i in I["instances"]:
        d = {k: i.get(k) for k in keep}
        d["missed"] = (i.get("missed_after_last_seen") or [])[:8]
        d["n_missed_after"] = len(i.get("missed_after_last_seen") or [])
        out.append(d)
    return out, {k: I[k] for k in ("built", "built_time", "n_pictures", "n_sightings")}


def phrase_bank(recs, extra):
    names = Counter()
    combos = Counter()
    for r in recs:
        for o in (r.get("seen") or {}).get("objects", []):
            c = M.canon(o["name"])
            names[c] += 1
            if o.get("colour"):
                combos[f"{o['colour'].lower()} {c}"] += 1
    phrases = sorted({n for n, k in names.items() if k >= 2} | {c for c, k in combos.items() if k >= 3}
                     | {e.lower().strip() for e in extra if e.strip()})
    sid, V = E.load_store()
    Vf = V.astype(np.float32)
    bank = {}
    for a in range(0, len(phrases), 64):
        chunk = phrases[a:a + 64]
        Q = E.embed_text([f"a photo of {p}." for p in chunk]).astype(np.float32)
        S = np.einsum("nvd,qd->qnv", Vf, Q).max(axis=2)
        for p, s in zip(chunk, S):
            top = np.argsort(-s)[:30]
            bank[p] = [[sid[j], round(float(s[j]), 3)] for j in top]
    return bank


def traces():
    convs = []
    for f in sorted(CHATS.glob("*.json")):
        ev = json.loads(f.read_text())
        turns = []
        for e in ev:
            k, text, extra = e["kind"], e.get("text") or "", e.get("extra")
            if k == "oliver":
                turns.append({"t": e["t"], "q": text.strip(), "steps": [], "answers": []})
            elif not turns:
                continue
            elif k == "tool":
                turns[-1]["steps"].append({"t": e["t"], "tool": text, "args": extra or {}, "ids": [], "out": ""})
            elif k == "result" and turns[-1]["steps"]:
                st = turns[-1]["steps"][-1]
                st["ids"] = list(dict.fromkeys(ID_RE.findall(text)))[:30]
                st["out"] = text[:700]
                st["images"] = (extra or {}).get("images", 0)
            elif k == "agent":
                turns[-1]["answers"].append({"t": e["t"], "text": text.strip()})
        convs.append({"id": f.stem, "start": ev[0]["t"] if ev else "", "turns": turns})
    return convs


def evals(recs):
    labels = json.loads((EVAL / "labels.json").read_text())
    out = []
    for q, lab in labels.items():
        rel = lab.get("relevant", []) if isinstance(lab, dict) else lab
        row = {"q": q, "relevant": rel}
        for mode in ("words", "images", "fused"):
            hits = M.search(q, k=10, recs=[dict(r) for r in recs], mode=mode)
            row[mode] = [h["id"] for h in hits]
        out.append(row)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    recs = M.load()
    P = json.loads(M.PLACES.read_text())
    print(f"{len(recs)} pictures", flush=True)
    pics = pictures(recs, P)
    inst, inst_meta = instances()
    tr = traces()
    ev = evals(recs)
    print(f"{len(inst)} instances, {len(tr)} conversations, {len(ev)} labelled queries", flush=True)
    logged = [s["args"].get("query", "") for c in tr for t in c["turns"] for s in t["steps"]
              if s["tool"] == "search_memory"]
    bank = phrase_bank(recs, [e["q"] for e in ev] + logged)
    print(f"{len(bank)} phrases in the bank", flush=True)
    meta = json.loads((INST / "map_meta.json").read_text())
    graph = {"built": M.clock(__import__("time").time()), "pictures": pics, "instances": inst,
             "instances_meta": inst_meta, "places": P,
             "map": {"png": "data:image/png;base64," + base64.b64encode((INST / "map.png").read_bytes()).decode(),
                     "resolution": meta["resolution"], "origin": meta["origin"], "width": meta["width"],
                     "height": meta["height"]},
             "search": {"stop": sorted(M.STOP), "same": M.SAME, "canon": M.CANON, "kind": M.KIND,
                        "clutter": sorted(M.CLUTTER), "word_boost": M.WORD_BOOST, "hfov": M.HFOV},
             "bank": bank}
    (OUT / "graph.json").write_text(json.dumps(graph, separators=(",", ":")))
    (OUT / "traces.json").write_text(json.dumps(tr, separators=(",", ":")))
    (OUT / "evals.json").write_text(json.dumps(ev, separators=(",", ":")))
    thumbs = {r["id"]: jpg_uri(r["path"], 224, 62) for r in recs if Path(r["path"]).exists()}
    (OUT / "thumbs.json").write_text(json.dumps(thumbs, separators=(",", ":")))
    full, n, size = {}, 0, 0
    for r in recs:
        if not Path(r["path"]).exists():
            continue
        u = jpg_uri(r["path"], 640, 70)
        full[r["id"]] = u
        size += len(u)
        if size > 12_000_000:
            (OUT / f"full_{n}.json").write_text(json.dumps(full, separators=(",", ":")))
            full, n, size = {}, n + 1, 0
    if full:
        (OUT / f"full_{n}.json").write_text(json.dumps(full, separators=(",", ":")))
    index = {}
    for f in sorted(OUT.glob("full_*.json")):
        for i in json.loads(f.read_text()):
            index[i] = f.name
    (OUT / "full_index.json").write_text(json.dumps(index, separators=(",", ":")))
    for f in sorted(OUT.glob("*.json")):
        print(f"{f.name}: {f.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
