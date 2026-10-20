"""Fixed answers with no memory at all (the audit's question 1): lookback "no", when "cannot tell",
happened = a guess from the room alone ("cooking" in the kitchen), unseen "cannot tell", left "no".
Written as arm Z so score.py judges it like any arm.   python fixed_answers.py"""
import json

import common as C

ROOM = {"kitchen": "cooking", "dining_room": "eating a meal", "living_room": "relaxing with a drink or reading",
        "bathroom_1": "getting washed and ready", "bathroom_2": "getting washed and ready",
        "bedroom_1": "getting dressed or going to bed", "entryway": "coming home or going out",
        "office": "working at the desk", "hallway_2": "playing the piano"}
views = C.load_views("1.0")
recs = []
for q in json.loads((C.OUT / "questions.json").read_text()):
    k = q["kind"]
    if k == "lookback":
        a = {"answer": "no"}
    elif k in ("when", "unseen"):
        a = {"answer": "cannot tell"}
    elif k == "happened":
        a = {"who": "cannot tell", "doing": ROOM.get(views[q["spot"]]["room"], "cleaning up")}
    else:
        a = {"left_behind": "no", "items": []}
    recs.append({"id": q["id"], "arm": "Z", "answer": {**a, "explanation": "fixed answer", "evidence": []}, "looked": []})
for h in ("1.0", "0.4"):
    C.dump(recs, C.OUT / f"answers_{h}_Z.json")
print(len(recs))
