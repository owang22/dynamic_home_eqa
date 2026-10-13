"""Where-is questions answered by searching the rendered home, household A.

The robot patrols a third of the rooms at 08, 12, 16 and 20 h and keeps notes of what it
saw on each piece of furniture. At 10, 14, 18 and 22 h it is asked where a thing is and may
look at up to 8 pieces of furniture; each look shows the pictures of that furniture's open
spots at the question time. It stops at the first look where it judges the thing is there.

Two things are varied separately, so the loss can be put where it happens:
  notes   truth: every thing with >= NOTE_PX pixels in a patrol picture, by its type name
          vlm:   the vision model's own list of what it sees in each patrol picture
  judge   truth: the look succeeds when the thing has >= NOTE_PX pixels in the pictures
          vlm:   the vision model is shown the pictures and asked whether the thing is there
and the order of looks comes from
  nearest      no memory, nearest furniture not yet looked at (from the entrance)
  last seen    where the notes last had it, then nearest   (truth notes only)
  most often   furniture by how often the notes had it, then nearest   (truth notes only)
  llm          the model reads the last 7 days of notes and ranks up to 8 pieces of furniture

Questions name a thing by its type ("Where is the hand cream?") and accept any object of
that type; only types with at most 2 objects in the house are asked. A question is asked only
when the thing covers >= FIND_PX pixels in some picture at the question time, so every
question can be answered by looking.

    python search.py build      writes questions.json
    python search.py captions   captions every patrol picture (vlm notes)
    python search.py run ARM... e.g. 'llm:truth:truth' 'llm:vlm:vlm' 'last seen:truth:vlm'
    python search.py report
"""
from __future__ import annotations

import collections
import concurrent.futures as cf
import json
import math
import pathlib
import random
import sys

import vlm
from world import FIND_PX, NOTE_PX, QUESTION_TIMES, World

HERE = pathlib.Path(__file__).parent
OUT = HERE / "search"
OUT.mkdir(exist_ok=True)
SETTLE = 3
MAX_LOOKS = 8
NOTE_DAYS = 7
WORKERS = 8


def article(t):
    return t if t.endswith("s") and not t.endswith("ss") else t


def where_q(t):
    return f"Where {'are' if play_plural(t) else 'is'} the {t}?"


def play_plural(t):
    from lived_home.play import is_plural
    return is_plural(t)


# ----------------------------------------------------------------------------- notes
def truth_notes(W: World, plan):
    """[(day, hhmm, rooms, {fkey: [oids]})]"""
    out = []
    for day, t, rooms in plan:
        if not W.rendered(day, t):
            continue
        seen = W.seen_at(day, t, NOTE_PX)
        out.append((day, t, rooms, {f: sorted(seen.get(f, set())) for f in W.furniture
                                   if W.places[W.furniture[f][0]]["room"] in rooms}))
    return out


def caption_prompt(W, spot):
    return (f"This picture was taken by a home robot looking at the {W.views[spot]['spot_name']}. "
            "List the separate objects you can see lying on or in it (not the furniture itself, "
            "not things built into the room). Use short everyday names, one per line, no "
            "numbering, each kind of object once. If there is nothing on it, write: nothing")


def captions(W: World, plan):
    jobs = []
    for day, t, rooms in plan:
        if not W.rendered(day, t):
            continue
        for f, spots in W.furniture.items():
            if W.places[spots[0]]["room"] in rooms:
                for s in spots:
                    jobs.append((day, t, s))
    path = OUT / "captions.json"
    have = json.loads(path.read_text()) if path.exists() else {}
    todo = [j for j in jobs if f"{j[0]}|{j[1]}|{j[2]}" not in have]
    print(f"{len(jobs)} patrol pictures, {len(todo)} to caption")

    def one(j):
        day, t, s = j
        text, _ = vlm.ask(caption_prompt(W, s), [W.picture(day, t, s)], max_tokens=200)
        items = [x.strip(" -*•.").lower() for x in text.splitlines() if x.strip()]
        items = [x for x in dict.fromkeys(items) if len(x) < 40][:15]   # repeats and loops
        items = [] if items in (["nothing"], []) else [x for x in items if x != "nothing"]
        return f"{day}|{t}|{s}", items
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        for n, (k, items) in enumerate(ex.map(one, todo)):
            have[k] = items
            if n % 200 == 0:
                path.write_text(json.dumps(have))
                print(f"  {n}/{len(todo)}", flush=True)
    path.write_text(json.dumps(have))
    return have


