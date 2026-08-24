#!/usr/bin/env python3
"""Task 4 of the hosted-generation pilot: assemble
reports/hosted_pilot/PILOT.md from the run's own records — build logs,
cache records (which carry per-call usage/cost on the hosted path), the
spend ledger, the probe output and the stage timings file. Numbers only,
plus the verdict section; tolerant of a partial run (partial evidence is
the deliverable).

Usage (after run_hosted_pilot.sh, or on whatever partial state exists):
  python src/revamp_v2/hosted_pilot_report.py [--model gpt-5.6-luna]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from dynamic_home_eqa.generation.hosted_spend import SpendGuard  # noqa: E402

QWEN_SLUG = "qwen3.8-27b"
HH = "hh4"


def _tok(usage_list, key):
    return sum(int((u.get("usage") or {}).get(key) or 0)
               for u in usage_list)


def _reasoning_tok(usage_list):
    return sum(int(((u.get("usage") or {}).get("completion_tokens_details")
                    or {}).get("reasoning_tokens") or 0)
               for u in usage_list)


def _cost(usage_list):
    return sum(float(u.get("cost_usd") or 0) for u in usage_list)


def _stage_row(name, usage_list, attempts=None, failures=None, wall=None):
    return {"stage": name, "calls": len(usage_list),
            "attempts": attempts, "failures": failures or [],
            "prompt_tokens": _tok(usage_list, "prompt_tokens"),
            "completion_tokens": _tok(usage_list, "completion_tokens"),
            "reasoning_tokens": _reasoning_tok(usage_list),
            "usd": _cost(usage_list), "wall_s": wall}


def collect_l2(build_log_path: pathlib.Path):
    """Stage rows for calendar / objects / special_events out of the
    build log's per-attempt hosted_usage records."""
    if not build_log_path.exists():
        return [], None
    log = json.loads(build_log_path.read_text())
    per = {"calendar": [], "objects": []}
    fails = {"calendar": [], "objects": []}
    special_usage, special_fails = [], []
    for a in log.get("attempts") or []:
        stage = a.get("stage")
        if stage in per:
            per[stage] += a.get("hosted_usage") or []
            if a.get("failures"):
                fails[stage].append(
                    {"attempt": a.get("attempt"),
                     "failures": [str(f)[:160] for f in a["failures"][:4]]})
        special_usage += a.get("special_hosted_usage") or []
        if a.get("special_failures"):
            special_fails += [str(f)[:160]
                              for f in a["special_failures"][:4]]
    rows = [
        _stage_row("L2 calendar", per["calendar"],
                   attempts=sum(1 for a in log.get("attempts") or []
                                if a.get("stage") == "calendar"),
                   failures=fails["calendar"]),
        _stage_row("L2 objects", per["objects"],
                   attempts=sum(1 for a in log.get("attempts") or []
                                if a.get("stage") == "objects"),
                   failures=fails["objects"]),
        _stage_row("L2 special events", special_usage,
                   failures=special_fails),
    ]
    return rows, log


def collect_story_cache(cache_dir: pathlib.Path):
    """(story_records, bind_records) out of the story cache dir — hosted
    records carry usage/cost; the bind-pass prompt is identifiable by its
    'already bound to:' object lines."""
    story, bind = [], []
    if not cache_dir.is_dir():
        return story, bind
    for p in sorted(cache_dir.glob("*.json")):
        try:
            rec = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if not rec.get("usage"):
            continue                       # local-era record, no usage
        (bind if "already bound to:" in (rec.get("prompt") or "")
         else story).append(rec)
    return story, bind


def read_timings(path: pathlib.Path) -> dict:
    out = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if "\t" in line:
                k, v = line.split("\t", 1)
                try:
                    out[k] = float(v)
                except ValueError:
                    pass
    return out


def panel_row(panel_md: pathlib.Path, hh: str) -> str | None:
    """The hh row (panel labels households hh_004-style; `hh` is hh4)."""
    if not panel_md.exists():
        return None
    n = int("".join(c for c in hh if c.isdigit()))
    for line in panel_md.read_text().splitlines():
        if re.search(rf"\bhh_?0*{n}\b", line):
            return line.strip()
    return None


