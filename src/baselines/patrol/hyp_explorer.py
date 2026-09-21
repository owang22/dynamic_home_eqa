"""Build the hypothesis explorer page: how the longleaf mixture's documents
gain and lose weight over the week, told vs not told, per household.

    python3 -m baselines.patrol.hyp_explorer --study DIR/heldout/hyp/study --banks DIR/heldout/banks \
        --classical DIR/heldout/classical --naive DIR/heldout/llm --out DIR/hyp_explorer.html

Reads, per household: the arm folders (per_question.jsonl.gz with the
per-question particle weights, diagnostics.json, revisions/*.json), the
bank header (residents, shift days, messages, day causes) and, for the
reference lines, the most-frequent and naive-LLM logs. Everything is
inlined into the template as JSON.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import pathlib
import re
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional

from baselines.patrol.bank import MAJOR_EVENTS
from baselines.patrol.run import spots_only

TEMPLATE = pathlib.Path(__file__).with_name("hyp_explorer_template.html")
ARM_DIR = "passive__longleaf__longleaf_named__{arm}"


def pid(name: str) -> str:
    m = re.search(r"\((p_[0-9a-f]{4})\)", name)
    return m.group(1) if m else name


def load_rows(p: pathlib.Path) -> List[dict]:
    with gzip.open(p, "rt") as fh:
        return [json.loads(l) for l in fh]


def prose_of(markdown: str, limit: int = 1400) -> str:
    body = markdown.split("```")[0]
    body = re.sub(r"^# .*\n", "", body.strip())
    return body.strip()[:limit]


def doc_targets(raw: dict, objects: List[str]) -> Dict[str, list]:
    t = raw.get("targets") or {}
    out = {}
    for k in objects:
        if k in t:
            out[k] = t[k]
        else:
            cls = "class:" + k.rsplit("_", 1)[0]
            if cls in t:
                out[k] = t[cls]
    return out


def household_blob(hh: str, study: pathlib.Path, banks: pathlib.Path, classical: pathlib.Path,
                   naive: pathlib.Path, library_dir: pathlib.Path) -> Optional[dict]:
    bank = banks / f"{hh}_p2.jsonl"
    rows = [json.loads(l) for l in bank.read_text().splitlines() if l.strip()]
    header = rows[0]
    qs = {r["question_id"]: r for r in rows if r["kind"] == "question"}
    arm_dirs = {arm: study / f"{hh}_p2__bank0" / "arms" / "passive" / ARM_DIR.format(arm=arm) for arm in ("told", "nottold")}
    arms = {}
    for arm, d in arm_dirs.items():
        if not (d / "per_question.jsonl.gz").exists():
            continue
        pq = load_rows(d / "per_question.jsonl.gz")
        diag = json.loads((d / "diagnostics.json").read_text())
        revs = []
        for p in sorted((d / "revisions").glob("*.json"), key=lambda p: int(re.search(r"(\d+)\.json$", p.name).group(1))):
            r = json.loads(p.read_text())
            revs.append({"index": r.get("call_index"), "day": r.get("day"), "trigger": r.get("trigger"),
                         "n_valid": r.get("n_valid"), "outcome": r.get("outcome"),
                         "seconds": r.get("generation_seconds"), "revive": r.get("revive", []),
                         "dropped_n": len(r.get("dropped", []) or []), "problems": r.get("problems", [])})
        arms[arm] = {"pq": pq, "diag": diag, "revs": revs}
    if not arms:
        return None
    # documents: union over arms (initial library + revisions)
    docs: Dict[str, dict] = {}
    lib_raw = json.loads((library_dir / f"{hh}.json").read_text()) if (library_dir / f"{hh}.json").exists() else {"hypotheses": []}
    for h in lib_raw.get("hypotheses", []):
        docs[h["hypothesis_id"]] = {"id": h["hypothesis_id"], "title": h.get("title", ""), "born": "library",
                                    "born_day": 0, "prose": prose_of(h.get("markdown", "")), "targets": h.get("targets", {}),
                                    "claims": h.get("claims", [])}
    for arm, a in arms.items():
        for lr in a["diag"].get("final_hypotheses", []) or []:
            if not (isinstance(lr, dict) and lr.get("hypothesis_id")):
                continue
            i = lr["hypothesis_id"]
            if i not in docs:
                docs[i] = {"id": i, "title": lr.get("title", ""), "born": "revision", "born_day": None,
                           "prose": lr.get("prose") or prose_of(lr.get("markdown", "")), "targets": lr.get("targets", {}),
                           "claims": lr.get("claims", []), "forked_from": lr.get("forked_from")}
            elif not docs[i]["targets"]:
                docs[i]["targets"] = lr.get("targets", {})
    # per-question series per arm
    qids = [q for q in sorted(qs, key=lambda q: qs[q]["t_query"])]
    series = {}
    for arm, a in arms.items():
        by = {r["question_id"]: r for r in a["pq"]}
        W: Dict[str, List[Optional[float]]] = defaultdict(lambda: [None] * len(qids))
        ans, conf, ok, ess, agree = [], [], [], [], []
        for i, q in enumerate(qids):
            r = by.get(q)
            if r is None:
                ans.append(None); conf.append(None); ok.append(None); ess.append(None); agree.append(None); continue
            dist, _ = spots_only({k: float(v) for k, v in r["dist"].items()})
            a_ = max(dist, key=lambda k: (dist[k], k)) if dist else r["argmax"]
            ans.append(a_); conf.append(round(dist.get(a_, 0.0), 3)); ok.append(None)
            wts = r.get("weights") or {}
            ag = 0.0
            for name, pd in (r.get("particles") or {}).items():
                pdist, _ = spots_only({k: float(v) for k, v in pd.items()})
                if pdist and max(pdist, key=lambda k: (pdist[k], k)) == a_:
                    ag += float(wts.get(name, 0.0))
            agree.append(round(ag, 3))
            ess.append(round(r["ess"], 2) if r.get("ess") is not None else None)
            for name, w in (r.get("weights") or {}).items():
                W[pid(name)][i] = round(w, 4)
        series[arm] = {"answer": ans, "conf": conf, "agree": agree, "ess": ess, "weights": dict(W),
                       "status": a["diag"].get("library", {}).get("status", {}),
                       "revisions": a["revs"], "wall_seconds": a["diag"].get("wall_seconds")}
    # truth from the harness log (same bank): reuse the classical log's truth
    truth = {}
    cl = classical / f"{hh}_p2.jsonl"
    ref = defaultdict(dict)
    if cl.exists():
        for l in cl.read_text().splitlines():
            r = json.loads(l)
            truth[r["question_id"]] = r["truth"]
            if r["belief"].startswith("MostFrequent"):
                ref["most frequent"][r["question_id"]] = (r["answer"], r["top_prob"], r["correct"])
    for arm_dir, label in ((f"{hh}_p2_naive_told_lookoff", "naive told"), (f"{hh}_p2_naive_nottold_lookoff", "naive not told")):
        p = naive / arm_dir / "run_log.jsonl"
        if p.exists():
            for l in p.read_text().splitlines():
                r = json.loads(l)
                ref[label][r["question_id"]] = (r["answer"], r["top_prob"], r["correct"])
    for arm, s in series.items():
        s["correct"] = [None if a is None else (a == truth.get(q)) for a, q in zip(s["answer"], qids)]
    for d in docs.values():
        if d["born_day"] is None:
            firsts = [qs[qids[i]]["day_index"] for s in series.values() for i, w in enumerate(s["weights"].get(d["id"], []))
                      if w is not None]
            d["born_day"] = min(firsts) if firsts else None
    questions = [{"id": q, "day": qs[q]["day_index"], "t": qs[q]["t_query"], "object": qs[q]["object_id"],
                  "moment": qs[q].get("moment", ""), "truth": truth.get(q)} for q in qids]
    refs = {label: [d.get(q) for q in qids] for label, d in ref.items()}
    day_names = {int(k): v for k, v in header["day_names"].items()}
    events = {int(d): [c for c in v if c.split(":")[0] in MAJOR_EVENTS] for d, v in header["day_causes"].items()}
    objects = sorted({q["object"] for q in questions})
    for d in docs.values():
        d["targets"] = doc_targets(d, objects)
    return {"household": hh, "residents": header["protocol"]["residents"], "day_names": day_names,
            "shift_days": header["shift_days"], "messages": header.get("hint_messages", []), "events": events,
            "patrol": header.get("patrol_hours"), "questions": questions, "docs": sorted(docs.values(), key=lambda d: (d["born_day"] if d["born_day"] is not None else 99, d["id"])),
            "arms": series, "refs": refs}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=pathlib.Path, required=True)
    ap.add_argument("--banks", type=pathlib.Path, required=True)
    ap.add_argument("--classical", type=pathlib.Path, required=True)
    ap.add_argument("--naive", type=pathlib.Path, required=True)
    ap.add_argument("--library-dir", type=pathlib.Path,
                    default=pathlib.Path(__file__).resolve().parents[3] / "results/llm_hypotheses/hypotheses/longleaf_named/patrol")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    a = ap.parse_args(argv)
    hhs = sorted({pathlib.Path(p).name.split("_p2__")[0] for p in glob.glob(str(a.study / "*__bank0"))})
    blobs = [b for b in (household_blob(h, a.study, a.banks, a.classical, a.naive, a.library_dir) for h in hhs) if b]
    if not blobs:
        print("no arm outputs found", file=sys.stderr)
        return 1
    html = TEMPLATE.read_text().replace("/*DATA*/null", json.dumps(blobs, separators=(",", ":")))
    a.out.write_text(html)
    print(f"wrote {a.out} ({a.out.stat().st_size / 1e6:.1f} MB, households {[b['household'] for b in blobs]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