def vlm_notes(W, plan, caps):
    out = []
    for day, t, rooms in plan:
        if not W.rendered(day, t):
            continue
        notes = {}
        for f, spots in W.furniture.items():
            if W.places[spots[0]]["room"] in rooms:
                items = []
                for s in spots:
                    items += caps.get(f"{day}|{t}|{s}", [])
                notes[f] = items
        out.append((day, t, rooms, notes))
    return out


def notes_text(W, notes, before, kind):
    lines = []
    for day, t, rooms, seen in notes:
        if (day, t) >= before or day < before[0] - NOTE_DAYS:
            continue
        lines.append(f"Day {day} {t[:2]}:{t[2:]} patrol, rooms: {', '.join(r.replace('_', ' ') for r in rooms)}")
        for f in sorted(seen):
            things = seen[f]
            if kind == "truth":
                names = [W.objects[o]["type"] for o in things]
            else:
                names = things
            lines.append(f"  {W.fname(f)}: {', '.join(names) if names else 'nothing seen'}")
    return "\n".join(lines)


# ----------------------------------------------------------------------------- questions
def build(W: World, seed=0, n_moved=110, n_same=60, n_never=40):
    rng = random.Random(seed)
    plan = W.patrol_plan()
    notes = truth_notes(W, plan)
    moves = collections.Counter()
    keys = sorted(k for k in W.states if W.rendered(*k))
    for a, b in zip(keys, keys[1:]):
        for oid in W.objects:
            if W.states[a]["objects"][oid].get("place") != W.states[b]["objects"][oid].get("place"):
                moves[oid] += 1
    types = collections.defaultdict(list)
    for oid, o in W.objects.items():
        types[o["type"]].append(oid)
    askable = [t for t, ids in types.items() if len(ids) <= 2 and any(moves[i] >= 2 for i in ids)
               and W.verdict.get(t) != "none"]
    pools = collections.defaultdict(list)
    for day, t in keys:
        if day <= SETTLE or t not in QUESTION_TIMES:
            continue
        seen_now = W.seen_at(day, t, FIND_PX)
        for typ in askable:
            ids = set(types[typ])
            where_now = sorted(f for f, s in seen_now.items() if s & ids)
            if not where_now:
                continue
            last = None
            for nd, nt, rooms, seen in notes:
                if (nd, nt) >= (day, t):
                    break
                for f, oids in seen.items():
                    if set(oids) & ids:
                        last = f
            cat = "never seen" if last is None else ("at last sighting" if last in where_now else "moved since")
            pools[cat].append({"day": day, "time": t, "type": typ, "accept": sorted(ids),
                               "where": where_now, "last_seen": last, "category": cat,
                               "model": W.verdict.get(typ)})
    out = []
    for cat, n in [("moved since", n_moved), ("at last sighting", n_same), ("never seen", n_never)]:
        pool = pools[cat]
        # at most 2 questions per type per category so a few busy types do not dominate
        rng.shuffle(pool)
        per_type, picked = collections.Counter(), []
        for q in pool:
            if per_type[q["type"]] < 2:
                picked.append(q)
                per_type[q["type"]] += 1
            if len(picked) >= n:
                break
        out += picked
        print(f"{cat}: {len(pool)} possible, {len(picked)} picked, {len(per_type)} types")
    out.sort(key=lambda q: (q["day"], q["time"], q["type"]))
    for i, q in enumerate(out):
        q["id"] = i
    (OUT / "questions.json").write_text(json.dumps(out, indent=1))
    return out


