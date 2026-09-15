"""The log-reader arm, offline: a stub client stands in for the served
model. Checks the plumbing (decision relayed through predict/decide,
senses land in the log and the budget), the information condition (no
object the robot has not seen is named; anonymized tokens round-trip),
prefix stability (every call's prompt extends the previous one within a
day), invalid-output handling, and the notes variant's once-a-day
rewrite."""

from __future__ import annotations

import json
import pathlib
import random

import pytest

from baselines.agent import Agent
from baselines.bank import JsonlBank, write_gate_pass_bank
from baselines.harness import run_episode
from baselines.llm_hypotheses.log_reader import (LogReaderBelief,
                                                 LogReaderBrain,
                                                 LogReaderPolicy)
from baselines.llm_hypotheses.prompt import build_anonymization_maps
from baselines.types import DAY_SECONDS


class _Stub:
    """Answers: sense the first sensable receptacle once per question,
    then answer with the last receptacle the log mentions for the
    object. Records every prompt. ``script`` overrides per call."""

    def __init__(self, script=None):
        self.prompts = []
        self.script = list(script or [])
        self.notes_calls = 0

    def generate(self, system, user, seed, temperature, max_tokens,
                 reasoning_effort="medium", schema=None):
        self.prompts.append(user)
        if schema is None:                      # notes rewrite
            self.notes_calls += 1
            return {"payload": f"NOTES v{self.notes_calls}: nothing yet",
                    "think": "", "prompt_tokens": 10, "completion_tokens": 5,
                    "generation_seconds": 0.1, "cached": False}
        if self.script:
            payload = self.script.pop(0)
        else:
            question = user.rsplit("QUESTION: where is ", 1)[1].split(" ", 1)[0]
            already = "already looked this question" in user
            no_budget = "BUDGET: 0 looks" in user
            first_rec = user.split("RECEPTACLES")[1].split("\n")[1].strip().split()[0]
            if not already and not no_budget:
                payload = {"action": "sense", "receptacle": first_rec, "why": "look"}
            else:
                last = None
                for line in reversed(user.split("LOG:\n", 1)[1].split("\n\nQUESTION")[0].split("\n")):
                    if f" {question} at " in line:
                        last = line.split(" at ", 1)[1].strip(); break
                payload = {"action": "answer", "ranked": [last or first_rec], "why": "log"}
        return {"payload": json.dumps(payload), "think": "", "prompt_tokens": 10,
                "completion_tokens": 5, "generation_seconds": 0.1, "cached": False}


