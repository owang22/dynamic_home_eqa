"""Score the answers against the truth.

    python score.py --height 1.0 [--arms A,B,C,D,F,O,Z] [--tag ""] [--clean]
(--clean: only the questions validity.py keeps at that height; writes out/scores_<h><tag>_clean.json)

lookback  right when the answer equals yes/no truth ("cannot tell" is wrong: the robot was there).
unseen    right when "cannot tell" (the robot never visits that place).
when      right when the interval equals the true one.
happened  doing: a text-only judge (Qwen, given the residents' records in that room in that time and what was
          put down or picked up there) says whether the answer names the main activity and whether it adds
          something specific and true; right = main activity named. Who is scored on its own (people are
          never seen). (First judge, replaced 14:05: "right / partly / wrong" against the whole-house list
          gave "partly" to nearly everything.)
left      positives: right when left_behind is yes and at least one item that was in a picture at that
          time is named (by kind: keys, wallet, phone, bag) at its true place; negatives: right when no.
Per arm: share right per kind, overall (each kind weighted equally), pictures kept, memory length.
Paired differences between arms are over questions (each question right/wrong in both arms), with
2 standard errors.  Writes out/scores_<height>.json.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as st

import common as C

KIND_WORDS = {"keys": ["key"], "wallet": ["wallet"], "phone": ["phone"], "tote bag": ["tote", "bag"],
              "backpack": ["backpack", "bag"]}

JUDGE_SCHEMA = {"type": "object", "properties": {"why": {"type": "string", "maxLength": 400},
                                                 "main_activity": {"type": "string", "enum": ["yes", "no"]},
                                                 "specific": {"type": "string", "enum": ["yes", "no"]}},
                "required": ["why", "main_activity", "specific"]}
JUDGE_ASK = """A robot was asked what was probably going on at the {place} between {t1} and {t2} on day {day}.
What the residents did in that room in that time (their own records):
{doing}
Things put down or picked up at that place: {puts}

The robot's answer: "{answer}"

1. main_activity: does the answer name the main activity at that place in that time (for example "cooking dinner"
   or "preparing a meal" when they chopped and cooked; "eating" when they ate; "tidying" when they cleared up)?
   An answer that names a different activity, or only says "cannot tell", is no.
