"""Summary of the teacher-forced next-action runs: strict (tool + main arg) and lenient (also accepts go_to <the
place> where Opus first called list_places, and release where Opus answered after releasing)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from router import classify  # noqa: E402

P = list(json.loads((HERE / "data" / "places_snapshot.json").read_text()))
cases = {c["id"]: c for c in json.load(open(HERE / "cases_logged.json"))}
out = {}
for tag in sys.argv[1:] or ["8b", "27b"]:
    R = json.load(open(HERE / "results" / f"driving_{tag}.json"))
    rows = []
    for r in R:
        c = cases[r["case"]]
        route = classify(c["text"], P)
        pred = r["pred"] or {}
        lenient = r["arg_match"]
        nxt = c["opus_calls"][r["k"] + 1] if r["k"] + 1 < len(c["opus_calls"]) else None
        if not lenient and r["ref"][0]["tool"] == "list_places" and pred.get("tool") == "go_to" and nxt \
                and nxt["tool"] == "go_to" and (pred.get("args") or {}).get("place") == nxt["args"].get("place"):
            lenient = True
        rows.append({"case": r["case"], "k": r["k"], "route": route.name, "ref": r["ref"][0]["tool"],
                     "pred": pred.get("tool"), "strict": r["arg_match"], "tool": r["tool_match"], "lenient": lenient,
                     "secs": r["secs"]})
    def agg(rs):
        n = len(rs)
        return {"n": n, "tool": sum(x["tool"] for x in rs), "strict": sum(x["strict"] for x in rs),
                "lenient": sum(x["lenient"] for x in rs),
                "median_s": sorted(x["secs"] for x in rs if x["secs"])[len(rs) // 2] if rs else None}
    out[tag] = {"all": agg(rows), "place_route": agg([x for x in rows if x["route"] == "place"]),
                "big_route": agg([x for x in rows if x["route"] != "place"]),
                "first_action": agg([x for x in rows if x["k"] == 0]),
                "stop_positions": agg([x for x in rows if x["ref"] == "stop"]), "rows": rows}
    for k_, v in out[tag].items():
        if k_ != "rows":
            print(tag, k_, v)
(HERE / "results" / "driving_summary.json").write_text(json.dumps(out, indent=1))