# ----------------------------------------------------------------------------- orders
def nearest_order(W, start_xy, exclude=()):
    xz = W.furniture_xz()
    left = [f for f in xz if f not in exclude]
    order, at = [], start_xy
    while left:
        f = min(left, key=lambda k: math.dist(at, xz[k]))
        order.append(f)
        left.remove(f)
        at = xz[f]
    return order


def entry_xy(W):
    xz = W.furniture_xz()
    e = W.spec["layout"]["entry"]
    if e in W.views:
        return xz[W.fkey(e)]
    return next(iter(xz.values()))


def rule_order(W, q, notes, method):
    counts, last = collections.Counter(), None
    ids = set(q["accept"])
    for day, t, rooms, seen in notes:
        if (day, t) >= (q["day"], q["time"]):
            break
        for f, oids in seen.items():
            if set(oids) & ids:
                counts[f] += 1
                last = f
    xz = W.furniture_xz()
    if method == "nearest":
        first = []
    elif method == "last seen":
        first = [last] if last else []
    else:
        first = [f for f, _ in counts.most_common()]
    start = xz[first[-1]] if first else entry_xy(W)
    return (first + nearest_order(W, start, exclude=first))[:MAX_LOOKS]


def llm_order(W, q, notes, kind, think=False):
    names = {W.fname(f): f for f in W.furniture}
    text = notes_text(W, notes, (q["day"], q["time"]), kind)
    prompt = (
        "You are a home robot. You patrol part of the home a few times a day and note what you "
        "see on each piece of furniture. Here are your notes from the past days:\n\n"
        f"{text}\n\n"
        f"It is now day {q['day']}, {q['time'][:2]}:{q['time'][2:]}. Someone asks: "
        f"\"{where_q(q['type'])}\"\n"
        "You can go and look at pieces of furniture one at a time. List up to 8 pieces of "
        "furniture to look at, most likely first. Think about where it was last seen, where it "
        "usually is, and where people would leave it at this time of day. Use the names exactly "
        "as in this list:\n" + "\n".join(sorted(names)))
    schema = {"type": "object", "properties": {"order": {
        "type": "array", "items": {"type": "string", "enum": sorted(names)}, "maxItems": MAX_LOOKS}},
        "required": ["order"]}
    ans, info = vlm.ask(prompt, think=think, schema=schema, max_tokens=8000 if think else 400)
    if think and info.get("finish") == "length":
        # 42 of 174 thinking rankings ran out at 8000 tokens and returned no list; give those more room
        ans, info = vlm.ask(prompt, think=think, schema=schema, max_tokens=30000)
    try:
        order = [names[x] for x in json.loads(ans)["order"]]
    except Exception:  # noqa: BLE001
        order = []
    order = list(dict.fromkeys(order))
    return order[:MAX_LOOKS], info


def pics_order(W, q, plan, caps, max_pics=40):
    """The model sees the most recent patrol pictures themselves (newest first, skipping
    pictures its own caption called empty), up to max_pics, and ranks furniture."""
    names = {W.fname(f): f for f in W.furniture}
    pics, capt = [], []
    for day, t, rooms in sorted(plan, reverse=True):
        if (day, t) >= (q["day"], q["time"]) or not W.rendered(day, t):
            continue
        for f, spots in W.furniture.items():
            if W.places[spots[0]]["room"] not in rooms:
                continue
            for s in spots:
                if caps.get(f"{day}|{t}|{s}"):
                    pics.append(W.picture(day, t, s))
                    capt.append(f"Day {day} {t[:2]}:{t[2:]}, {W.fname(f)}:")
        if len(pics) >= max_pics:
            break
    pics, capt = pics[:max_pics], capt[:max_pics]
    prompt = (
        "You are a home robot. Above are pictures from your most recent patrols, newest first, "
        "each labelled with when it was taken and which piece of furniture it shows. Pictures of "
        "empty furniture are left out.\n\n"
        f"It is now day {q['day']}, {q['time'][:2]}:{q['time'][2:]}. Someone asks: "
        f"\"{where_q(q['type'])}\"\n"
        "List up to 8 pieces of furniture to look at, most likely first. Use the names exactly "
        "as in this list:\n" + "\n".join(sorted(names)))
    schema = {"type": "object", "properties": {"order": {
        "type": "array", "items": {"type": "string", "enum": sorted(names)}, "maxItems": MAX_LOOKS}},
        "required": ["order"]}
    ans, info = vlm.ask(prompt, pics, captions=capt, schema=schema, max_tokens=400)
    try:
        order = [names[x] for x in json.loads(ans)["order"]]
    except Exception:  # noqa: BLE001
        order = []
    return list(dict.fromkeys(order))[:MAX_LOOKS], info


