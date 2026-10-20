"""Flag questions that do not test what they claim (from the independent audit, 2026-10-19 14:40).

    python validity.py  -> out/question_flags.json: {id: {"clean_1.0": bool, "clean_0.4": bool, "reasons": [...]}}

Rules:
- smoke: one of the 14 questions used in the smoke test that shaped the prompts.
- lookback no, near match in view: a thing of a similar type is in the picture (thermos asked as "water bottle",
  wine glass asked as "water glass"); a person could fairly say yes.
- unseen, visible elsewhere: the asked thing shows (>= 300 px) in a picture of a place the robot does visit.
- when, re-drawn: on that day at that place the asked thing stayed put across two visits but its drawn size
  changed by more than 2x, or it was on the place but under 300 px: the renderer laid it out again, which
  makes a fake change (the real robot will not have this).
- happened, whole-house truth: no activity record in the place's room, so the judge saw unrelated records.
- left: the truth uses a hidden list of usual belongings, two positives come from a generator slip (Mara
  "leaves with the tote" and never picks it up), and no arm beats always "no": the kind is not valid yet.
- 0.4 m only: lookback yes / when where the thing is under 300 px in the 0.4 m picture that holds the answer.
"""
from __future__ import annotations

import json

import common as C
import score as S

SYN = {"water bottle": {"thermos", "bottle"}, "water glass": {"wine glass", "glass", "drinking glass"},
       "mug": {"cup", "teacup"}, "cup": {"mug"}, "wine glass": {"water glass"}}


def near(asked, other):
    if other == asked:
        return False
    a, o = asked.split(), other.split()
    return other in SYN.get(asked, set()) or a[-1] == o[-1]


def main():
    qs = json.loads((C.OUT / "questions.json").read_text())
    smoke = {q["id"] for q in qs[::max(1, len(qs) // 14)][:14]}
    tru = {h: {} for h in ("1.0", "0.4")}

    def T(h, d, t):
        if (d, t) not in tru[h]:
            tru[h][(d, t)] = C.truth(h, d, t)
        return tru[h][(d, t)]

    def px(h, d, t, spot, oid):
        for o in T(h, d, t)["pictures"].get(spot, {}).get("objects", []):
            if o["object"] == oid:
                return o["pixels"]
        return 0

    flags = {}
    for q in qs:
        r = []
        if q["id"] in smoke:
            r.append("smoke")
        k = q["kind"]
        low = False
        if k == "lookback":
            pic = T("1.0", q["day"], q["time"])["pictures"][q["spot"]]
            asked = C.positions(q["day"], q["time"])["objects"][q["object"]]["type"]
            if q["truth"]["answer"] == "no" and any(near(asked, o["type"]) and o["pixels"] >= C.SEEN_PX for o in pic["objects"]):
                r.append("lookback no, near match in view")
            if q["truth"]["answer"] == "yes" and px("0.4", q["day"], q["time"], q["spot"], q["object"]) < C.SEEN_PX:
                low = True
        elif k == "unseen":
            for s in C.PATROL:
                if px("1.0", q["day"], q["time"], s, q["object"]) >= C.SEEN_PX:
                    r.append(f"unseen, visible in the {s} picture")
                    break
        elif k == "when":
            d, s, oid = q["day"], q["spot"], q["object"]
            pos = [C.positions(d, t)["objects"][oid] for t in C.TIMES]
            on = [p["place"] == s and p.get("reference_kind") != "person" for p in pos]
            p10 = [px("1.0", d, t, s, oid) for t in C.TIMES]
            for i in range(1, 8):
                if on[i] and on[i - 1] and p10[i] and p10[i - 1] and max(p10[i], p10[i - 1]) > 2 * min(p10[i], p10[i - 1]):
                    r.append(f"when, re-drawn {C.TIMES[i - 1]}->{C.TIMES[i]} ({p10[i - 1]} -> {p10[i]} px)")
                    break
            if any(on[i] and p10[i] < C.SEEN_PX for i in range(8)):
                r.append("when, on the place but under 300 px at some visit")
            p04 = [px("0.4", d, t, s, oid) for t in C.TIMES]
            if max(p04[i] for i in range(8) if on[i]) < C.SEEN_PX:
                low = True
        elif k == "happened":
            room = C.load_views("1.0")[q["spot"]]["room"]
            if S.room_doing(q) == q["truth"]["doing"][:8] and not any(x.split(": ", 1)[0] for x in []):
                # room_doing fell back to the whole-house list
                m1 = int(q["time"][:2]) * 60
                m2 = int(q["time2"][:2]) * 60
                if not any(e["verb"] == "do" and e.get("text") and (e["to"] or "").startswith(room)
                           and m1 < e["minute"] <= m2 for e in C.events(q["day"])):
                    r.append("happened, whole-house truth")
        elif k == "left":
            r.append("left, not valid yet")
        flags[q["id"]] = {"reasons": r + (["0.4 m: not visible at 0.4 m"] if low else []),
                          "clean_1.0": not r, "clean_0.4": not r and not low}
    C.dump(flags, C.OUT / "question_flags.json")
    import collections
    print("clean at 1.0 m:", collections.Counter(q["kind"] for q in qs if flags[q["id"]]["clean_1.0"]))
    print("clean at 0.4 m:", collections.Counter(q["kind"] for q in qs if flags[q["id"]]["clean_0.4"]))
    print(collections.Counter(x.split(" (")[0].split(" in the ")[0].split(" ->")[0][:40] for f in flags.values() for x in f["reasons"]))


if __name__ == "__main__":
    main()
