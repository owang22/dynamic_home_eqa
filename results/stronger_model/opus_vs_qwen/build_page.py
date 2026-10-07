"""Data for the Opus-vs-Qwen reader page: one JSON per home, plus the instructions word for word.

    PYTHONPATH=src python3 results/stronger_model/opus_vs_qwen/build_page.py

Writes results/stronger_model/opus_vs_qwen/page/data_<home>.json and words.json. Qwen's reasoning for each
first room is read back from the original cell's cache (replay only, every call must hit); Opus's comes from
the answers files. Notes are shipped as version lists; the page rebuilds the notes as they stood each night.
"""
import json
import pathlib
import sys

sys.path.insert(0, "src")
from baselines.patrol.llm import LLMClient  # noqa: E402
from stronger_model.opus_beliefs import BELIEF_QUESTIONS, CELLS  # noqa: E402

D = pathlib.Path("results/stronger_model/opus_vs_qwen")
OUT = D / "page"
HH = ["hh_s2_t03", "hh_s32_t03", "hh_s48_t03"]
WHO = {"hh_s2_t03": ["Tomas", "works from home at the office desk, about 9 to 5:30", "Ines"],
       "hh_s32_t03": ["Leo", "works from home at the desk, about 9 to 5:30", "Aisha and Elena"],
       "hh_s48_t03": ["Marco", "a student, at classes about 8:40 to 2:30, then studying at home", "Priya"]}
OPUS_BELIEFS = "results/stronger_model/opus_beliefs/claude_opus/cells/walk/{h}/beliefs.jsonl"


def versions(claims):
    out = []
    for c in claims:
        hist = c.get("revision_history") or []
        states = [h["was"] for h in hist] + [{k: c.get(k) for k in ("statement", "holds_under", "status", "standing")}]
        days = [c.get("first_written_day") or 0] + [h["day"] for h in hist]
        whys = [""] + [h.get("why", "") for h in hist]
        out.append({"id": c["claim_id"],
                    "v": [{"d": d, "s": s.get("statement"), "h": s.get("holds_under"), "st": s.get("standing"),
                           "y": w} for d, s, w in zip(days, states, whys)]})
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    qcache = LLMClient(pathlib.Path("llm_prior_cache/self_improve"), replay_only=True)
    for h in HH:
        prompts = [json.loads(l) for l in open(D / "memory_qwen" / f"prompts_{h}.jsonl")]
        opus_own = {r["question_id"]: r for r in map(json.loads, open(D / "answers_opus_notes_by_opus" / f"{h}.jsonl"))}
        opus_qn = {r["question_id"]: r for r in map(json.loads, open(D / "answers_qwen_notes_by_opus" / f"{h}.jsonl"))}
        qs = []
        for p in prompts:
            text, _ = qcache.complete(p["messages"], p["schema"], p["max_tokens"])
            if text is None:
                raise RuntimeError(f"{h} {p['question_id']}: Qwen's first choice is not in the cache")
            qa = json.loads(text)
            if qa["room"] != p["rooms_opened"][0]:
                raise AssertionError(f"{h} {p['question_id']}: cached room differs from the cell's first room")
            row = {"q": p["question_id"], "d": p["day"], "t": p["time"], "o": p["object_id"], "m": p["is_a_mover"],
                   "true": p["true_room"], "opened": p["rooms_opened"], "qr": qa["room"], "qy": qa.get("why", "")}
            for key, src in (("oo", opus_own), ("oq", opus_qn)):
                if p["question_id"] in src:
                    row[key + "r"] = src[p["question_id"]]["room"]
                    row[key + "y"] = src[p["question_id"]]["why"]
            qs.append(row)
        beliefs = {r["day"]: r["beliefs"] for r in map(json.loads, open(OPUS_BELIEFS.format(h=h)))}
        qwen_beliefs = {}
        qb = D / "memory_qwen" / f"beliefs_{h}.jsonl"
        if qb.exists():
            qwen_beliefs = {r["day"]: r["beliefs"] for r in map(json.loads, open(qb)) if r.get("beliefs")}
        data = {"home": h, "who": WHO[h],
                "notes": {"opus": versions(json.load(open(D / "memory_opus" / f"notes_{h}.json"))["claims"]),
                          "qwen": versions(json.load(open(CELLS / h / "notes.json"))["claims"])},
                "beliefs": {"opus": beliefs, "qwen": qwen_beliefs}, "questions": qs}
        (OUT / f"data_{h}.json").write_text(json.dumps(data, separators=(",", ":")))
        print(h, len(qs), "questions,", sum("oor" in q for q in qs), "with Opus answers;",
              round((OUT / f"data_{h}.json").stat().st_size / 1e6, 1), "MB")

    # the instructions, word for word: one nightly notes prompt (day 2, hh_s2) cut where the day's sightings go,
    # the five belief questions, and one room-choice prompt (day 33, hh_s2, Opus's notes) cut the same way
    scratch = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
    words = {"belief": BELIEF_QUESTIONS}
    if scratch and (scratch / "notes_call_3.json").exists():
        u = json.load(open(scratch / "notes_call_3.json"))["messages"]
        words["notes_system"] = u[0]["content"]
        body = u[1]["content"]
        words["notes"] = (body.split("WHAT YOU SAW TODAY")[0] + "WHAT YOU SAW TODAY ... [that day's looks] ...\n\n"
                          + "YOUR MEMORY AS IT STANDS:\n\n[the notes]\n\n" + body.split("YOUR MEMORY AS IT STANDS:")[1].split("\n\n", 2)[2])
    for l in open(D / "memory_opus" / "prompts_hh_s2_t03.jsonl"):
        r = json.loads(l)
        if r["day"] == 33:
            words["choice_system"] = r["messages"][0]["content"]
            words["choice"] = r["messages"][1]["content"]
            words["choice_note"] = f"{r['question_id']}, {r['object_id']}, day 33, hh_s2_t03, with Opus's notes"
            break
    (OUT / "words.json").write_text(json.dumps(words))
    print("words.json", list(words))


if __name__ == "__main__":
    main()