# ----------------------------------------------------------------------------- judges
# A look finds the thing when the thing is in the look's pictures, whatever piece of furniture it
# rests on (audit 2026-10-13: counting only things placed on the looked-at furniture scored a
# backpack plainly visible on the island, seen from the kitchen-floor camera, as a false find).
def judge_truth(W, q, f):
    tr = W.raw_truth(q["day"], q["time"])
    return any(tr.get(s, {}).get(o, 0) >= NOTE_PX for s in W.furniture[f] for o in q["accept"])


def present(W, q, f, px=30):
    tr = W.raw_truth(q["day"], q["time"])
    return any(tr.get(s, {}).get(o, 0) >= px for s in W.furniture[f] for o in q["accept"])


def judge_vlm(W, q, f):
    spots = W.furniture[f]
    pics = [W.picture(q["day"], q["time"], s) for s in spots]
    caps = [f"Picture of the {W.views[s]['spot_name']}:" for s in spots]
    t = q["type"]
    # the same words as judge_bench.py 'strict' (an earlier version ended "Answer yes or no.",
    # which with the forced format made the model say yes far less: audit 2026-10-13)
    prompt = (f"You are a home robot looking for the {t}. Is a {t} visible in "
              f"{'this picture' if len(pics) == 1 else 'any of these pictures'}?")
    return bool(vlm.yes_no(prompt, pics, captions=caps))


def judge_lenient(W, q, f):
    """By name, with the same 'partly hidden' cue as the crop prompt, to separate the crop's
    effect from the wording's."""
    spots = W.furniture[f]
    pics = [W.picture(q["day"], q["time"], s) for s in spots]
    caps = [f"Picture of the {W.views[s]['spot_name']}:" for s in spots]
    t = q["type"]
    prompt = (f"You are a home robot looking for the {t}. Could any object in "
              f"{'this picture' if len(pics) == 1 else 'these pictures'} be the {t}, even if it looks a bit "
              "different from usual or is partly hidden?")
    return bool(vlm.yes_no(prompt, pics, captions=caps))


def judge_ref(W, q, f):
    """Shows the model a close-up of the thing from an earlier picture (as a robot would keep
    from a patrol, or a person would show), else asks by name when it has never been seen."""
    import judge_bench
    it = dict(q, f=f)
    seen_by = {(d, t_, r) for d, t_, rooms in W.patrol_plan() for r in rooms}
    ref, _ = judge_bench.reference_crop(W, it, seen_by=seen_by)   # only from the robot's own patrol pictures
    if ref is None:
        return judge_vlm(W, q, f)
    spots = W.furniture[f]
    pics = [W.picture(q["day"], q["time"], s) for s in spots]
    caps = [f"Picture of the {W.views[s]['spot_name']}:" for s in spots]
    t = q["type"]
    prompt = (f"You are a home robot looking for the {t}. The first picture is a close-up of this "
              f"exact {t}, taken earlier. Is this same {t} visible in "
              f"{'the next picture' if len(pics) == 1 else 'any of the next pictures'}? It may be "
              "seen from another side or partly hidden.")
    return bool(vlm.yes_no(prompt, [ref] + pics, captions=["Close-up taken earlier:"] + caps))


