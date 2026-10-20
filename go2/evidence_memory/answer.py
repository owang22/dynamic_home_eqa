"""Answer the questions from each memory arm.

    python answer.py --height 1.0 --arms A,B,C,D,F,O [--workers 16] [--limit N] [--tag T]
    EM_RERUN=1 python answer.py ...   # fresh calls into a separate cache (rerun noise)

Arms (what the robot kept; DESIGN.md has the reasons):
  A captions, no pictures            B captions + every picture
  F evidence notes, no pictures      D evidence notes + every picture
  C evidence notes + the pictures the writer marked important (2-3) and the picture before each
  E evidence notes + the same number of pictures per day, evenly spaced (the control for C's choice)
  O oracle: no notes, exactly the right pictures for the question (a ceiling set by perception)
  Bf, Cf, Df  B, C, D with a "fresh look": each picked picture is first asked about on its own, without the notes
  Ep, Ep2, Ep3  evidence notes + random before/after pairs at C's budget (three draws; the fair control for C;
              E above never kept a before/after pair, so it is not a valid control: see RESULTS.md, audit)
With pictures, the model first picks up to 6 kept pictures from the notes, then answers looking at them.
Writes out/answers_<height>_<arm>.json.
"""
from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor

import common as C

ARMS = {"A": ("caption", "none"), "B": ("caption", "all"), "F": ("evidence", "none"), "D": ("evidence", "all"),
        "C": ("evidence", "important"), "E": ("evidence", "even"), "O": (None, "oracle"),
        # "fresh look" (added 13:20 after the first results): each picture picked from memory is first asked about
        # on its own, without the notes; the answer then uses the notes plus those fresh looks (text), so a note
        # that left a thing out cannot override what the picture shows.
        "Bf": ("caption", "all"), "Cf": ("evidence", "important"), "Df": ("evidence", "all"),
        # Ep (added 14:40 after the audit): the control E could never keep two visits of one place in a row, so it
        # never held a before/after pair. Ep keeps the same number of pictures per day as C, as random
        # (picture + the one before it at that place) pairs.
        "Ep": ("evidence", "pairs"),
        # 2026-10-19 16:00: two more random draws of the pairs control (seeds 8 and 9; Ep is seed 7)
        "Ep2": ("evidence", "pairs2"), "Ep3": ("evidence", "pairs3")}
FRESH_SCHEMA = {"type": "object", "properties": {"sees": {"type": "string", "maxLength": 400}}, "required": ["sees"]}
FRESH_ASK = ("This is your picture of the {place} at {time} on day {day}. Question you are trying to answer: {question}\n"
             "Look carefully at this picture only. Describe what in it bears on the question: name the things you can "
             "see that matter, including small or partly hidden ones, and say if something the question asks about is "
             "not there. At most 60 words.")
MAX_LOOK = 6

SYSTEM = ("You are a home robot answering questions from your own memory of patrols. You patrol fixed places every two "
          "hours (08:00 to 22:00) and photograph each one. You only know what your memory below shows: your notes, and "
          "the pictures you kept. People are never in your pictures. If you have a note or picture of the place at that "
          "time and the thing is not there, the answer is \"no\". Say \"cannot tell\" only when your memory has no "
          "note or picture that could show the answer.")


def kept_pictures(visits, how):
    """Which visits keep their picture for later looking back."""
    if how == "none":
        return set()
    if how == "all":
        return {v["id"] for v in visits if v["picture"]}
    imp = set()
    by_spot = {}
    for v in visits:
        prev = by_spot.get(v["spot"])
        by_spot[v["spot"]] = v
        if v["picture"] and (v["evidence"] or {}).get("importance", 0) >= 2:
            imp.add(v["id"])
            if prev and prev["picture"]:
                imp.add(prev["id"])          # the before picture of an important change
    if how == "important":
        return imp
    if how.startswith("pairs"):
        import random
        rng = random.Random(7 + (int(how[5:]) - 1 if how[5:] else 0))
        out = set()
        for d in sorted({v["day"] for v in visits}):
            k = sum(1 for v in visits if v["day"] == d and v["id"] in imp)
            prev_of, last = {}, {}
            for v in visits:                    # the visit before each one at the same place (may be the day before)
                if v["day"] == d and v["picture"] and last.get(v["spot"]) and last[v["spot"]]["picture"]:
                    prev_of[v["id"]] = last[v["spot"]]["id"]
                last[v["spot"]] = v
            cands = sorted(prev_of)
            rng.shuffle(cands)
            day_set = set()
            for vid in cands:
                if len(day_set) >= k:
                    break
                day_set |= {vid, prev_of[vid]}
            out |= day_set
        return out
    if how == "even":                           # same count per day as "important", evenly spaced in time
        out = set()
        for d in sorted({v["day"] for v in visits}):
            today = [v for v in visits if v["day"] == d and v["picture"]]
            k = sum(1 for v in today if v["id"] in imp)
            if k:
                step = len(today) / k
                out |= {today[int(i * step)]["id"] for i in range(k)}
        return out
    raise ValueError(how)


