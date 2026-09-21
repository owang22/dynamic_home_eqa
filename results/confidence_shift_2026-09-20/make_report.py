"""Assemble report.md from the summaries, figures and LLM stats.

Protocol dirs (2026-09-21): primary = heldout_fb (nightly round + found-it feedback, configs/frozen_2026-09-21.yaml);
secondary = heldout_p8 (8 h patrol, sealed); tuning sets under tuning/frozen_fb and tuning/frozen_p8.

    cd src && python3 ../results/confidence_shift_2026-09-20/make_report.py
"""
import glob
import json
import pathlib
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parent
SRC = R.parents[1] / "src"
sys.path.insert(0, str(SRC))


def run(*args):
    subprocess.run([sys.executable, "-m", *args], cwd=str(SRC), check=True, stdout=subprocess.DEVNULL)


def section(path: pathlib.Path, start: str, end: str) -> str:
    t = path.read_text()
    i = t.index(start)
    j = t.index(end, i + 1) if end and end in t[i + 1:] else len(t)
    return t[i:j].rstrip()


def main() -> None:
    H = R / "heldout_fb"; LABEL = "t03"
    hh5 = sorted(glob.glob(str(H / "llm" / "*" / "run_log.jsonl")))
    hyp = sorted(glob.glob(str(H / "hyp" / "logs" / "*.jsonl"))) + \
        sorted(glob.glob(str(H / "hyp_v5_message_parity" / "logs" / "*_msg_*.jsonl")))   # v5 told arms, labelled llm_longleaf_msg
    naive_hh = {pathlib.Path(p).parent.name.split(f"_{LABEL}")[0] for p in hh5}
    hyp_hh = {pathlib.Path(p).name.split(f"_{LABEL}")[0] for p in hyp}
    # the main LLM table is over the households that have EVERY agent (naive + mixture); naive-only households get their own table
    llm_hh = sorted(naive_hh & hyp_hh) if hyp_hh else sorted(naive_hh) or [f"hh_s{s}" for s in (10, 11, 12, 13, 14, 18, 19, 25)]
    naive_only = sorted(naive_hh - set(llm_hh))
    hh5 = [p for p in hh5 if pathlib.Path(p).parent.name.split(f"_{LABEL}")[0] in llm_hh]
    # tables and figures
    run("baselines.patrol.confshift", "report", "--logs", str(R / "tuning/frozen_fb/classical/*.jsonl"),
        "--banks", str(R / "tuning/frozen_fb/banks"), "--out", str(R / "tuning/frozen_fb/report_classical"), "--title", "Tuning set (seeds 0-9), classical agents")
    run("baselines.patrol.confshift_figs", "--logs", str(R / "tuning/frozen_fb/classical/*.jsonl"),
        "--banks", str(R / "tuning/frozen_fb/banks"), "--out", str(R / "tuning/frozen_fb/report_classical/figs"))
    run("baselines.patrol.confshift", "report", "--logs", str(H / "classical/*.jsonl"), str(H / "classical_extra/*.jsonl"),
        "--banks", str(H / "banks"), "--out", str(H / "report_classical"), "--title", "Held-out set (seeds 10-29), classical agents")
    run("baselines.patrol.confshift_figs", "--logs", str(H / "classical/*.jsonl"), str(H / "classical_extra/*.jsonl"),
        "--banks", str(H / "banks"), "--out", str(H / "report_classical/figs"))
    extra = [str(H / "classical_extra" / f"{h}_{LABEL}_wweb.jsonl") for h in llm_hh
             if (H / "classical_extra" / f"{h}_{LABEL}_wweb.jsonl").exists()]   # post-freeze honest timetable (tuning_log #46)
    logs = [str(H / "classical" / f"{h}_{LABEL}.jsonl") for h in llm_hh] + extra + hh5 + hyp
    run("baselines.patrol.confshift", "report", "--logs", *logs, "--banks", str(H / "banks"),
        "--out", str(H / "report_llm"), "--title", f"Held-out households {', '.join(llm_hh)}: every agent (found-it feedback protocol)")
    run("baselines.patrol.confshift", "report", "--confidence", "agreement", "--logs", *logs, "--banks", str(H / "banks"),
        "--out", str(H / "report_llm_agreement"), "--title", "Same, confidence = library agreement for the mixture")
    run("baselines.patrol.confshift", "report", "--confidence", "monitored", "--logs", *logs, "--banks", str(H / "banks"),
        "--out", str(H / "report_llm_monitored"), "--title", "Same, confidence = top_prob x own running hit rate on today's feedback")
    run("baselines.patrol.confshift_figs", "--logs", *logs, "--banks", str(H / "banks"), "--out", str(H / "report_llm/figs"))

    S_only = None
    if naive_only:
        only_logs = [str(H / "classical" / f"{h}_{LABEL}.jsonl") for h in naive_only] + \
            sorted(p for h in naive_only for p in glob.glob(str(H / "llm" / f"{h}_{LABEL}_naive_*" / "run_log.jsonl")))
        run("baselines.patrol.confshift", "report", "--logs", *only_logs, "--banks", str(H / "banks"),
            "--out", str(H / "report_naive_only"), "--title", f"Households {', '.join(naive_only)}: naive LLM and classical agents (no mixture run)")
        S_only = H / "report_naive_only/summary.md"
    S_tune = R / "tuning/frozen_fb/report_classical/summary.md"
    S_held = H / "report_classical/summary.md"
    S_llm = H / "report_llm/summary.md"
    S_agree = H / "report_llm_agreement/summary.md"
    S_mon = H / "report_llm_monitored/summary.md"
    sys.path.insert(0, str(R))
    from llm_usage import usage
    stats = ["### Feedback protocol (primary)", "", usage("heldout_fb", "t03"), "",
             "### 8 h patrol protocol (secondary)", "", usage("heldout_p8", "p8")]
    for p in sorted(glob.glob(str(H / "hyp/study/*/arms/passive/*/diagnostics.json"))):
        d = json.loads(pathlib.Path(p).read_text())
        stats.append(f"- mixture arm {pathlib.Path(p).parent.name} ({pathlib.Path(p).parents[3].name}): "
                     f"{d.get('wall_seconds', 0) / 60:.0f} min wall, {len(d.get('elicitor_calls') or [])} elicitor calls.")
    # secondary protocol: the sealed 8 h patrol (classical + naive + mixture told on s10-14)
    P8 = R / "heldout_p8"
    p8_logs = sorted(glob.glob(str(P8 / "classical/hh_s1[0-4]_p8.jsonl"))) + sorted(glob.glob(str(P8 / "llm/*/run_log.jsonl"))) + \
        sorted(glob.glob(str(P8 / "hyp/logs/*.jsonl")))
    run("baselines.patrol.confshift", "report", "--logs", *p8_logs, "--banks", str(P8 / "banks"),
        "--out", str(P8 / "report_llm"), "--title", "8 h patrol protocol (secondary, sealed 2026-09-20), households s10-14")
    run("baselines.patrol.confshift_figs", "--logs", *p8_logs, "--banks", str(P8 / "banks"), "--out", str(P8 / "report_llm/figs"))
    S_p8 = P8 / "report_llm/summary.md"
    findings = (R / "findings.md").read_text() if (R / "findings.md").exists() else ""

    L = ["# Confidence-based shift evaluation, 2026-09-20/21", "",
         "Protocol (frozen 2026-09-21, `configs/frozen_2026-09-21.yaml`): the robot walks through the home on Tuesday "
         "evening, does one full round every night at 03:00, and 10 minutes after every question is told where the "
         "object turned out to be (found-it feedback; an ordinary sighting every agent receives). Questions arise around "
         "what the residents do (64 a day, activity-driven, in-house truths only). Shift days = the weekend plus days "
         "with a guest visit or a sick day; the told arms get one dated message per shift day. Every agent sees the "
         "identical stream, never senses, and answers one in-house spot plus a confidence; score is plain accuracy. "
         "Tuned on seeds 0-9 with the classical agents only; seeds 10-29 are held out. The earlier sealed 8 h-patrol "
         "protocol (`heldout_p8/`) is kept as a secondary section. See `tuning_log.md`, `problems_found.md`, `open_questions.md`.", "",
         "Read the tables in two halves: questions whose object MOVED since the robot's nightly round (about half) are "
         "where learning and the shift live; the STILL half is answered by recency almost by definition.", "",
         findings, "",
         "## Held-out households with every agent (paper figures)", "",
         f"Households {', '.join(llm_hh)} (the LLM agents were run on these; the other held-out households have the classical agents only, below).", "",
         "![fig1](heldout_fb/report_llm/figs/fig1_accuracy_per_day.png)", "",
         "![fig2](heldout_fb/report_llm/figs/fig2_coverage_selective_0.7.png)", "",
         "![fig3](heldout_fb/report_llm/figs/fig3_reliability.png)", "",
         section(S_llm, "## Figure 1", "## Tuning criteria"), "",
         "### Same households, confidence = library agreement for the mixture", "",
         section(S_agree, "## Figure 2 (threshold 0.7)", "## Figure 2 (threshold 0.9)") if S_agree.exists() else "", "",
         "### Same households, confidence = self-monitored (top_prob x the agent's running hit rate on the feedback it has already received today, every agent)", "",
         section(S_mon, "## Questions whose object moved", "## Reliability") if S_mon.exists() else "", "",
         section(S_llm, "## Split by household kind", "## Per household"), "",
         section(S_llm, "## Per household", ""), "",
         *(["### Households with the naive LLM only (" + ", ".join(naive_only) + "; the mixture was not run on them tonight)", "",
            section(S_only, "## Figure 1", "## Figure 2 (threshold 0.5)"), "",
            section(S_only, "## Questions whose object moved", "## Reliability"), ""] if S_only else []),
         "## Held-out set, all 20 households, classical agents", "",
         "![fig1](heldout_fb/report_classical/figs/fig1_accuracy_per_day.png)", "",
         "![fig2](heldout_fb/report_classical/figs/fig2_coverage_selective_0.7.png)", "",
         section(S_held, "## Figure 1", "## Per household"), "",
         "## Tuning set (seeds 0-9), classical agents only", "",
         "![fig1](tuning/frozen_fb/report_classical/figs/fig1_accuracy_per_day.png)", "",
         section(S_tune, "## Figure 1", "## Per household"), "",
         "## Secondary: the sealed 8 h patrol protocol (no feedback), households s10-14", "",
         "Kept because it is what the brief first described; it is where we learned that patrol-only observation makes "
         "recency unbeatable (nothing reaches 12% on moved questions) - see `problems_found.md` #12-16.", "",
         "![fig1](heldout_p8/report_llm/figs/fig1_accuracy_per_day.png)", "",
         section(S_p8, "## Figure 1", "## Figure 2 (threshold 0.5)"), "",
         section(S_p8, "## Questions whose object moved", "## Reliability"), "",
         "## LLM tokens and time (local vLLM Qwen/Qwen3.8-27B; no hosted model was called, spend $0)", "", *stats, ""]
    (R / "report.md").write_text("\n".join(L))
    print("wrote", R / "report.md")


if __name__ == "__main__":
    main()
