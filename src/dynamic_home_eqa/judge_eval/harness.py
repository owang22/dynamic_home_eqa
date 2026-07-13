"""
Judge regression harness — score the EVAL set under a judge configuration and
report agreement with the human bands.

Each EVAL candidate is re-scored in its ORIGINAL activity-batch context (the
full grounded pool the judge saw at generation time), so the measured score
reflects how the judge actually behaves in the pipeline, not an artificial
one-candidate prompt. Scoring goes through the normal score_realism_batch /
ResponseCache path with the normal versioned stage tags, so repeat runs of
the same configuration are free.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import statistics
from typing import Optional

from ..generation.cache import ResponseCache
from ..generation.llm_client import DEFAULT_MODEL
from ..generation.stages import score_realism_batch
from . import metrics
from .labels import Candidate


@dataclasses.dataclass(frozen=True)
class JudgeConfig:
    name: str                       # short label for the report/index
    judge_style: str = "strict"     # "asis" | "strict"
    judge_thinking: bool = False
    temperature: float = 0.7
    include_context: bool = False   # occupant_card + temporal_context (Phase 2.1)
    use_exemplars: bool = False     # few-shot exemplar block (Phase 2.2)
    k: int = 1                      # self-consistency samples, median (Phase 2.3)
    # Out-of-process model (e.g. the 80B MoE served by vllm_q): when endpoint
    # is set the thinking judge scores against it over HTTP; model_tag keeps
    # its cache separate from the in-process Qwen3-32B.
    endpoint: Optional[str] = None
    model_name: Optional[str] = None
    model_tag: str = ""


def _identity(scene: str, occupant: str, activity: str,
              obj: str, rel: str, anchor: str) -> tuple:
    return (scene, occupant, activity, obj, rel, anchor)


def load_generation(gen_dir: pathlib.Path, folders: list[str]) -> dict:
    """Index every grounded candidate by content identity and group into the
    batches score_realism_batch expects. Returns
    {identity: batch_key} and {batch_key: batch_info}."""
    identity_to_batch: dict[tuple, tuple] = {}
    batches: dict[tuple, dict] = {}
    for folder in folders:
        path = gen_dir / folder / "generation_result.json"
        if not path.exists():
            continue
        d = json.loads(path.read_text())
        scene = d.get("scene_id", folder.split("_")[0])
        persona = d["persona"]
        hid = d["household_id"]
        day = d["day"]
        trace_by_occ = {t.get("occupant_name"): t for t in d.get("traces", [])}
        for c in d.get("candidates", []):
            bkey = (scene, c["_occupant"], c["_activity"], float(c["_start"]), float(c["_end"]))
            b = batches.setdefault(bkey, {
                "candidates": [], "persona": persona, "household_id": hid, "day": day,
                "occupant": c["_occupant"], "activity": c["_activity"],
                "start": float(c["_start"]), "end": float(c["_end"]),
                "occupant_index": int(c.get("_occupant_index", 0)),
                "trace": trace_by_occ.get(c["_occupant"]),
            })
            b["candidates"].append(c)
            idk = _identity(scene, c["_occupant"], c["_activity"],
                            c["object_category"], c["target_relationship"], c["target_anchor"])
            identity_to_batch.setdefault(idk, bkey)
    return {"identity_to_batch": identity_to_batch, "batches": batches}


def _score_batch(b: dict, config: JudgeConfig, cache, model, exemplar_block, judge_client=None):
    """Score one batch under the config; for k>1 take the per-candidate median
    across k self-consistency samples at distinct seeds."""
    samples: list[list[float]] = []
    for si in range(max(1, config.k)):
        scores, _meta = score_realism_batch(
            candidates=b["candidates"], activity=b["activity"], occupant_name=b["occupant"],
            persona=b["persona"], household_id=b["household_id"], day=b["day"],
            start=b["start"], end=b["end"], occupant_index=b["occupant_index"], model=model,
            temperature=config.temperature, cache=cache,
            judge_thinking=config.judge_thinking, judge_style=config.judge_style,
            trace=b["trace"], include_context=config.include_context,
            exemplar_block=exemplar_block if config.use_exemplars else None,
            sample_index=si, judge_client=judge_client, model_tag=config.model_tag,
        )
        samples.append(scores)
    if len(samples) == 1:
        return samples[0]
    return [statistics.median(s[j] for s in samples) for j in range(len(b["candidates"]))]


def score_eval(
    eval_cands: list[Candidate], gen: dict, config: JudgeConfig,
    cache: Optional[ResponseCache], model: str = DEFAULT_MODEL,
    exemplar_block: Optional[str] = None,
) -> dict[str, float]:
    """candidate_id -> judge score under `config`. Scores each needed batch
    once (k samples, median for k>1) and reads every EVAL candidate's score
    out of it."""
    identity_to_batch = gen["identity_to_batch"]
    batches = gen["batches"]
    judge_client = None
    if config.endpoint:
        from ..generation.http_judge import HTTPThinkingClient
        judge_client = HTTPThinkingClient(config.endpoint, config.model_name or "")
    scored_batches: dict[tuple, dict] = {}
    out: dict[str, float] = {}
    for ec in eval_cands:
        idk = _identity(ec.scene, ec.occupant, ec.activity,
                        ec.object_category, ec.target_relationship, ec.target_anchor)
        bkey = identity_to_batch.get(idk)
        if bkey is None:
            out[ec.candidate_id] = None  # not found — reported as a gap
            continue
        if bkey not in scored_batches:
            b = batches[bkey]
            scores = _score_batch(b, config, cache, model, exemplar_block, judge_client)
            scored_batches[bkey] = {
                _identity(ec.scene, c["_occupant"], c["_activity"],
                          c["object_category"], c["target_relationship"], c["target_anchor"]): s
                for c, s in zip(b["candidates"], scores)
            }
        out[ec.candidate_id] = scored_batches[bkey].get(idk)
    return out


def evaluate(eval_cands: list[Candidate], scores_by_id: dict[str, float]) -> dict:
    """Compute all metrics for a config's scores against human bands."""
    paired = [(c, scores_by_id.get(c.candidate_id)) for c in eval_cands]
    scored = [(c, s) for c, s in paired if s is not None]
    missing = [c.candidate_id for c, s in paired if s is None]
    scores = [s for _c, s in scored]
    bands = [c.human_band for c, _s in scored]
    dl = [{"candidate_id": c.candidate_id, "object": c.object_category,
           "anchor": c.target_anchor, "activity": c.activity,
           "human_band": c.human_band, "judge_score": round(s, 2),
           "pred_band": metrics.score_to_band(s)}
          for c, s in scored if c.is_dinner_laptop]
    return {
        "n_eval": len(eval_cands),
        "n_scored": len(scored),
        "missing_ids": missing,
        "spearman": metrics.spearman(scores, bands),
        "band_separation": metrics.band_separation(scores, bands),
        "confusion": metrics.confusion(scores, bands),
        "worst": metrics.worst_disagreements(scored, k=10),
        "dinner_laptop": dl,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _fmt(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def write_report(config: JudgeConfig, res: dict, out_dir: pathlib.Path) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    L: list[str] = []
    L.append(f"# Judge harness — `{config.name}`\n")
    L.append(f"- style: **{config.judge_style}**, thinking: **{config.judge_thinking}**, "
             f"temperature: **{config.temperature}**, k: **{config.k}**")
    L.append(f"- scored {res['n_scored']}/{res['n_eval']} EVAL candidates"
             + (f" (missing: {', '.join(res['missing_ids'])})" if res["missing_ids"] else ""))
    c = res["confusion"]
    L.append("\n## Headline\n")
    L.append(f"- **Spearman rank corr vs human band: {_fmt(res['spearman'])}**")
    L.append(f"- exact-band match: {_fmt(c['exact_rate'])}   within-one: {_fmt(c['within_one_rate'])}")
    L.append(f"- **over-scored (judge > human): {_fmt(c['over_rate'])}**   under: {_fmt(c['under_rate'])}")

    L.append("\n## Band separation (judge score within each human band)\n")
    L.append("| human band | n | mean judge score | std |")
    L.append("|---|---|---|---|")
    bs = res["band_separation"]
    for b in (3, 2, 1, 0):
        r = bs[b]
        L.append(f"| {b} {metrics.BAND_LABEL[b]} | {r['n']} | {_fmt(r['mean'])} | {_fmt(r['std'])} |")

    L.append("\n## Confusion (rows = human band, cols = predicted band)\n")
    L.append("| human ↓ / pred → | 0 | 1 | 2 | 3 |")
    L.append("|---|---|---|---|---|")
    for h in (3, 2, 1, 0):
        L.append(f"| {h} | " + " | ".join(str(c["matrix"][h][p]) for p in (0, 1, 2, 3)) + " |")

    L.append("\n## Dinner-laptop candidates (the case the judge should nail)\n")
    if res["dinner_laptop"]:
        L.append("| id | object | anchor | activity | human | judge score | pred |")
        L.append("|---|---|---|---|---|---|---|")
        for d in res["dinner_laptop"]:
            L.append(f"| {d['candidate_id']} | {d['object']} | {d['anchor']} | {d['activity']} "
                     f"| {d['human_band']} | {d['judge_score']} | {d['pred_band']} |")
    else:
        L.append("_none in EVAL (all dinner-laptop cases fell in EXEMPLAR)._")

    L.append("\n## Worst disagreements\n")
    L.append("| id | object | rel | anchor | activity | human | judge | pred | gap | notes |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for w in res["worst"]:
        L.append(f"| {w['candidate_id']} | {w['object']} | {w['relation']} | {w['anchor']} "
                 f"| {w['activity']} | {w['human_band']} | {w['judge_score']} | {w['pred_band']} "
                 f"| {w['band_gap']:+d} | {w['notes']} |")

    path = out_dir / f"{config.name}.md"
    path.write_text("\n".join(L) + "\n")
    return path


def update_index(config: JudgeConfig, res: dict, out_dir: pathlib.Path) -> None:
    """Accumulating index so configurations are comparable side by side."""
    idx_json = out_dir / "index.json"
    rows: dict[str, dict] = {}
    if idx_json.exists():
        rows = json.loads(idx_json.read_text())
    c = res["confusion"]
    bs = res["band_separation"]
    rows[config.name] = {
        "style": config.judge_style, "thinking": config.judge_thinking,
        "context": config.include_context, "exemplars": config.use_exemplars,
        "temperature": config.temperature, "k": config.k,
        "spearman": res["spearman"], "exact_rate": c["exact_rate"],
        "over_rate": c["over_rate"], "under_rate": c["under_rate"],
        "n_scored": res["n_scored"],
        "mean_by_band": {str(b): bs[b]["mean"] for b in (0, 1, 2, 3)},
    }
    idx_json.write_text(json.dumps(rows, indent=2))

    L = ["# Judge harness index\n",
         "Higher Spearman + monotonically increasing mean-by-band = better. "
         "`over` is the fraction the judge scored above the human (its known failure).\n",
         "| config | style | ctx | fs | think | k | Spearman | exact | over | mean@band 0/1/2/3 |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in sorted(rows.items(), key=lambda kv: (kv[1]["spearman"] is None, -(kv[1]["spearman"] or 0))):
        mb = r["mean_by_band"]
        mbs = "/".join(_fmt(mb[str(b)]) for b in (0, 1, 2, 3))
        ck = "✓" if r.get("context") else "·"
        fs = "✓" if r.get("exemplars") else "·"
        L.append(f"| {name} | {r['style']} | {ck} | {fs} | {r['thinking']} | {r['k']} | {_fmt(r['spearman'])} "
                 f"| {_fmt(r['exact_rate'])} | {_fmt(r['over_rate'])} | {mbs} |")
    (out_dir / "INDEX.md").write_text("\n".join(L) + "\n")
