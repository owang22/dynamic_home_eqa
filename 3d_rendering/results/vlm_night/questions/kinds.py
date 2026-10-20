"""Other ways to ask about the rendered home, each scored against what the pictures truly show.

  change     two pictures of one spot, at a patrol time and two hours later.
             "Which of these was put on the <spot> between the two pictures?" Options: the
             added thing (or none), things visible in both pictures, and "nothing new".
             Asked also about a thing taken away. Chance is 1 in the number of options.
  stray      one picture of a spot at a question time with 3+ things in view, at least one of
             them away from its usual place (homes.json, the household's own arrangement).
             "Which of these things has been left here and is normally kept somewhere else?"
             Arms: the vision model from the picture alone (common sense), and the text model
             given the household's usual places and the true list of things (the ceiling).
  usual      "Is the <thing> where it is usually kept?" The robot looks at the usual spot (one
             picture at the question time). Yes when the thing is drawn there (>= FIND_PX, 500 px);
           "not there" items have it elsewhere and 0 px in the picture.
             Half the questions are asked when it is there, half when it is not.
  presence   one picture, "Is there a <type> in this picture?", for things truly in view
             (by pixel size band) and for absent types, to give the recognition curve.

    python kinds.py build ; python kinds.py run ; python kinds.py report
"""
from __future__ import annotations

import collections
import concurrent.futures as cf
import json
import pathlib
import random
import sys

import vlm
from world import FIND_PX, PATROL_TIMES, QUESTION_TIMES, RUN, World

HERE = pathlib.Path(__file__).parent
OUT = HERE / "kinds"
OUT.mkdir(exist_ok=True)
WORKERS = 8
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def tname(W, oid):
    return W.objects[oid]["type"]


def visible(W, day, t, spot, px=FIND_PX):
    return {o for o, n in W.truth(day, t).get(spot, {}).items() if n >= px}


