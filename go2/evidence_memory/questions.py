"""Build the question set from household A's truth (positions, events, rendered pictures at 1.0 m).

    python questions.py            -> out/questions.json, and a few printed samples per kind

Kinds (DESIGN.md has the reasons):
  lookback   "When you passed <place> at <time> on day D, was there a <thing> there?"  yes / no.
             Yes: a thing on the place, clearly in the picture (>= 300 px) but small there (<= 4000 px),
             so a short description may skip it. No: a thing seen on the same place at another visit,
             absent from this picture and not on the place by the positions.
  when       "On day D, when was the <thing> put on / taken off <place>?"  one patrol interval.
             The thing changed exactly once that day there, and is clearly seen on the side where it is.
  happened   "Between t1 and t2 on day D, things changed on <place>. What was going on, and who?"
             At least 3 things appeared or went; truth is the residents who put down or picked up
             there in the interval and what they were doing (events.json 'do' texts and reasons).
  left       "It is <time> on day D and <person> is out. Did they leave without something they
             usually take?"  Their keys / wallet / main phone / tote or backpack (taken on >= 60% of
             their outings over the 14 days) at home on a patrol place and clearly in the picture.
             Negatives: the person is out with all of those.
  unseen     lookback questions about places the robot never visits: the right answer is "cannot tell".
"""
from __future__ import annotations

import collections
import json
import random


import common as C

RNG = random.Random(19)
USUAL = {"mara": ["keys_brass_house", "wallet_tan_zippered", "phone_black_glass", "tote_bag_olive_canvas"],
         "julian": ["keys_brass_house_and_steel", "wallet_brown_leather_bifold", "phone_black_glass_and_aluminum",
                    "backpack_charcoal_canvas"]}
NAME = {"mara": "Mara", "julian": "Julian"}


# The drawn 3D models often do not look like the household's words ("ochre checked dish towel" is drawn
# as a white towel), so questions name things by type only, and leave out stand-in models and the assets
# the 2026-10-13 VLM night found unrecognisable.
BAD_TYPES = {"wooden tray", "market herbs", "project folder", "dish towel", "paper towels", "parcel", "cloth napkin",
             "tea towels", "kitchen towel"}
STAND_IN = {}


def thing(o):
    return o["type"]


def a_thing(o):
    t = o["type"]
    return f"any {t}" if t.endswith("s") else f"a {t}"


def fair(oid, o):
    return o["type"] not in BAD_TYPES and not STAND_IN.get(oid, False)


def load_all():
    pos, tru = {}, {}
    for d in C.DAYS:
        for t in C.TIMES:
            pos[(d, t)] = C.positions(d, t)
            tru[(d, t)] = C.truth("1.0", d, t)
            for oid, o in tru[(d, t)]["objects"].items():
                STAND_IN[oid] = STAND_IN.get(oid, False) or bool(o.get("model_is_stand_in"))
    return pos, tru


def types_in_picture(tru, d, t, spot):
    pic = tru[(d, t)]["pictures"].get(spot)
    return {o["type"] for o in (pic or {}).get("objects", []) if o["pixels"] > 0}


def px(tru, d, t, spot, oid):
    pic = tru[(d, t)]["pictures"].get(spot)
    if not pic:
        return 0
    for o in pic["objects"]:
        if o["object"] == oid:
            return o["pixels"]
    return 0


def on(pos, d, t, spot, oid):
    return pos[(d, t)]["objects"][oid]["place"] == spot and pos[(d, t)]["objects"][oid].get("reference_kind") != "person"