# ----------------------------------------------------------------------------- run
def run_arm(W, qs, arm):
    order_m, notes_kind, judge_kind = arm.split(":")
    plan = W.patrol_plan()
    caps = json.loads((OUT / "captions.json").read_text()) if (OUT / "captions.json").exists() else {}
    if notes_kind == "truth":
        notes = truth_notes(W, plan)
    elif notes_kind == "pics":
        notes = None
    else:
        notes = vlm_notes(W, plan, json.loads((OUT / "captions.json").read_text()))
    judge = {"truth": judge_truth, "vlm": judge_vlm, "lenient": judge_lenient, "ref": judge_ref}[judge_kind]

    def one(q):
        info = None
        if notes_kind == "pics":
            order, info = pics_order(W, q, plan, caps)
            order += [f for f in nearest_order(W, W.furniture_xz()[order[-1]] if order else entry_xy(W), order)]
            order = order[:MAX_LOOKS]
        elif order_m.startswith("llm"):
            order, info = llm_order(W, q, notes, notes_kind, think=order_m == "llm-think")
            order += [f for f in nearest_order(W, W.furniture_xz()[order[-1]] if order else entry_xy(W), order)]
            order = order[:MAX_LOOKS]
        else:
            order = rule_order(W, q, notes, order_m)
        looks, result = [], "not found"
        for f in order:
            yes = judge(W, q, f)
            looks.append({"f": f, "said": yes, "there": present(W, q, f)})
            if yes:
                result = "found" if present(W, q, f) else "false find"
                break
        return {"id": q["id"], "result": result, "looks": len(looks), "trace": looks,
                "order": order, "reasoning": (info or {}).get("reasoning", "")[:1500]}
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        rows = list(ex.map(one, qs))
    path = OUT / f"run_{arm.replace(':', '__').replace(' ', '_')}.json"
    path.write_text(json.dumps(rows, indent=1))
    return rows


def summarise(qs, rows):
    by = {q["id"]: q for q in qs}
    out = {}
    for cat in ["all", "moved since", "at last sighting", "never seen"]:
        rs = [r for r in rows if cat == "all" or by[r["id"]]["category"] == cat]
        if not rs:
            continue
        n = len(rs)
        f1 = sum(r["result"] == "found" and r["looks"] <= 1 for r in rs)
        f3 = sum(r["result"] == "found" and r["looks"] <= 3 for r in rs)
        f8 = sum(r["result"] == "found" for r in rs)
        ff = sum(r["result"] == "false find" for r in rs)
        out[cat] = {"n": n, "found_1": f1, "found_3": f3, "found_8": f8, "false_find": ff}
    return out


def report():
    qs = json.loads((OUT / "questions.json").read_text())
    lines = ["| order : notes : judge | n | found in 1 look | in 3 | in 8 | false find |", "|---|---|---|---|---|---|"]
    res = {}
    for f in sorted(OUT.glob("run_*.json")):
        arm = f.stem[4:].replace("__", " : ").replace("_", " ")
        s = summarise(qs, json.loads(f.read_text()))
        res[arm] = s
        for cat, v in s.items():
            n = v["n"]
            lines.append(f"| {arm} · {cat} | {n} | {v['found_1']} ({100*v['found_1']/n:.0f}%) | "
                         f"{v['found_3']} ({100*v['found_3']/n:.0f}%) | {v['found_8']} ({100*v['found_8']/n:.0f}%) | {v['false_find']} |")
    (OUT / "summary.json").write_text(json.dumps(res, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    W = World()
    cmd = sys.argv[1]
    if cmd == "build":
        build(W)
    elif cmd == "captions":
        captions(W, W.patrol_plan())
    elif cmd == "run":
        qs = json.loads((OUT / "questions.json").read_text())
        for arm in sys.argv[2:]:
            rows = run_arm(W, qs, arm)
            print(arm, json.dumps(summarise(qs, rows)))
    elif cmd == "report":
        report()
