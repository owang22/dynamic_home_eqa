"""Naive LLM belief floor: a local LLM answers a stratified sample of the
1x-rate questions, scored beside the classical models and the oracle.

The pipeline is split so the GPU work is one offline batch:

  sample    stratified question sample: at most CAP_PER_CELL questions per
            (home, seed, age-of-last-sighting bin); bins with fewer keep
            every question. 28-day banks, the fleet's 1x patrol rate, all
            20 homes, seeds 0 and 1.
  prompts   replay every bank with the LLM belief in collect mode: one
            prompt per distinct cache key, plus the per-question facts
            (truth, age bin, four-case situation) the report needs.
  test      answer ONE prompt and print it with the completion, to look
            at before anything else runs.
  generate  offline vLLM batch in the cu129 venv (``--limit`` for the
            warmup); completions are keyed and resumable.
  warmup    tokens/question, parse-failure rate and the wall-clock
            projection for the rest, from what has been answered so far.
  score     replay every bank again with the completions in the cache,
            beside LastObs, DaytypeMix, Perpetua, the two expiring-
            exclusion LastObs variants and the routine oracle, all on the
            same sampled questions -> scored.csv.gz.
  report    age-bin tables, paired per-home-seed stats, four-case split,
            OUT_OF_HOUSE / ON_PERSON accuracy, the expiring-exclusion
            table, figures, and 100 prompt/completion pairs to read.

Every number in the report is computed on the stratified sample, and
every table and figure says so with its n. Homes are never pooled with
each other in the paired statistics; seeds of a home are.

Usage:
  python -m baselines.llm_floor --stage sample prompts
  python -m baselines.llm_floor --stage test
  python -m baselines.llm_floor --stage generate --limit 200
  python -m baselines.llm_floor --stage warmup
  python -m baselines.llm_floor --stage generate
  python -m baselines.llm_floor --stage score report --workers 40
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import csv
import datetime
import gzip
import json
import logging
import math
import os
import pathlib
import random
import statistics
import subprocess
import sys
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from baselines.bank import JsonlBank
from baselines.beliefs.base import BeliefModel
from baselines.beliefs.llm_belief import (JSON_SCHEMA, LLMBelief,
                                          PromptCache, parse_completion)
from baselines.cli import _derived_rng, git_state
from baselines.household_analysis import (FINE_AGE_EDGES_H, bank_path,
                                          household_meta, select_specs,
                                          timeline_dir, truth_category)
from baselines.household_report import (AGE_LABEL, AGE_ORDER, MIN_N,
                                        wilson)
from baselines.passive_eval import PassiveProtocolConfig, question_ages
from baselines.registry import build_registered_belief
from baselines.routine_oracle import ORACLE_SEED_BASE, oracle_predictions
from baselines.types import DAY_SECONDS, Episode

logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BANK_DIR = REPO_ROOT / "banks" / "baselines" / "sweep" / "visits6"
"""The rate sweep's 1x banks (6 patrol visits a day, 28 days)."""
REPORT_DIR = REPO_ROOT / "reports" / "baselines" / "llm_floor"
VENV_PYTHON = pathlib.Path("/data/oliver/venvs/vllm-v4-cu129/bin/python")
GENERATE_SCRIPT = pathlib.Path(__file__).resolve().parent / "llm_generate.py"

SEEDS = (0, 1)
CAP_PER_CELL = 150
WARMUP_N = 200
INSPECT_N = 100
ORACLE_SEEDS = 200
LOG_LOSS_EPS = PassiveProtocolConfig().log_loss_epsilon
MODEL = "Qwen/Qwen3.8-27B"
GPUS = "0,1"

LLM = "LLMBelief"
ORACLE = "routine_oracle"
EXPIRY_HOURS = (6.0, 24.0)
LABEL = {LLM: "LLM", "LastObservation": "LastObs",
         "DaytypeMixture": "DaytypeMix", "Perpetua": "Perpetua",
         "LastObsExpiring6h": "LastObs+expire6h",
         "LastObsExpiring24h": "LastObs+expire24h", ORACLE: "oracle"}
MODEL_ORDER = (LLM, "LastObservation", "DaytypeMixture", "Perpetua",
               "LastObsExpiring6h", "LastObsExpiring24h", ORACLE)
COMPARATORS = ("LastObservation", "DaytypeMixture", "Perpetua",
               "LastObsExpiring6h", "LastObsExpiring24h", ORACLE)
DIST_MODELS = (LLM, "LastObservation", "DaytypeMixture", "Perpetua",
               "LastObsExpiring6h", "LastObsExpiring24h")
"""Models with a distribution (log-loss is defined); the oracle is a
modal answer only."""

PAIRED_BINS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("6-12h", ("[6h,12h)",)), ("12-24h", ("[12h,24h)",)),
    ("1-2d", ("[24h,48h)",)), ("2d+", ("[48h,72h)", "[72h,inf)")))
CASE_BLOCKS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("last sighting 12-24 h old", ("[12h,24h)",)),
    ("last sighting 1 day old or older",
     ("[24h,48h)", "[48h,72h)", "[72h,inf)")))
CASES = (("stayed, not excluded", False, False),
         ("stayed, EXCLUDED", False, True),
         ("moved, not excluded", True, False),
         ("moved, EXCLUDED", True, True))
SPECIAL_TRUTH = ("out of house", "on a person")

SCORED_COLUMNS = ("household", "seed", "qid", "object", "t_query",
                  "age_bin", "truth", "truth_category", "case", "model",
                  "answer", "correct", "logloss", "fallback", "pending",
                  "p_top")

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e8e7e2"
COLOR = {LLM: "#e34948", "LastObservation": "#2a78d6",
         "DaytypeMixture": "#eda100", "Perpetua": "#1baf7a",
         "LastObsExpiring6h": "#7ecdd3", "LastObsExpiring24h": "#00646d",
         ORACLE: "#8a8983"}


def bank_key(household: str, seed: int) -> str:
    return f"{household}:{seed}"


def _episode(household: str, seed: int) -> Episode:
    return next(iter(JsonlBank(path=bank_path(household, seed,
                                              BANK_DIR)).episodes()))


def _config() -> PassiveProtocolConfig:
    return PassiveProtocolConfig(seed=0, recency_bin_edges_h=FINE_AGE_EDGES_H)


