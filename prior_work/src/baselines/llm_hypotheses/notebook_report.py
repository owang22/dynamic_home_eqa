"""Summarize one notebook-mixture arm folder as Markdown: calls and
seconds per call type per day, population size per day, forks and
retirements, look outcomes, accuracy, and one example fork (parent
beliefs, child beliefs, why).

    python -m baselines.llm_hypotheses.notebook_report <arm folder>
"""

from __future__ import annotations

import gzip
import json
import pathlib
import sys
from typing import Any, Dict, List


def _rows(path: pathlib.Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def report(arm: pathlib.Path) -> str:
    diag = json.loads((arm / "diagnostics.json").read_text()) \
        if (arm / "diagnostics.json").exists() else {}
    nb = diag.get("notebook_mixture") or {}
    calls = _rows(arm / "calls.jsonl")
    looks = _rows(arm / "looks.jsonl")
    events = _rows(arm / "population.jsonl")
    out: List[str] = [f"# notebook mixture — {arm.name}", ""]

    # --- calls and seconds per type per day (from calls.jsonl, so a
    # run that is still going reports too)
    types = ("initial", "question_forecast", "look_forecast", "follow_up",
             "fork", "review")
    per_day: Dict[int, Dict[str, List[float]]] = {}
    for c in calls:
        d = per_day.setdefault(int(c["day"]), {t: [0, 0.0] for t in types})
        d.setdefault(c["type"], [0, 0.0])
        d[c["type"]][0] += 1
        d[c["type"]][1] += float(c.get("seconds") or 0.0)
    out.append("## calls (n / seconds) per call type per day")
    out.append("| day | " + " | ".join(types) + " | total |")
    out.append("|---|" + "---|" * (len(types) + 1))
    for day in sorted(per_day):
        cells = [f"{int(per_day[day][t][0])} / {per_day[day][t][1]:.0f}s"
                 for t in types]
        n = sum(v[0] for v in per_day[day].values())
        s = sum(v[1] for v in per_day[day].values())
        out.append(f"| d{day:02d} | " + " | ".join(cells) + f" | {int(n)} / {s:.0f}s |")
    out.append("")

    # --- population
    births = [e for e in events if e["event"] == "birth"]
    forks = [e for e in events if e["event"] == "fork"]
    retires = [e for e in events if e["event"] == "retire"]
    reviews = [e for e in events if e["event"] == "review"]
    out.append("## population")
    if nb.get("population_size_per_day"):
        out.append("size at the start of each day: " + ", ".join(
            f"d{int(d):02d}={n}" for d, n in sorted(
                nb["population_size_per_day"].items(), key=lambda kv: int(kv[0]))))
    for r in reviews:
        out.append(f"- end of d{r['day']:02d} review: {r['population']} agents, "
                   f"candidate {r['candidate'] or 'none (all at or above 1/N)'}")
    out.append(f"- births {len(births)}, forks {len(forks)} "
               f"(rejected {nb.get('forks_rejected', 0)}), retirements "
               f"{len(retires)}, reviews failed {nb.get('reviews_failed', 0)}, "
               f"scratch truncations {nb.get('scratch_truncated', 0)}, invalid "
               f"forecasts {nb.get('invalid_forecasts', 0)}")
    if events:
        out.append("- final weights: " + ", ".join(
            f"{a} {w:.3f}" for a, w in sorted(events[-1]["weights"].items(),
                                             key=lambda kv: -kv[1])))
    out.append("")

    # --- looks
    out.append("## looks")
    out.append(f"{len(looks)} looks; budget ran out at: " + ", ".join(
        f"d{int(d):02d} {s or 'never'}" for d, s in sorted(
            (nb.get("budget_exhausted_at") or {}).items(),
            key=lambda kv: int(kv[0]))))
    n_person = sum(1 for l in looks if l["kind"] == "resident")
    n_found = sum(1 for l in looks if l["result"])
    out.append(f"receptacle looks {len(looks) - n_person}, person looks "
               f"{n_person}; {n_found} looks found something")
    out.append("")

    # --- accuracy from per_question
    pq = arm / "per_question.jsonl.gz"
    if pq.exists():
        rows = [json.loads(l) for l in gzip.open(pq, "rt")]
        by_day: Dict[int, List[int]] = {}
        for r in rows:
            by_day.setdefault(int(r["day_index"]), []).append(
                int(r["argmax"] == r["truth"]))
        out.append("## accuracy (exact, queried objects)")
        for d, oks in sorted(by_day.items()):
            out.append(f"- d{d:02d}: {sum(oks)}/{len(oks)} = {sum(oks) / len(oks):.2f}")
        total = [o for oks in by_day.values() for o in oks]
        out.append(f"- all: {sum(total)}/{len(total)} = {sum(total) / len(total):.2f}")
        out.append("")

    # --- example fork
    if forks:
        f = forks[0]
        child = (arm / "notebooks" / f["agent"] / "v1.md")
        parent = (arm / "notebooks" / f["parent"] / "v1.md")
        out.append(f"## example fork: {f['parent']} -> {f['agent']}")
        out.append(f"**why:** {f['why']}")
        out.append("")
        out.append(f"### parent {f['parent']} beliefs")
        out.append(parent.read_text().split("\n\n", 2)[-1].strip()
                   if parent.exists() else "(missing)")
        out.append("")
        out.append(f"### child {f['agent']} beliefs")
        out.append(child.read_text().split("\n\n", 2)[-1].strip()
                   if child.exists() else "(missing)")
        out.append("")
    return "\n".join(out)


def main() -> None:
    arm = pathlib.Path(sys.argv[1])
    text = report(arm)
    (arm / "REPORT.md").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