def memory_text(visits, notes, keep, usual, upto, day):
    """The notes of the question's day as one text, oldest first, up to the question time; short ids v001...
    Every arm gets the same time filter (a memory tool that searches by date), plus, for evidence notes, the
    "usually here" notes that carry the earlier days."""
    lines, ids = [], {}
    for v in visits:
        if (v["day"], v["time"]) > upto or (day is not None and v["day"] != day):
            continue
        sid = f"v{len(ids) + 1:03d}"
        ids[sid] = v
        pic = " [picture kept]" if v["id"] in keep else ""
        head = f"{sid} day {v['day']} {C.hhmm(v['time'])} | {v['place']}{pic} |"
        if notes == "caption":
            lines.append(f"{head} {(v['caption'] or {}).get('things', '?')}")
        else:
            e = v["evidence"] or {}
            ch = "; ".join(f"{c['thing']} {c['change']}" for c in e.get("changes", []))
            things = e.get("things", "?")
            body = f"changes: {ch or 'none'} | now: {things}"
            extra = ""
            if e.get("importance", 0) >= 2:
                extra = f" | importance {e['importance']}: {e.get('why_important', '')} | guess: {e.get('guess', '')}"
            lines.append(f"{head} {body}{extra}")
    text = "YOUR MEMORY (oldest first):\n" + "\n".join(lines)
    if usual:
        text += "\n\nWHAT IS USUALLY ON EACH PLACE (your own notes):\n" + "\n".join(f"- {C.spot_name(s)}: {u}" for s, u in usual.items())
    return text, ids


def schema_for(q):
    base = {"explanation": {"type": "string", "maxLength": 500},
            "evidence": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 8}}}
    if q["kind"] in ("lookback", "unseen"):
        props = {"answer": {"type": "string", "enum": ["yes", "no", "cannot tell"]}}
    elif q["kind"] == "when":
        props = {"answer": {"type": "string", "enum": q["options"]}}
    elif q["kind"] == "happened":
        props = {"who": {"type": "string", "enum": q["options"]}, "doing": {"type": "string", "maxLength": 300}}
    else:
        places = [C.spot_name(s) for s in C.PATROL] + ["somewhere I did not see"]
        props = {"left_behind": {"type": "string", "enum": ["yes", "no", "cannot tell"]},
                 "items": {"type": "array", "maxItems": 4, "items": {"type": "object", "properties": {
                     "thing": {"type": "string", "maxLength": 60}, "place": {"type": "string", "enum": places}},
                     "required": ["thing", "place"]}}}
    props = {**props, **base}
    return {"type": "object", "properties": props, "required": list(props)}


PICK_SCHEMA = {"type": "object", "properties": {
    "look_at": {"type": "array", "maxItems": MAX_LOOK, "items": {"type": "string", "maxLength": 8}},
    "why": {"type": "string", "maxLength": 300}}, "required": ["look_at", "why"]}


def oracle_visits(q, visits):
    vs = [v for v in visits if v["picture"]]
    if q["kind"] == "lookback":
        return [v for v in vs if (v["day"], v["time"], v["spot"]) == (q["day"], q["time"], q["spot"])]
    if q["kind"] == "when":
        return [v for v in vs if v["day"] == q["day"] and v["spot"] == q["spot"]]
    if q["kind"] == "happened":
        return [v for v in vs if v["day"] == q["day"] and v["spot"] == q["spot"] and v["time"] in (q["time"], q["time2"])]
    if q["kind"] == "left":
        return [v for v in vs if (v["day"], v["time"]) == (q["day"], q["time"])][:16]
    return []


