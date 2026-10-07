"""Opus against Qwen on the same sightings: hypotheses, notes, and where to look first.

Oliver, 2026-10-03: does Opus make smarter decisions, summarise memory better and propose better
hypotheses than Qwen? Every comparison here holds the sightings fixed: both models see exactly what the
robot saw in the 50-day two-illness Qwen cell (see opus_beliefs.py), so a difference is the model's.

  walk    Re-walk the cell with one model's nightly notes, and save the prompt behind every question's FIRST
          room choice (the call whose room list still holds every room). The notes calls are replayed from
          cache and must all hit: Qwen's from the cell's own cache (exact: the replayed notes equal the
          cell's), Opus's from opus_beliefs. With --memory qwen it also asks plain Qwen the five nightly
          belief questions, with Qwen's own notes, so both models' beliefs can be scored the same way.
  answer  Put the saved first-choice prompts for the chosen days to one model and score the first room
          against the true room. Two models x two note-writers gives the 2x2: who chooses, whose notes.

    PYTHONPATH=src python3 -m stronger_model.opus_vs_qwen walk --memory qwen --household hh_s2_t03
    PYTHONPATH=src python3 -m stronger_model.opus_vs_qwen answer --memory opus --by qwen --household hh_s2_t03
"""
from __future__ import annotations

import argparse
import json
import pathlib
import tempfile
from concurrent.futures import ThreadPoolExecutor

from baselines.patrol.llm import LLMClient
from self_improve.frozen_household import FrozenHousehold
from self_improve.overnight_wave import run_one_arm
from stronger_model.clients import ClaudeClient
from stronger_model.opus_beliefs import (ARM, BANKS, BELIEF_SCHEMA, BELIEF_SYSTEM, BUDGET, CACHE, CELLS,
                                         LAST_DAY, QPD, SEED, belief_prompt)
from stronger_model.swap_records import FollowTheCell

OUT = pathlib.Path("results/stronger_model/opus_vs_qwen")
QWEN_CELL_CACHE = pathlib.Path("llm_prior_cache/self_improve")
QWEN_FRESH = pathlib.Path("llm_prior_cache/stronger_model/qwen_vs_opus")  # never the shared cache: fresh answers
# settled, first onset, first return, second onset, second return
WINDOWS = [12, 13, 14, 15, 16, 24, 25, 26, 32, 33, 34, 42, 43, 44]
WINDOW_NAME = {12: "settled", 13: "settled", 14: "onset 1", 15: "onset 1", 16: "onset 1",
               24: "return 1", 25: "return 1", 26: "return 1", 32: "onset 2", 33: "onset 2", 34: "onset 2",
               42: "return 2", 43: "return 2", 44: "return 2"}


def notes_client(memory: str):
    if memory == "qwen":
        c = LLMClient(QWEN_CELL_CACHE)
    else:
        c = ClaudeClient(CACHE / "claude_opus", model="opus")
    c.replay_only = True
    return c


class Walk(FollowTheCell):
    def __init__(self, rows, notes, n_rooms, believer=None, beliefs_path=None):
        super().__init__(rows)
        self.notes, self.n_rooms, self.believer, self.beliefs_path = notes, n_rooms, believer, beliefs_path
        self.firsts, self.stats = [], {"calls": 0}

    def complete(self, messages, schema, max_tokens):
        props = (schema or {}).get("properties", {})
        if "room" in props:
            new_question = not self.queue
            text, u = super().complete(messages, schema, max_tokens)
            if new_question:
                if len(props["room"]["enum"]) != self.n_rooms:
                    raise AssertionError("a question's first call did not offer every room")
                self.firsts.append({"messages": messages, "schema": schema, "max_tokens": max_tokens})
            return text, u
        if "location" in props:
            return super().complete(messages, schema, max_tokens)
        user = next(m["content"] for m in messages if m["role"] == "user")
        if self.believer is not None:
            day = int(user.split("It is the end of day ")[1].split(".")[0])
            if day >= 1:
                text, _ = self.believer.complete([{"role": "system", "content": BELIEF_SYSTEM},
                                                  {"role": "user", "content": belief_prompt(user)}],
                                                 BELIEF_SCHEMA, 8000)
                with open(self.beliefs_path, "a") as f:
                    f.write(json.dumps({"day": day, "beliefs": json.loads(text) if text else None}) + "\n")
        text, u = self.notes.complete(messages, schema, max_tokens)
        if text is None:
            raise RuntimeError("a nightly notes call missed the cache: these notes cannot be replayed exactly")
        return text, u


