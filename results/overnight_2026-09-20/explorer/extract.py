"""Compact data for the run explorer page: per-household per-question records for every agent on the
4 h banks, the routine-summary agent's daily notes, and the prompt tails of two arms."""
import json, glob, pathlib, re, bisect, collections
R = pathlib.Path(__file__).resolve().parents[1]
HH = [f"hh_s{i}" for i in range(10)]
OUT = {"households": [], "agents": [], "days": [1, 2, 3, 4, 5, 6, 7], "records": {}, "notes": {}, "prompts": {}, "questions": {}, "locs": {}}
agents_seen = collections.OrderedDict()

def kind(loc):
    return 1 if loc == "ON_PERSON" else 2 if loc == "OUT_OF_HOUSE" else 0

for hh in HH:
    bank = [json.loads(l) for l in open(R / "banks" / f"{hh}_p4.jsonl")]
    h = bank[0]
    truth_t = collections.defaultdict(list)
    for r in bank:
        if r["kind"] == "truth":
            truth_t[r["object_id"]].append(int(r["t"]))
    qs = [r for r in bank if r["kind"] == "question"]
    qindex = {q["question_id"]: i for i, q in enumerate(qs)}
    OUT["questions"][hh] = [{"id": q["question_id"], "obj": q["object_id"], "cls": q["object_class"], "day": q["day_index"],
                             "min": (q["t_query"] % 86400) // 60,
                             "moved": any(q["t_query"] - 86400 < t <= q["t_query"] for t in truth_t[q["object_id"]] if t > 0)} for q in qs]
    day_causes = h["day_causes"]
    events = {int(d): sorted({c.split(":")[0] for c in cs if c.split(":")[0] in ("guest_visit", "sick_day", "rain", "laundry_day", "late_work", "grocery_delivery")}) for d, cs in day_causes.items()}
    cards = h["protocol"]["residents"]
    from baselines.patrol.bank import card_sentences
    OUT["households"].append({"id": hh, "shift": h["shift_days"], "names": {int(k): v for k, v in h["day_names"].items()},
                              "events": {d: e for d, e in events.items() if d >= 1}, "hints": [x["text"] for x in h["hint_messages"]],
                              "residents": [card_sentences(c) for c in cards], "n_objects": len(h["object_classes"]),
                              "rooms": sorted({v for k, v in h["receptacle_rooms"].items() if k != "ON_PERSON"})})
    locs = []
    loc_i = {}
    def li(x):
        if x not in loc_i:
            loc_i[x] = len(locs); locs.append(x)
        return loc_i[x]
    recs = {}
    def add(rows, agent):
        arr = []
        for r in sorted(rows, key=lambda r: qindex[r["question_id"]]):
            arr.append([qindex[r["question_id"]], li(r["truth"]), li(r["answer"]), int(r["correct"]), round(r.get("top_prob", 0), 2),
                        r.get("look_room") or "", int(bool(r.get("found_in_look"))), int(r.get("correct_before_look", r["correct"])),
                        int(bool(r.get("abstain_direct")))])
        recs[agent] = arr
        agents_seen.setdefault(agent, None)
    for look in ("off", "voi"):
        for f in (R / "classical" / f"{hh}_p4_{look}.jsonl", R / "classical" / f"{hh}_p4_{look}_perpetua.jsonl"):
            rows = [json.loads(l) for l in open(f)]
            for b in sorted({r["belief"] for r in rows}):
                add([r for r in rows if r["belief"] == b], f"{b}|look {look}")
    for d in sorted(glob.glob(str(R / "llm" / f"{hh}_p4_*"))):
        p = pathlib.Path(d) / "run_log.jsonl"
        if not p.exists():
            continue
        rows = [json.loads(l) for l in open(p)]
        add(rows, rows[0]["agent"])
        arm = pathlib.Path(d).name.split("_p4_")[1]
        calls = [json.loads(l) for l in open(pathlib.Path(d) / "calls.jsonl")]
        if "summary" in arm:
            OUT["notes"].setdefault(hh, {})[arm] = {int(c["where"].split()[-1]): c["completion"] for c in calls if c["where"].startswith("notes")}
        if arm == "summary_told_lookon" or (hh == "hh_s0" and arm == "naive_told_lookon"):
            pr = {}
            for c in calls:
                if c["where"].startswith("notes"):
                    continue
                qid, after = c["where"].split()[0], "after" in c["where"]
                txt = c["messages"][1]["content"]
                tail = txt.split("\nQuestion:", 1)[1] if "\nQuestion:" in txt else txt
                tail = re.sub(r"Your notes on this home \(written at the end of each day so far\):\n.*?\n\nLast sightings", "Your notes on this home: [the notes of the previous day, shown in the notes panel]\n\nLast sightings", tail, flags=re.S)
                hints = txt.split("Messages from the residents:")[1].split("\n\nQuestion:")[0] if "Messages from the residents:" in txt else ""
                e = pr.setdefault(qid, {})
                e["a2" if after else "a"] = c["completion"]
                e["q2" if after else "q"] = ("Question:" + tail).strip()
                if hints:
                    e["h"] = hints.strip()
            OUT["prompts"].setdefault(hh, {})[arm] = pr
    OUT["records"][hh] = recs
    OUT["locs"][hh] = locs
OUT["agents"] = list(agents_seen)
s = json.dumps(OUT, separators=(",", ":"))
(R / "explorer" / "data.json").write_text(s)
print(len(s) / 1e6, "MB", len(OUT["agents"]), "agents")
