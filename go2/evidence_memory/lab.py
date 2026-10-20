"""The evidence memory on real lab pictures (the Go2 patrol, or photos taken by hand at dog height).

Pictures go in the patrol layout:  go2/data/patrols/<date>/<HHMM>/<place>.jpg
(one folder per round; the place is the file name, e.g. under_desk_2.jpg, water_cooler.jpg).

    python lab.py update go2/data/patrols/2026-10-19      # write notes for every new round (oldest first)
    python lab.py ask "Did anyone forget anything at the bench?" [--at 15:00]
    python lab.py show                                     # the notes so far

    python lab.py ask "..." --answerer qwen             # local model instead of Opus
    python lab.py ask "..." --memory captions           # the plain baseline: captions only, no pictures

Who is who: edit lab/people.txt (who sits where, what their things look like). Notes: lab/memory.json.
The method is the strongest one in the simulation (RESULTS.md): every picture is kept; the note per visit says
what changed since the last picture of that place, how important it is (0-3) and a guess at what happened; a
"usually here" note per place is rewritten after each round; at question time the answering model reads all
the notes and opens up to 6 pictures (Opus by default; on the same memory it beat the local Qwen by 47 points on the questions a fixed answer sheet cannot get, 2 SE 13: RESULTS.md).
A caption is written for every visit too, for the captions-only baseline.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys

import answer as AN
import common as C
import write_memory as WM

LAB = C.HERE / "lab"
LAB.mkdir(exist_ok=True)
(LAB / "kept").mkdir(exist_ok=True)
MEM = LAB / "memory.json"
PEOPLE = LAB / "people.txt"
if not PEOPLE.exists():
    PEOPLE.write_text("People in the lab (edit me): name, where they usually sit, what their things look like.\n")

ANSWER_SCHEMA = {"type": "object", "properties": {
    "answer": {"type": "string", "maxLength": 600},
    "happened_between": {"type": "string", "maxLength": 80},
    "who": {"type": "string", "maxLength": 80},
    "confidence": {"type": "string", "enum": ["high", "medium", "low", "cannot tell"]},
    "explanation": {"type": "string", "maxLength": 800},
    "evidence": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 8}}},
    "required": ["answer", "happened_between", "who", "confidence", "explanation", "evidence"]}


def load():
    return json.loads(MEM.read_text()) if MEM.exists() else {"visits": [], "usual": {}}


def place_name(p):
    return p.replace("_", " ")


def update(root):
    mem = load()
    done = {v["picture"] for v in mem["visits"]}
    people = PEOPLE.read_text()
    rounds = sorted(d for d in pathlib.Path(root).iterdir() if d.is_dir() and d.name.isdigit())
    for rd in rounds:
        new = [p for p in sorted(rd.glob("*.jpg")) if str(p) not in done]
        if not new:
            continue
        for p in new:
            spot = p.stem
            v = {"id": f"{pathlib.Path(root).name}_{rd.name}_{spot}", "day": 1, "time": rd.name, "spot": spot,
                 "place": place_name(spot), "picture": str(p)}
            prev = [w for w in mem["visits"] if w["spot"] == spot]
            prev = prev[-1] if prev else None
            fill = dict(place=v["place"], time=C.hhmm(v["time"]), day=1, usual=mem["usual"].get(spot) or "(no note yet)",
                        people=people)
            if prev:
                ev, _ = C.ask(WM.EVIDENCE_ASK.format(prev_time=C.hhmm(prev["time"]), **fill),
                              images=[prev["picture"], v["picture"]], schema=WM.EVIDENCE_SCHEMA, system=WM.SYSTEM,
                              max_tokens=900)
            else:
                ev, _ = C.ask(WM.EVIDENCE_FIRST.format(**fill), images=[v["picture"]], schema=WM.EVIDENCE_SCHEMA,
                              system=WM.SYSTEM, max_tokens=900)
            v["evidence"] = ev
            cap, _ = C.ask(WM.CAPTION_ASK.format(place=v["place"], time=C.hhmm(v["time"]), day=1), images=[v["picture"]],
                           schema=WM.CAPTION_SCHEMA, system=WM.SYSTEM, max_tokens=400)
            v["caption"] = cap
            mem["visits"].append(v)
            print(f"{rd.name} {spot}: importance {(ev or {}).get('importance')} | "
                  f"{'; '.join(c['thing'] + ' ' + c['change'] for c in (ev or {}).get('changes', [])) or 'no change'}"
                  f" | guess: {(ev or {}).get('guess')}")
        for spot in sorted({v["spot"] for v in mem["visits"]}):
            mem["usual"][spot] = WM.write_usual(spot, place_name(spot), [v for v in mem["visits"] if v["spot"] == spot],
                                                mem["usual"].get(spot))
    for v in mem["visits"]:              # every picture is kept (a day is a few MB); importance is in the note
        v["kept"] = True
        dst = LAB / "kept" / f"{v['id']}.jpg"
        if not dst.exists():
            shutil.copy(v["picture"], dst)
        v["picture"] = str(dst)
    C.dump(mem, MEM)
    print(f"{len(mem['visits'])} visits, all pictures kept in {LAB / 'kept'}")


def ask(question, at, answerer="opus", memory="evidence"):
    mem = load()
    vs = mem["visits"]
    keep = {v["id"] for v in vs if v.get("kept")} if memory == "evidence" else set()
    upto = (1, at.replace(":", "")) if at else (1, "2359")
    text, ids = AN.memory_text(vs, memory, keep, mem["usual"] if memory == "evidence" else None, upto, 1)
    prefix = "PEOPLE SHEET:\n" + PEOPLE.read_text() + "\n\n" + text
    if answerer == "opus":
        import opus
        pics = "\n".join(f"{s}: {v['picture']}" for s, v in ids.items() if v["id"] in keep)
        prompt = (f"{AN.SYSTEM}\n\n{prefix}\n\nKEPT PICTURES (id: file). You may open up to {AN.MAX_LOOK} of them with "
                  f"the Read tool; open none if the notes are enough. Do not open any other file.\n{pics or '(none)'}\n\n"
                  f"QUESTION: {question}\n\nSay between which two visits something happened when you can, who if the "
                  f"evidence suggests it, how sure you are, and which notes or pictures (v###) you used. Reply with only "
                  f"one JSON object that fits this schema, plus a field \"looked\" listing the pictures you opened:\n"
                  f"{json.dumps(ANSWER_SCHEMA)}")
        r = opus.run_claude(prompt, dirs=[LAB / "kept"])
        out = opus.parse(r.get("result"))
        looked = (out or {}).get("looked", [])
        print(json.dumps({"answerer": "opus", "memory": memory, **(out or {"raw": r})}, indent=1))
        with open(LAB / "asked.jsonl", "a") as f:
            f.write(json.dumps({"question": question, "at": at, "answerer": "opus", "memory": memory,
                                "looked_at": looked, "answer": out}) + "\n")
        return
    pick, _ = C.ask(f"QUESTION: {question}\n\nWhich of your kept pictures (marked [picture kept]) should you look at "
                    f"again to answer? Give up to {AN.MAX_LOOK} ids (v###), most useful first, or none.",
                    prefix=prefix, schema=AN.PICK_SCHEMA, system=AN.SYSTEM, max_tokens=400)
    looked = [s for s in (pick or {}).get("look_at", []) if s in ids and ids[s]["id"] in keep][:AN.MAX_LOOK]
    caps = [f"{s}: the {ids[s]['place']} at {C.hhmm(ids[s]['time'])}:" for s in looked]
    out, _ = C.ask(f"QUESTION: {question}\n\nAnswer from your memory. Say between which two visits something happened "
                   f"when you can, who if the evidence suggests it, how sure you are, and which notes or pictures (v###) "
                   f"you used.", images=[ids[s]["picture"] for s in looked], captions=caps, prefix=prefix,
                   schema=ANSWER_SCHEMA, system=AN.SYSTEM, max_tokens=1500)
    print(json.dumps({"answerer": "qwen", "memory": memory, "looked_at": looked, **(out or {})}, indent=1))
    with open(LAB / "asked.jsonl", "a") as f:
        f.write(json.dumps({"question": question, "at": at, "answerer": "qwen", "memory": memory,
                            "looked_at": looked, "answer": out}) + "\n")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("update")
    u.add_argument("root")
    q = sub.add_parser("ask")
    q.add_argument("question")
    q.add_argument("--at", default=None)
    q.add_argument("--answerer", choices=["opus", "qwen"], default="opus")
    q.add_argument("--memory", choices=["evidence", "captions"], default="evidence")
    sub.add_parser("show")
    a = ap.parse_args()
    if a.cmd == "update":
        update(a.root)
    elif a.cmd == "ask":
        ask(a.question, a.at, a.answerer, "caption" if a.memory == "captions" else "evidence")
    else:
        mem = load()
        text, _ = AN.memory_text(mem["visits"], "evidence", {v["id"] for v in mem["visits"] if v.get("kept")},
                                 mem["usual"], (1, "2359"), 1)
        print(text)


if __name__ == "__main__":
    sys.exit(main())
