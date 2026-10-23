"""Per-tier memory metrics for REPORT.md: judge scores, time, steps, invalid actions, citations, invented sightings."""
import json
import statistics
from pathlib import Path

RES = Path(__file__).resolve().parent / "results"
V = {"agree": 1.0, "partial": 0.5, "disagree": 0.0}
gen = {c["id"]: c for c in json.load(open(RES.parent / "cases_generated.json"))}
out = {}


def tier(name, traces, judges, kind_of):
    J = {j["case"]: j for j in judges}
    T = {t["case"]: t for t in traces}
    ids = [i for i in J if i in T]
    sc = [V[J[i]["verdict"]] for i in ids]
    secs = [T[i]["secs"] for i in ids]
    steps = [len([s for s in T[i].get("steps", T[i].get("calls", [])) if s.get("tool") not in (None, "answer")]) for i in ids]
    invalid = sum(sum(1 for s in T[i].get("steps", []) if s.get("tool") is None) for i in ids)
    m = {"n": len(ids), "score": round(sum(sc) / len(sc), 3), "agree": sc.count(1.0), "partial": sc.count(0.5),
         "disagree": sc.count(0.0), "median_s": round(statistics.median(secs), 1), "mean_tool_calls": round(sum(steps) / len(steps), 1),
         "invalid_actions": invalid}
    if kind_of:
        neg = [i for i in ids if kind_of(i) in ("neg", "trap")]
        pos = [i for i in ids if kind_of(i) in ("find", "attr")]
        m["invented_sightings"] = f"{sum(J[i].get('candidate_says_seen') == 'yes' for i in neg)}/{len(neg)}"
        m["false_not_seen"] = f"{sum(J[i].get('candidate_says_seen') == 'no' for i in pos)}/{len(pos)}"
    return m


for tag in ("8b_v0", "8b_v1", "8b_v2", "27b_v1"):
    out[f"generated {tag}"] = tier(tag, json.load(open(RES / f"generated_{tag}.json")),
                                   json.load(open(RES / f"judge_generated_{tag}.json")), lambda i: gen[i]["kind"])
out["generated opus"] = tier("opus", json.load(open(RES / "opus_generated.json")),
                             json.load(open(RES / "judge_generated_opus.json")), lambda i: gen[i]["kind"])
for tag, f in (("8b_v0", "8b"), ("8b_v1", "8b_v1"), ("8b_v2", "8b_v2"), ("27b_v0", "27b"), ("27b_v1", "27b_v1")):
    out[f"logged {tag}"] = tier(tag, json.load(open(RES / f"memory_{f}.json")), json.load(open(RES / f"judge_memory_{f}.json")), None)
out["logged opus re-run (5)"] = tier("opus", json.load(open(RES / "opus_logged.json")),
                                     json.load(open(RES / "judge_memory_opus_rerun.json")), None)
for k, v in out.items():
    print(f"{k:24s}", json.dumps(v))
(RES / "tier_metrics.json").write_text(json.dumps(out, indent=1))
