"""What Opus believes about the people, night by night, through two illness spells.

Oliver, 2026-10-03: can a Claude model asked only to answer questions form hypotheses about the people
in the home and their routines, update them when an illness strikes, and what does it do when the illness
comes back?

The record is held fixed. This walks a finished cell of the 50-day two-illness run (Qwen, "the log and
notes about the routine": resident ill on days 14-23 and 32-41, back on 24 and 42) and answers every room
choice and every answer from what that cell actually did, so the robot looks into exactly the same rooms
at exactly the same times and Opus sees exactly Qwen's sightings. Only the nightly call changes hands:

  notes    the arm's own nightly notes prompt goes to Opus (one fresh `claude -p`, no tools, no settings),
           so Opus keeps its own notes across the 50 nights and sees them each night as Qwen saw its own.
  beliefs  before the notes call, the same prompt (today's looks + its notes as they stand) goes to Opus
           with the edit instructions replaced by five questions about the people. The questions are
           the same every night, from night 1, and say nothing about illness or any change, so they carry
           no information about when anything happens.

The walk is checked against the cell question by question (same rooms opened, same finds), like
swap_records.record. Nothing here changes what is scored; the first-guess step is separate.

    PYTHONPATH=src python3 -m stronger_model.opus_beliefs --household hh_s2_t03
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

from self_improve.frozen_household import FrozenHousehold
from self_improve.overnight_wave import run_one_arm
from stronger_model.clients import ClaudeClient
from stronger_model.swap_records import FollowTheCell

ARM = "the log and notes about the routine"
CELLS = pathlib.Path("results/self_improve/wave_the_second_illness/cells/the_log_and_notes_about_the_routine")
BANKS = pathlib.Path("results/self_improve/varied_homes/all_generated_v2_twice/banks")
OUT = pathlib.Path("results/stronger_model/opus_beliefs")
CACHE = pathlib.Path("llm_prior_cache/stronger_model/claude_opus_beliefs")
LAST_DAY, QPD, BUDGET, SEED = 49, 24, 3, 0

MEMORY_HEADER = "YOUR MEMORY AS IT STANDS:"
EDIT_INSTRUCTIONS = "YOUR MEMORY is a list of separate notes"

BELIEF_QUESTIONS = """Tonight, before you write any notes, answer five questions about the people who live here. Answer from what you saw today and what your memory says. Write plain sentences. If you do not know, say so.

1. routines: for each person, what does a normal day look like for them, as you understand it now? Where are they at different times, and what do they do with their things?
2. anything_changed: has anything about anyone's days changed compared with before? If yes, who, what changed, and since about which day.
3. why: if something changed, what do you think is the reason? Give your best guess and how sure you are.
4. happened_before: has anything like the present pattern happened before in this home? If yes, when, and how did it end?
5. expect_tomorrow: what do you expect each person to do tomorrow, and how long do you expect the present pattern to last?"""

BELIEF_SCHEMA = {
    "type": "object",
    "properties": {k: {"type": "string", "maxLength": 6000}
                   for k in ("routines", "anything_changed", "why", "happened_before", "expect_tomorrow")},
    "required": ["routines", "anything_changed", "why", "happened_before", "expect_tomorrow"],
    "additionalProperties": False,
}
BELIEF_SYSTEM = ("You are a robot in somebody's home. At the end of each day you say what you believe about the "
                 "people who live there. Answer with JSON only.")


def belief_prompt(notes_user: str) -> str:
    """The notes prompt with its edit instructions swapped for the five questions. Everything the note
    writer sees - who lives here, the rooms, today's looks, its memory - is kept word for word."""
    cut = notes_user.index(EDIT_INSTRUCTIONS)
    if MEMORY_HEADER not in notes_user[:cut]:
        raise ValueError("the notes prompt no longer has its memory block where expected")
    return notes_user[:cut].rstrip() + "\n\n" + BELIEF_QUESTIONS


class OpusAtNight(FollowTheCell):
    def __init__(self, rows, opus: ClaudeClient, beliefs_path: pathlib.Path):
        super().__init__(rows)
        self.opus, self.beliefs_path = opus, beliefs_path
        self.stats = opus.stats

    def complete(self, messages, schema, max_tokens):
        props = (schema or {}).get("properties", {})
        if "room" in props or "location" in props:
            return super().complete(messages, schema, max_tokens)
        if "edits" not in props:
            raise RuntimeError(f"a call this walk does not know how to answer: {list(props)}")
        user = next(m["content"] for m in messages if m["role"] == "user")
        day = int(re.search(r"It is the end of day (\d+)\.", user).group(1))
        if day >= 1:
            text, _ = self.opus.complete([{"role": "system", "content": BELIEF_SYSTEM},
                                          {"role": "user", "content": belief_prompt(user)}], BELIEF_SCHEMA, 4000)
            with open(self.beliefs_path, "a") as f:
                f.write(json.dumps({"day": day, "beliefs": json.loads(text) if text else None}) + "\n")
        return self.opus.complete(messages, schema, max_tokens)


def run(hh: str, model: str, effort: str | None) -> None:
    rows = [r for r in map(json.loads, open(CELLS / hh / "searches.jsonl")) if r.get("kind") == "search"]
    tag = f"claude_{model}" + (f"_{effort}" if effort else "")
    out = OUT / tag / "cells" / "walk" / hh
    out.mkdir(parents=True, exist_ok=True)
    beliefs = out / "beliefs.jsonl"
    beliefs.write_text("")
    opus = ClaudeClient(CACHE / tag, model=model, effort=effort)
    client = OpusAtNight(rows, opus, beliefs)
    run_one_arm(FrozenHousehold(BANKS / f"{hh}.jsonl"), ARM, client, out, LAST_DAY, QPD, BUDGET, SEED)
    again = [r for r in map(json.loads, open(out / "searches.jsonl")) if r.get("kind") == "search"]
    if len(again) != len(rows):
        raise AssertionError(f"walk asked {len(again)} questions, the cell {len(rows)}")
    for a, b in zip(rows, again):
        for k in ("question_id", "object_id", "true_room", "rooms_opened", "found_it"):
            if a[k] != b[k]:
                raise AssertionError(f"walk left the cell's path at {a['question_id']}: {k} {a[k]} != {b[k]}")
    (out / "backend.json").write_text(json.dumps({"model": model, "effort": effort, "cache": str(CACHE / tag),
                                                  "walked_cell": str(CELLS / hh), "stats": opus.stats,
                                                  "path_check": f"{len(rows)} questions match the cell"}, indent=1))
    print(hh, "walk matches the cell on every question;", json.dumps(opus.stats))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--household", required=True)
    p.add_argument("--model", default="opus")
    p.add_argument("--effort", default=None)
    a = p.parse_args(argv)
    run(a.household, a.model, a.effort)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
