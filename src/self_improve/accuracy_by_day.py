"""Accuracy on every day of the month, for a memory that keeps learning and one
that stopped.

The figure this produces has four lines and the whole claim of the paper is in
their SHAPES rather than in any single number:

  unfrozen        day D's questions are answered with the notes as they stood at
                  the end of night D-1. This memory keeps learning. Expected to
                  drop when the resident falls ill on day 14, climb back through
                  the spell as the notes are revised, drop again when ordinary
                  life returns on day 24, and climb again.

  zero looks      day D's questions, for every D, are answered with the notes as
                  they stood at the end of night 0 - the one walkthrough of the
                  whole house that every arm is given before the study starts.
                  The robot then never looks again. The cleanest baseline in the
                  figure: whatever shape it has comes from the WORLD moving away
                  from and back to what one walkthrough saw, not from anything the
                  robot did.

  frozen at 13    day D's questions, for every D, are answered with the notes as
                  they stood at the end of night 13 - the last ordinary night -
                  and nothing after. Expected to drop on day 14 and stay flat and
                  low, then BOUNCE BACK on day 24, because the world returns to
                  the routine this memory still holds. If that bounce is there it
                  is the paper's point: the old routine was never wrong, only
                  temporarily inapplicable.

Each line is run for both ways of writing the notes, so six lines in all.

NO NIGHTLY WRITING IS REDONE. The notes carry their own history and the memory as
of any day is reconstructed from it:

  wholesale rewrite   `nightly_summaries` holds one entry per night with its `day`,
                      so the memory as of day D is that night's summary.

  incremental edits   each claim carries `first_written_day` and a
                      `revision_history` whose entries snapshot what the claim USED
                      TO say. `were_the_nights_vacuous.statement_as_of` is the
                      function of record for this and it is what is used here.
                      Reconstructing from `first_written_day` plus the CURRENT
                      wording is wrong: it misses every revision and makes the store
                      look as though it never changed its mind.

                      The same reconstruction is applied to holds_under, status,
                      standing and last_revised_day, and the supporting and
                      contradicting observation ids are filtered to the ones whose
                      sighting had happened by day D. Without that filter a claim
                      would be shown on day 5 with the evidence count it only
                      reached on day 28, which is information from the future
                      leaking into the prompt.

Sampling. Eight questions per household per day per cell, taken EVENLY ACROSS THE
DAY rather than as the first eight. The bank asks 24 a day in time order, so a
`[:8]` slice would be a measurement of the morning; that exact fault has already
cost this project a set of numbers. The sample depends only on the household and
the day, so all six lines answer the identical questions.

Scoring is reported at both levels - naming the exact shelf, and naming only the
right room - and split by whether the disruption ever moved that object.

    python -m self_improve.accuracy_by_day --households hh_s0_t03 --formats wholesale_rewrite
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.patrol.llm import CONF_SCHEMA, LLMClient, parse_conf
from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold, period_of_day
from self_improve.frozen_memory_test import (question_prompt_and_what_was_read,
                                             questions_in_the_window, sanity_assay)
from self_improve.memory_notes import Claim, Notes
from self_improve.score_at_both_levels import room_of
from self_improve.study_settings import LOCKED
from self_improve.were_the_nights_vacuous import statement_as_of
from self_improve.which_objects_moved import describe_one_household

DEFAULT_SWEEP = pathlib.Path("results/self_improve/memory_factor_v1")
DEFAULT_OUT = pathlib.Path("results/self_improve/accuracy_by_day")

FORMAT_OF_DIR = {"wholesale_rewrite": "wholesale rewrite",
                 "incremental_edits": "incremental edits"}

UNFROZEN = "unfrozen"
FROZEN = "frozen at day 13"
ZERO_LOOKS = "zero looks after the warm start"
FREEZE_DAY = 13

# Which night each condition's memory comes from. `unfrozen` is the only one that
# moves with the day being answered.
#
# `zero looks after the warm start` is the sensing control Oliver asked for: the
# robot gets the one walkthrough of the whole house on day 0 at 18:00 that every
# arm gets, and then never looks again. Night 0 IS that walkthrough written up, so
# the control costs no new nightly writing - it is the day-0 notes answering every
# day, exactly as the frozen line is the day-13 notes answering every day.
#
# The two gaps this buys are the sensing argument of the paper:
#   frozen at 13 minus zero looks  = what thirteen days of one room a day is worth
#   unfrozen minus frozen at 13    = what continuing to look and revise is worth
FREEZE_NIGHT = {FROZEN: FREEZE_DAY, ZERO_LOOKS: 0}

ALL_OBJECTS = "all objects"
MOVERS = "objects the disruption moved"
STAYERS = "objects that never moved"


# ------------------------------------------------- reconstructing the memory --


def sighting_day(looks_file: pathlib.Path) -> Dict[str, int]:
    """observation id -> the day it was made, for both sightings and the looks
    themselves. Used to strip evidence a claim had not yet collected."""
    out: Dict[str, int] = {}
    if not looks_file.exists():
        return out
    for line in looks_file.open():
        row = json.loads(line)
        if row.get("kind") != "look":
            continue
        day = int(row.get("day", 0))
        if row.get("look_id"):
            out[row["look_id"]] = day
        for sighting in row.get("sightings", []):
            out[sighting["observation_id"]] = int(sighting.get("day", day))
    return out


def claim_as_of(raw: Dict[str, Any], day: int,
                day_of_observation: Dict[str, int]) -> Optional[Claim]:
    """One claim exactly as it stood at the end of night `day`, or None if it had
    not been written yet.

    The wording comes from `statement_as_of`, which is the function of record. The
    other three revisable fields are recovered from the same `was` snapshot, so the
    claim is not shown with a day-28 status attached to day-5 wording.
    """
    if int(raw.get("first_written_day", 0)) > day:
        return None
    statement = statement_as_of(raw, day)
    if statement is None:
        return None
    history = sorted((r for r in (raw.get("revision_history") or [])),
                     key=lambda r: (int(r.get("day", 0)), int(r.get("time", 0))))
    later = [r for r in history if int(r.get("day", 0)) > day]
    earlier = [r for r in history if int(r.get("day", 0)) <= day]
    if later:
        was = later[0].get("was") or {}
        holds_under = was.get("holds_under", raw["holds_under"])
        status = was.get("status", raw["status"])
        standing = was.get("standing", raw.get("standing", "still standing"))
    else:
        holds_under = raw["holds_under"]
        status = raw["status"]
        standing = raw.get("standing", "still standing")
    if earlier:
        last_day = int(earlier[-1].get("day", 0))
        last_time = int(earlier[-1].get("time", 0))
    else:
        last_day = int(raw.get("first_written_day", 0))
        last_time = 0

    def by_then(ids: Sequence[str]) -> List[str]:
        # An id we have no day for is kept: dropping it silently would understate
        # the evidence rather than merely failing to date it.
        return [i for i in ids if day_of_observation.get(i, -1) <= day]

    return Claim(claim_id=raw["claim_id"], statement=statement, holds_under=holds_under,
                 supporting_observation_ids=by_then(raw.get("supporting_observation_ids") or []),
                 contradicting_observation_ids=by_then(
                     raw.get("contradicting_observation_ids") or []),
                 last_revised_day=last_day, last_revised_time=last_time,
                 status=status, standing=standing,
                 first_written_day=int(raw.get("first_written_day", 0)),
                 revision_history=[r for r in history if int(r.get("day", 0)) <= day])


class MemoryHistory:
    """One cell's notes.json, able to hand back the memory as of any day."""

    def __init__(self, cell_dir: pathlib.Path) -> None:
        self.cell_dir = cell_dir
        self.raw = json.loads((cell_dir / "notes.json").read_text())
        self.household = self.raw["household"]
        self.arm = self.raw["arm"]
        self.how_memory_is_written = self.raw["how_memory_is_written"]
        self.summaries = sorted(self.raw.get("nightly_summaries") or [],
                                key=lambda r: int(r["day"]))
        self.claims_raw = self.raw.get("claims") or []
        self.day_of_observation = sighting_day(cell_dir / "looks.jsonl")
        if self.summaries:
            self.last_night_written = int(self.summaries[-1]["day"])
        elif self.claims_raw:
            self.last_night_written = int(self.raw.get("written_up_to_day", -1))
        else:
            self.last_night_written = -1

    def as_of(self, day: int) -> Tuple[Notes, int]:
        """(the memory at the end of night `day`, the night it actually comes from).

        The two differ when `day` is after the last night that was written: the
        notes stop at night 28 while the bank asks questions to day 31, so days 30
        and 31 are answered with a memory that is one and two nights stale. That
        is recorded on every row rather than hidden.
        """
        effective = min(day, self.last_night_written)
        notes = Notes(self.cell_dir / "__not_written__.json", self.household, self.arm,
                      self.how_memory_is_written)
        if self.how_memory_is_written == "wholesale rewrite":
            kept = [s for s in self.summaries if int(s["day"]) <= effective]
            notes.nightly_summaries = kept
            notes.written_up_to_day = int(kept[-1]["day"]) if kept else -1
        else:
            claims = [claim_as_of(c, effective, self.day_of_observation)
                      for c in self.claims_raw]
            notes.claims = [c for c in claims if c is not None]
            notes.written_up_to_day = effective
        return notes, effective