def walk(memory: str, hh: str) -> None:
    rows = [r for r in map(json.loads, open(CELLS / hh / "searches.jsonl")) if r.get("kind") == "search"]
    household = FrozenHousehold(BANKS / f"{hh}.jsonl")
    out = OUT / f"memory_{memory}"
    out.mkdir(parents=True, exist_ok=True)
    believer, beliefs_path = None, None
    if memory == "qwen":
        believer = LLMClient(QWEN_FRESH / "beliefs")
        beliefs_path = out / f"beliefs_{hh}.jsonl"
        beliefs_path.write_text("")
    w = Walk(rows, notes_client(memory), len(household.rooms), believer, beliefs_path)
    cell = pathlib.Path(tempfile.mkdtemp(prefix="vs_walk_")) / "cells" / "walk" / hh
    run_one_arm(household, ARM, w, cell, LAST_DAY, QPD, BUDGET, SEED)
    again = [r for r in map(json.loads, open(cell / "searches.jsonl")) if r.get("kind") == "search"]
    for a, b in zip(rows, again):
        for k in ("question_id", "rooms_opened", "found_it"):
            if a[k] != b[k]:
                raise AssertionError(f"walk left the cell's path at {a['question_id']}: {k}")
    if not (len(again) == len(rows) == len(w.firsts)):
        raise AssertionError(f"{len(rows)} questions, {len(again)} walked, {len(w.firsts)} first choices")
    if memory == "qwen":
        a = [c["statement"] for c in json.load(open(CELLS / hh / "notes.json"))["claims"]]
        b = [c["statement"] for c in json.load(open(cell / "notes.json"))["claims"]]
        if a != b:
            raise AssertionError("replayed Qwen notes differ from the cell's")
    (out / f"notes_{hh}.json").write_text((cell / "notes.json").read_text())
    with open(out / f"prompts_{hh}.jsonl", "w") as f:
        for c, r in zip(w.firsts, rows):
            f.write(json.dumps({k: r[k] for k in ("question_id", "day", "time", "object_id", "is_a_mover",
                                                   "true_room", "rooms_opened")} | c) + "\n")
    print(f"{hh} memory={memory}: {len(rows)} questions walked, path and notes checked; prompts saved")


def answer(memory: str, by: str, hh: str, days, parallel: int, tag: str) -> None:
    rows = [json.loads(l) for l in open(OUT / f"memory_{memory}" / f"prompts_{hh}.jsonl")]
    rows = [r for r in rows if r["day"] in days]
    if by == "qwen":
        client = LLMClient(QWEN_FRESH / ("first_choice" + (f"_{tag}" if tag else "")))
    else:
        client = ClaudeClient(CACHE.parent / ("opus_vs_qwen_first_choice" + (f"_{tag}" if tag else "")), model="opus")
    out = OUT / (f"answers_{memory}_notes_by_{by}" + (f"_{tag}" if tag else ""))
    out.mkdir(parents=True, exist_ok=True)

    def one(r):
        text, _ = client.complete(r["messages"], r["schema"], r["max_tokens"])
        obj = json.loads(text) if text else {}
        return {k: r[k] for k in ("question_id", "day", "time", "object_id", "is_a_mover", "true_room")} | {
            "window": WINDOW_NAME.get(r["day"], ""), "cell_first_room": r["rooms_opened"][0],
            "room": obj.get("room"), "why": obj.get("why"), "right": obj.get("room") == r["true_room"]}

    with ThreadPoolExecutor(parallel) as ex:
        res = list(ex.map(one, rows))
    with open(out / f"{hh}.jsonl", "w") as f:
        for x in res:
            f.write(json.dumps(x) + "\n")
    n = len(res)
    print(f"{hh} {memory} notes, chosen by {by}: {sum(x['right'] for x in res)}/{n} first room right; "
          f"lost {sum(x['room'] is None for x in res)}; {json.dumps(client.stats)}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("step", choices=["walk", "answer"])
    p.add_argument("--memory", required=True, choices=["qwen", "opus"])
    p.add_argument("--by", choices=["qwen", "opus"])
    p.add_argument("--household", required=True)
    p.add_argument("--days", default=",".join(map(str, WINDOWS)))
    p.add_argument("--parallel", type=int, default=4)
    p.add_argument("--tag", default="", help="a repeat: its own cache and output")
    a = p.parse_args(argv)
    if a.step == "walk":
        walk(a.memory, a.household)
    else:
        answer(a.memory, a.by, a.household, {int(d) for d in a.days.split(",")}, a.parallel, a.tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
