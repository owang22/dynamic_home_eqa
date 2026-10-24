"""Answer the collect-session memory questions with the two baseline memories, offline (no dog).

    python3 memory_qa.py retrieval                  # did each search find the evidence pictures? (no model calls)
    python3 memory_qa.py answer --arms A,B          # answer every question with each arm (claude -p, Sonnet)
    python3 memory_qa.py grade                      # grade the answers against the gold answers (claude -p, Sonnet)

Arms (the two baselines; both only see pictures taken before the question's ask_at):
  A  text tags: word search over the vision model's descriptions (objects, colours, places) plus time and pose;
     the answerer reads the top descriptions as text and never sees a picture.
  B  embeddings: SigLIP text-to-picture search; the answerer is shown the top pictures with their time and pose,
     and no descriptions.
Both use the question itself as the search query and the same answerer (claude -p --model sonnet, Read tool only).

Outputs go to go2/data/collection/analysis/: retrieval_<day>.json, answers_<day>_<arm>.json, grades_<day>.json,
memory_qa_<day>.md. Model replies are cached by prompt in analysis/cache/.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lab_agent"))
import memory as M  # noqa: E402

DAY = "2026-10-23"
OUT = HERE.parent / "data" / "collection" / "analysis"
CACHE = OUT / "cache"
PICS = M.DATA / "pictures"
K = 8
MODEL = "claude-sonnet-5-5"
SCRATCH = "/tmp/claude-1027/-home-oliver/ecbfd7be-8fd0-4ab0-98fa-ac6c500efc55/scratchpad"


def questions():
    return json.loads((OUT / f"questions_{DAY}.json").read_text())


def epoch(s):
    return time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S"))


def retrieve(q, mode, k=K, recs=None):
    return M.search(q["question"], until=epoch(q["ask_at"]), k=k, recs=recs, mode=mode)


def retrieval():
    recs = M.load()
    rows = []
    for q in questions():
        row = {"id": q["id"], "ask_at": q["ask_at"], "evidence": q["evidence"]}
        for arm, mode in (("A", "words"), ("B", "images")):
            for k in (K, 30):
                ids = [h["id"] for h in retrieve(q, mode, k, recs)]
                row[f"{arm}@{k}"] = [i for i in q["evidence"] if i in ids]
        rows.append(row)
        print(f"{q['id']:<22} " + "  ".join(f"{c}={len(row[c])}/{len(q['evidence'])}"
                                            for c in ("A@8", "A@30", "B@8", "B@30")))
    (OUT / f"retrieval_{DAY}.json").write_text(json.dumps(rows, indent=1))
    for c in ("A@8", "A@30", "B@8", "B@30"):
        print(c, "found at least one evidence picture for", sum(bool(r[c]) for r in rows), "of", len(rows))


ASK = """You are the memory of a four-legged robot dog in a university robotics lab. The dog walks around with a
camera about 30 cm off the floor and keeps the pictures it takes. It is now {now}. Someone asks:

"{question}"

Below are the memories a search returned for that question (best first). {what}
Answer only from these memories; do not guess beyond them. Say when the answer may be out of date.

{memories}

Reply with only this JSON:
{{"answer": "<one to three sentences>", "evidence": ["<memory ids you relied on>"],
 "action": "answer" | "answer_then_look" | "look" | "abstain",
 "confidence": <0 to 1>}}
action: "answer" if memory is enough; "answer_then_look" if you answer but the dog should go and check;
"look" if memory cannot answer and the dog should go and look; "abstain" if there is nothing to find."""


def memory_text(arm, hits):
    lines = []
    for h in hits:
        p = h.get("pose") or {}
        where = f"near {h.get('near_place')}, map ({p.get('x')}, {p.get('y')}) facing {p.get('yaw_deg')} deg"
        if arm == "A":
            seen = h.get("summary") or "(no description: the vision model has not described this picture)"
            obj = h.get("match")
            lines.append(f"[{h['id']}] {h['time']}, {where}; people {h.get('people')}; "
                         + (f"match: {obj}; " if obj else "") + seen)
        else:
            lines.append(f"[{h['id']}] {h['time']}, {where}; picture: {PICS / (h['id'] + '.jpg')}")
    return "\n".join(lines) or "(the search returned nothing)"


def run_claude(prompt):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.sha256((MODEL + prompt).encode()).hexdigest()[:24] + ".json")
    if f.exists():
        return json.loads(f.read_text())
    cmd = ["claude", "-p", "--model", MODEL, "--tools", "Read", "--allowedTools", "Read", "--strict-mcp-config",
           "--max-turns", "16", "--output-format", "json", "--add-dir", str(PICS)]
    t0 = time.time()
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=900, cwd=SCRATCH)
    try:
        d = json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        return {"result": None, "error": (r.stdout + r.stderr)[-1500:]}
    out = {"result": d.get("result"), "turns": d.get("num_turns"), "is_error": d.get("is_error"),
           "seconds": round(time.time() - t0, 1)}
    if out["result"] and not out["is_error"]:
        f.write_text(json.dumps(out))
    return out


def parse(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except Exception:  # noqa: BLE001
        return None


def answer_one(q, arm, recs):
    hits = retrieve(q, "words" if arm == "A" else "images", K, recs)
    what = ("Each memory is the text a vision model wrote about one picture; you cannot see the pictures."
            if arm == "A" else
            "Each memory is one picture with its time and place; open the pictures with the Read tool and look.")
    prompt = ASK.format(now=time.strftime("%a %Y-%m-%d %H:%M", time.localtime(epoch(q["ask_at"]))),
                        question=q["question"], what=what, memories=memory_text(arm, hits))
    out = run_claude(prompt)
    return {"id": q["id"], "arm": arm, "retrieved": [h["id"] for h in hits],
            "evidence_retrieved": [i for i in q["evidence"] if i in [h["id"] for h in hits]],
            "reply": parse(out.get("result")), "raw": out.get("result"), "error": out.get("error"),
            "seconds": out.get("seconds")}


def answer(arms, workers):
    recs = M.load()
    qs = questions()
    for arm in arms:
        with ThreadPoolExecutor(workers) as ex:
            rows = list(ex.map(lambda q: answer_one(q, arm, recs), qs))
        (OUT / f"answers_{DAY}_{arm}.json").write_text(json.dumps(rows, indent=1))
        for r in rows:
            a = (r["reply"] or {}).get("answer") or r["error"] or r["raw"]
            print(f"[{arm}] {r['id']:<22} {str(a)[:150]}")


GRADE = """Grade a robot memory's answer against the gold answer.