# ------------------------------------------------------------- the questions --


def spread_across_the_hours(questions: Sequence[dict], how_many: int) -> List[dict]:
    """A capped sample taken EVENLY ACROSS ONE DAY, not the first N.

    The day's 24 questions are in time order. `questions[:8]` would take the first
    third of the day and every number built on it would be a statement about the
    morning; that is the fault that has already been found and repaired once in
    `spread_across_the_days`, which strides over days. This is its within-day twin.
    """
    ordered = sorted(questions, key=lambda q: (q["t_query"], q["question_id"]))
    n = len(ordered)
    if how_many >= n:
        return ordered
    if how_many <= 1:
        return [ordered[n // 2]]
    wanted = [round(i * (n - 1) / (how_many - 1)) for i in range(how_many)]
    taken: List[dict] = []
    used: set = set()
    for index in wanted:
        while index in used and index < n - 1:
            index += 1
        if index in used:
            index = next((j for j in range(n) if j not in used), None)
            if index is None:
                break
        used.add(index)
        taken.append(ordered[index])
    return sorted(taken, key=lambda q: (q["t_query"], q["question_id"]))


def questions_by_day(household: FrozenHousehold, days: Sequence[int],
                     how_many: int) -> Dict[int, List[dict]]:
    """The same sample for every line: it depends only on the household and day."""
    return {day: spread_across_the_hours(questions_in_the_window(household, [day]),
                                         how_many)
            for day in days}


def movers_and_stayers(household: FrozenHousehold) -> Dict[str, bool]:
    """object id -> did the disruption move it.

    Measured over daytime hours, which is the study's locked choice
    (study_settings.exclusion_rule_measured); at question times s4 has only one
    mover because the question stream does not sample it at the hours it moved.
    """
    description = describe_one_household(household)
    return {o["object_id"]: bool(o[LOCKED.exclusion_rule_measured]["moved"])
            for o in description["objects"]}


# ----------------------------------------------------------------- answering --


def answer_one_day(household: FrozenHousehold, notes: Notes, questions: Sequence[dict],
                   client: LLMClient, read_budget_lines: int) -> List[Dict[str, Any]]:
    """Put one day's questions to one frozen memory. No looking happens here: the
    notes are read-only and nothing is written back."""
    allowed = set(household.places)
    out: List[Dict[str, Any]] = []
    for question in questions:
        messages, was_read = question_prompt_and_what_was_read(
            household, notes, question, read_budget_lines)
        text, _ = client.complete(messages, CONF_SCHEMA, max_tokens=400)
        place, confidence, reasoning, status = parse_conf(text, allowed)
        true_place = household.true_place_for_question(question)
        out.append({
            "question_id": question["question_id"],
            "object_id": question["object_id"],
            "object_class": question.get("object_class", ""),
            "day": question["day_index"],
            "time": question["t_query"],
            "answer_place": place,
            "true_place": true_place,
            "answer_room": room_of(household, place),
            "true_room": room_of(household, true_place),
            "right_shelf": None if place is None else place == true_place,
            "right_room": None if place is None else (
                room_of(household, place) == room_of(household, true_place)),
            "confidence": confidence,
            "reasoning": reasoning,
            "parse_status": status,
            "n_lines_of_notes_available": was_read.n_lines_available,
            "n_lines_of_notes_shown": was_read.n_lines_shown,
            "read_budget_bit": was_read.budget_bit,
        })
    return out


def rows_for_one_day(answers: Sequence[Dict[str, Any]], moved: Dict[str, bool],
                     common: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One tidy row per slice. Counts, never pre-aggregated shares alone."""
    slices = {
        ALL_OBJECTS: list(answers),
        MOVERS: [a for a in answers if moved.get(a["object_id"])],
        STAYERS: [a for a in answers if not moved.get(a["object_id"], True)],
    }
    rows = []
    for name, group in slices.items():
        scored = [a for a in group if a["right_shelf"] is not None]
        row = dict(common)
        row.update({
            "slice": name,
            "n_asked": len(group),
            "n_scored": len(scored),
            "n_unparsed": len(group) - len(scored),
            "n_right_shelf": sum(1 for a in scored if a["right_shelf"]),
            "n_right_room": sum(1 for a in scored if a["right_room"]),
            "share_right_shelf": (sum(1 for a in scored if a["right_shelf"]) / len(scored))
                                 if scored else None,
            "share_right_room": (sum(1 for a in scored if a["right_room"]) / len(scored))
                                if scored else None,
            "mean_lines_of_notes_available": (
                sum(a["n_lines_of_notes_available"] for a in group) / len(group))
                if group else None,
            "share_where_the_read_budget_bit": (
                sum(1 for a in group if a["read_budget_bit"]) / len(group)) if group else None,
        })
        rows.append(row)
    return rows


# ---------------------------------------------------------------------- run --


def run_one_cell(household: FrozenHousehold, cell_dir: pathlib.Path, format_name: str,
                 client: LLMClient, days: Sequence[int], per_day: int,
                 read_budget_lines: int, out_dir: pathlib.Path,
                 conditions: Sequence[str]) -> Dict[str, Any]:
    history = MemoryHistory(cell_dir)
    if history.how_memory_is_written != format_name:
        raise ValueError(f"{cell_dir}: notes say {history.how_memory_is_written!r}, "
                         f"expected {format_name!r}")
    sample = questions_by_day(household, days, per_day)
    moved = movers_and_stayers(household)

    out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{household.name}__{format_name.replace(' ', '_')}"
    if len(conditions) < 2:
        # a process running one condition only must not overwrite the other's part
        tag += "__" + conditions[0].replace(" ", "_")
    rows_path = out_dir / "parts" / f"{tag}.rows.jsonl"
    answers_path = out_dir / "parts" / f"{tag}.answers.jsonl"
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    rows_file = rows_path.open("w")
    answers_file = answers_path.open("w")

    assays: Dict[str, Any] = {}
    n_rows = 0
    started = time.time()
    for condition in conditions:
        for day in days:
            questions = sample[day]
            if not questions:
                continue
            wanted_night = ((day - 1) if condition == UNFROZEN
                            else FREEZE_NIGHT[condition])
            notes, from_night = history.as_of(wanted_night)
            answers = answer_one_day(household, notes, questions, client,
                                     read_budget_lines)
            common = {
                "household": household.name,
                "day": day,
                "period": period_of_day(day),
                "memory_format": format_name,
                "condition": condition,
                "notes_wanted_from_night": wanted_night,
                "notes_actually_from_night": from_night,
                "notes_stale_by_nights": wanted_night - from_night,
                "n_claims_or_summary_lines": (
                    len(notes.claims) if notes.claims
                    else len((notes.newest_summary() or "").splitlines())),
                "read_budget_lines": read_budget_lines,
                "questions_per_day_asked_for": per_day,
            }
            for row in rows_for_one_day(answers, moved, common):
                rows_file.write(json.dumps(row) + "\n")
                n_rows += 1
            for answer in answers:
                answer.update({k: common[k] for k in
                               ("household", "memory_format", "condition",
                                "notes_actually_from_night")})
                answer["object_moved_in_the_disruption"] = moved.get(answer["object_id"])
                answers_file.write(json.dumps(answer) + "\n")
            rows_file.flush()
            answers_file.flush()
            if condition not in assays:
                # the first day of each condition, before anything is believed
                assays[condition] = sanity_assay({
                    "answers": [{"answer_place": a["answer_place"]} for a in answers],
                    "n_unparsed": sum(1 for a in answers if a["right_shelf"] is None)})
            print(f"{household.name} | {format_name:18s} | {condition:16s} | day {day:2d} "
                  f"| notes from night {from_night:2d} | "
                  f"{sum(1 for a in answers if a['right_shelf']):d}/{len(answers)} shelf, "
                  f"{sum(1 for a in answers if a['right_room']):d}/{len(answers)} room",
                  flush=True)
    rows_file.close()
    answers_file.close()
    report = {"cell": tag, "n_rows": n_rows, "sanity_assay_on_the_first_day": assays,
              "seconds": round(time.time() - started, 1),
              "last_night_written": history.last_night_written,
              "llm": dict(client.stats)}
    (out_dir / "parts" / f"{tag}.report.json").write_text(json.dumps(report, indent=1))
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep", type=pathlib.Path, default=DEFAULT_SWEEP)
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/self_improve"))
    parser.add_argument("--households", nargs="+", default=None)
    parser.add_argument("--formats", nargs="+", default=list(FORMAT_OF_DIR),
                        choices=list(FORMAT_OF_DIR))
    parser.add_argument("--conditions", nargs="+",
                        default=[UNFROZEN, FROZEN, ZERO_LOOKS],
                        choices=[UNFROZEN, FROZEN, ZERO_LOOKS])
    parser.add_argument("--days", type=int, nargs="+", default=list(range(1, 32)))
    parser.add_argument("--per-day", type=int, default=8)
    parser.add_argument("--read-budget-lines", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true",
                        help="reconstruct the memory for every day and print what the "
                             "prompt would read, without calling the model")
    args = parser.parse_args(argv)

    budget = LOCKED.read_budget_lines if args.read_budget_lines is None \
        else args.read_budget_lines
    names = args.households or [p.name for p in sorted(args.sweep.glob("hh_s*"))]
    client = LLMClient(args.cache)

    for name in names:
        household = FrozenHousehold(args.banks / f"{name}.jsonl")
        for directory in args.formats:
            cell_dir = args.sweep / name / directory
            if not (cell_dir / "notes.json").exists():
                print(f"no notes at {cell_dir}", file=sys.stderr)
                continue
            if args.dry_run:
                dry_run(household, cell_dir, args.days, args.per_day, budget)
                continue
            report = run_one_cell(household, cell_dir, FORMAT_OF_DIR[directory], client,
                                  args.days, args.per_day, budget, args.out,
                                  args.conditions)
            print(json.dumps(report["sanity_assay_on_the_first_day"], indent=1),
                  flush=True)
    print(f"model calls {client.stats['calls']}, cache hits {client.stats['cached']}",
          flush=True)
    return 0


def dry_run(household: FrozenHousehold, cell_dir: pathlib.Path, days: Sequence[int],
            per_day: int, budget: int) -> None:
    """Prove the reconstruction changes with the day before a single token is spent."""
    history = MemoryHistory(cell_dir)
    sample = questions_by_day(household, days, per_day)
    seen: List[str] = []
    for day in days:
        notes, from_night = history.as_of(day - 1)
        text = notes.what_the_robot_can_read(budget).text
        seen.append(text)
        questions = sample[day]
        times = [q["t_query"] % 86400 // 3600 for q in questions]
        print(f"{household.name} {cell_dir.name} day {day:2d} <- night {from_night:2d} | "
              f"{len(questions)} questions at hours {times} | "
              f"{len(notes.claims)} claims / {len(notes.nightly_summaries)} summaries | "
              f"first line: {text.splitlines()[0][:90] if text else '(none)'}")
    distinct = len(set(seen))
    print(f"  -> {distinct} distinct reconstructed memories across {len(days)} days "
          f"({'GOOD' if distinct > 1 else 'BROKEN: the memory never changes'})")


if __name__ == "__main__":
    raise SystemExit(main())
