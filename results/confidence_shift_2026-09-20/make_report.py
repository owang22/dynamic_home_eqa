"""Assemble report.md from the summaries, figures and LLM stats.

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
    hh5 = sorted(glob.glob(str(R / "heldout" / "llm" / "*" / "run_log.jsonl")))
    hyp = sorted(glob.glob(str(R / "heldout" / "hyp" / "logs" / "*.jsonl")))
    llm_hh = sorted({pathlib.Path(p).parent.name.split("_p2")[0] for p in hh5} |
                    {pathlib.Path(p).name.split("_p2")[0] for p in hyp})
    # tables and figures
    run("baselines.patrol.confshift", "report", "--logs", str(R / "tuning/frozen/classical/*.jsonl"),
        "--banks", str(R / "tuning/frozen/banks"), "--out", str(R / "tuning/frozen/report_classical"), "--title", "Tuning set (seeds 0-9), classical agents")
    run("baselines.patrol.confshift_figs", "--logs", str(R / "tuning/frozen/classical/*.jsonl"),
        "--banks", str(R / "tuning/frozen/banks"), "--out", str(R / "tuning/frozen/report_classical/figs"))
    run("baselines.patrol.confshift", "report", "--logs", str(R / "heldout/classical/*.jsonl"),
        "--banks", str(R / "heldout/banks"), "--out", str(R / "heldout/report_classical"), "--title", "Held-out set (seeds 10-29), classical agents")
    run("baselines.patrol.confshift_figs", "--logs", str(R / "heldout/classical/*.jsonl"),
        "--banks", str(R / "heldout/banks"), "--out", str(R / "heldout/report_classical/figs"))
    logs = [str(R / "heldout/classical" / f"{h}_p2.jsonl") for h in llm_hh] + hh5 + hyp
    run("baselines.patrol.confshift", "report", "--logs", *logs, "--banks", str(R / "heldout/banks"),
        "--out", str(R / "heldout/report_llm"), "--title", f"Held-out households {', '.join(llm_hh)}: every agent")
    run("baselines.patrol.confshift_figs", "--logs", *logs, "--banks", str(R / "heldout/banks"), "--out", str(R / "heldout/report_llm/figs"))

    S_tune = R / "tuning/frozen/report_classical/summary.md"
    S_held = R / "heldout/report_classical/summary.md"
    S_llm = R / "heldout/report_llm/summary.md"
    naive = json.loads((R / "heldout/llm/llm_stats.json").read_text()) if (R / "heldout/llm/llm_stats.json").exists() else {}
    stats = [f"- naive LLM (10 arms on {len(llm_hh)} households): {naive.get('calls', 0)} calls "
             f"({naive.get('cached', 0)} cache replays), {naive.get('prompt_tokens', 0) / 1e6:.2f} M prompt tokens, "
             f"{naive.get('completion_tokens', 0) / 1e6:.2f} M completion tokens, {naive.get('seconds', 0) / 3600:.1f} h summed call time "
             f"(10 threads in flight), hosted spend $0."]
    for p in sorted(glob.glob(str(SRC.parent / "results/llm_hypotheses/logs/longleaf_named/patrol/hh_s1*_p2.json"))):
        d = json.loads(pathlib.Path(p).read_text())
        stats.append(f"- hypothesis library, {pathlib.Path(p).stem}: {len(d.get('hypotheses', []))} documents, "
                     f"{d.get('generation_seconds', 0) / 60:.0f} min of generation (thinking mode).")
    for p in sorted(glob.glob(str(R / "heldout/hyp/study/*/arms/passive/*/diagnostics.json"))):
        d = json.loads(pathlib.Path(p).read_text())
        stats.append(f"- mixture arm {pathlib.Path(p).parent.name} ({pathlib.Path(p).parents[3].name}): "
                     f"{d.get('wall_seconds', 0) / 60:.0f} min wall, elicitor calls {len(d.get('elicitor_calls', d.get('reask_events', [])) or [])}.")

    L = ["# Confidence-based shift evaluation, 2026-09-20", "",
         "Frozen config: `configs/frozen_2026-09-20.yaml` (patrol every 2 h, activity-driven questions, 64 per day, "
         "sick_day 0.10 and guest_visit 0.10 per weekday, timetable bins 2 h, empty-look suppression off for the pure "
         "classical baselines). Tuned on seeds 0-9 with the classical agents only; seeds 10-29 are held out. Every "
         "agent sees the identical patrol stream, never senses, and answers one in-house spot plus a confidence. "
         "Score is plain accuracy. See `tuning_log.md`, `problems_found.md`, `open_questions.md`.", "",
         "## Held-out households with every agent (paper figures)", "",
         f"Households {', '.join(llm_hh)} (the LLM agents were run on these; the other held-out households have the classical agents only, below).", "",
         "![fig1](heldout/report_llm/figs/fig1_accuracy_per_day.png)", "",
         "![fig2](heldout/report_llm/figs/fig2_coverage_selective_0.7.png)", "",
         "![fig3](heldout/report_llm/figs/fig3_reliability.png)", "",
         section(S_llm, "## Figure 1", "## Tuning criteria"), "",
         section(S_llm, "## Split by household kind", "## Per household"), "",
         section(S_llm, "## Per household", ""), "",
         "## Held-out set, all 20 households, classical agents", "",
         "![fig1](heldout/report_classical/figs/fig1_accuracy_per_day.png)", "",
         "![fig2](heldout/report_classical/figs/fig2_coverage_selective_0.7.png)", "",
         section(S_held, "## Figure 1", "## Per household"), "",
         "## Tuning set (seeds 0-9), classical agents only", "",
         "![fig1](tuning/frozen/report_classical/figs/fig1_accuracy_per_day.png)", "",
         section(S_tune, "## Figure 1", "## Per household"), "",
         "## LLM tokens and time (local vLLM Qwen/Qwen3.8-27B; no hosted model was called)", "", *stats, ""]
    (R / "report.md").write_text("\n".join(L))
    print("wrote", R / "report.md")


if __name__ == "__main__":
    main()
