"""Shared loader for the memory lab (2026-10-25 overnight): the real picture memory as a list of events, with the
best description available for each picture, and helpers to remap time.

    import data as D
    ev = D.events()                       # every picture, oldest first
    ev = D.events(described_only=True)    # only pictures with a description

An event:
    {"id", "t" (epoch seconds, may be remapped), "real_t" (the real time, never changed), "kind": "picture",
     "source": trail | photo | look_around, "x", "y", "yaw_deg", "place" (nearest saved place), "place_m",
     "path" (the JPEG), "seen" (description dict or None), "describer": "27b-h100" | "27b" | "8b" | None,
     "text" (one line: summary + objects + people, "" if not described)}

Descriptions, three describers (collection_analysis/redescribe.py writes the two overnight files):
  "27b-h100"  Qwen3.8-27B on the H100, every picture, overnight 2026-10-25 (descriptions_qwen3.8-27b-h100.jsonl)
  "27b"       the same model on cheetah, in the live index, 10-19 to 10-23 01:50 only
  "8b"        Qwen3-VL-8B on the control PC, overnight (descriptions_qwen3-vl-8b.jsonl)
prefer = the order to try them in (default 27b-h100, then 27b, then 8b); only = keep one describer, which is what a
fair comparison needs. The overnight files grow during the night: call events() again to pick up new lines.

Real timestamps are never overwritten on disk. remap() returns copies with a new "t" and keeps "real_t".
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lab_agent"))
import memory as M  # noqa: E402

DATA = M.DATA
OUT = HERE.parent / "data" / "memory_lab"
COLLECTION = HERE.parent / "data" / "collection"
FILES = {"27b-h100": DATA / "descriptions_qwen3.8-27b-h100.jsonl", "8b": DATA / "descriptions_qwen3-vl-8b.jsonl"}


def descriptions(who):
    out = {}
    f = FILES[who]
    if f.exists():
        for l in f.read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                if r.get("seen"):
                    out[r["id"]] = r["seen"]
    return out


def line(seen):
    if not seen:
        return ""
    objs = ", ".join(f"{o.get('colour', '')} {o['name']} on {o.get('on', '?')}".strip()
                     for o in seen.get("objects", []))
    ppl = seen.get("people") or 0
    s = seen.get("summary", "")
    if objs:
        s += f" Objects: {objs}."
    if ppl:
        s += f" People: {ppl} ({seen.get('people_notes', '')})."
    if seen.get("states"):
        s += " States: " + "; ".join(seen["states"]) + "."
    return s


def events(described_only=False, prefer=("27b-h100", "27b", "8b"), only=None):
    P = M.places()
    D = {w: descriptions(w) for w in FILES}
    out = []
    for r in sorted(M.load(), key=lambda r: r["t"]):
        have = {"27b-h100": D["27b-h100"].get(r["id"]), "27b": r.get("seen"), "8b": D["8b"].get(r["id"])}
        order = [only] if only else list(prefer)
        who, seen = next(((w, have[w]) for w in order if have[w]), (None, None))
        if described_only and not seen:
            continue
        place, dist = M.nearest_place(r["x"], r["y"], P) if r.get("x") is not None else (None, None)
        out.append({"id": r["id"], "t": r["t"], "real_t": r["t"], "kind": "picture", "source": r["source"],
                    "x": r.get("x"), "y": r.get("y"), "yaw_deg": r.get("yaw_deg"), "place": place, "place_m": dist,
                    "path": r["path"], "seen": seen, "describer": who, "text": line(seen)})
    return out


def facts():
    """Ground-truth notes Oliver and the protocol logged during the collect sessions (note_kind fact/expected)."""
    out = []
    f = COLLECTION / "events.jsonl"
    for l in f.read_text().splitlines():
        if l.strip():
            e = json.loads(l)
            if e.get("kind") == "note" and e.get("note_kind") in ("fact", "expected"):
                out.append(e)
    return out


def clock(t):
    return time.strftime("%a %Y-%m-%d %H:%M", time.localtime(t))


def remap(evs, mapping):
    """mapping: real_t -> new t (a function). Returns copies, sorted by the new t; real_t is kept."""
    out = [dict(e, t=mapping(e["real_t"])) for e in evs]
    return sorted(out, key=lambda e: e["t"])


if __name__ == "__main__":
    ev = events()
    n = {}
    for e in ev:
        n[e["describer"]] = n.get(e["describer"], 0) + 1
    print(len(ev), "pictures;", n)
    print(ev[-1]["id"], clock(ev[-1]["t"]), ev[-1]["place"], ev[-1]["text"][:200])
