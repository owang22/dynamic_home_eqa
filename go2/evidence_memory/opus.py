"""The same answer step with Opus (claude -p on Oliver's Max plan: counts against the plan's usage limit, no API
account; the CLI's cost field is an API-price estimate, not a charge).

    python opus.py --height 1.0 --arms C,D [--workers 4] [--limit N]
    python opus.py --height 1.0 --arms D --all_days          # whole five-day memory, no date filter
    python opus.py --height 1.0 --arms D,C --memory out/memory_1.0_opuswriter.json --tag _opuswriter
    OPUS_RERUN=1 python opus.py ... --tag _rerun               # same prompts asked again (rerun noise)
Opus may use only the Read tool (--tools Read --strict-mcp-config).

Same notes (written by Qwen), same day filter, same kept pictures and the same answer format as answer.py.
Opus reads the pictures itself with the Read tool (up to 6), instead of a separate pick step.
Writes out/answers_<height>_<arm>_opus.json (scored by score.py --tag _opus).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

import answer as AN
import common as C

MODEL = "claude-opus-5-5"
import os
# OPUS_RERUN=<name>: a separate cache, so identical prompts are asked again (the Opus rerun noise floor)
CACHE = C.HERE / (f"cache_opus_rerun_{os.environ['OPUS_RERUN']}" if os.environ.get("OPUS_RERUN") else "cache_opus")
CACHE.mkdir(exist_ok=True)


def run_claude(prompt, dirs=()):
    key = hashlib.sha256(prompt.encode()).hexdigest()[:24]
    f = CACHE / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text())
    # --tools Read: the only tool available (the first runs used --allowedTools Read, and about 10 sessions still
    # ran Bash to crop pictures; the auditor found no reads outside the kept list); --strict-mcp-config: no connectors
    cmd = ["claude", "-p", "--model", MODEL, "--tools", "Read", "--strict-mcp-config", "--allowedTools", "Read",
           "--max-turns", "12", "--output-format", "json",
           "--add-dir", str(C.PICS["1.0"]), "--add-dir", str(C.PICS["0.4"])]
    for d in dirs:
        cmd += ["--add-dir", str(d)]
    t0 = time.time()
    for attempt in range(3):
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=900,
                           cwd="/tmp/claude-1027/-home-oliver-robot-dynamic-home-eqa/70109b99-ad14-4bc5-be52-bd122cfe3581/scratchpad")
        try:
            d = json.loads(r.stdout)
            break
        except Exception:  # noqa: BLE001
            if attempt == 2:
                return {"result": None, "error": (r.stdout + r.stderr)[-1500:]}
            time.sleep(30)
    out = {"result": d.get("result"), "cost_usd": d.get("total_cost_usd"), "turns": d.get("num_turns"),
           "is_error": d.get("is_error"), "seconds": round(time.time() - t0, 1)}
    if out["result"] and not out["is_error"]:
        f.write_text(json.dumps(out))
    return out


def parse(text):
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except Exception:  # noqa: BLE001
        return None


def answer_one(q, arm, mem, all_days=False):
    notes, how = AN.ARMS[arm]
    visits = mem["visits"]
    upto = tuple(q["ask_at"])
    keep = AN.kept_pictures(visits, how)
    u_day = upto[0] if upto[1] >= "2200" else upto[0] - 1
    usual = mem["usual"].get(str(u_day)) if notes == "evidence" else None
    # all_days: the whole memory (five days) with no date filter, to test searching all of it
    text, ids = AN.memory_text(visits, notes, keep, usual, upto, None if all_days else q["day"])
    pics = "\n".join(f"{s}: {v['picture']}" for s, v in ids.items() if v["id"] in keep)
    schema = AN.schema_for(q)
    prompt = (f"{AN.SYSTEM}\n\nPEOPLE SHEET:\n{C.PEOPLE_SHEET}\n\n{text}\n\nKEPT PICTURES (id: file). You may open up to "
              f"{AN.MAX_LOOK} of them with the Read tool; open none if the notes are enough. Do not open any other file.\n"
              f"{pics or '(none)'}\n\nQUESTION: {q['question']}\n\nReply with only one JSON object that fits this JSON "
              f"schema (use the enum strings exactly), plus a field \"looked\" listing the ids of the pictures you opened:\n"
              f"{json.dumps(schema)}")
    out = run_claude(prompt)
    ans = parse(out.get("result"))
    return {"id": q["id"], "arm": arm, "answer": ans, "looked": (ans or {}).get("looked", []), "kept": len(keep),
            "memory_chars": len(text), "info": {k: out.get(k) for k in ("cost_usd", "turns", "seconds", "error")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--height", default="1.0")
    ap.add_argument("--arms", default="C,D")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--all_days", action="store_true")
    ap.add_argument("--memory", default=None, help="another memory file, e.g. out/memory_1.0_opuswriter.json")
    ap.add_argument("--tag", default="", help="extra tag for the output name")
    a = ap.parse_args()
    tag = ("_opus_alldays" if a.all_days else "_opus") + (f"_n{a.limit}" if a.limit else "") + a.tag
    mem = json.loads(open(a.memory or C.OUT / f"memory_{a.height}.json").read())
    qs = json.loads((C.OUT / "questions.json").read_text())
    if a.limit:
        qs = qs[::max(1, len(qs) // a.limit)][:a.limit]
    for arm in a.arms.split(","):
        t0 = time.time()
        with ThreadPoolExecutor(a.workers) as pool:
            recs = list(pool.map(lambda q: answer_one(q, arm, mem, a.all_days), qs))
        C.dump(recs, C.OUT / f"answers_{a.height}_{arm}{tag}.json")
        cost = sum((r["info"].get("cost_usd") or 0) for r in recs)
        bad = sum(1 for r in recs if r["answer"] is None)
        print(f"{time.strftime('%H:%M:%S')} opus height {a.height} arm {arm}: {len(recs)} answers, {bad} unparsed, "
              f"{time.time() - t0:.0f} s, cost-equivalent ${cost:.2f}", flush=True)


if __name__ == "__main__":
    main()