def _read_jsonl(path: pathlib.Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _write_jsonl(path: pathlib.Path, rows: Sequence[Dict[str, Any]]) -> None:
    with path.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


# --------------------------------------------------------------- sample --

def sample_bank(household: str, seed: int, cap: int) -> Dict[str, List[str]]:
    """age bin -> sampled question ids for one bank."""
    episode = _episode(household, seed)
    cfg = _config()
    ages = question_ages(episode)
    by_bin: Dict[str, List[str]] = collections.defaultdict(list)
    for day in episode.questions_by_day:
        for q in day:
            by_bin[cfg.recency_bin(ages[q.question_id])].append(q.question_id)
    out = {}
    for b, qids in by_bin.items():
        rng = _derived_rng(0, "llm_floor", "sample", household, str(seed), b)
        out[b] = sorted(qids) if len(qids) <= cap else sorted(
            rng.sample(sorted(qids), cap))
    return out


def stage_sample(out_dir: pathlib.Path, households: Sequence[str],
                 cap: int) -> Dict[str, Any]:
    sample: Dict[str, Dict[str, List[str]]] = {}
    totals: Dict[str, List[int]] = collections.defaultdict(lambda: [0, 0])
    for hh in households:
        for seed in SEEDS:
            if not bank_path(hh, seed, BANK_DIR).exists():
                logger.warning("no bank for %s seed %d", hh, seed)
                continue
            per_bin = sample_bank(hh, seed, cap)
            sample[bank_key(hh, seed)] = per_bin
            episode = _episode(hh, seed)
            cfg = _config()
            ages = question_ages(episode)
            for day in episode.questions_by_day:
                for q in day:
                    totals[cfg.recency_bin(ages[q.question_id])][0] += 1
            for b, qids in per_bin.items():
                totals[b][1] += len(qids)
    doc = {"cap_per_cell": cap, "seeds": list(SEEDS),
           "bank_dir": str(BANK_DIR), "n_banks": len(sample),
           "totals_by_bin": {b: {"all": v[0], "sampled": v[1]}
                             for b, v in totals.items()},
           "n_sampled": sum(v[1] for v in totals.values()),
           "sample": sample}
    (out_dir / "sample.json").write_text(json.dumps(doc, indent=1))
    logger.info("sample: %d questions over %d banks -> sample.json",
                doc["n_sampled"], len(sample))
    return doc


def _load_sample(out_dir: pathlib.Path) -> Dict[str, Dict[str, List[str]]]:
    return json.loads((out_dir / "sample.json").read_text())["sample"]


# --------------------------------------------------------------- replay --

def replay(episode: Episode, beliefs: Dict[str, BeliefModel],
           wanted: Set[str]) -> Tuple[Dict[str, Dict[str, Any]],
                                      Dict[Tuple[str, str], Dict[str, Any]]]:
    """Kept-current replay (evidence strictly before each query, as in
    :func:`passive_eval.evaluate_continuous`), predicting only the
    ``wanted`` questions. Returns per-question facts (truth, age bin,
    four-case situation, from the first belief's shared bookkeeping) and
    per (question, belief) results."""
    cfg = _config()
    ages = question_ages(episode)
    for b in beliefs.values():
        b.reset(episode.agent_view())
        for obs in episode.initial_observations:
            b.update(obs)
    probe = next(iter(beliefs.values()))
    events = list(episode.evidence_stream())
    questions = sorted((q for day in episode.questions_by_day for q in day),
                       key=lambda q: q.t_query)
    facts: Dict[str, Dict[str, Any]] = {}
    results: Dict[Tuple[str, str], Dict[str, Any]] = {}
    i = 0
    for q in questions:
        while i < len(events) and events[i].t < q.t_query:
            for b in beliefs.values():
                b.update(events[i])
            i += 1
        if q.question_id not in wanted:
            continue
        truth = episode.true_location(q.object_id, q.t_query)
        history = probe._history.get(q.object_id, [])
        last_seen = history[-1][1] if history else None
        moved = truth != last_seen
        excluded = last_seen in probe._active_exclusions(q.object_id)
        case = next(label for label, m, e in CASES
                    if m == moved and e == excluded)
        facts[q.question_id] = {
            "qid": q.question_id, "object": q.object_id,
            "t_query": q.t_query, "truth": truth,
            "age_bin": cfg.recency_bin(ages[q.question_id]),
            "truth_category": truth_category(truth), "case": case}
        for name, b in beliefs.items():
            pred = b.predict_readonly(q.object_id, q.t_query)
            diag = b.last_prediction_diagnostics() or {}
            p_truth = pred.distribution.get(truth, 0.0)
            results[(q.question_id, name)] = {
                "answer": pred.argmax, "correct": pred.argmax == truth,
                "logloss": -math.log(max(p_truth, LOG_LOSS_EPS)),
                "fallback": int(diag.get("fallback", 0.0)),
                "pending": int(diag.get("pending", 0.0)),
                "p_top": diag.get("p_top", float("nan"))}
            if name == LLM:
                results[(q.question_id, name)]["key"] = getattr(b, "last_key")
    return facts, results


def bank_rooms(household: str, seed: int) -> Dict[str, str]:
    """receptacle id -> room, from the bank's room-visit rows (every
    receptacle of these banks is visited in exactly one room)."""
    rooms: Dict[str, str] = {}
    with bank_path(household, seed, BANK_DIR).open() as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("kind") == "room_visit":
                for rec in r["contents"]:
                    rooms.setdefault(rec, r["room"])
    return rooms


def _llm_spec(cache: PromptCache, rooms: Dict[str, str]) -> Dict[str, Any]:
    return {"name": "llm", "model": MODEL, "cache": cache, "rooms": rooms}


def _build(spec: Dict[str, Any], episode_id: str, stage: str) -> BeliefModel:
    rng = _derived_rng(0, "llm_floor", stage, str(spec["name"]),
                       str(spec.get("expiry_h", "")), episode_id)
    return build_registered_belief(dict(spec), rng)


# -------------------------------------------------------------- prompts --

def collect_bank(task: Dict[str, Any]) -> Dict[str, Any]:
    household, seed = task["household"], task["seed"]
    episode = _episode(household, seed)
    cache = PromptCache(collect=True)
    belief = _build(_llm_spec(cache, bank_rooms(household, seed)),
                    episode.episode_id, "collect")
    wanted = {qid for qids in task["sample"].values() for qid in qids}
    facts, results = replay(episode, {LLM: belief}, wanted)
    questions = []
    for qid, f in facts.items():
        questions.append({"household": household, "seed": seed, **f,
                          "key": results[(qid, LLM)]["key"]})
    prompts = [{"key": key, "messages": msgs,
                "allowed": list(episode.receptacle_ids)}
               for key, msgs in cache.prompts.items()]
    return {"household": household, "seed": seed, "questions": questions,
            "prompts": prompts}


def stage_prompts(out_dir: pathlib.Path, workers: int) -> None:
    sample = _load_sample(out_dir)
    tasks = [{"household": k.split(":")[0], "seed": int(k.split(":")[1]),
              "sample": v} for k, v in sample.items()]
    questions: List[Dict[str, Any]] = []
    prompts: Dict[str, Dict[str, Any]] = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        for res in pool.map(collect_bank, tasks):
            questions += res["questions"]
            for p in res["prompts"]:
                prompts.setdefault(p["key"], p)
            logger.info("prompts: %s seed %d, %d questions, %d prompts so far",
                        res["household"], res["seed"],
                        len(res["questions"]), len(prompts))
    questions.sort(key=lambda r: (r["household"], r["seed"], r["qid"]))
    _write_jsonl(out_dir / "questions.jsonl", questions)
    _write_jsonl(out_dir / "prompts.jsonl", list(prompts.values()))
    n_chars = sum(len(m["content"]) for p in prompts.values()
                  for m in p["messages"])
    logger.info("prompts: %d questions, %d distinct prompts (%.2f reuse), "
                "%.0f chars/prompt", len(questions), len(prompts),
                len(questions) / max(1, len(prompts)),
                n_chars / max(1, len(prompts)))


# ------------------------------------------------------------- generate --

def run_generate(prompts: pathlib.Path, out: pathlib.Path,
                 stats: pathlib.Path, limit: int, tp: int, gpus: str,
                 model: str, guided: bool = True) -> None:
    env = dict(os.environ)
    env.update({"CUDA_VISIBLE_DEVICES": gpus,
                "VLLM_ALLREDUCE_USE_SYMM_MEM": "0",
                "HF_HOME": env.get("HF_HOME", "/data/oliver/huggingface_cache")})
    cmd = [str(VENV_PYTHON), str(GENERATE_SCRIPT), "--prompts", str(prompts),
           "--out", str(out), "--stats", str(stats), "--model", model,
           "--tensor-parallel", str(tp), "--limit", str(limit)]
    if not guided:
        cmd.append("--no-guided")
    logger.info("generate: %s", " ".join(cmd))
    subprocess.run(cmd, env=env, check=True)


def _assert_schema_in_sync() -> None:
    text = GENERATE_SCRIPT.read_text()
    start = text.index("JSON_SCHEMA: Dict[str, Any] = {")
    end = text.index("\n}\n", start) + 3
    ns: Dict[str, Any] = {"Dict": Dict, "Any": Any}
    exec(text[start:end], ns)
    if ns["JSON_SCHEMA"] != JSON_SCHEMA:
        raise SystemExit("llm_generate.JSON_SCHEMA differs from "
                         "llm_belief.JSON_SCHEMA")


def stage_generate(out_dir: pathlib.Path, limit: int, tp: int, gpus: str,
                   model: str) -> None:
    _assert_schema_in_sync()
    stats = out_dir / ("warmup_stats.json" if limit else "generate_stats.json")
    run_generate(out_dir / "prompts.jsonl", out_dir / "completions.jsonl",
                 stats, limit, tp, gpus, model)


def stage_test(out_dir: pathlib.Path, tp: int, gpus: str, model: str,
               household: str = "hh_001", seed: int = 0) -> None:
    """Answer one prompt (a 12-24 h question with negative evidence, so
    the whole prompt shape is exercised) and print it."""
    _assert_schema_in_sync()
    questions = [q for q in _read_jsonl(out_dir / "questions.jsonl")
                 if q["household"] == household and q["seed"] == seed]
    pick = next((q for q in questions
                 if q["age_bin"] == "[12h,24h)" and "EXCLUDED" in q["case"]),
                questions[0])
    prompts = {p["key"]: p for p in _read_jsonl(out_dir / "prompts.jsonl")}
    prompt = prompts[pick["key"]]
    test_dir = out_dir / "test"
    test_dir.mkdir(exist_ok=True)
    _write_jsonl(test_dir / "prompt.jsonl", [prompt])
    comp_path = test_dir / "completion.jsonl"
    if comp_path.exists():
        comp_path.unlink()
    run_generate(test_dir / "prompt.jsonl", comp_path,
                 test_dir / "stats.json", 1, tp, gpus, model)
    comp = _read_jsonl(comp_path)[0]
    ranking, p_top, status = parse_completion(comp["text"], prompt["allowed"], 5)
    lines = [f"# Single test run ({model}, tp={tp}, GPUs {gpus})", "",
             f"Question {pick['qid']} of {household} seed {seed}: object "
             f"{pick['object']}, age bin {pick['age_bin']}, situation "
             f"'{pick['case']}', truth **{pick['truth']}**.", "",
             "## System", "", "```", prompt["messages"][0]["content"], "```",
             "", "## User", "", "```", prompt["messages"][1]["content"],
             "```", "", "## Completion", "", "```", comp["text"], "```", "",
             f"Parsed: status={status}, ranking={ranking}, p_top={p_top}; "
             f"correct={ranking is not None and ranking[0] == pick['truth']}. "
             f"Tokens: {comp['prompt_tokens']} prompt, "
             f"{comp['completion_tokens']} completion, finish="
             f"{comp['finish_reason']}."]
    (test_dir / "test_run.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


# --------------------------------------------------------------- warmup --

def completion_stats(out_dir: pathlib.Path) -> Dict[str, Any]:
    prompts = {p["key"]: p for p in _read_jsonl(out_dir / "prompts.jsonl")}
    comps = _read_jsonl(out_dir / "completions.jsonl")
    status = collections.Counter()
    ranked = []
    for c in comps:
        allowed = prompts.get(c["key"], {}).get("allowed", [])
        ranking, _, st = parse_completion(c["text"], allowed, 5)
        status[st] += 1
        if ranking:
            ranked.append(len(ranking))
    n = len(comps)
    return {"n_completions": n, "n_prompts": len(prompts),
            "status": dict(status),
            "parse_failure_rate": (n - status["ok"]) / n if n else None,
            "mean_ranking_length": statistics.mean(ranked) if ranked else None,
            "n_truncated": sum(c["finish_reason"] == "length" for c in comps)}


def stage_warmup(out_dir: pathlib.Path) -> None:
    stats_path = out_dir / "warmup_stats.json"
    gen = json.loads(stats_path.read_text()) if stats_path.exists() else {}
    cs = completion_stats(out_dir)
    remaining = cs["n_prompts"] - cs["n_completions"]
    qps = gen.get("questions_per_second")
    proj_h = remaining / qps / 3600 if qps else None
    tp = int(gen.get("tensor_parallel", 1))
    proj_wall = "-" if proj_h is None else f"{proj_h:.2f} h"
    proj_gpu_h = "-" if proj_h is None else f"{proj_h * tp:.2f}"
    qps_s = "-" if qps is None else f"{qps:.2f}"
    pfr = cs["parse_failure_rate"]
    pfr_s = "-" if pfr is None else f"{pfr:.3%}"
    lines = ["# Warmup", "",
             f"Model {gen.get('model')}, tensor parallel "
             f"{gen.get('tensor_parallel')}, GPUs {gen.get('cuda_visible_devices')}, "
             f"guided JSON {gen.get('guided_json')}.", "",
             "| quantity | value |", "|---|---|",
             f"| completions answered | {cs['n_completions']} |",
             f"| distinct prompts in total | {cs['n_prompts']} |",
             f"| prompt tokens / question | {gen.get('prompt_tokens_per_question', float('nan')):.0f} |",
             f"| completion tokens / question | {gen.get('completion_tokens_per_question', float('nan')):.1f} |",
             f"| questions / s | {qps_s} |",
             f"| tokens / s | {gen.get('tokens_per_second', float('nan')):.0f} |",
             f"| model load (s) | {gen.get('load_seconds')} |",
             f"| parse failures | {cs['status']} |",
             f"| parse-failure rate | {pfr_s} |",
             f"| truncated completions | {cs['n_truncated']} |",
             f"| mean ranking length | {cs['mean_ranking_length']} |",
             f"| remaining prompts | {remaining} |",
             f"| projected wall-clock for the rest | {proj_wall} |",
             f"| projected GPU-hours ({tp} GPUs) | {proj_gpu_h} |"]
    (out_dir / "warmup.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


# ---------------------------------------------------------------- score --

def score_bank(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    household, seed = task["household"], task["seed"]
    episode = _episode(household, seed)
    wanted = {qid for qids in task["sample"].values() for qid in qids}
    answers = task["answers"]
    cache = PromptCache(answers=answers)
    beliefs: Dict[str, BeliefModel] = {}
    llm = _build(_llm_spec(cache, bank_rooms(household, seed)),
                 episode.episode_id, "score")
    beliefs[LLM] = llm
    for spec in select_specs(["last_observation", "daytype_mixture",
                              "perpetua"]):
        b = _build(spec, episode.episode_id, "score")
        beliefs[b.name] = b
    for h in EXPIRY_HOURS:
        b = _build({"name": "last_observation_expiring", "expiry_h": h},
                   episode.episode_id, "score")
        beliefs[b.name] = b
    facts, results = replay(episode, beliefs, wanted)
    rows: List[Dict[str, Any]] = []
    for (qid, model), r in results.items():
        f = facts[qid]
        rows.append({"household": household, "seed": seed, "qid": qid,
                     "object": f["object"], "t_query": f["t_query"],
                     "age_bin": f["age_bin"], "truth": f["truth"],
                     "truth_category": f["truth_category"],
                     "case": f["case"], "model": model,
                     "answer": r["answer"], "correct": int(r["correct"]),
                     "logloss": round(r["logloss"], 6),
                     "fallback": r["fallback"], "pending": r["pending"],
                     "p_top": ("" if r["p_top"] != r["p_top"]
                               else round(r["p_top"], 4))})
    oracle = oracle_predictions(timeline_dir(household, seed), episode,
                                n_seeds=task["oracle_seeds"],
                                seed_base=ORACLE_SEED_BASE + seed * 10_000)
    if oracle is not None:
        modal, _ = oracle
        questions = [q for day in episode.questions_by_day for q in day]
        for pred, q in zip(modal, questions):
            if q.question_id not in facts:
                continue
            f = facts[q.question_id]
            rows.append({"household": household, "seed": seed,
                         "qid": q.question_id, "object": f["object"],
                         "t_query": f["t_query"], "age_bin": f["age_bin"],
                         "truth": f["truth"],
                         "truth_category": f["truth_category"],
                         "case": f["case"], "model": ORACLE, "answer": pred,
                         "correct": int(pred == f["truth"]), "logloss": "",
                         "fallback": 0, "pending": 0, "p_top": ""})
    logger.info("score: %s seed %d done (%d rows; LLM counts %s)", household,
                seed, len(rows), llm.counts)
    return rows


def stage_score(out_dir: pathlib.Path, workers: int, oracle_seeds: int
                ) -> None:
    sample = _load_sample(out_dir)
    answers = {c["key"]: c["text"]
               for c in _read_jsonl(out_dir / "completions.jsonl")}
    tasks = [{"household": k.split(":")[0], "seed": int(k.split(":")[1]),
              "sample": v, "answers": answers, "oracle_seeds": oracle_seeds}
             for k, v in sample.items()]
    n = 0
    with gzip.open(out_dir / "scored.csv.gz", "wt", newline="") as fh, \
            concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        w = csv.DictWriter(fh, fieldnames=SCORED_COLUMNS)
        w.writeheader()
        for rows in pool.map(score_bank, tasks):
            w.writerows(rows)
            n += len(rows)
    logger.info("score: %d rows -> scored.csv.gz", n)


# --------------------------------------------------------------- report --

def load_scored(out_dir: pathlib.Path) -> List[Dict[str, Any]]:
    with gzip.open(out_dir / "scored.csv.gz", "rt") as fh:
        rows = []
        for r in csv.DictReader(fh):
            r["seed"] = int(r["seed"])
            r["correct"] = int(r["correct"])
            r["fallback"] = int(r["fallback"])
            r["pending"] = int(r["pending"])
            r["logloss"] = float(r["logloss"]) if r["logloss"] else None
            r["p_top"] = float(r["p_top"]) if r["p_top"] else None
            rows.append(r)
    return rows


class Acc:
    """Pooled n / correct / summed log-loss by key."""

    def __init__(self, rows: Sequence[Dict[str, Any]], key: Any) -> None:
        self.n: Dict[Any, int] = collections.defaultdict(int)
        self.c: Dict[Any, int] = collections.defaultdict(int)
        self.ll: Dict[Any, float] = collections.defaultdict(float)
        for r in rows:
            k = key(r)
            self.n[k] += 1
            self.c[k] += r["correct"]
            if r["logloss"] is not None:
                self.ll[k] += r["logloss"]

    def acc(self, k: Any) -> Optional[float]:
        return self.c[k] / self.n[k] if self.n.get(k, 0) >= MIN_N else None

    def mean_ll(self, k: Any) -> Optional[float]:
        return self.ll[k] / self.n[k] if self.n.get(k, 0) >= MIN_N else None


def _f(v: Optional[float]) -> str:
    return "-" if v is None else f"{v:.3f}"


def _table(head: Sequence[str], body: Sequence[Sequence[str]]) -> List[str]:
    return (["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
            + ["| " + " | ".join(r) + " |" for r in body])


def bins_present(rows: Sequence[Dict[str, Any]]) -> List[str]:
    present = {r["age_bin"] for r in rows}
    return [b for b in AGE_ORDER if b in present]


def age_tables(rows: Sequence[Dict[str, Any]], meta: Dict[str, Any]
               ) -> List[str]:
    lines: List[str] = []
    groups = [("all homes", None)] + [
        (f"{g}-resident homes", g) for g in ("1", "2", "3+")
        if any(m["resident_group"] == g for m in meta.values())]
    for title, g in groups:
        sel = [r for r in rows if g is None
               or meta[r["household"]]["resident_group"] == g]
        n_homes = len({r["household"] for r in sel})
        lines += [f"### {title} ({n_homes} homes, seeds 0 and 1 pooled; "
                  f"stratified sample, n per row)", ""]
        acc = Acc(sel, lambda r: (r["model"], r["age_bin"]))
        body = []
        for b in bins_present(sel):
            n = acc.n.get((LLM, b), 0)
            body.append([AGE_LABEL[b], str(n)]
                        + [_f(acc.acc((m, b))) for m in MODEL_ORDER])
        lines += _table(["age of last sighting", "n (sample)"]
                        + [LABEL[m] for m in MODEL_ORDER], body) + [""]
    return lines


def logloss_table(rows: Sequence[Dict[str, Any]]) -> List[str]:
    acc = Acc(rows, lambda r: (r["model"], r["age_bin"]))
    body = []
    for b in bins_present(rows):
        body.append([AGE_LABEL[b], str(acc.n.get((LLM, b), 0))]
                    + [_f(acc.mean_ll((m, b))) for m in DIST_MODELS])
    return _table(["age of last sighting", "n (sample)"]
                  + [LABEL[m] for m in DIST_MODELS], body)


def paired_table(rows: Sequence[Dict[str, Any]]) -> List[str]:
    """LLM minus each comparator per (home, seed) in a bin group; a pair
    counts when the cell has >= MIN_N sampled questions."""
    def bin_group(r: Dict[str, Any]) -> Optional[str]:
        for label, bins in PAIRED_BINS:
            if r["age_bin"] in bins:
                return label
        return None
    acc = Acc(rows, lambda r: (r["household"], r["seed"], r["model"],
                               bin_group(r)))
    homes_seeds = sorted({(r["household"], r["seed"]) for r in rows})
    body = []
    for label, _ in PAIRED_BINS:
        for comp in COMPARATORS:
            deltas = []
            for hh, seed in homes_seeds:
                a1 = acc.acc((hh, seed, LLM, label))
                a0 = acc.acc((hh, seed, comp, label))
                if a1 is None or a0 is None:
                    continue
                deltas.append(a1 - a0)
            if not deltas:
                cell = ["0", "-", "-", "-", "-"]
            else:
                cell = [str(len(deltas)), str(sum(d > 0 for d in deltas)),
                        str(sum(d < 0 for d in deltas)),
                        f"{statistics.median(deltas):+.3f}",
                        f"{statistics.mean(deltas):+.3f}"]
            body.append([label, f"LLM - {LABEL[comp]}"] + cell)
    return _table(["bin", "pair", "home-seed pairs", "LLM wins",
                   "LLM losses", "median delta", "mean delta"], body)


def case_tables(rows: Sequence[Dict[str, Any]]) -> List[str]:
    lines: List[str] = []
    for title, bins in CASE_BLOCKS:
        sel = [r for r in rows if r["age_bin"] in bins]
        acc = Acc(sel, lambda r: (r["model"], r["case"]))
        grand = sum(acc.n[(LLM, c)] for c, _, _ in CASES)
        body = []
        for c, _, _ in CASES:
            n = acc.n.get((LLM, c), 0)
            if not n:
                continue
            body.append([c, f"{n / grand:.2f}", str(n)]
                        + [_f(acc.acc((m, c))) for m in MODEL_ORDER])
        lines += [f"### {title} (stratified sample, n = {grand})", ""]
        lines += _table(["situation", "share", "n"]
                        + [LABEL[m] for m in MODEL_ORDER], body) + [""]
    return lines


def special_truth_tables(rows: Sequence[Dict[str, Any]]) -> List[str]:
    """Accuracy on questions whose true answer is OUT_OF_HOUSE or
    ON_PERSON, and how often each model gives such an answer."""
    groups = (("under 12 h", ("[0h,0.25h)", "[0.25h,1h)", "[1h,3h)",
                              "[3h,6h)", "[6h,12h)")),
              ("12-24 h", ("[12h,24h)",)),
              ("1 day or older", ("[24h,48h)", "[48h,72h)", "[72h,inf)")),
              ("all ages", tuple(AGE_ORDER)))
    lines = ["Accuracy on questions whose TRUE answer is OUT_OF_HOUSE or "
             "ON_PERSON (the ability the LLM is given from the start):", ""]
    body = []
    for label, bins in groups:
        sel = [r for r in rows if r["age_bin"] in bins]
        for cat in SPECIAL_TRUTH:
            sub = [r for r in sel if r["truth_category"] == cat]
            acc = Acc(sub, lambda r: r["model"])
            n = acc.n.get(LLM, 0)
            if not n:
                continue
            body.append([label, cat, str(n)]
                        + [_f(acc.acc(m)) for m in MODEL_ORDER])
    lines += _table(["age of last sighting", "true answer", "n (sample)"]
                    + [LABEL[m] for m in MODEL_ORDER], body)
    lines += ["", "How often each model ANSWERS out of house / on a person, "
              "and how often that answer is right (all sampled questions):", ""]
    body = []
    by_model: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)
    for m in MODEL_ORDER:
        rs = by_model.get(m, [])
        if not rs:
            continue
        for cat in SPECIAL_TRUTH:
            said = [r for r in rs if truth_category(r["answer"]) == cat]
            truly = sum(r["truth_category"] == cat for r in rs)
            hit = sum(r["correct"] for r in said)
            body.append([LABEL[m], cat, f"{len(said) / len(rs):.3f}",
                         f"{truly / len(rs):.3f}",
                         "-" if len(said) < MIN_N else f"{hit / len(said):.3f}",
                         "-" if truly < MIN_N else f"{hit / truly:.3f}"])
    lines += _table(["model", "answer", "share answered", "share true",
                     "precision", "recall"], body)
    return lines


def fallback_lines(rows: Sequence[Dict[str, Any]], out_dir: pathlib.Path
                   ) -> List[str]:
    llm = [r for r in rows if r["model"] == LLM]
    n = len(llm)
    fb = sum(r["fallback"] for r in llm)
    pend = sum(r["pending"] for r in llm)
    cs = completion_stats(out_dir)
    right = [r["p_top"] for r in llm if r["correct"] and r["p_top"] is not None]
    wrong = [r["p_top"] for r in llm if not r["correct"] and r["p_top"] is not None]
    lines = [f"- LLM questions scored: {n}; answered by the LLM: {n - fb}; "
             f"fell back to LastObs: {fb} ({fb / max(1, n):.2%}), of which "
             f"{pend} had no completion at all.",
             f"- Completion parse status over the {cs['n_completions']} "
             f"distinct prompts: {cs['status']} (failure rate "
             f"{cs['parse_failure_rate']:.2%}); truncated: {cs['n_truncated']}; "
             f"mean ranking length {cs['mean_ranking_length']:.2f}.",
             f"- p_top (logged, not used): mean {statistics.mean(right):.2f} "
             f"when the top answer was right (n={len(right)}), "
             f"{statistics.mean(wrong):.2f} when wrong (n={len(wrong)})."
             if right and wrong else "- p_top: not enough answers to summarize."]
    return lines


def expiring_table(rows: Sequence[Dict[str, Any]]) -> List[str]:
    models = ("LastObservation", "LastObsExpiring6h", "LastObsExpiring24h")
    acc = Acc(rows, lambda r: (r["model"], r["age_bin"]))
    body = []
    for b in bins_present(rows):
        body.append([AGE_LABEL[b], str(acc.n.get((LLM, b), 0))]
                    + [_f(acc.acc((m, b))) for m in models]
                    + [_f(acc.mean_ll((m, b))) for m in models])
    head = (["age of last sighting", "n (sample)"]
            + [f"{LABEL[m]} acc" for m in models]
            + [f"{LABEL[m]} logloss" for m in models])
    lines = _table(head, body)
    for title, bins in CASE_BLOCKS:
        sel = [r for r in rows if r["age_bin"] in bins]
        cacc = Acc(sel, lambda r: (r["model"], r["case"]))
        body = []
        for c, _, _ in CASES:
            n = cacc.n.get((LLM, c), 0)
            if n:
                body.append([c, str(n)] + [_f(cacc.acc((m, c))) for m in models])
        lines += ["", f"By situation, {title}:", ""]
        lines += _table(["situation", "n"] + [LABEL[m] for m in models], body)
    return lines


def fig_accuracy_by_age(rows: Sequence[Dict[str, Any]], out: pathlib.Path,
                        n_homes: int) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    acc = Acc(rows, lambda r: (r["model"], r["age_bin"]))
    bins = bins_present(rows)
    xs = list(range(len(bins)))
    fig, ax = plt.subplots(figsize=(8.4, 4.4), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for m in MODEL_ORDER:
        pts = [(x, acc.c[(m, b)], acc.n[(m, b)]) for x, b in zip(xs, bins)
               if acc.n.get((m, b), 0) >= MIN_N]
        if not pts:
            continue
        ys = [c / n for _, c, n in pts]
        lo = [wilson(c, n)[0] for _, c, n in pts]
        hi = [wilson(c, n)[1] for _, c, n in pts]
        style = dict(linestyle=(0, (4, 3))) if m == ORACLE else {}
        ax.plot([p[0] for p in pts], ys, color=COLOR[m],
                linewidth=2.4 if m == LLM else 1.6, label=LABEL[m],
                marker="o", markersize=3.5, **style)
        ax.fill_between([p[0] for p in pts], lo, hi, color=COLOR[m],
                        alpha=0.12, linewidth=0)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{AGE_LABEL[b]}\nn={acc.n.get((LLM, b), 0)}"
                        for b in bins], fontsize=7.5)
    ax.set_ylim(0, 1)
    ax.set_ylabel("top-1 accuracy (shaded: Wilson 95%)", fontsize=8, color=INK2)
    ax.set_xlabel("age of the object's last sighting", fontsize=8, color=INK2)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=INK2, labelsize=7.5)
    ax.legend(frameon=False, fontsize=7.5, ncol=4, loc="lower left")
    ax.set_title(f"Accuracy by age of last sighting: STRATIFIED SAMPLE "
                 f"(at most {CAP_PER_CELL} questions per home-seed-bin; "
                 f"{n_homes} homes, seeds 0+1 pooled; n per bin on the axis)",
                 fontsize=8.5, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def fig_paired_by_home(rows: Sequence[Dict[str, Any]], meta: Dict[str, Any],
                       out: pathlib.Path, comp: str = "LastObservation"
                       ) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    def bin_group(r: Dict[str, Any]) -> Optional[str]:
        for label, bins in PAIRED_BINS:
            if r["age_bin"] in bins:
                return label
        return None
    acc = Acc(rows, lambda r: (r["household"], r["model"], bin_group(r)))
    homes = sorted(meta, key=lambda h: (meta[h]["resident_group"], h))
    ys = list(range(len(homes)))[::-1]
    fig, axes = plt.subplots(1, len(PAIRED_BINS),
                             figsize=(11.5, 0.34 * len(homes) + 2.2),
                             sharey=True, facecolor=SURFACE)
    for ax, (label, _) in zip(axes, PAIRED_BINS):
        ax.set_facecolor(SURFACE)
        ax.axvline(0, color=INK2, linewidth=1.2)
        ax.grid(True, axis="x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=INK2, labelsize=7, length=0)
        for y, hh in zip(ys, homes):
            v, r0 = acc.acc((hh, LLM, label)), acc.acc((hh, comp, label))
            n = acc.n.get((hh, LLM, label), 0)
            if v is None or r0 is None:
                continue
            se = ((v * (1 - v) + r0 * (1 - r0)) / n) ** 0.5
            ax.plot([v - r0 - 1.96 * se, v - r0 + 1.96 * se], [y, y],
                    color=COLOR[LLM], linewidth=1.2, zorder=2)
            ax.plot(v - r0, y, marker="o", markersize=6, color=COLOR[LLM],
                    markeredgecolor=SURFACE, markeredgewidth=1,
                    linestyle="none", zorder=3)
            ax.text(1.02, y, f"n={n}", transform=ax.get_yaxis_transform(),
                    fontsize=6, color=INK2, va="center")
        ax.set_title(f"LLM - {LABEL[comp]}, {label}", fontsize=9, color=INK,
                     loc="left")
        ax.set_xlabel("accuracy difference", fontsize=8, color=INK2)
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([f"{h} · {meta[h]['residents']}r" for h in homes],
                            fontsize=7)
    fig.suptitle(f"LLM minus {LABEL[comp]} per home on the STRATIFIED SAMPLE "
                 f"(seeds pooled; bars = conservative 95% interval; n per "
                 f"home at right; cells under {MIN_N} questions not drawn)",
                 fontsize=9.5, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 0.98, 0.95))
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def fig_cases(rows: Sequence[Dict[str, Any]], out: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(CASE_BLOCKS), figsize=(11, 4),
                             facecolor=SURFACE, sharey=True)
    models = [m for m in MODEL_ORDER if m != ORACLE]
    width = 0.8 / len(models)
    for ax, (title, bins) in zip(axes, CASE_BLOCKS):
        ax.set_facecolor(SURFACE)
        sel = [r for r in rows if r["age_bin"] in bins]
        acc = Acc(sel, lambda r: (r["model"], r["case"]))
        labels = []
        for ci, (c, _, _) in enumerate(CASES):
            n = acc.n.get((LLM, c), 0)
            labels.append(f"{c}\nn={n}")
            for mi, m in enumerate(models):
                v = acc.acc((m, c))
                if v is None:
                    continue
                lo, hi = wilson(acc.c[(m, c)], acc.n[(m, c)])
                x = ci + (mi - (len(models) - 1) / 2) * width
                ax.bar(x, v, width=width * 0.95, color=COLOR[m],
                       label=LABEL[m] if ci == 0 else None)
                ax.plot([x, x], [lo, hi], color=INK, linewidth=0.8)
        ax.set_xticks(range(len(CASES)))
        ax.set_xticklabels(labels, fontsize=7)
        ax.set_ylim(0, 1)
        ax.grid(True, axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=INK2, labelsize=7.5)
        ax.set_title(title, fontsize=9, color=INK, loc="left")
    axes[0].set_ylabel("top-1 accuracy (bars: Wilson 95%)", fontsize=8,
                       color=INK2)
    axes[0].legend(frameon=False, fontsize=7, ncol=3, loc="upper right")
    fig.suptitle("Accuracy by situation (moved since last sighting x last-seen "
                 "receptacle excluded by a later visit), STRATIFIED SAMPLE, "
                 "all homes and seeds pooled, n per situation on the axis",
                 fontsize=9, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def write_inspection(out_dir: pathlib.Path, rows: Sequence[Dict[str, Any]]
                     ) -> pathlib.Path:
    questions = {(q["household"], q["seed"], q["qid"]): q
                 for q in _read_jsonl(out_dir / "questions.jsonl")}
    prompts = {p["key"]: p for p in _read_jsonl(out_dir / "prompts.jsonl")}
    comps = {c["key"]: c for c in _read_jsonl(out_dir / "completions.jsonl")}
    llm = [r for r in rows if r["model"] == LLM]
    rng = _derived_rng(0, "llm_floor", "inspection")
    picks = rng.sample(llm, min(INSPECT_N, len(llm)))
    picks.sort(key=lambda r: (r["household"], r["seed"], r["qid"]))
    lines = [f"# {len(picks)} random sampled questions: prompt, completion, "
             f"truth", "", "Drawn uniformly from the scored LLM rows with a "
             "fixed seed. The system prompt is identical for every "
             "question and shown once.", "", "```",
             prompts[next(iter(prompts))]["messages"][0]["content"], "```", ""]
    for r in picks:
        q = questions[(r["household"], r["seed"], r["qid"])]
        p = prompts[q["key"]]
        c = comps.get(q["key"], {})
        lines += [f"## {r['household']} seed {r['seed']} {r['qid']}: "
                  f"{r['object']}, age {AGE_LABEL[r['age_bin']]}, "
                  f"{r['case']}", "",
                  f"Truth **{r['truth']}**; LLM answered **{r['answer']}** "
                  f"({'right' if r['correct'] else 'wrong'}"
                  f"{', FALLBACK to LastObs' if r['fallback'] else ''}).", "",
                  "```", p["messages"][1]["content"], "```", "",
                  "Completion:", "", "```", c.get("text", "<none>"), "```", ""]
    path = out_dir / "inspection.md"
    path.write_text("\n".join(lines) + "\n")
    return path


def stage_report(out_dir: pathlib.Path) -> pathlib.Path:
    rows = load_scored(out_dir)
    meta = {h: m for h, m in household_meta(BANK_DIR).items()
            if any(r["household"] == h for r in rows)}
    sample = json.loads((out_dir / "sample.json").read_text())
    gen_stats = {}
    for name in ("generate_stats.json", "warmup_stats.json"):
        if (out_dir / name).exists():
            gen_stats = json.loads((out_dir / name).read_text())
            break
    n_q = len({(r["household"], r["seed"], r["qid"]) for r in rows})
    n_homes = len(meta)
    fig_accuracy_by_age(rows, out_dir / "accuracy_by_age.png", n_homes)
    fig_paired_by_home(rows, meta, out_dir / "paired_by_home_lastobs.png")
    fig_paired_by_home(rows, meta, out_dir / "paired_by_home_perpetua.png",
                       comp="Perpetua")
    fig_cases(rows, out_dir / "cases.png")
    inspection = write_inspection(out_dir, rows)
    commit, dirty = git_state(REPO_ROOT)
    md = [
        "# Naive LLM belief floor (local vLLM) on a stratified sample of "
        "the 1x banks", "",
        f"Generated {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M} UTC, "
        f"commit {commit[:10]}{' (dirty)' if dirty else ''}.", "",
        f"**Read every number here as computed on a STRATIFIED SAMPLE**: at "
        f"most {sample['cap_per_cell']} questions per (home, seed, "
        f"age-of-last-sighting bin), bins with fewer keep all of theirs; "
        f"n = {n_q} of {sum(v['all'] for v in sample['totals_by_bin'].values())} "
        f"questions over {n_homes} homes x seeds {sample['seeds']} "
        f"(28-day banks, 1x patrol rate, {BANK_DIR.relative_to(REPO_ROOT)}). "
        f"Short-age bins are heavily subsampled, long-age bins barely; "
        f"pooled-over-bins accuracies are therefore NOT comparable to the "
        f"rate sweep's, per-bin ones are. Every comparator is scored on "
        f"exactly the same sampled questions. Cells under {MIN_N} questions "
        f"are masked.", "",
        f"LLM: {gen_stats.get('model', MODEL)}, one vLLM instance, "
        f"tensor parallel {gen_stats.get('tensor_parallel', '?')}, greedy, "
        f"seed {gen_stats.get('seed', 0)}, guided JSON "
        f"{gen_stats.get('guided_json', '?')}; prompt v1 (no reasoning, no "
        f"examples, no routine summary; newest 60 sightings; negative "
        f"evidence since the last sighting; answers ranked, geometric "
        f"weights 0.5/0.25/... renormalized for log-loss). Fallback on a "
        f"failed parse or an off-list name is the LastObs answer.", "",
        "## Sample composition", "",
    ]
    md += _table(["age of last sighting", "questions in the banks",
                  "sampled", "share sampled"],
                 [[AGE_LABEL.get(b, b), str(v["all"]), str(v["sampled"]),
                   f"{v['sampled'] / v['all']:.2f}"]
                  for b, v in sorted(sample["totals_by_bin"].items(),
                                     key=lambda kv: AGE_ORDER.index(kv[0]))])
    md += ["", "## LLM output handling", ""] + fallback_lines(rows, out_dir)
    md += ["", "## 1. Accuracy by age of last sighting", "",
           "![](accuracy_by_age.png)", ""] + age_tables(rows, meta)
    md += ["## 2. Log-loss by age of last sighting (all homes; eps 1e-3; "
           "oracle has no distribution)", ""] + logloss_table(rows)
    md += ["", "## 3. Paired per-home-seed comparisons (LLM minus "
           "comparator; a pair counts when the home-seed cell has >= "
           f"{MIN_N} sampled questions)", "",
           "![](paired_by_home_lastobs.png)", "",
           "![](paired_by_home_perpetua.png)", ""] + paired_table(rows)
    md += ["", "## 4. The four-case split", "", "![](cases.png)", ""]
    md += case_tables(rows)
    md += ["## 5. OUT_OF_HOUSE and ON_PERSON", ""] + special_truth_tables(rows)
    md += ["", "## 6. Expiring-exclusion comparator (LastObs whose "
           "exclusions lapse N hours after the inspection)", "",
           "Classical LastObs with the base class's permanent exclusion "
           "against the same belief with an exclusion that expires after "
           "6 h or 24 h. Same sampled questions.", ""] + expiring_table(rows)
    md += ["", "## 7. Prompts and completions to read", "",
           f"[{inspection.name}]({inspection.name}): {INSPECT_N} random "
           f"sampled questions with prompt, completion, truth and verdict. "
           f"The single test run is in test/test_run.md; warmup numbers in "
           f"warmup.md.", ""]
    path = out_dir / "summary.md"
    path.write_text("\n".join(md) + "\n")
    (out_dir / "provenance.json").write_text(json.dumps({
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git": [commit, dirty], "bank_dir": str(BANK_DIR),
        "seeds": list(SEEDS), "cap_per_cell": sample["cap_per_cell"],
        "n_questions": n_q, "households": sorted(meta),
        "models": list(MODEL_ORDER), "generation": gen_stats,
        "oracle_seeds_per_bank": ORACLE_SEEDS}, indent=2))
    return path


# ----------------------------------------------------------------- main --

def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", nargs="+",
                    choices=["sample", "prompts", "test", "generate",
                             "warmup", "score", "report"], required=True)
    ap.add_argument("--out-dir", type=pathlib.Path, default=REPORT_DIR)
    ap.add_argument("--households", nargs="*", default=None)
    ap.add_argument("--cap", type=int, default=CAP_PER_CELL)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--limit", type=int, default=0,
                    help="generate: answer at most this many new prompts")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--tensor-parallel", type=int, default=2)
    ap.add_argument("--gpus", default=GPUS)
    ap.add_argument("--oracle-seeds", type=int, default=ORACLE_SEEDS)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for stage in args.stage:
        if stage == "sample":
            households = args.households or sorted(household_meta(BANK_DIR))
            stage_sample(args.out_dir, households, args.cap)
        elif stage == "prompts":
            stage_prompts(args.out_dir, args.workers)
        elif stage == "test":
            stage_test(args.out_dir, args.tensor_parallel, args.gpus,
                       args.model)
        elif stage == "generate":
            stage_generate(args.out_dir, args.limit, args.tensor_parallel,
                           args.gpus, args.model)
        elif stage == "warmup":
            stage_warmup(args.out_dir)
        elif stage == "score":
            stage_score(args.out_dir, args.workers, args.oracle_seeds)
        elif stage == "report":
            print(f"-> {stage_report(args.out_dir)}")


if __name__ == "__main__":
    main()
