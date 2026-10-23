"""Replay the logged Opus turns against a small model.

    python3 run_replay.py memory  --url http://127.0.0.1:8301/v1 --tag 8b     # memory-only turns, full agent runs
    python3 run_replay.py driving --url http://127.0.0.1:8301/v1 --tag 8b     # driving turns: next-action agreement
    python3 run_replay.py judge   --tag 8b                                    # 27B judges memory answers vs Opus

Outputs go to replay/results/<kind>_<tag>.json (an existing file is moved to *_v1, *_v2, ... first).
Memory turns: the memory is the index snapshot cut at the turn's K (build_cases.py), "now" is the turn's time,
earlier turns of the conversation are given as text (question + Opus's answer). Driving turns are not executed:
for each Opus tool call, the model sees the turn so far (Opus's calls, their results and photos) and picks the next
action; the last position asks whether it answers. Nothing here talks to the console.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from llm import LLM, image_part  # noqa: E402
from memtools import Memory  # noqa: E402
from small_agent import DRIVE_TOOLS, MEMORY_TOOLS, MemEnv, SmallAgent  # noqa: E402

INDEX = Path(sorted(glob.glob(str(HERE / "data" / "index_snapshot_*.jsonl")))[0])
PICS = HERE.parents[2] / "data" / "lab_agent" / "pictures"
RES = HERE / "results"
PIC = re.compile(r"\b([tpl]\d{9,}(?:_\d+)?)\b")


def save(name, obj):
    RES.mkdir(exist_ok=True)
    p = RES / f"{name}.json"
    if p.exists():
        n = 1
        while (RES / f"{name}_v{n}.json").exists():
            n += 1
        p.rename(RES / f"{name}_v{n}.json")
    p.write_text(json.dumps(obj, indent=1))
    print("->", p)


def cases(kind):  # logged turns of one kind
    return [c for c in json.load(open(HERE / "cases_logged.json")) if c["kind"] == kind]


def dog_status_for(c):
    """The last logged status before this turn (only the 16:21 one exists), else None."""
    if c["time"] >= "16:21:26":
        return ("console up. map: localized (saved map loaded (same session as when it was saved)). dog at "
                "(-0.58, 2.55) facing 26 deg, nearest place sofa (0.66 m). control owner: None")
    return None


# ---------------- memory turns ----------------

def run_memory(llm, tools=MEMORY_TOOLS, workers=2, vlm=None, only=None, which="logged", prompt="v0"):
    def one(c):
        m = Memory.from_index(INDEX, c["K"], c["t"])  # K None = the whole snapshot
        ag = SmallAgent(llm, MemEnv(m, dog_status_for(c) if which == "logged" else None, vlm=vlm), tools,
                        place_ids=list(m.P), places_text=m.list_places(), now=c["t"], prompt=prompt)
        tr = ag.run(c["text"], c["history"])
        tr.update(case=c["id"], prompt=prompt)
        if which == "logged":
            tr.update(note=c["note"], opus_answer=c["opus_answer"], opus_secs=c["opus_secs"],
                      opus_calls=len(c["opus_calls"]), opus_opened=c["opus_opened"], opus_cited=c["opus_cited"])
        else:
            tr.update(kind=c["kind"], key=c["key"], accept_ids=c["accept_ids"])
        tr["metrics"] = memory_metrics(tr, m)
        print(c["id"], tr["model"], f"{tr['secs']:.1f}s", len(tr["steps"]), "steps", json.dumps(tr["metrics"]), flush=True)
        return tr
    pool = cases("memory") if which == "logged" else json.load(open(HERE / "cases_generated.json"))
    cs = [c for c in pool if not only or c["id"] in only]
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(one, cs))


def memory_metrics(tr, m):
    ans = tr.get("answer") or {}
    text = ans.get("text") or ""
    cited = list(dict.fromkeys((ans.get("cited_ids") or []) + PIC.findall(text)))
    returned = set()
    for s in tr["steps"]:
        returned |= set(PIC.findall(s.get("result") or ""))
    opened = set(tr["opened"])
    calls = [s for s in tr["steps"] if s["tool"] not in (None, "answer")]
    keys = [json.dumps([s["tool"], s.get("args")], sort_keys=True) for s in calls]
    return {"answered": bool(text), "steps": len(calls), "invalid": sum(s["tool"] is None for s in tr["steps"]),
            "asked_expert": any(s["tool"] == "ask_expert" for s in calls),
            "repeated_call": len(keys) != len(set(keys)),
            "cited": len(cited), "cited_opened": sum(i in opened for i in cited),
            "cited_not_in_memory": [i for i in cited if i not in m.by],
            "cited_never_returned": [i for i in cited if i not in returned and i not in opened],
            "opened": len(opened)}


# ---------------- driving turns: next-action agreement ----------------

def logged_action(call):
    a = dict(call["args"])
    if call["tool"] == "go_to":
        a.setdefault("place", "")
    return {"thought": "", "tool": call["tool"], "args": a}


def prefix_messages(c, upto, places_text, place_ids, now, max_images):
    ag = SmallAgent(None, None, DRIVE_TOOLS, place_ids=place_ids, places_text=places_text, now=now,
                    max_images=max_images)
    msgs = ag.messages(c["text"], c["history"])
    for call in c["opus_calls"][:upto]:
        msgs.append({"role": "assistant", "content": json.dumps(logged_action(call))})
        ids = list(call["pics"])
        if call["tool"] == "show_pictures":
            ids = call["args"].get("ids", [])
        content = [{"type": "text", "text": f"Result of {call['tool']}:\n{(call['result'] or '')[:4000]}"}]
        for i in ids:
            p = PICS / f"{i}.jpg"
            if p.exists():
                content += [{"type": "text", "text": f"picture {i}:"}, image_part(p.read_bytes(), 768)]
        msgs.append({"role": "user", "content": content if len(content) > 1 else content[0]["text"]})
    SmallAgent.trim_images(msgs, max_images)
    return msgs, ag


def same_action(pred, ref):
    """(tool_match, arg_match) per the plan in research_hierarchy.md section 4."""
    if pred is None or pred.get("tool") != ref["tool"]:
        return False, False
    a, b, t = pred.get("args") or {}, ref["args"], ref["tool"]
    if t == "go_to":
        if b.get("place"):
            return True, a.get("place") == b["place"]
        if a.get("x") is None or a.get("y") is None:
            return True, False
        return True, math.hypot(a["x"] - b["x"], a["y"] - b["y"]) <= 0.5
    if t == "turn":
        return True, abs(a.get("deg", 0) - b["deg"]) <= 30 and (a.get("deg", 0) > 0) == (b["deg"] > 0)
    if t == "move":
        return True, abs(a.get("metres", 0) - b["metres"]) <= 0.5 and (a.get("metres", 0) > 0) == (b["metres"] > 0)
    if t == "photo":
        return True, (a.get("look_deg", 0) > 0) == (b.get("look_deg", 0) > 0) and (a.get("look_deg", 0) < 0) == (b.get("look_deg", 0) < 0)
    if t in ("show_pictures", "locate"):
        return True, bool(set(a.get("ids") or []) & set(b.get("ids") or []))
    if t == "search_memory":
        wa, wb = set(re.findall(r"[a-z]+", (a.get("query") or "").lower())), set(re.findall(r"[a-z]+", b["query"].lower()))
        return True, bool(wa & wb)
    return True, True


def run_driving(llm, workers=2, max_images=6):
    P = json.loads((HERE / "data" / "places_snapshot.json").read_text())
    m = Memory(list(), P, 0)
    places_text = m.list_places()
    jobs = []
    for c in cases("driving"):
        calls = c["opus_calls"]
        for k in range(len(calls) + (1 if c["opus_answer"] else 0)):
            # Opus sometimes made several calls at once: any of that batch counts as the next action
            if k < len(calls):
                batch = [x for x in calls[k:] if abs(x["t"] - calls[k]["t"]) < 0.3]
                refs = [logged_action(x) for x in batch]
            else:
                refs = [{"tool": "answer", "args": {}}]
            jobs.append((c, k, refs))

    def one(job):
        c, k, refs = job
        msgs, ag = prefix_messages(c, k, places_text, list(P), c["t"], max_images)
        ag.llm = llm
        try:
            r = llm.chat(msgs, schema=ag.schema, max_tokens=600)
            pred = r["json"]
        except Exception as e:  # noqa: BLE001
            r, pred = {"secs": None, "text": str(e)}, None
        tm = am = False
        for ref in refs:
            t_, a_ = same_action(pred, ref)
            tm, am = tm or t_, am or a_
        out = {"case": c["id"], "note": c["note"], "k": k, "ref": refs, "pred": pred, "tool_match": tm,
               "arg_match": am, "secs": r.get("secs")}
        print(c["id"], k, "ref", [x["tool"] for x in refs], "pred", (pred or {}).get("tool"),
              json.dumps((pred or {}).get("args"))[:80], "OK" if am else ("tool" if tm else "MISS"), flush=True)
        return out
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(one, jobs))


# ---------------- judge ----------------

JUDGE_SCHEMA = {"type": "object", "properties": {
    "why": {"type": "string", "maxLength": 400},
    "reference_says_seen": {"type": "string", "enum": ["yes", "no", "not applicable"]},
    "candidate_says_seen": {"type": "string", "enum": ["yes", "no", "not applicable"]},
    "verdict": {"type": "string", "enum": ["agree", "partial", "disagree"]}},
    "required": ["why", "reference_says_seen", "candidate_says_seen", "verdict"]}

JUDGE_ASK = """Two answers to the same question to a robot dog's lab assistant, which answers from pictures the dog \
took. The REFERENCE {refwho}; treat it as correct.
Judge the CANDIDATE against it on the main facts only: whether the thing/person was seen, when, where (which \
desk/place or what it was next to), how many, what colour. Extra detail, style, and length do not matter. A \
candidate that names a different place, time, count or colour as its main claim disagrees. One that has the main \
claim right but misses or gets wrong a secondary fact is partial. "Not seen" vs a sighting is a disagreement.
reference_says_seen / candidate_says_seen: does the answer claim the asked-about thing was seen in a picture \
("not applicable" if the question is not about finding something).

