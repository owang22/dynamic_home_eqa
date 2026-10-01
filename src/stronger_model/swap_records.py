"""Same record, other model: separate "reasons better" from "built a better record".

Each model chooses where the robot looks, so each log-only cell builds its own record, and a difference in
first-room-right mixes how a model READS a record with how good the record its own looking produced. The
independent audit of 2026-09-30 found exactly that mix (when newest and commonest sighting disagree, Qwen and
Sonnet both follow the newest 65 times; when they agree, Sonnet's record is right more often).

This replays a finished log-only cell from its cache (no model is called; every call must hit), records the exact
prompt behind each question's FIRST room choice (the call whose allowed-room enum still holds every room), checks
the replayed choice equals the room the cell opened first, and saves those prompts. `answer` then puts the same
prompts to another model and scores the first room against the true room. Only the first choice is swapped: what
happens after it depends on what the robot finds, so later choices are not comparable.

    PYTHONPATH=src python3 -m stronger_model.swap_records record --from qwen --household hh_s2_t03
    PYTHONPATH=src python3 -m stronger_model.swap_records answer --from qwen --by sonnet --household hh_s2_t03
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import tempfile

from baselines.patrol.llm import LLMClient
from self_improve.frozen_household import FrozenHousehold
from self_improve.overnight_wave import run_one_arm
from stronger_model.clients import ClaudeClient

BANKS = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks")
ARM = "log only, no notes"
CELLS = {"qwen": pathlib.Path("results/self_improve/wave_log_only/cells/log_only_no_notes"),
         "sonnet": pathlib.Path("results/stronger_model/claude_sonnet/cells/log_only_no_notes"),
         # the fresh-cache Qwen rerun of 1 Oct; the 29 Sep cells above turned out to be weak runs in the change window
         "qwen2": pathlib.Path("results/stronger_model/qwen38_plain_rerun2/cells/log_only_no_notes")}
OUT = pathlib.Path("results/stronger_model/swap")


def client_for(model: str):
    if model == "qwen":
        return LLMClient(pathlib.Path("llm_prior_cache/self_improve"))
    if model == "qwen2":
        return LLMClient(pathlib.Path("llm_prior_cache/stronger_model/qwen38_plain_fresh"))
    return ClaudeClient(pathlib.Path("llm_prior_cache/stronger_model/claude_sonnet"), model="sonnet")


class FollowTheCell:
    """Answers each call with what the finished cell actually did, so the replay walks the cell's own path
    without needing the cache. Room choices are fed from `rooms_opened` question by question; an answer call
    (schema with `location`) gets the cell's recorded place and confidence. Needed because the cache is
    last-writer-wins: on day 1 the log-only and log+notes prompts are byte-identical (both notes blocks are
    empty), the two Sonnet cells ran at once, Sonnet is not deterministic, and one cell's cache entry was
    overwritten by the other's answer - a cache replay then drifts off the path at the first such question."""

    def __init__(self, rows):
        self.rows, self.i, self.queue = rows, -1, []
        self.stats = {"calls": 0, "cached": 0}

    def complete(self, messages, schema, max_tokens):
        props = (schema or {}).get("properties", {})
        if "room" in props:
            if not self.queue:
                self.i += 1
                self.queue = list(self.rows[self.i]["rooms_opened"])
            return json.dumps({"why": "", "room": self.queue.pop(0)}), {}
        if "location" in props:
            r = self.rows[self.i]
            return json.dumps({"reasoning": "", "location": r["answer_place"], "confidence": r["confidence"]}), {}
        raise RuntimeError(f"a call this replay does not know how to answer: {list(props)}")


class Recorder:
    def __init__(self, inner):
        self.inner, self.calls = inner, []

    @property
    def stats(self):
        return self.inner.stats

    def complete(self, messages, schema, max_tokens):
        text, usage = self.inner.complete(messages, schema, max_tokens)
        if text is None:
            raise RuntimeError("replay missed the cache: this cell cannot be replayed exactly")
        self.calls.append({"messages": messages, "schema": schema, "max_tokens": max_tokens, "text": text})
        return text, usage


def is_first_choice(call, n_rooms):
    sch = call["schema"] or {}
    room = sch.get("properties", {}).get("room")
    return room is not None and len(room.get("enum", [])) == n_rooms


def record(src: str, hh: str) -> pathlib.Path:
    rows = [r for r in map(json.loads, open(CELLS[src] / hh / "searches.jsonl")) if r.get("kind") == "search"]
    rec = Recorder(FollowTheCell(rows))
    household = FrozenHousehold(BANKS / f"{hh}.jsonl")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="swap_replay_"))
    run_one_arm(household, ARM, rec, tmp / "cells" / "arm" / hh, 31, 8, 3, 0)
    again = [r for r in map(json.loads, open(tmp / "cells" / "arm" / hh / "searches.jsonl")) if r.get("kind") == "search"]
    for a, b in zip(rows, again):
        for k in ("question_id", "object_id", "true_room", "rooms_opened", "found_it"):
            if a[k] != b[k]:
                raise AssertionError(f"replay left the cell's path at {a['question_id']}: {k} {a[k]} != {b[k]}")
    if len(again) != len(rows):
        raise AssertionError(f"replay asked {len(again)} questions, the cell {len(rows)}")
    n_rooms = max(len((c["schema"] or {}).get("properties", {}).get("room", {}).get("enum", [])) for c in rec.calls)
    firsts = [c for c in rec.calls if is_first_choice(c, n_rooms)]
    if len(firsts) != len(rows):
        raise AssertionError(f"{len(firsts)} first-choice calls for {len(rows)} questions")
    out = OUT / f"prompts_from_{src}_{hh}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    mismatched = 0
    with open(out, "w") as f:
        for c, r in zip(firsts, rows):
            chose = json.loads(c["text"])["room"]
            mismatched += chose != r["rooms_opened"][0]
            f.write(json.dumps({"question_id": r["question_id"], "day": r["day"], "object_id": r["object_id"],
                                "is_a_mover": r["is_a_mover"], "true_room": r["true_room"],
                                "own_first_room": r["rooms_opened"][0], "messages": c["messages"],
                                "schema": c["schema"], "max_tokens": c["max_tokens"]}) + "\n")
    shutil.rmtree(tmp, ignore_errors=True)
    if mismatched:
        raise AssertionError(f"{mismatched} replayed first choices differ from the cell's own first room")
    print(f"{out}: {len(rows)} questions, replay matches the cell on every first room")
    return out


def answer(src: str, by: str, hh: str) -> None:
    client = client_for(by)
    rows = [json.loads(l) for l in open(OUT / f"prompts_from_{src}_{hh}.jsonl")]
    out = OUT / f"answers_from_{src}_by_{by}_{hh}.jsonl"
    with open(out, "w") as f:
        for r in rows:
            text, _ = client.complete(r["messages"], r["schema"], r["max_tokens"])
            room = json.loads(text)["room"] if text else None
            why = json.loads(text)["why"] if text else None
            f.write(json.dumps({k: r[k] for k in ("question_id", "day", "object_id", "is_a_mover", "true_room",
                                                   "own_first_room")} | {"room": room, "why": why}) + "\n")
            f.flush()
    print(out, client.stats)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("step", choices=["record", "answer"])
    p.add_argument("--from", dest="src", required=True, choices=list(CELLS))
    p.add_argument("--by", choices=list(CELLS))
    p.add_argument("--household", required=True)
    a = p.parse_args(argv)
    if a.step == "record":
        record(a.src, a.household)
    else:
        answer(a.src, a.by, a.household)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