def _episode(tmp_path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    return next(JsonlBank(tmp_path / "bank.jsonl").episodes())


def _run(tmp_path, stub, notes=False, anonymized=False, episode=None):
    episode = episode or _episode(tmp_path)
    if anonymized:
        omap, rmap, cmap = build_anonymization_maps(episode)
    else:
        omap, rmap, cmap = {}, {}, {}
    brain = LogReaderBrain(stub, notes=notes, omap=omap, rmap=rmap, cmap=cmap,
                           log_dir=tmp_path / "notes")
    belief = LogReaderBelief(random.Random(0), brain)
    records = list(run_episode(Agent(belief, LogReaderPolicy(brain)), episode))
    return episode, brain, records


def test_decision_flows_through_predict_and_decide(tmp_path):
    stub = _Stub()
    episode, brain, records = _run(tmp_path, stub)
    assert records and all(r.n_senses in (0, 1) for r in records)
    sensed = [r for r in records if r.n_senses == 1]
    assert sensed, "the stub senses once per question while budget lasts"
    # The recorded answer is the brain's ranked top-1 (or the find).
    for r in records:
        found = [a for a in r.actions if a["type"] == "sense"
                 and r.object_id in a["contents"]]
        if found:
            assert r.answer_receptacle == found[0]["receptacle_id"]
    # Budget: senses stop when the day's budget is spent.
    by_day = {}
    for r in records:
        by_day.setdefault(r.day_index, 0)
        by_day[r.day_index] += r.n_senses
    assert max(by_day.values()) <= episode.budget_per_day
    stats = brain.stats()
    assert stats["calls"] == len(stub.prompts) and stats["invalid_decisions"] == 0
    assert stats["log_lines"] > 0


def test_prompts_are_prefix_stable_and_name_only_seen_objects(tmp_path):
    stub = _Stub()
    episode, brain, records = _run(tmp_path, stub)
    # Within a day, each prompt's prefix through the log is a prefix of
    # the next prompt (append-only log, stable header).
    def head(p): return p.split("\n\nQUESTION:")[0]
    def day_of(p): return p.rsplit("NOW: d", 1)[1][:2]
    prev = None
    for p in stub.prompts:
        h = head(p)
        if prev is not None and day_of(prev) == day_of(p):
            # the objects block may grow; the stable prefix must not change
            assert p.split("OBJECTS the robot")[0] == prev.split("OBJECTS the robot")[0]
            assert h.split("LOG:\n", 1)[1].startswith(head(prev).split("LOG:\n", 1)[1])
        prev = p
    # No object appears in a prompt before the robot has seen it.
    first_seen = {}
    for e in episode.evidence_stream():
        for o in ([e.object_id] if hasattr(e, "object_id") else e.contents):
            first_seen.setdefault(o, e.t)
    for o in episode.initial_observations:
        first_seen[o.object_id] = min(first_seen.get(o.object_id, o.t), o.t)
    for p in stub.prompts:
        now_day = int(day_of(p))
        for obj, t in first_seen.items():
            if t // DAY_SECONDS > now_day:
                assert obj not in p.split("\n\nQUESTION:")[0], (obj, now_day)


def test_anonymized_condition_round_trips(tmp_path):
    stub = _Stub()
    episode, brain, records = _run(tmp_path, stub, anonymized=True)
    for p in stub.prompts:
        for real in list(episode.object_classes) + list(episode.receptacle_ids):
            assert real not in p
    # Answers and senses come back as real ids.
    assert all(r.answer_receptacle in episode.receptacle_ids for r in records)
    assert all(a["receptacle_id"] in episode.receptacle_ids
               for r in records for a in r.actions if a["type"] == "sense")


def test_invalid_output_degrades_to_an_answer_and_is_counted(tmp_path):
    bad = [{"action": "sense", "receptacle": "nowhere", "why": ""},
           {"action": "answer", "ranked": [], "why": ""},
           "not json at all"]
    stub = _Stub(script=bad)
    episode, brain, records = _run(tmp_path, stub)
    assert brain.invalid_decisions >= 3
    assert records[0].n_senses == 0                 # the bad sense became an answer
    assert records[0].answer_receptacle in episode.receptacle_ids


def test_notes_variant_rewrites_once_a_day_and_prefixes_notes(tmp_path):
    stub = _Stub()
    episode, brain, records = _run(tmp_path, stub, notes=True)
    days = {r.day_index for r in records}
    assert stub.notes_calls == len(days)
    assert len(brain.notes_versions) == len(days)
    assert (tmp_path / "notes" / f"notes_day{min(days):02d}.md").exists()
    decision_prompts = [p for p in stub.prompts if "QUESTION: where is" in p]
    assert all("YOUR NOTES" in p for p in decision_prompts)
    assert any("NOTES v1" in p for p in decision_prompts)
    # The notes sit before the log: a day's decision prompts still share
    # the prefix through the notes.
    late = [p for p in decision_prompts if "NOTES v2" in p]
    if late:
        assert all(p.split("LOG:\n")[0] == late[0].split("LOG:\n")[0] for p in late[:3])


def test_readonly_snapshot_never_calls_the_model(tmp_path):
    stub = _Stub()
    episode = _episode(tmp_path)
    brain = LogReaderBrain(stub)
    belief = LogReaderBelief(random.Random(0), brain)
    belief.reset(episode.agent_view())
    for obs in episode.initial_observations:
        belief.update(obs)
    p = belief.predict_readonly(episode.initial_observations[0].object_id, 3600)
    assert stub.prompts == [] and p.argmax == episode.initial_observations[0].receptacle_id


def test_notes_cleaning_unwraps_json_and_rejects_unclosed_thinking():
    clean = LogReaderBrain._clean_notes
    assert clean({"payload": '{"notes": "A\\nB"}', "think_closed": True}) == "A\nB"
    assert clean({"payload": "```markdown\nplain notes\n```", "think_closed": True}) == "plain notes"
    assert clean({"payload": "just text", "think_closed": True}) == "just text"
    # The thinking template's unclosed block: payload is reasoning, think empty.
    assert clean({"payload": "The user wants me to...", "think_closed": False,
                  "think": ""}) is None
    assert clean({"payload": "", "think_closed": True}) is None
    # A truncated wrapper still yields the text written so far.
    got = clean({"payload": '{\n  "notes": "=== d04 ===\\nBUDGET: 24', "think_closed": True})
    assert got and got.startswith("=== d04 ===")


def test_rejected_notes_keep_the_previous_file(tmp_path):
    class _NotesStub(_Stub):
        def __init__(self):
            super().__init__(); self.n = 0
        def generate(self, system, user, seed, temperature, max_tokens,
                     reasoning_effort="medium", schema=None):
            if schema is None:
                self.n += 1
                if self.n == 2:      # second day: unclosed think block
                    return {"payload": "Let me think about the log...", "think": "",
                            "think_closed": False, "finish_reason": "length",
                            "prompt_tokens": 1, "completion_tokens": 1,
                            "generation_seconds": 0.1, "cached": False}
                return {"payload": f"NOTES v{self.n}", "think": "t", "think_closed": True,
                        "finish_reason": "stop", "prompt_tokens": 1, "completion_tokens": 1,
                        "generation_seconds": 0.1, "cached": False}
            return super().generate(system, user, seed, temperature, max_tokens,
                                    reasoning_effort, schema)
    stub = _NotesStub()
    episode, brain, records = _run(tmp_path, stub, notes=True)
    statuses = [v["status"] for v in brain.notes_versions]
    assert statuses[:2] == ["ok", "rejected"]
    assert brain.notes_versions[1]["notes"] == "NOTES v1"     # kept
    assert brain.stats()["notes_rejected"] == 1