def build(W: World, seed=0):
    rng = random.Random(seed)
    homes = json.loads((RUN / "homes.json").read_text())
    slots = sorted(k for k in W.states if W.rendered(*k) and k[0] >= 2)
    out = {"change": [], "stray": [], "usual": [], "presence": []}
    # change: pairs (patrol time, +2 h)
    for day, t in slots:
        if t not in PATROL_TIMES:
            continue
        t2 = f"{int(t[:2]) + 2:02d}00"
        if not W.rendered(day, t2):
            continue
        for spot in W.views:
            a, b = visible(W, day, t, spot), visible(W, day, t2, spot)
            # a thing counts as added only if it was absent (not merely small) before
            before_any = {o for o, n in W.truth(day, t).get(spot, {}).items() if n > 0}
            after_any = {o for o, n in W.truth(day, t2).get(spot, {}).items() if n > 0}
            added, removed, both = b - before_any, a - after_any, a & b
            types_both = {tname(W, o) for o in both}
            for kind, changed in [("added", added), ("removed", removed)]:
                cands = [o for o in changed if tname(W, o) not in types_both]
                if cands and len(both) >= 1:
                    right = rng.choice(cands)
                    opts = [tname(W, right)] + rng.sample(sorted(types_both), min(3, len(types_both)))
                    out["change"].append({"day": day, "t1": t, "t2": t2, "spot": spot, "kind": kind,
                                          "options": opts, "answer": tname(W, right)})
            if not added and not removed and len(both) >= 2 and rng.random() < 0.08:
                opts = rng.sample(sorted(types_both), min(4, len(types_both)))
                out["change"].append({"day": day, "t1": t, "t2": t2, "spot": spot, "kind": "added",
                                      "options": opts, "answer": "nothing new"})
    # stray
    for day, t in slots:
        if t not in QUESTION_TIMES:
            continue
        for spot in W.views:
            vis = sorted(visible(W, day, t, spot))
            types = collections.Counter(tname(W, o) for o in vis)
            vis = [o for o in vis if types[tname(W, o)] == 1]
            away = [o for o in vis if (homes.get(o) or {}).get("place") not in (None, spot)]
            home_ = [o for o in vis if (homes.get(o) or {}).get("place") == spot]
            if len(vis) >= 3 and away and len(home_) >= 2:
                out["stray"].append({"day": day, "time": t, "spot": spot,
                                     "options": [tname(W, o) for o in vis],
                                     "away": [tname(W, o) for o in away],
                                     "usual": {tname(W, o): homes[o]["place"] for o in vis if (homes.get(o) or {}).get("place")}})
    # usual
    for day, t in slots:
        if t not in QUESTION_TIMES:
            continue
        for oid, h in homes.items():
            spot = (h or {}).get("place")
            if spot not in W.views or W.type_count[tname(W, oid)] > 1:
                continue
            n = W.truth(day, t).get(spot, {}).get(oid, 0)
            o = W.states[(day, t)]["objects"][oid]
            if n >= FIND_PX:
                out["usual"].append({"day": day, "time": t, "spot": spot, "oid": oid, "there": True})
            elif o.get("place") != spot and n == 0:
                out["usual"].append({"day": day, "time": t, "spot": spot, "oid": oid, "there": False})
    # presence
    alltypes = sorted({o["type"] for o in W.objects.values()})
    for day, t in slots:
        for spot in W.views:
            tr = W.truth(day, t).get(spot, {})
            here = {tname(W, o) for o in tr}
            for oid, n in tr.items():
                if W.type_count[tname(W, oid)] == 1 and n >= 30:
                    out["presence"].append({"day": day, "time": t, "spot": spot, "type": tname(W, oid),
                                            "px": n, "there": True, "model": W.verdict.get(tname(W, oid))})
            if tr:
                t_abs = rng.choice([x for x in alltypes if x not in here])
                out["presence"].append({"day": day, "time": t, "spot": spot, "type": t_abs,
                                        "px": 0, "there": False, "model": W.verdict.get(t_abs)})
    # sample down
    caps = {"change": 240, "stray": 150, "usual": 300, "presence": 900}
    for k in out:
        pool = out[k]
        if k == "usual":
            yes = [q for q in pool if q["there"]]
            no = [q for q in pool if not q["there"]]
            pool = rng.sample(yes, min(len(yes), caps[k] // 2)) + rng.sample(no, min(len(no), caps[k] // 2))
        elif k == "presence":
            yes = [q for q in pool if q["there"]]
            no = [q for q in pool if not q["there"]]
            pool = rng.sample(yes, min(len(yes), 600)) + rng.sample(no, min(len(no), 300))
        elif k == "change":
            nothing = [q for q in pool if q["answer"] == "nothing new"]
            rest = [q for q in pool if q["answer"] != "nothing new"]
            pool = rng.sample(rest, min(len(rest), 200)) + rng.sample(nothing, min(len(nothing), 40))
        else:
            pool = rng.sample(pool, min(len(pool), caps[k]))
        print(f"{k}: {len(out[k])} possible, {len(pool)} kept")
        out[k] = pool
    (OUT / "questions.json").write_text(json.dumps(out, indent=1))


def mc(options, rng):
    opts = list(options)
    rng.shuffle(opts)
    return opts


def ask_change(W, q):
    rng = random.Random(f"{q['day']}{q['t1']}{q['spot']}{q['kind']}")
    opts = mc(q["options"], rng) + ["nothing new" if q["kind"] == "added" else "nothing taken away"]
    if q["answer"] == "nothing new" and q["kind"] == "added":
        pass
    spot = W.views[q["spot"]]["spot_name"]
    verb = "put on" if q["kind"] == "added" else "taken off"
    prompt = (f"These two pictures show the {spot}, the first at {q['t1'][:2]}:00 and the second at "
              f"{q['t2'][:2]}:00 the same day, from the same place. Which of these things was {verb} "
              f"the {spot.split(' (')[0]} between the two pictures?\n" +
              "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(opts)) +
              "\nAnswer with the letter only.")
    pics = [W.picture(q["day"], q["t1"], q["spot"]), W.picture(q["day"], q["t2"], q["spot"])]
    letter = vlm.choice(prompt, LETTERS[:len(opts)], pics, captions=[f"{q['t1'][:2]}:00", f"{q['t2'][:2]}:00"])
    chosen = opts[LETTERS.index(letter)] if letter else None
    right = q["answer"] if q["answer"] != "nothing new" else opts[-1]
    return {"chosen": chosen, "right": chosen == right, "n_options": len(opts)}


def ask_stray(W, q, arm):
    rng = random.Random(f"{q['day']}{q['time']}{q['spot']}")
    opts = mc(q["options"], rng)
    spot = W.views[q["spot"]]["spot_name"]
    listing = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(opts))
    if arm == "picture":
        prompt = (f"This picture shows the {spot} in a home. These things are on it:\n{listing}\n"
                  "Which one has most likely been left here by someone and is normally kept "
                  "somewhere else in the home? Answer with the letter only.")
        letter = vlm.choice(prompt, LETTERS[:len(opts)], [W.picture(q["day"], q["time"], q["spot"])])
    else:
        usual = "\n".join(f"- {t}: usually kept on/in the {W.views.get(p, {}).get('spot_name') or p.replace('_', ' ')}"
                          for t, p in q["usual"].items())
        prompt = (f"In this home, things are usually kept here:\n{usual}\n\nRight now these things "
                  f"are on the {spot}:\n{listing}\nWhich one has been left here and is normally "
                  "kept somewhere else? Answer with the letter only.")
        letter = vlm.choice(prompt, LETTERS[:len(opts)])
    chosen = opts[LETTERS.index(letter)] if letter else None
    return {"chosen": chosen, "right": chosen in q["away"], "n_options": len(opts),
            "chance": len(q["away"]) / len(opts)}


def ask_usual(W, q):
    t = tname(W, q["oid"])
    spot = W.views[q["spot"]]["spot_name"]
    prompt = (f"The {t} is usually kept on the {spot}. This picture of it was just taken. "
              f"Is the {t} there now? Answer yes or no.")
    said = bool(vlm.yes_no(prompt, [W.picture(q["day"], q["time"], q["spot"])]))
    return {"said": said, "right": said == q["there"]}


def ask_presence(W, q):
    spot = W.views[q["spot"]]["spot_name"]
    prompt = f"This picture shows the {spot}. Is there a {q['type']} on it? Answer yes or no."
    said = bool(vlm.yes_no(prompt, [W.picture(q["day"], q["time"], q["spot"])]))
    return {"said": said, "right": said == q["there"]}


def run(W):
    qs = json.loads((OUT / "questions.json").read_text())
    res = {}
    jobs = [("change", q, lambda q: ask_change(W, q)) for q in qs["change"]] + \
           [("stray:picture", q, lambda q: ask_stray(W, q, "picture")) for q in qs["stray"]] + \
           [("stray:usual places", q, lambda q: ask_stray(W, q, "usual places")) for q in qs["stray"]] + \
           [("usual", q, lambda q: ask_usual(W, q)) for q in qs["usual"]] + \
           [("presence", q, lambda q: ask_presence(W, q)) for q in qs["presence"]]
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        outs = list(ex.map(lambda j: (j[0], j[1], j[2](j[1])), jobs))
    for kind, q, r in outs:
        res.setdefault(kind, []).append(dict(q, **r))
    (OUT / "results.json").write_text(json.dumps(res, indent=1))
    report()


def report():
    res = json.loads((OUT / "results.json").read_text())
    lines = []
    for kind, rows in res.items():
        n, right = len(rows), sum(r["right"] for r in rows)
        line = f"{kind}: {right}/{n} right ({100*right/max(n,1):.0f}%)"
        if kind == "change":
            chance = sum(1 / r["n_options"] for r in rows) / n
            for sub in ["added", "removed"]:
                rs = [r for r in rows if r["kind"] == sub and r["answer"] != "nothing new"]
                if rs:
                    line += f"; {sub}: {sum(r['right'] for r in rs)}/{len(rs)}"
            rs = [r for r in rows if r["answer"] == "nothing new"]
            line += f"; no change: {sum(r['right'] for r in rs)}/{len(rs)}; chance {100*chance:.0f}%"
        if kind.startswith("stray"):
            chance = sum(r["chance"] for r in rows) / n
            line += f"; chance {100*chance:.0f}%"
        if kind in ("usual", "presence"):
            yes = [r for r in rows if r["there"]]
            no = [r for r in rows if not r["there"]]
            line += (f"; said yes when there {sum(r['said'] for r in yes)}/{len(yes)}, "
                     f"said yes when not {sum(r['said'] for r in no)}/{len(no)}")
        if kind == "presence":
            for lo, hi in [(30, 300), (300, 1000), (1000, 3000), (3000, 10**9)]:
                rs = [r for r in rows if r["there"] and lo <= r["px"] < hi]
                if rs:
                    line += f"\n    {lo}-{hi if hi < 10**9 else '...'} px: seen {sum(r['said'] for r in rs)}/{len(rs)}"
            for m in ["right", "near"]:
                rs = [r for r in rows if r["there"] and r.get("model") == m]
                if rs:
                    line += f"\n    model {m}: seen {sum(r['said'] for r in rs)}/{len(rs)}"
        lines.append(line)
    text = "\n".join(lines)
    (OUT / "summary.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    W = World()
    {"build": lambda: build(W), "run": lambda: run(W), "report": report}[sys.argv[1]]()