QUESTION: {q}

REFERENCE: {ref}

CANDIDATE: {cand}"""


def judge(judge_llm, q, ref, cand, refwho="was written by a strong model that looked at the pictures"):
    r = judge_llm.chat([{"role": "user", "content": JUDGE_ASK.format(q=q, ref=ref, cand=cand or "(no answer)", refwho=refwho)}],
                       schema=JUDGE_SCHEMA, max_tokens=600)
    return r["json"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["memory", "driving", "judge", "generated", "judge_generated"])
    ap.add_argument("--prompt", default="v0")
    ap.add_argument("--url", default="http://127.0.0.1:8301/v1")
    ap.add_argument("--model")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--max-images", type=int, default=6)
    ap.add_argument("--judge-url", default="http://127.0.0.1:8300/v1")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    if a.what == "memory":
        llm = LLM(a.url, a.model)
        save(f"memory_{a.tag}", run_memory(llm, workers=a.workers, only=a.only, prompt=a.prompt))
    elif a.what == "generated":
        llm = LLM(a.url, a.model)
        save(f"generated_{a.tag}", run_memory(llm, workers=a.workers, only=a.only, which="generated", prompt=a.prompt))
    elif a.what == "judge_generated":
        jl = LLM(a.judge_url)
        gc = {c["id"]: c for c in json.load(open(HERE / "cases_generated.json"))}
        src = RES / ("opus_generated.json" if a.tag == "opus" else f"generated_{a.tag}.json")
        rows = json.load(open(src))

        def oneg(tr):
            ans = tr.get("answer")
            ans = ans if isinstance(ans, str) else (ans or {}).get("text")
            c = gc[tr["case"]]
            j = judge(jl, c["text"], c["key"], ans, refwho="is the answer key, checked by a person who looked at the pictures")
            cited = set(PIC.findall(ans or "")) | set(((tr.get("answer") or {}) if isinstance(tr.get("answer"), dict) else {}).get("cited_ids") or [])
            j.update(case=c["id"], kind=c["kind"], cited_accept=bool(cited & set(c["accept_ids"])),
                     cited=sorted(cited), opened=tr.get("opened", []))
            print(c["id"], c["kind"], j["verdict"], "cited_ok" if j["cited_accept"] else "", j["why"][:120], flush=True)
            return j
        with ThreadPoolExecutor(min(a.workers, 4)) as ex:
            save(f"judge_generated_{a.tag}", list(ex.map(oneg, rows)))
    elif a.what == "driving":
        llm = LLM(a.url, a.model)
        save(f"driving_{a.tag}", run_driving(llm, workers=a.workers, max_images=a.max_images))
    else:
        jl = LLM(a.judge_url)
        rows = json.load(open(RES / f"memory_{a.tag}.json"))
        cs = {c["id"]: c for c in cases("memory")}

        def one(tr):
            j = judge(jl, cs[tr["case"]]["text"], tr["opus_answer"], (tr.get("answer") or {}).get("text"))
            print(tr["case"], j["verdict"], j["why"][:150], flush=True)
            return {"case": tr["case"], **j}
        with ThreadPoolExecutor(min(a.workers, 4)) as ex:
            save(f"judge_memory_{a.tag}", list(ex.map(one, rows)))


if __name__ == "__main__":
    main()
