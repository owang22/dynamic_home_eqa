"""Per-class drop at a stage boundary: timetable (and last seen) accuracy on the 5 days before the boundary vs the
first 2 days after, all questions and the moved half. Usage: boundary.py <dir> <boundary_day> [more days]"""
import sys, json, glob, collections, bisect, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)).rsplit('/results', 1)[0], 'src'))
from baselines.patrol.bank import _Truth
D = sys.argv[1]; bounds = [int(x) for x in sys.argv[2:]]
acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))   # (agent, cls, window) -> hits,n
for bank in sorted(glob.glob(f"{D}/banks/*.jsonl")):
    rows = [json.loads(l) for l in open(bank)]; h = rows[0]
    truth = _Truth([r for r in rows if r["kind"] == "truth"]); rounds = sorted({r["t"] for r in rows if r["kind"] == "room_visit"})
    qs = {q["question_id"]: q for q in rows if q["kind"] == "question"}
    def moved(q):
        i = bisect.bisect_right(rounds, q["t_query"]) - 1; tr = rounds[i] if i >= 0 else h["tour_t"]
        return truth.at(q["object_id"], tr) != truth.at(q["object_id"], q["t_query"])
    log = bank.replace("/banks/", "/classical/")
    for l in open(log):
        r = json.loads(l); ag = r["belief"].split("(")[0]
        if ag not in ("TimetableLookup", "LastObservation", "MostFrequentLocation"): continue
        q = qs[r["question_id"]]; d = r["day_index"]
        for b in bounds:
            win = "before" if b - 5 <= d < b else "after" if b <= d < b + 2 else None
            if not win: continue
            for cls in (q["object_class"], "ALL"):
                for half in ("all",) + (("moved",) if moved(q) else ()):
                    a = acc[(ag, cls, half)][(b, win)]; a[0] += r["correct"]; a[1] += 1
for b in bounds:
    print(f"\n=== boundary day {b}: accuracy 5 days before -> first 2 days after (delta), timetable | last seen | most frequent; n = timetable questions before/after")
    print(f"{'class':16s} {'all':>26s} | {'moved half':>26s}")
    rows = []
    for (ag, cls, half), w in acc.items():
        pass
    classes = sorted({k[1] for k in acc}, key=lambda c: -acc[("TimetableLookup", c, "all")][(b, "before")][1])
    for cls in classes:
        cells = []
        for half in ("all", "moved"):
            s = []
            for ag in ("TimetableLookup", "LastObservation", "MostFrequentLocation"):
                w = acc[(ag, cls, half)]; bf, af = w[(b, "before")], w[(b, "after")]
                if bf[1] < 20 or af[1] < 10: s.append("   -   "); continue
                pb, pa = 100 * bf[0] / bf[1], 100 * af[0] / af[1]
                s.append(f"{pb:3.0f}->{pa:3.0f}({pa - pb:+3.0f})")
            cells.append(" ".join(s))
        n = acc[("TimetableLookup", cls, "all")]
        print(f"{cls:16s} {cells[0]} | {cells[1]}   n={n[(b,'before')][1]}/{n[(b,'after')][1]}")
