"""Do the two ways of writing notes actually produce different notes?

The cheapest experiment that can kill a whole factor of the study. Same model,
same temperature, same household, same look stream, same words describing what
was seen. Only the instruction about how to write differs. If a nightly wholesale
rewrite and an incremental claim store converge on the same content, the memory
factor is dead however well the rest is designed.

We report the diff, not a score:
  how many distinct claims each holds, at three points in the month;
  whether the ordinary-routine claim survives in each;
  how much text the two have in common;
  whether the rewrite arm is just reproducing its previous night's summary.

    python -m self_improve.compare_the_two_memory_formats --household hh_s2_t03
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re
from typing import Any, Dict, List, Optional, Sequence

from baselines.patrol.llm import LLMClient
from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold, period_of_day
from self_improve.looking import (FixedLookSchedule, TheHouseAsSeen, clock_to_seconds)
from self_improve.memory_notes import Notes
from self_improve.study_settings import LOCKED
from self_improve.write_the_notes import write_the_notes

LOOK_AT_THE_END_OF_DAY = 23 * 3600 + 30 * 60
PEEK_DAYS = (13, 18, 28)


def words_of(text: str) -> set:
    return set(re.findall(r"[a-z_0-9]+", (text or "").lower()))


def run_one_format(household: FrozenHousehold, how_memory_is_written: str,
                   client: LLMClient, out_dir: pathlib.Path, last_day: int,
                   settings=LOCKED) -> Dict[str, Any]:
    arm = f"the fixed schedule with {how_memory_is_written}"
    out_dir.mkdir(parents=True, exist_ok=True)
    eyes = TheHouseAsSeen(household, out_dir / "looks.jsonl", settings.granularity)
    schedule = FixedLookSchedule(household, settings.granularity,
                                 settings.fixed_schedule_kind, settings.budget_per_look,
                                 settings.visit_times, settings.rotation_seed)
    notes = Notes(out_dir / "notes.json", household.name, arm, how_memory_is_written)
    nightly: List[Dict[str, Any]] = []
    peeks: Dict[int, Dict[str, Any]] = {}

    for day in range(last_day + 1):
        looks_today = [eyes.look(schedule.targets_for(day, i), day,
                                 clock_to_seconds(when), "the fixed schedule")
                       for i, when in enumerate(settings.visit_times)]
        report = write_the_notes(notes, household, day,
                                 day * 86400 + LOOK_AT_THE_END_OF_DAY,
                                 looks_today, client)
        report["period"] = period_of_day(day)
        nightly.append(report)
        notes.save()
        if day in PEEK_DAYS:
            peeks[day] = {
                "period": period_of_day(day),
                "n_claims": len(notes.claims),
                "what_the_robot_can_read": notes.what_the_robot_can_read(
                    settings.retrieval_budget),
                "everything_written_down": (
                    "\n".join(c.as_plain_words() for c in notes.claims)
                    if notes.claims else (notes.newest_summary() or "")),
            }
            notes.snapshot_to(out_dir / f"notes_frozen_at_day_{day}.json")
    eyes.close()
    return {"arm": arm, "how_memory_is_written": how_memory_is_written,
            "schedule": schedule.describe(), "nightly": nightly, "peeks": peeks,
            "n_looks": len(eyes.looks),
            "n_sightings": len(eyes.sightings_so_far()),
            "n_absences_recorded": len(eyes.absences_so_far())}


def compare(rewrite: Dict[str, Any], incremental: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"per_peek": {}}
    for day in sorted(set(rewrite["peeks"]) & set(incremental["peeks"])):
        a = rewrite["peeks"][day]["everything_written_down"]
        b = incremental["peeks"][day]["everything_written_down"]
        wa, wb = words_of(a), words_of(b)
        out["per_peek"][day] = {
            "period": rewrite["peeks"][day]["period"],
            "wholesale_rewrite_characters": len(a),
            "incremental_edits_characters": len(b),
            "wholesale_rewrite_n_claims": rewrite["peeks"][day]["n_claims"],
            "incremental_edits_n_claims": incremental["peeks"][day]["n_claims"],
            "share_of_words_in_common": (len(wa & wb) / len(wa | wb)) if (wa | wb) else None,
            "how_similar_the_text_is": difflib.SequenceMatcher(None, a, b).ratio(),
        }
    nights = rewrite["nightly"]
    repeats = [n for n in nights if n.get("identical_to_last_night")]
    out["the_rewrite_arm"] = {
        "n_nights": len(nights),
        "n_nights_identical_to_the_night_before": len(repeats),
        "share_identical_to_the_night_before": len(repeats) / len(nights) if nights else None,
        "n_nights_the_model_call_failed": sum(1 for n in nights if n.get("model_call_failed")),
    }
    inights = incremental["nightly"]
    out["the_incremental_arm"] = {
        "n_nights": len(inights),
        "n_claims_at_the_end": inights[-1].get("n_claims_now") if inights else None,
        "n_nights_with_no_edit_at_all": sum(1 for n in inights if not n.get("n_edits_offered")),
        "total_added": sum(n.get("applied", {}).get("add", 0) for n in inights),
        "total_revised": sum(n.get("applied", {}).get("revise", 0) for n in inights),
        "total_evidence_attached": sum(n.get("applied", {}).get("record evidence", 0)
                                       for n in inights),
        "n_edits_rejected": sum(len(n.get("rejected") or ()) for n in inights),
        "n_nights_the_model_call_failed": sum(1 for n in inights if n.get("model_call_failed")),
    }
    concerns: List[str] = []
    late = out["per_peek"].get(28) or out["per_peek"].get(18)
    if late and late["how_similar_the_text_is"] > 0.6:
        concerns.append(
            f"the two formats' notes are {late['how_similar_the_text_is']:.0%} similar as "
            f"text: they are converging and the memory factor may not be separable")
    if out["the_rewrite_arm"]["share_identical_to_the_night_before"] and \
            out["the_rewrite_arm"]["share_identical_to_the_night_before"] > 0.5:
        concerns.append(
            "the rewrite arm mostly reproduces its previous night's summary, so it is "
            "not really rewriting and the contrast with incremental editing is weaker "
            "than the design assumes")
    if out["the_incremental_arm"]["total_revised"] == 0:
        concerns.append(
            "the incremental arm never revised a claim, so it is an append-only log "
            "rather than an edited store")
    if out["the_incremental_arm"]["n_nights_with_no_edit_at_all"] > 0.7 * len(inights):
        concerns.append("the incremental arm made no edit on most nights")
    out["concerns"] = concerns
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--household", default="hh_s2_t03")
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--last-day", type=int, default=28)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/memory_format_diff"))
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/self_improve"))
    args = parser.parse_args(argv)

    household = FrozenHousehold(args.banks / f"{args.household}.jsonl")
    client = LLMClient(args.cache)
    results = {}
    for how in ("wholesale rewrite", "incremental edits"):
        print(f"running {how} on {household.name} through day {args.last_day} ...",
              flush=True)
        results[how] = run_one_format(household, how, client,
                                      args.out / how.replace(" ", "_"), args.last_day)
    verdict = compare(results["wholesale rewrite"], results["incremental edits"])

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "diff.json").write_text(json.dumps(
        {"household": household.name, "runs": results, "comparison": verdict,
         "llm": {**client.stats, "model": client.model}}, indent=1))
    print()
    print(json.dumps(verdict, indent=1))
    print()
    print(f"model calls {client.stats['calls']}, cache hits {client.stats['cached']}, "
          f"{client.stats['seconds']:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