def lookback(pos, tru, n=50):
    yes, no = [], []
    for d in C.Q_DAYS:
        for t in C.TIMES:
            for s in C.PATROL:
                pic = tru[(d, t)]["pictures"].get(s)
                if not pic:
                    continue
                for o in pic["objects"]:
                    same_type = [x for x in pic["objects"] if x["type"] == o["type"] and x["pixels"] > 0]
                    if o["on_this_spot"] and C.SEEN_PX <= o["pixels"] <= 4000 and fair(o["object"], o) \
                            and len(same_type) == 1:
                        yes.append((d, t, s, o["object"], o["pixels"]))
                ever = {o["object"] for (dd, tt) in tru for o in tru[(dd, tt)]["pictures"].get(s, {}).get("objects", [])
                        if o["on_this_spot"] and o["pixels"] >= C.SEEN_PX}
                for oid in ever:
                    o = pos[(d, t)]["objects"][oid]
                    if px(tru, d, t, s, oid) == 0 and not on(pos, d, t, s, oid) and fair(oid, o) \
                            and o["type"] not in types_in_picture(tru, d, t, s):
                        no.append((d, t, s, oid, 0))
    out = []
    for lst, ans in ((yes, "yes"), (no, "no")):
        RNG.shuffle(lst)
        used = set()
        for d, t, s, oid, p in lst:
            if (d, t, s) in used or len([q for q in out if q["truth"]["answer"] == ans]) >= n // 2:
                continue
            used.add((d, t, s))
            o = pos[(d, t)]["objects"][oid]
            out.append({"kind": "lookback", "day": d, "time": t, "spot": s, "object": oid, "ask_at": (7, "2200"),
                        "question": f"When you passed the {C.spot_name(s)} at {C.hhmm(t)} on day {d}, "
                                    f"was there {a_thing(o)} there?",
                        "truth": {"answer": ans, "pixels": p}})
    return out


def when(pos, tru, n=30):
    cands = []
    for d in C.Q_DAYS:
        for s in C.PATROL:
            for oid in pos[(d, "0800")]["objects"]:
                state = [on(pos, d, t, s, oid) for t in C.TIMES]
                flips = [k for k in range(1, 8) if state[k] != state[k - 1]]
                o = pos[(d, "0800")]["objects"][oid]
                if len(flips) != 1 or not fair(oid, o):
                    continue
                if any(o2["type"] == o["type"] and o2id != oid and on(pos, d, t, s, o2id)
                       for t in C.TIMES for o2id, o2 in pos[(d, t)]["objects"].items()):
                    continue
                k = flips[0]
                where = k if state[k] else k - 1          # the visit where the thing is on the place
                if px(tru, d, C.TIMES[where], s, oid) < C.SEEN_PX:
                    continue
                cands.append((d, s, oid, k, "put on" if state[k] else "taken off"))
    RNG.shuffle(cands)
    out, used = [], collections.Counter()
    for d, s, oid, k, verb in cands:
        if used[(d, s)] >= 2 or len(out) >= n:
            continue
        used[(d, s)] += 1
        o = pos[(d, "0800")]["objects"][oid]
        opts = [f"between {C.hhmm(C.TIMES[i - 1])} and {C.hhmm(C.TIMES[i])}" for i in range(1, 8)]
        out.append({"kind": "when", "day": d, "spot": s, "object": oid, "ask_at": (7, "2200"),
                    "question": f"On day {d}, when was the {thing(o)} {verb} the {C.spot_name(s)}?",
                    "options": opts + ["cannot tell"],
                    "truth": {"answer": opts[k - 1], "verb": verb}})
    return out


def interval_events(d, t1, t2, spot):
    m1, m2 = int(t1[:2]) * 60 + int(t1[2:]), int(t2[:2]) * 60 + int(t2[2:])
    ev = [e for e in C.events(d) if m1 < e["minute"] <= m2]
    # 'to' / 'from' read like "on top <place>" or "next to <object> at <place>": the place is the last word
    touched = [e for e in ev if e["verb"] in ("put_down", "pick_up")
               and spot in ((e["to"] or "").split()[-1:] + (e["from"] or "").split()[-1:])]
    who = sorted({e["resident"] for e in touched})
    doing = [f"{e['time']} {e['resident']}: {e['text']} ({e['why']})" for e in ev
             if e["resident"] in who and e["verb"] == "do" and e.get("text")]
    puts = [f"{e['time']} {e['resident']} {e['verb']} {e['object']} ({e['why']})" for e in touched]
    return who, doing, puts