Question (asked at {ask_at}): {question}
Gold answer: {gold}
An answer must get these right: {key}
What the robot should ideally do: {good_action} (answer = memory is enough; answer_then_look = answer but check;
look = memory cannot know, go look; abstain = nothing to find)

Robot's answer: {answer}
Robot's chosen action: {action}

Grade "right" if it gets every key point right, "partly" if it gets some, "wrong" if it gets none or asserts
something false. Saying "I don't know" is "wrong" when the memory needed to answer was there, unless the gold
action is look or abstain. Reply with only this JSON: {{"grade": "right" | "partly" | "wrong", "why": "<one sentence>"}}"""


def grade():
    qs = {q["id"]: q for q in questions()}
    rows = []
    for f in sorted(OUT.glob(f"answers_{DAY}_*.json")):
        for a in json.loads(f.read_text()):
            q = qs[a["id"]]
            rep = a["reply"] or {}
            prompt = GRADE.format(ask_at=q["ask_at"], question=q["question"], gold=q["answer"],
                                  key="; ".join(q["key"]), good_action=q["good_action"],
                                  answer=rep.get("answer") or a["raw"] or "(no answer)", action=rep.get("action"))
            g = parse(run_claude(prompt).get("result")) or {}
            rows.append({"id": a["id"], "arm": a["arm"], "grade": g.get("grade"), "why": g.get("why"),
                         "action": rep.get("action"), "good_action": q["good_action"],
                         "evidence_retrieved": a["evidence_retrieved"], "answer": rep.get("answer")})
    (OUT / f"grades_{DAY}.json").write_text(json.dumps(rows, indent=1))
    report(rows, qs)


def report(rows, qs):
    arms = sorted({r["arm"] for r in rows})
    by = {(r["id"], r["arm"]): r for r in rows}
    lines = [f"# Memory questions from the {DAY} collect session: baselines", "",
             "A = text tags (word search over descriptions, answerer reads text). B = embeddings (SigLIP picture "
             f"search, answerer looks at the top {K} pictures). Same answerer (Sonnet) and grader (Sonnet).", "",
             "| question | asked | " + " | ".join(f"{a}: evidence found / grade / action" for a in arms) + " |",
             "|---|---|" + "---|" * len(arms)]
    for qid, q in qs.items():
        cells = []
        for a in arms:
            r = by.get((qid, a))
            cells.append("-" if not r else f"{len(r['evidence_retrieved'])}/{len(q['evidence'])} / {r['grade']} / "
                                           f"{r['action']}")
        lines.append(f"| {q['question']} | {q['ask_at'][11:16]} | " + " | ".join(cells) + " |")
    lines += [""]
    for a in arms:
        rs = [r for r in rows if r["arm"] == a]
        n = {g: sum(r["grade"] == g for r in rs) for g in ("right", "partly", "wrong")}
        act = sum(r["action"] == r["good_action"] for r in rs)
        lines.append(f"- **{a}:** right {n['right']}, partly {n['partly']}, wrong {n['wrong']} of {len(rs)}; "
                     f"evidence retrieved for {sum(bool(r['evidence_retrieved']) for r in rs)}; "
                     f"chose the ideal action {act} times.")
    (OUT / f"memory_qa_{DAY}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["retrieval", "answer", "grade"])
    ap.add_argument("--arms", default="A,B")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.step == "retrieval":
        retrieval()
    elif a.step == "answer":
        answer(a.arms.split(","), a.workers)
    else:
        grade()
