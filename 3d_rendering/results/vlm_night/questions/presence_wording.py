"""Same 900 presence questions as kinds.py, three wordings, to see how much of the low
'yes when there' rate is the model's caution about exact names rather than seeing.

  strict    (kinds.py) "Is there a <type> on it? Answer yes or no."
  lenient   "Could any object on it be a <type>, even if it looks a bit different or is
             partly hidden? Answer yes or no."
  list      the model first lists what is on the spot, then answers the strict question
            in the same reply (JSON {"objects": [...], "answer": "yes"|"no"})
"""
import concurrent.futures as cf, json, pathlib, sys
import vlm
from world import World
HERE = pathlib.Path(__file__).parent
W = World()
qs = json.loads((HERE / "kinds/questions.json").read_text())["presence"]

def ask(q, how):
    spot = W.views[q["spot"]]["spot_name"]
    pic = [W.picture(q["day"], q["time"], q["spot"])]
    if how == "lenient":
        p = (f"This picture shows the {spot}. Could any object on it be a {q['type']}, even if it "
             "looks a bit different from usual or is partly hidden? Answer yes or no.")
        return bool(vlm.yes_no(p, pic))
    p = (f"This picture shows the {spot}. First list the objects on it, then say whether there is "
         f"a {q['type']} on it.")
    schema = {"type": "object", "properties": {"objects": {"type": "array", "items": {"type": "string"}, "maxItems": 15},
              "answer": {"type": "string", "enum": ["yes", "no"]}}, "required": ["objects", "answer"]}
    a, _ = vlm.ask(p, pic, schema=schema, max_tokens=300)
    try:
        return json.loads(a)["answer"] == "yes"
    except Exception:
        return False

out = {}
for how in ["lenient", "list"]:
    with cf.ThreadPoolExecutor(8) as ex:
        said = list(ex.map(lambda q: ask(q, how), qs))
    yes = [s for s, q in zip(said, qs) if q["there"]]
    no = [s for s, q in zip(said, qs) if not q["there"]]
    bands = {}
    for lo, hi in [(30, 500), (500, 3000), (3000, 10**9)]:
        b = [s for s, q in zip(said, qs) if q["there"] and lo <= q["px"] < hi]
        bands[f"{lo}-{hi}"] = f"{sum(b)}/{len(b)}"
    out[how] = {"yes_when_there": f"{sum(yes)}/{len(yes)}", "yes_when_not": f"{sum(no)}/{len(no)}", "bands": bands}
    print(how, out[how], flush=True)
r = json.loads((HERE / "kinds/results.json").read_text())["presence"]
b = {}
for lo, hi in [(30, 500), (500, 3000), (3000, 10**9)]:
    x = [q["said"] for q in r if q["there"] and lo <= q["px"] < hi]
    b[f"{lo}-{hi}"] = f"{sum(x)}/{len(x)}"
out["strict"] = {"yes_when_there": f"{sum(q['said'] for q in r if q['there'])}/{sum(q['there'] for q in r)}",
                 "yes_when_not": f"{sum(q['said'] for q in r if not q['there'])}/{sum(not q['there'] for q in r)}", "bands": b}
print("strict", out["strict"])
(HERE / "kinds/presence_wording.json").write_text(json.dumps(out, indent=1))