2. specific: does it also say something specific that is true (what was cooked, what meal, what was cleared)?
Ignore who it names. Give the reason first."""


def room_doing(q):
    """The true activity, limited to the 'do' records in the same room as the place (the whole-house list
    included unrelated things, such as playing the piano in the hallway)."""
    room = C.load_views("1.0")[q["spot"]]["room"]
    m1 = int(q["time"][:2]) * 60 + int(q["time"][2:])
    m2 = int(q["time2"][:2]) * 60 + int(q["time2"][2:])
    ev = [e for e in C.events(q["day"]) if m1 < e["minute"] <= m2 and e["verb"] == "do" and e.get("text")
          and (e["to"] or "").startswith(room)]
    return [f"{e['time']} {e['resident']}: {e['text']}" for e in ev][:14] or q["truth"]["doing"][:8]


def judge_doing(q, ans):
    if not ans or not ans.get("doing") or ans.get("doing", "").strip().lower() in ("cannot tell", "unclear"):
        return "wrong", "no answer"
    out, _ = C.ask(JUDGE_ASK.format(place=C.spot_name(q["spot"]), t1=C.hhmm(q["time"]), t2=C.hhmm(q["time2"]), day=q["day"],
                                    doing="\n".join(room_doing(q)), puts="; ".join(q["truth"]["puts"]),
                                    answer=ans["doing"]), schema=JUDGE_SCHEMA, max_tokens=500)
    if not out:
        return "wrong", "judge failed"
    v = "right" if out["main_activity"] == "yes" and out["specific"] == "yes" else \
        "partly" if out["main_activity"] == "yes" else "wrong"
    return v, out.get("why", "")


def place_match(name, spot):
    return name == C.spot_name(spot)


def score_one(q, rec):
    a = rec.get("answer") or {}
    k = q["kind"]
    r = {"id": q["id"], "kind": k}
    if k in ("lookback", "unseen", "when"):
        r["right"] = a.get("answer") == q["truth"]["answer"]
        r["said_cannot_tell"] = a.get("answer") == "cannot tell"
    elif k == "happened":
        r["who_right"] = a.get("who") == q["truth"]["who"]
        r["doing"], r["judge_why"] = judge_doing(q, a)
        # people are never in the pictures, so "who" is reported on its own and not part of "right";
        # right = the main activity is named (partly = main activity only, right = also something specific)
        r["right"] = r["doing"] in ("right", "partly")
    elif k == "left":
        if q["truth"]["left_behind"]:
            seen = [i for i in q["truth"]["items"] if i["seen_now"]]
            named = a.get("items") or []
            hit = any(any(w in n["thing"].lower() for w in KIND_WORDS.get(i["thing"], [i["thing"]]))
                      and place_match(n["place"], i["place"]) for i in seen for n in named)
            r["right"] = a.get("left_behind") == "yes" and hit
        else:
            r["right"] = a.get("left_behind") == "no"
    r["looked"] = len(rec.get("looked") or [])
    return r


def paired(xs, ys):
    d = [float(x) - float(y) for x, y in zip(xs, ys)]
    if len(d) < 2:
        return None
    return {"diff": st.mean(d), "two_se": 2 * st.stdev(d) / math.sqrt(len(d)), "n": len(d)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--height", default="1.0")
    ap.add_argument("--arms", default="Z,A,B,Bf,F,C,Cf,E,Ep,D,Df,O")
    ap.add_argument("--tag", default="")
    ap.add_argument("--clean", action="store_true", help="only the questions validity.py marks clean at this height")
    a = ap.parse_args()
    qs = {q["id"]: q for q in json.loads((C.OUT / "questions.json").read_text())}
    if a.clean:
        fl = json.loads((C.OUT / "question_flags.json").read_text())
        qs = {i: q for i, q in qs.items() if fl[i][f"clean_{a.height}"]}
    res, rows = {}, {}
    for arm in a.arms.split(","):
        f = C.OUT / f"answers_{a.height}_{arm}{a.tag}.json"
        if not f.exists():
            continue
        recs = [r for r in json.loads(f.read_text()) if r["id"] in qs]
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(16) as pool:
            rs = list(pool.map(lambda rec: score_one(qs[rec["id"]], rec), recs))
        rows[arm] = {r["id"]: r for r in rs}
        kinds = sorted({r["kind"] for r in rs})
        per = {k: st.mean(float(r["right"]) for r in rs if r["kind"] == k) for k in kinds}
        # "left" has 11 questions and "always no" scores 7/11, so it is read case by case, not in the overall
        main_kinds = [k for k in per if k != "left"]
        res[arm] = {"by_kind": per, "overall_kinds_equal": st.mean(per[k] for k in main_kinds),
                    "overall_note": "mean over lookback, when, happened, unseen (left is read case by case)",
                    "happened_strict": st.mean(float(r.get("doing") == "right") for r in rs if r["kind"] == "happened") if "happened" in kinds else None,
                    "n": len(rs), "kept": recs[0].get("kept"), "memory_chars": st.mean(r.get("memory_chars") or 0 for r in recs),
                    "looked_mean": st.mean(r["looked"] for r in rs),
                    "cannot_tell_on_lookback": st.mean(float(r.get("said_cannot_tell", False)) for r in rs if r["kind"] == "lookback"),
                    "happened_who": st.mean(float(r["who_right"]) for r in rs if r["kind"] == "happened") if "happened" in kinds else None,
                    "happened_doing": {v: sum(1 for r in rs if r.get("doing") == v) for v in ("right", "partly", "wrong")}}
    arms = list(res)
    kinds = sorted({k for arm in arms for k in res[arm]["by_kind"]})
    print(f"height {a.height}{a.tag}{' (clean questions only)' if a.clean else ''}")
    print(f"{'arm':4s} {'overall':>8s} " + " ".join(f"{k:>9s}" for k in kinds) + "   kept  mem_chars  looked")
    for arm in arms:
        x = res[arm]
        print(f"{arm:4s} {x['overall_kinds_equal']:8.3f} " + " ".join(f"{x['by_kind'].get(k, float('nan')):9.3f}" for k in kinds)
              + f"  {x['kept']!s:>5s}  {x['memory_chars']:9.0f}  {x['looked_mean']:.1f}")
    print("\npaired differences over questions (A - B); 'all' leaves out the 11 left-behind questions")
    res["_paired"] = {}
    pairs = [("B", "A"), ("D", "F"), ("F", "A"), ("D", "B"), ("C", "E"), ("C", "D"), ("C", "F"), ("C", "B"), ("O", "D"),
             ("Bf", "B"), ("Cf", "C"), ("Df", "D"), ("Cf", "A"), ("Cf", "Df"), ("Bf", "A"), ("C", "Ep"), ("A", "Z"), ("AR", "A"), ("BfR", "Bf")]
    for x, y in pairs:
        if x in rows and y in rows:
            ids = sorted(i for i in set(rows[x]) & set(rows[y]) if rows[x][i]["kind"] != "left")
            for label, sel in (("all", ids), ("lookback", [i for i in ids if rows[x][i]["kind"] == "lookback"]),
                               ("not lookback", [i for i in ids if rows[x][i]["kind"] != "lookback"])):
                p = paired([rows[x][i]["right"] for i in sel], [rows[y][i]["right"] for i in sel])
                if p:
                    res["_paired"][f"{x}-{y}:{label}"] = p
                    print(f"  {x} - {y} {label:13s} {p['diff']:+.3f} (2 SE {p['two_se']:.3f}, n {p['n']})")
    res["_rows"] = {arm: list(r.values()) for arm, r in rows.items()}
    C.dump(res, C.OUT / f"scores_{a.height}{a.tag}{'_clean' if a.clean else ''}.json")


if __name__ == "__main__":
    main()