def answer_one(q, arm, mem):
    notes, how = ARMS[arm]
    visits = mem["visits"]
    upto = tuple(q["ask_at"])
    ask = (f"QUESTION: {q['question']}\n\nAnswer from your memory. In 'evidence' list the ids (v###) of the notes or "
           f"pictures you used. In 'explanation' say what you saw and when, and how you reached the answer.")
    rec = {"id": q["id"], "arm": arm}
    if how == "oracle":
        vs = oracle_visits(q, visits)
        caps = [f"Picture of the {v['place']} at {C.hhmm(v['time'])} on day {v['day']}:" for v in vs]
        out, info = C.ask(C.PEOPLE_SHEET + "\n\n" + ask, images=[v["picture"] for v in vs], captions=caps,
                          schema=schema_for(q), system=SYSTEM, max_tokens=1200)
        rec.update(answer=out, looked=[v["id"] for v in vs], info={k: info.get(k) for k in ("seconds", "finish", "bad_text")})
        return rec
    keep = kept_pictures(visits, how)
    # the "usually here" note written at the end of a day is only known after 22:00 that day
    u_day = upto[0] if upto[1] >= "2200" else upto[0] - 1
    usual = mem["usual"].get(str(u_day)) if notes == "evidence" else None
    text, ids = memory_text(visits, notes, keep, usual, upto, q["day"])
    prefix = "PEOPLE SHEET:\n" + C.PEOPLE_SHEET + "\n\n" + text
    looked = []
    if keep:
        pick, _ = C.ask(f"QUESTION: {q['question']}\n\nWhich of your kept pictures (marked [picture kept]) should you "
                        f"look at again to answer? Give up to {MAX_LOOK} ids (v###), most useful first, or none.",
                        prefix=prefix, schema=PICK_SCHEMA, system=SYSTEM, max_tokens=400)
        looked = [s for s in (pick or {}).get("look_at", []) if s in ids and ids[s]["id"] in keep][:MAX_LOOK]
        rec["pick"] = pick
    vs = [ids[s] for s in looked]
    caps = [f"{s}: the {v['place']} at {C.hhmm(v['time'])} on day {v['day']}:" for s, v in zip(looked, vs)]
    if arm.endswith("f"):
        looks = []
        for s, v in zip(looked, vs):
            f, _ = C.ask(FRESH_ASK.format(place=v["place"], time=C.hhmm(v["time"]), day=v["day"], question=q["question"]),
                         images=[v["picture"]], schema=FRESH_SCHEMA, system=SYSTEM, max_tokens=300)
            looks.append(f"{s} (the {v['place']} at {C.hhmm(v['time'])} on day {v['day']}): {(f or {}).get('sees', '?')}")
        rec["fresh"] = looks
        fresh = ("FRESH LOOKS (you just looked again at these kept pictures, one at a time, with this question in mind; "
                 "trust them over your older notes when they disagree):\n" + "\n".join(looks) + "\n\n") if looks else ""
        out, info = C.ask(fresh + ask, prefix=prefix, schema=schema_for(q), system=SYSTEM, max_tokens=1200)
    else:
        out, info = C.ask(ask, images=[v["picture"] for v in vs], captions=caps, prefix=prefix, schema=schema_for(q),
                          system=SYSTEM, max_tokens=1200)
    rec.update(answer=out, looked=[v["id"] for v in vs], kept=len(keep), memory_chars=len(text),
               info={k: info.get(k) for k in ("seconds", "finish", "bad_text", "usage")})
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--height", default="1.0")
    ap.add_argument("--arms", default="A,B,C,D,E,F,O")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--memory", default=None)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    mem = json.loads(open(a.memory or C.OUT / f"memory_{a.height}.json").read())
    qs = json.loads((C.OUT / "questions.json").read_text())
    if a.limit:
        qs = qs[::max(1, len(qs) // a.limit)][:a.limit]
    for arm in a.arms.split(","):
        t0 = time.time()
        with ThreadPoolExecutor(a.workers) as pool:
            recs = list(pool.map(lambda q: answer_one(q, arm, mem), qs))
        bad = sum(1 for r in recs if r["answer"] is None)
        C.dump(recs, C.OUT / f"answers_{a.height}_{arm}{a.tag}.json")
        print(f"{time.strftime('%H:%M:%S')} height {a.height} arm {arm}: {len(recs)} answers, {bad} unparsed, "
              f"{time.time() - t0:.0f} s, kept {recs[0].get('kept')}, memory {recs[0].get('memory_chars')} chars, {C.stats()}",
              flush=True)


if __name__ == "__main__":
    main()