def panel_header(panel_md: pathlib.Path) -> str | None:
    if panel_md.exists():
        for line in panel_md.read_text().splitlines():
            if line.startswith("| household"):
                return line.strip()
    return None


def qwen_attempts(build_log_path: pathlib.Path):
    if not build_log_path.exists():
        return None
    log = json.loads(build_log_path.read_text())
    per = {}
    for a in log.get("attempts") or []:
        per[a.get("stage")] = per.get(a.get("stage"), 0) + 1
    per["persona"] = len(log.get("persona_attempts") or [])
    return per


def fmt_row(r):
    fail_n = len(r["failures"])
    wall = f"{r['wall_s']:.0f}" if r.get("wall_s") is not None else "—"
    att = r["attempts"] if r.get("attempts") is not None else "—"
    return (f"| {r['stage']} | {r['calls']} | {att} | {fail_n} | "
            f"{r['prompt_tokens']} | {r['completion_tokens']} | "
            f"{r['reasoning_tokens']} | ${r['usd']:.4f} | {wall} |")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--escalation-model", default="gpt-5.6-terra")
    ap.add_argument("--out", type=pathlib.Path,
                    default=REPO_ROOT / "reports" / "hosted_pilot"
                    / "PILOT.md")
    args = ap.parse_args()
    slug = args.model
    profiles = REPO_ROOT / "profiles" / "revamp_v2"
    reports = REPO_ROOT / "reports" / "hosted_pilot"

    rows, build_log = collect_l2(
        profiles / "rule_based" / slug / HH / "build_log.json")
    terra_rows, terra_log = collect_l2(
        profiles / "rule_based" / args.escalation_model / HH
        / "build_log.json")
    story, bind = collect_story_cache(
        pathlib.Path(f"/tmp/dynamic-home-eqa-gen-cache-story-{slug}"))
    rows.append(_stage_row("story calendar (21d)", story))
    rows.append(_stage_row("bind pass", bind))
    timings = read_timings(reports / "timings.txt")
    for r in rows:
        r["wall_s"] = timings.get(r["stage"])

    probe = {}
    probe_path = reports / "schema_compat.json"
    if probe_path.exists():
        probe = json.loads(probe_path.read_text())

    guard = SpendGuard.from_env()
    total_usd = sum(r["usd"] for r in rows)
    snapshot = (build_log or {}).get("hosted", {}).get("model_snapshot") \
        or probe.get("snapshot")

    lines = [
        "# Hosted-generation pilot — " + HH + " on " + slug, "",
        f"Snapshot: `{snapshot}` — spend ledger: {guard.summary()}", "",
        "## Per stage", "",
        "| stage | calls | attempts | failed attempts | prompt tok | "
        "completion tok | (of which reasoning) | $ | wall s |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    lines += [fmt_row(r) for r in rows]
    if terra_rows and terra_log:
        lines += ["", f"### Escalation ({args.escalation_model})", ""]
        lines += ["| stage | calls | attempts | failed attempts | "
                  "prompt tok | completion tok | (of which reasoning) | $ "
                  "| wall s |",
                  "|---|---|---|---|---|---|---|---|---|"]
        lines += [fmt_row(r) for r in terra_rows]
    for r in rows:
        for f in r["failures"]:
            lines += [f"- {r['stage']} failure: `{json.dumps(f)[:300]}`"]
    if timings:
        lines += ["", "### Wall-clock (CLI stages, from timings.txt)", ""]
        lines += [f"- {k}: {v:.0f} s" for k, v in timings.items()]

    lines += ["", "## Extrapolation (x10 households)", "",
              f"- measured {HH} total on {slug}: **${total_usd:.4f}** -> "
              f"x10 ~= **${10 * total_usd:.2f}**"]
    if terra_rows:
        terra_usd = sum(r["usd"] for r in terra_rows)
        lines += [f"- escalated stage on {args.escalation_model}: "
                  f"${terra_usd:.4f} -> x10 ~= ${10 * terra_usd:.2f}"]
    lines += ["", "  (Straight multiplication; hh4 is the 4-resident hard "
              "case, so this is an upper-leaning estimate for the set.)"]

    lines += ["", "## Quality", ""]
    gpt_md = profiles / "story_calendar" / slug / "realism_panel.md"
    qwen_md = profiles / "story_calendar" / QWEN_SLUG / "realism_panel.md"
    header = panel_header(gpt_md) or panel_header(qwen_md)
    gpt_panel = panel_row(gpt_md, HH)
    qwen_panel = panel_row(qwen_md, HH)
    if header:
        sep = "|" + "---|" * (header.count("|") - 1)
        lines += ["| model " + header, "|---" + sep,
                  f"| {slug} " + (gpt_panel or "| (not run) |"),
                  f"| {QWEN_SLUG} " + (qwen_panel or "| (not found) |"),
                  ""]
    else:
        lines += [f"- realism panel {HH} ({slug}): "
                  f"{gpt_panel or '(not run)'}",
                  f"- realism panel {HH} ({QWEN_SLUG}): "
                  f"{qwen_panel or '(not found)'}"]
    qa = qwen_attempts(
        profiles / "rule_based" / QWEN_SLUG / HH / "build_log.json")
    ga = {r["stage"]: r["attempts"] for r in rows
          if r.get("attempts") is not None}
    lines += ["- attempt burn per stage (legend: attempt burn is the "
              "model-quality signal here — a model that needs more "
              "resamples to satisfy the same contracts is the weaker "
              "generator for THIS pipeline, whatever its benchmarks say):",
              f"  - {slug}: {ga}",
              f"  - {QWEN_SLUG}: {qa or '(no build log)'}"]

    lines += ["", "## Caveats", "",
              "- hosted `seed` is best-effort: sent (it improves "
              "stability) but not a determinism guarantee — the "
              "ResponseCache is the source of truth for reproducing this "
              "run.",
              "- the model alias is pinned to the snapshot above from the "
              "first response; a mid-run change aborts. NOTE: the API "
              "echoes the ALIAS itself in the response `model` field "
              "(every cached record says `gpt-5.6-luna`, no dated id), so "
              "the pin detects mid-run changes but cannot name a dated "
              "snapshot — replay-level reproducibility rides the "
              "ResponseCache alone.",
              "- sampling params (`temperature`/`top_p`) pass through "
              "unchanged (probed accepted — see the behavior probes in "
              "schema_compat.md); `reasoning_effort: minimal` no longer "
              "exists on gpt-5.6 and maps to its successor `none`.",
              ]
    if probe:
        for row in probe.get("rows") or []:
            if row.get("removals"):
                kws = sorted({r.rsplit(": ", 1)[1]
                              for r in row["removals"]})
                lines.append(f"- schema `{row['name']}` lost to the "
                             f"transform: {', '.join(kws)} (coverage in "
                             f"schema_compat.md)")

    lines += ["", "## Verdict", "",
              "(per stage: works as-is / works with transform / needs "
              f"{args.escalation_model} / blocked)", ""]
    probe_by = {r["name"]: r for r in (probe.get("rows") or [])}

    def verdict(stage, probe_name, ok, escalated=False):
        if not ok:
            return "blocked (see failures above)"
        if escalated:
            return f"needs {args.escalation_model}"
        row = probe_by.get(probe_name)
        if row is None:
            return "works as-is (probe missing?)"
        return ("works as-is" if row["raw"]["accepted"]
                else "works with transform")

    program_ok = bool(build_log) and \
        build_log.get("accepted_attempt") is not None
    escalated = bool(terra_log) and \
        (terra_log or {}).get("accepted_attempt") is not None and \
        not program_ok
    story_meta_path = (profiles / "story_calendar" / slug / HH
                       / "timeline_seed0" / "meta.json")
    story_ok = story_meta_path.exists()
    lines += [
        f"- L2 calendar: {verdict('L2', 'l2_calendar', program_ok or escalated, escalated)}",
        f"- L2 objects: {verdict('L2', 'l2_objects', program_ok or escalated, escalated)}",
        f"- L2 special events: {verdict('L2', 'l2_special_events', program_ok or escalated, escalated)}",
        f"- story calendar: {verdict('story', 'story_day', story_ok)}",
        f"- bind pass: {verdict('bind', 'bind_pass', story_ok)}",
        "",
        "(Auto-derived from the run records; edit only with evidence.)",
    ]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
