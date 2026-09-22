#!/usr/bin/env python3
"""Extra story data: memory x spell sweep, affected/unaffected on the partial shift, natural-calendar robustness,
planning cost (from the research agent's summary if present)."""
import json, os, sys, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep import summarize, LABEL
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {"sweep": {}, "affected": {}, "planning": None}
for name, d in (("5", "sick5_all"), ("10", "sick10_all_hl"), ("20", "sick20_all"), ("natural10", "sick10_all_natural")):
    if len(glob.glob(f"{ROOT}/{d}/classical/*.jsonl")) >= 10:
        s, L = summarize(f"{ROOT}/{d}"); out["sweep"][name] = {ag: {k: (list(v) if isinstance(v, tuple) else v) for k, v in vals.items()} for ag, vals in s.items()}
# affected vs unaffected (sick10_partial), per agent per stage per group: mean acc, sd, mean conf
import subprocess
from analyze import load, SHORT
d = f"{ROOT}/sick10_partial"; acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0.0]))
for bp in sorted(glob.glob(f"{d}/banks/hh_s*_t03.jsonl")):
    hh = os.path.basename(bp).split("_t03")[0]; rows = [json.loads(l) for l in open(bp)]; h = rows[0]
    stages = {int(k): v for k, v in (h.get("stages") or {}).items()}
    n2i = {r["name"].lower(): r["resident_id"] for r in h["protocol"]["residents"]}
    qs = {r["question_id"]: r for r in rows if r["kind"] == "question"}
    cp = f"{d}/classical/{hh}_t03.jsonl"
    if not os.path.exists(cp): continue
    for l in open(cp):
        r = json.loads(l); q = qs.get(r["question_id"]); ag = SHORT.get(r["belief"])
        if not q or not ag: continue
        grp = "affected" if n2i.get(q["object_id"].rsplit("_", 1)[-1].lower()) == "resident_1" else "unaffected"
        x = acc[ag][(hh, stages.get(q["day_index"], "plain"), grp)]; x[0] += 1; x[1] += int(r["correct"]); x[2] += float(r.get("top_prob", 0))
for ag in acc:
    out["affected"][ag] = {}
    for st in ("lead", "sick", "return"):
        for g in ("affected", "unaffected"):
            vals = [(100 * v[1] / v[0], v[2] / v[0]) for (hh, s, gg), v in acc[ag].items() if s == st and gg == g and v[0]]
            if not vals: continue
            m = sum(a for a, _ in vals) / len(vals); sd = (sum((a - m) ** 2 for a, _ in vals) / max(1, len(vals) - 1)) ** 0.5
            out["affected"][ag][f"{st}_{g}"] = [m, sd, sum(b for _, b in vals) / len(vals)]
# planning summary from the research agent (markdown table) if present
p = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "planning", "sick10_all_summary.md")
if os.path.exists(p): out["planning"] = open(p).read()

# The ASK-RATE-MATCHED planning cost, parsed into numbers so the page can draw it rather than carry typed figures.
# Matching matters: the hedge's raw win was a confidence-scale confound (it already asked 68% of the time on lead
# days), so only a comparison at an equal lead-day ask rate says anything about cost. See NOTES.md 18:20.
pm = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "planning", "sick10_owner_matched25.md")
if os.path.exists(pm):
    rows = {}
    for line in open(pm):
        if not line.startswith("|") or line.startswith("|---") or "agent" in line[:12]:
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 11:
            continue
        try:
            rows[c[0]] = {"threshold": c[1], "lead_ask": c[2], "sick_ask": c[3], "return_ask": c[4],
                          "lead": float(c[5]), "sick": float(c[7]), "return": float(c[9])}
        except ValueError:
            continue
    if rows:
        out["planning_matched"] = {"source": "uq/planning/sick10_owner_matched25.md",
                                   "regime": "one person sick", "matched_ask": 25, "rows": rows}
# MERGE rather than overwrite: story_extra.json is written by several extractors (llm_live_extra.py writes
# llm_live/knowno_live/owner_split_live, gap_extra.py writes gap, shared_state_extra.py and
# affected_windows_extra.py write theirs). This script used to replace the whole file, silently dropping every
# other extractor's work until the next full rebuild -- it cost a page rebuild on 22 Sept to notice.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extra_store import write_keys  # noqa: E402
print(write_keys("story_extra", out))
print("sweep:", list(out["sweep"]), "affected agents:", len(out["affected"]), "planning:", bool(out["planning"]))
