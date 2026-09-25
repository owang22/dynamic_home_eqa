#!/usr/bin/env python3
"""Does how the notes were written change how well they answer?

Reports, for every freeze point, each arm's accuracy at two levels of strictness —
naming the exact shelf, and naming only the room — against that household's own
floor and ceiling, and then the paired within-household difference between the two
ways of writing notes.

Two rules this project learned the hard way:
  the household is the unit of evidence, never the question;
  at the control freeze point the floor is the PREDICTED value, not a bar to beat,
  because the notes have seen only the ordinary fortnight.

    python3 results/self_improve/summarise_the_answers.py
"""
import collections, json, pathlib, statistics, sys

sys.path.insert(0, "src")
from self_improve.frozen_household import FrozenHousehold

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                    else "results/self_improve/frozen_memory_test_v1")
BANKS = pathlib.Path("results/self_improve/runs/illness_v1/banks")

# which days the notes had seen, and which days the questions come from
WINDOWS = {
    "before_anything_changed":      (range(1, 14), range(14, 24), "the floor here is a PREDICTION"),
    "did_it_learn_the_new_routine": (range(1, 14), range(14, 24), "the floor here is a BAR to beat"),
    "did_the_looking_arm_find_it_sooner": (range(1, 14), range(17, 20), "the floor here is a BAR to beat"),
    "did_it_keep_the_old_routine": (range(1, 14), range(29, 32), "the floor here is a BAR to beat"),
}


def room_of(hh, place):
    r = hh.place_room
    return r.get(place) if isinstance(r, dict) else r(place)


def floor_and_ceiling(hh, settled, asked, level):
    """floor: each object's commonest place in the settled window, never updated.
       ceiling: each object's commonest place in the asked window, known perfectly."""
    def commonest(days):
        c = collections.defaultdict(collections.Counter)
        for d in days:
            for q in hh.questions_on_day(d):
                tp = hh.true_place_for_question(q)
                if tp:
                    c[q["object_id"]][tp if level == "place" else room_of(hh, tp)] += 1
        return {o: cc.most_common(1)[0][0] for o, cc in c.items() if cc}

    fl, ce = commonest(settled), commonest(asked)
    qs = [q for d in asked for q in hh.questions_on_day(d)]
    f = c = n = 0
    for q in qs:
        tp = hh.true_place_for_question(q)
        if not tp:
            continue
        truth = tp if level == "place" else room_of(hh, tp)
        n += 1
        f += fl.get(q["object_id"]) == truth
        c += ce.get(q["object_id"]) == truth
    return (f / n, c / n) if n else (None, None)


def main():
    cells = collections.defaultdict(dict)          # freeze point -> household -> arm -> scores
    for f in sorted(ROOT.rglob("held_out_answers.json")):
        d = json.loads(f.read_text())
        fp = f.parent.name
        hh = FrozenHousehold(BANKS / f"{d['household']}.jsonl")
        ans = [a for a in d["answers"] if a.get("answer_place")]
        if not ans:
            continue
        shelf = sum(1 for a in ans if a.get("correct")) / len(ans)
        room = sum(1 for a in ans
                   if room_of(hh, a["answer_place"]) and
                   room_of(hh, a["answer_place"]) == room_of(hh, a["true_place"])) / len(ans)
        arm = "incremental" if "incremental" in d["arm"] else "wholesale"
        cells[fp].setdefault(d["household"], {})[arm] = {
            "shelf": shelf, "room": room, "n": len(ans),
            "budget_bit": d.get("share_of_questions_where_the_budget_bit"),
        }

    if not cells:
        print(f"no answer files under {ROOT} yet")
        return 1

    for fp in sorted(cells):
        settled, asked, note = WINDOWS.get(fp, (range(1, 14), range(14, 24), ""))
        print("=" * 100)
        print(f"FREEZE POINT: {fp.replace('_', ' ')}      {note}")
        print("=" * 100)
        print(f"{'household':12s} {'arm':13s} {'shelf':>7} {'floor':>7} {'ceil':>6} {'of room':>9}   "
              f"{'room':>7} {'floor':>7} {'ceil':>6} {'of room':>9}")
        got = collections.defaultdict(dict)
        for h in sorted(cells[fp]):
            hh = FrozenHousehold(BANKS / f"{h}.jsonl")
            fc = {lv: floor_and_ceiling(hh, settled, asked, lv) for lv in ("place", "room")}
            for arm in ("wholesale", "incremental"):
                s = cells[fp][h].get(arm)
                if not s:
                    continue
                line = f"{h:12s} {arm:13s}"
                for lv, key in (("place", "shelf"), ("room", "room")):
                    fl, ce = fc[lv]
                    share = (s[key] - fl) / (ce - fl) if ce and ce > fl else float("nan")
                    line += (f" {s[key]*100:>6.0f}% {fl*100:>6.0f}% {ce*100:>5.0f}% {share*100:>8.0f}%  ")
                    got[arm].setdefault(key, []).append(s[key] - fl)
                print(line)

        print()
        for key, label in (("shelf", "naming the exact shelf"), ("room", "naming only the room")):
            for arm in ("wholesale", "incremental"):
                v = got[arm].get(key)
                if v:
                    m = statistics.mean(v)
                    se = statistics.stdev(v) / len(v) ** 0.5 if len(v) > 1 else float("nan")
                    print(f"  {label:24s} {arm:12s} {m*100:+6.1f} points above its own floor "
                          f"(standard error {se*100:4.1f}, n={len(v)})")
            # paired difference, only on households where BOTH arms ran
            both = [h for h in cells[fp] if len(cells[fp][h]) == 2]
            if len(both) >= 2:
                ds = [cells[fp][h]["incremental"][key] - cells[fp][h]["wholesale"][key] for h in both]
                m = statistics.mean(ds); se = statistics.stdev(ds) / len(ds) ** 0.5
                bar = "2 standard errors" if len(ds) >= 6 else "bigger than the spread"
                det = abs(m) > 2 * se if len(ds) >= 6 else abs(m) > statistics.stdev(ds)
                print(f"  {label:24s} PAIRED incremental minus wholesale: {m*100:+.1f} points "
                      f"(standard error {se*100:.1f}, n={len(ds)}) "
                      f"{'DETECTED' if det else 'not detected'} at the {bar} bar")
            elif both:
                print(f"  {label:24s} only {len(both)} household has both arms; no paired difference yet")
            else:
                print(f"  {label:24s} no household has both arms yet")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