def happened(pos, tru, n=24):
    cands = []
    for d in C.Q_DAYS:
        for k in range(1, 8):
            t1, t2 = C.TIMES[k - 1], C.TIMES[k]
            for s in C.PATROL:
                a = {o for o, v in pos[(d, t1)]["objects"].items() if on(pos, d, t1, s, o)}
                b = {o for o, v in pos[(d, t2)]["objects"].items() if on(pos, d, t2, s, o)}
                came, went = b - a, a - b
                seen = [o for o in came if px(tru, d, t2, s, o) >= C.SEEN_PX] + \
                       [o for o in went if px(tru, d, t1, s, o) >= C.SEEN_PX]
                if len(seen) < 3:
                    continue
                who, doing, puts = interval_events(d, t1, t2, s)
                if not who or not doing:
                    continue
                cands.append((d, t1, t2, s, sorted(came), sorted(went), who, doing, puts))
    RNG.shuffle(cands)
    out, used = [], collections.Counter()
    for d, t1, t2, s, came, went, who, doing, puts in cands:
        if used[s] >= 3 or len(out) >= n:
            continue
        used[s] += 1
        out.append({"kind": "happened", "day": d, "time": t1, "time2": t2, "spot": s, "ask_at": (7, "2200"),
                    "question": f"Between {C.hhmm(t1)} and {C.hhmm(t2)} on day {d}, several things changed on the "
                                f"{C.spot_name(s)}. What was probably going on there, and who was it?",
                    "options": ["Mara", "Julian", "both", "cannot tell"],
                    "truth": {"who": "both" if len(who) == 2 else NAME[who[0]], "doing": doing[:12],
                              "came": came, "went": went, "puts": puts[:20]}})
    return out


def left(pos, tru, n_pos=16, n_neg=8):
    posq, negq = [], []
    for d in C.Q_DAYS:
        for t in C.TIMES:
            for r in ("mara", "julian"):
                if pos[(d, t)]["people"][r]["room"] != "out_of_house":
                    continue
                home = []
                for oid in USUAL[r]:
                    o = pos[(d, t)]["objects"][oid]
                    if o["room"] == "out_of_house" or o.get("reference_kind") == "person":
                        continue
                    seen = o["place"] in C.PATROL and px(tru, d, t, o["place"], oid) >= C.SEEN_PX
                    home.append({"object": oid, "thing": thing(o), "place": o["place"], "seen_now": seen})
                if any(h["seen_now"] for h in home):
                    posq.append((d, t, r, home))
                elif not home:
                    negq.append((d, t, r, home))
    out = []
    for lst, k in ((posq, n_pos), (negq, n_neg)):
        RNG.shuffle(lst)
        used = set()
        for d, t, r, home in lst:
            if (d, r) in used or sum(1 for q in out if bool(q["truth"]["items"]) == bool(home)) >= k:
                continue
            used.add((d, r))
            out.append({"kind": "left", "day": d, "time": t, "person": r, "ask_at": (d, t),
                        "question": f"It is {C.hhmm(t)} on day {d} and {NAME[r]} is out of the house. Did {NAME[r]} "
                                    f"leave without something they usually take with them? If so, what, and where is it?",
                        "truth": {"left_behind": bool(home), "items": home}})
    # a second pass allows a second question per person-day if there are too few
    return out


def unseen(pos, tru, n=12):
    others = [s for s in C.load_views("1.0") if s not in C.PATROL]
    cands = []
    for d in C.Q_DAYS:
        for t in C.TIMES:
            for s in others:
                for o in tru[(d, t)]["pictures"].get(s, {}).get("objects", []):
                    if o["on_this_spot"] and o["pixels"] >= C.SEEN_PX:
                        cands.append((d, t, s, o["object"]))
    RNG.shuffle(cands)
    out, used = [], set()
    for d, t, s, oid in cands:
        if s in used or len(out) >= n:
            continue
        used.add(s)
        o = pos[(d, t)]["objects"][oid]
        if not fair(oid, o):
            continue
        out.append({"kind": "unseen", "day": d, "time": t, "spot": s, "object": oid, "ask_at": (7, "2200"),
                    "question": f"At {C.hhmm(t)} on day {d}, was there {a_thing(o)} on the {C.spot_name(s)}?",
                    "truth": {"answer": "cannot tell", "really": "yes"}})
    return out


def main():
    pos, tru = load_all()
    qs = lookback(pos, tru) + when(pos, tru) + happened(pos, tru) + left(pos, tru) + unseen(pos, tru)
    for i, q in enumerate(qs):
        q["id"] = f"q{i:03d}_{q['kind']}"
    C.dump(qs, C.OUT / "questions.json")
    print(collections.Counter(q["kind"] for q in qs))
    print(collections.Counter((q["kind"], json.dumps(q["truth"].get("answer", q["truth"].get("left_behind", q["truth"].get("who")))))
                              for q in qs))
    by = collections.defaultdict(list)
    for q in qs:
        by[q["kind"]].append(q)
    for k, lst in by.items():
        for q in lst[:2]:
            print("\n", k, q["id"], q["question"])
            print("   truth:", json.dumps(q["truth"])[:700])


if __name__ == "__main__":
    main()
