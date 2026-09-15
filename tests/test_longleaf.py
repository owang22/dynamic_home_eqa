"""treeLongLeaf offline: document parsing, the timetable converter
(priority stacking, fallback, class targets, learning, absence credit),
retire-not-delete with revival, prompt hygiene, anonymized round trip,
and an end-to-end run through the harness."""

from __future__ import annotations

import json
import random

import pytest

from baselines.agent import Agent
from baselines.bank import JsonlBank, write_gate_pass_bank
from baselines.beliefs.llm_hypothesis_mixture import ReaskConfig
from baselines.beliefs.longleaf_mixture import LongLeafMixture
from baselines.beliefs.timetable_hypothesis import TimetableBelief
from baselines.harness import run_episode
from baselines.llm_hypotheses.longleaf import (DELIMITER, anonymize_document,
                                               deanonymize_document,
                                               library_index, parse_document,
                                               parse_documents)
from baselines.llm_hypotheses.longleaf_prompt import (
    longleaf_revision_prompt, longleaf_tour_start_prompt)
from baselines.llm_hypotheses.prompt import (AWAY_SENTENCES,
                                             build_anonymization_maps,
                                             vocabulary_tables)
from baselines.llm_hypotheses.tree_prompt import (FORBIDDEN_PROMPT_STRINGS,
                                                  FORBIDDEN_WORD_RE)
from baselines.policies.voi_sense import VoIThresholdSense
from baselines.types import DAY_SECONDS, EpisodeContext, Observation, SenseResult

H = 3600
RECS = ("desk", "kitchen_table", "shelf", "hamper", "OUT_OF_HOUSE", "ON_PERSON")
OBJECTS = {"laptop_1": "laptop", "mug_1": "mug", "towel_1": "towel",
           "mug_2": "mug", "keys_1": "keys"}


def _ctx(n_days=28):
    return EpisodeContext(episode_id="ep", household_id="hh_test",
                          receptacle_ids=RECS, object_classes=OBJECTS,
                          budget_per_day=2, n_days=n_days,
                          unsensable_receptacle_ids=("OUT_OF_HOUSE", "ON_PERSON"))


def _obs(obj, rec, day, hour):
    return Observation(object_id=obj, object_class=OBJECTS[obj], receptacle_id=rec,
                       t=int(day * DAY_SECONDS + hour * H), source="scripted")


def _doc(hid, title, targets, check=None, claims=None):
    check = check or {"target": "laptop_1", "at": "desk", "days": "weekday",
                      "hour": 13.0, "if_seen": "right"}
    if claims is None:
        first = next(iter(targets))
        obj = first if not first.startswith("class:") else next(
            o for o, c in OBJECTS.items() if c == first[6:])
        claims = [{"claim": "it is where the top block says", "target": obj,
                   "expect": targets[first][-1]["at"], "days": "both",
                   "from": 0, "to": 24}]
    return (f"# {hid} — {title}\n\nSome prose about the home.\n\n```json\n"
            + json.dumps({"distinguishing_check": check, "targets": targets,
                          "claims": claims})
            + "\n```\n")


COMMUTER = {"laptop_1": [
    {"days": "both", "from": 0, "to": 24, "at": "desk", "chance": "usually"},
    {"days": "weekday", "from": 9, "to": 17, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
    "class:mug": [{"days": "both", "from": 0, "to": 24, "at": "shelf", "chance": "usually"},
                  {"days": "both", "from": 7, "to": 9, "at": "kitchen_table", "chance": "usually"}]}
HOMEBODY = {"laptop_1": [{"days": "both", "from": 0, "to": 24, "at": "desk", "chance": "almost_always"}],
            "class:mug": [{"days": "both", "from": 0, "to": 24, "at": "shelf", "chance": "usually"}]}
TABLE = {"laptop_1": [{"days": "both", "from": 0, "to": 24, "at": "kitchen_table", "chance": "usually"}],
         "towel_1": [{"days": "both", "from": 0, "to": 24, "at": "hamper", "chance": "usually"}]}
DOCS = [_doc("p_0001", "commuter", COMMUTER), _doc("p_0002", "homebody", HOMEBODY),
        _doc("p_0003", "table", TABLE)]


def _raws():
    valid, dropped = parse_documents(DELIMITER.join([""] + DOCS), OBJECTS, RECS,
                                     unsensable=("OUT_OF_HOUSE", "ON_PERSON"))
    assert not dropped, dropped
    return valid


def _mixture(tmp_path, raws=None, reask=None, elicitor=None, **kw):
    d = tmp_path / "ll"
    d.mkdir(exist_ok=True)
    (d / "hh_test.json").write_text(json.dumps(library_index(raws or _raws(), OBJECTS)))
    m = LongLeafMixture(random.Random(0), d, reask=reask, elicitor=elicitor, **kw)
    m.reset(_ctx())
    return m


def test_documents_parse_with_ids_prose_and_json_and_bad_ids_are_dropped():
    raws = _raws()
    assert [r["hypothesis_id"] for r in raws] == ["p_0001", "p_0002", "p_0003"]
    assert raws[0]["title"] == "commuter" and "prose" in raws[0]["prose"]
    assert raws[0]["markdown"].startswith("# p_0001 — commuter")
    # A bad receptacle is named verbatim; a missing json block too; a
    # duplicate id is replaced.
    bad = _doc("p_0004", "bad", {"laptop_1": [{"days": "both", "from": 0, "to": 24,
                                              "at": "sofa", "chance": "usually"}]})
    dup = _doc("p_0001", "dup", HOMEBODY)
    text = DELIMITER.join(["", bad, dup, "# p_0005 — no block\n\nprose only\n"])
    valid, dropped = parse_documents(text, OBJECTS, RECS, taken=["p_0001"])
    assert [d["bad_strings"] for d in dropped] == [["sofa"]]
    assert len(valid) == 1 and valid[0]["hypothesis_id"] != "p_0001"
    # A check at an away token is rejected.
    with pytest.raises(Exception):
        parse_document(_doc("p_0009", "x", HOMEBODY,
                            check={"target": "laptop_1", "at": "ON_PERSON",
                                   "days": "both", "hour": 9, "if_seen": "right"}),
                       OBJECTS, RECS, unsensable=("OUT_OF_HOUSE", "ON_PERSON"))


def test_blocks_stack_by_priority_and_uncovered_hours_fall_back():
    model = TimetableBelief(random.Random(0), _raws()[0])
    model.reset(_ctx())
    monday_noon = int(0 * DAY_SECONDS + 12 * H)
    p = model.predict_readonly("laptop_1", monday_noon).distribution
    assert p["OUT_OF_HOUSE"] > 0.6 and p["desk"] > 0.05      # override, then base
    sat_noon = int(5 * DAY_SECONDS + 12 * H)
    assert model.predict_readonly("laptop_1", sat_noon).argmax == "desk"
    # Class target covers mug_1 and mug_2, and an object registered later.
    assert model.predict_readonly("mug_2", int(8 * H)).argmax == "kitchen_table"
    model.ensure_object("mug_9", "mug")
    assert model.predict_readonly("mug_9", int(8 * H)).argmax == "kitchen_table"
    # An object no block covers uses its own sightings.
    for d in range(3):
        model.update(_obs("towel_1", "hamper", d, 10))
    assert model.predict_readonly("towel_1", int(3 * DAY_SECONDS + 10 * H)).argmax == "hamper"
    assert model.explain("laptop_1", monday_noon).startswith("block laptop_1 weekday 9-17h")


def test_sightings_move_block_chances_and_empty_looks_credit_away_blocks():
    model = TimetableBelief(random.Random(0), _raws()[0])
    model.reset(_ctx())
    away = next(s for s in model._states if s.block.at == "OUT_OF_HOUSE")
    s0, f0 = away.success, away.failure
    t = int(0 * DAY_SECONDS + 13 * H)
    model.update(SenseResult(receptacle_id="desk", t=t, contents=(), object_classes={}))
    assert away.success - s0 == pytest.approx(0.5, abs=0.03)    # empty desk in window
    model.update(SenseResult(receptacle_id="shelf", t=t, contents=(), object_classes={}))
    assert away.success - s0 == pytest.approx(0.5, abs=0.03)    # elsewhere: nothing
    model.update(_obs("laptop_1", "desk", 1, 13))                # found at desk: failure
    assert away.failure > f0
    fitted = model.fitted_parameters()["rules"]
    assert {r["to"] for r in fitted} == {"desk", "OUT_OF_HOUSE", "shelf", "kitchen_table"}


class _Elicitor:
    def __init__(self, new=(), revive=()):
        self.new, self.revive, self.calls = list(new), list(revive), []

    def __call__(self, report, previous, context):
        self.calls.append(report)
        return {"new": self.new, "revive": self.revive, "dropped": [], "problems": []}


def test_retire_keeps_the_document_and_revival_brings_it_back(tmp_path):
    extra = parse_document(_doc("p_0004", "spare", HOMEBODY), OBJECTS, RECS, taken=["p_0001", "p_0002", "p_0003"])
    rec = _Elicitor(revive=["p_0003"])
    m = _mixture(tmp_path, _raws() + [extra],
                 ReaskConfig(window=1000, scheduled_days=(6,), max_calls=1,
                             new_class_triggers=False), rec,
                 leaf_weight_floor=0.02, leaf_prune_days=1)
    for day in range(5):
        keys = [m._particle_key(h) for h in m._raw_hypotheses]
        if "p_0003" in keys:
            m._log_weights[keys.index("p_0003")] = -60.0
        m.update(_obs("mug_1", "shelf", day, 10))
    assert "p_0003" in m.retired and m.retired["p_0003"]["raw"]["title"] == "table"
    assert "p_0003" not in m.leaf_weights and m.prune_log[0]["kind"] == "retire"
    assert m.library_status()["p_0003"]["status"].startswith("retired")
    m.update(_obs("mug_1", "shelf", 6, 10))                      # fires: revive
    assert m.reask_events[-1]["changed"] is True
    assert "p_0003" in m.leaf_weights and "p_0003" not in m.retired
    assert m.edit_log[-1]["op"] == "revive"
    # Never below three live documents.
    (tmp_path / "b").mkdir()
    m2 = _mixture(tmp_path / "b", leaf_weight_floor=0.5, leaf_prune_days=1)
    for day in range(5):
        m2.update(_obs("mug_1", "shelf", day, 10))
    assert len(m2._raw_hypotheses) == 3 and m2.retired == {}


def test_revision_adds_documents_and_report_shows_the_library(tmp_path):
    new = parse_document(_doc("p_0007", "new one", TABLE), OBJECTS, RECS)
    rec = _Elicitor(new=[new])
    m = _mixture(tmp_path, reask=ReaskConfig(window=1000, scheduled_days=(2,),
                                             max_calls=1, new_class_triggers=False),
                 elicitor=rec)
    for day in range(3):
        m.update(_obs("laptop_1", "desk", day, 9))
    report = rec.calls[-1]
    assert {d["hypothesis_id"] for d in report["library"]} == {"p_0001", "p_0002", "p_0003"}
    assert all(d["markdown"] for d in report["library"])
    assert "p_0007" in m.leaf_weights and m.edit_log[-1]["op"] == "add_hypothesis"
    assert len(m.library_documents()) == 4
    assert m.library_diagnostics()["n_documents"] == 4


def test_prompts_are_clean_and_name_only_tour_seen_objects(tmp_path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    episode = next(JsonlBank(tmp_path / "bank.jsonl").episodes())
    seen = {o.object_id for o in episode.initial_observations}
    user, _ = longleaf_tour_start_prompt(episode)
    for obj in episode.object_classes:
        assert (obj in user) == (obj in seen), obj
    rec = _Elicitor()
    m = _mixture(tmp_path, reask=ReaskConfig(window=1000, scheduled_days=(2,),
                                             max_calls=1, new_class_triggers=False),
                 elicitor=rec)
    for day in range(3):
        m.update(_obs("laptop_1", "desk", day, 9))
    revision = longleaf_revision_prompt(rec.calls[-1],
                                        vocabulary_tables(episode, objects=dict(OBJECTS)))
    for text, name in ((user, "installation"), (revision, "revision")):
        assert AWAY_SENTENCES in text
        low = text.replace(AWAY_SENTENCES, "").lower()
        for bad in FORBIDDEN_PROMPT_STRINGS:
            assert bad.lower() not in low, (name, bad)
        assert not FORBIDDEN_WORD_RE.search(text), name
    assert DELIMITER in revision and "REVIVE" in revision


def test_anonymized_documents_round_trip_structured_fields(tmp_path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    episode = next(JsonlBank(tmp_path / "bank.jsonl").episodes())
    omap, rmap, cmap = build_anonymization_maps(episode)
    recs = list(episode.receptacle_ids)
    raw = parse_document(_doc("p_0001", "t", {"keys_shift": [
        {"days": "both", "from": 0, "to": 24, "at": recs[0], "chance": "usually"}],
        "class:tote": [{"days": "weekday", "from": 8, "to": 10, "at": recs[1], "chance": "rarely"}]},
        check={"target": "keys_shift", "at": recs[0], "days": "both", "hour": 9, "if_seen": "right"}),
        episode.object_classes, recs)
    anon = anonymize_document(raw, omap, rmap, cmap)
    assert anon["claims"][0]["target"] == omap["keys_shift"]
    assert set(anon["targets"]) == {omap["keys_shift"], "class:" + cmap["tote"]}
    assert anon["distinguishing_check"]["at"] == rmap[recs[0]]
    back = deanonymize_document(anon, omap, rmap, cmap)
    assert back["targets"] == raw["targets"]
    assert back["claims"] == raw["claims"]
    assert back["distinguishing_check"] == raw["distinguishing_check"]


def test_fork_heading_records_lineage_and_keeps_the_parent():
    doc = _doc("p_0009", "commuter, laptop travels (fork of p_0001)", COMMUTER)
    raw = parse_document(doc, OBJECTS, RECS)
    assert raw["forked_from"] == "p_0001" and raw["title"] == "commuter, laptop travels"
    assert raw["markdown"].startswith("# p_0009 — commuter, laptop travels (fork of p_0001)")
    plain = parse_document(_doc("p_0008", "plain", HOMEBODY), OBJECTS, RECS)
    assert plain["forked_from"] is None


def test_claims_resolve_for_against_and_weakly_for_away_claims():
    doc = _doc("p_0001", "commuter", COMMUTER, claims=[
        {"claim": "laptop leaves on weekdays", "target": "laptop_1",
         "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 9, "to": 17},
        {"claim": "mug on the table at breakfast", "target": "mug_1",
         "expect": "kitchen_table", "days": "both", "from": 7, "to": 9}])
    raw = parse_document(doc, OBJECTS, RECS)
    model = TimetableBelief(random.Random(0), raw)
    model.reset(_ctx())
    t = lambda d, h: int(d * DAY_SECONDS + h * H)
    looks = [(t(0, 12), "desk", ()),                 # empty at the overridden place: weak for
             (t(1, 12), "kitchen_table", ("laptop_1",)),   # seen in the house: against
             (t(0, 20), "desk", ("laptop_1",)),      # outside the window: nothing
             (t(0, 8), "kitchen_table", ("mug_1",)),  # for
             (t(1, 8), "kitchen_table", ()),          # against
             (t(2, 8), "shelf", ("mug_1",))]          # elsewhere: against
    rows = {r["claim"]: r for r in model.claim_tallies(looks)}
    assert rows["laptop leaves on weekdays"] == {**rows["laptop leaves on weekdays"], "for": 0, "against": 1, "weak_for": 1}
    assert rows["mug on the table at breakfast"] == {**rows["mug on the table at breakfast"], "for": 1, "against": 2, "weak_for": 0}
    # A document without claims is rejected; the first in-home claim
    # doubles as the legacy check.
    bare = _doc("p_0002", "x", HOMEBODY, claims=[])
    with pytest.raises(Exception):
        parse_document(bare, OBJECTS, RECS)
    assert model.hypothesis.distinguishing_check.target == "laptop_1"   # the explicit check wins


def test_end_to_end_through_the_harness(tmp_path):
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    episode = next(JsonlBank(tmp_path / "bank.jsonl").episodes())
    recs = list(episode.receptacle_ids)
    docs = [_doc(f"p_000{i}", f"d{i}", {"keys_shift": [
        {"days": "both", "from": 0, "to": 24, "at": recs[i], "chance": "usually"}]},
        check={"target": "keys_shift", "at": recs[i], "days": "both", "hour": 9, "if_seen": "right"})
        for i in range(3)]
    raws, dropped = parse_documents(DELIMITER.join([""] + docs), episode.object_classes, recs)
    assert not dropped
    d = tmp_path / "ll"
    d.mkdir()
    (d / f"{episode.household_id}.json").write_text(json.dumps(library_index(raws, episode.object_classes)))
    belief = LongLeafMixture(random.Random(1), d)
    records = list(run_episode(Agent(belief, VoIThresholdSense(random.Random(2), lam=0.05)), episode))
    assert records and all(r.answer_receptacle in recs for r in records)
    assert set(belief.leaf_weights) == {"p_0000", "p_0001", "p_0002"}
    assert belief.check_outcomes is not None


def test_block_where_learns_from_sightings_inside_its_hours():
    model = TimetableBelief(random.Random(0), _raws()[1])       # homebody: laptop desk all day
    model.reset(_ctx())
    assert model.predict_readonly("laptop_1", int(10 * H)).argmax == "desk"
    for day in range(4):
        for hour in (9, 12, 15):
            model.update(_obs("laptop_1", "kitchen_table", day, hour))
    p = model.predict_readonly("laptop_1", int(4 * DAY_SECONDS + 12 * H)).distribution
    assert p["kitchen_table"] > p["desk"]          # the block moved, the stated at is a prior


def test_new_document_enters_at_its_replayed_weight_not_the_mean(tmp_path):
    good = parse_document(_doc("p_0007", "table lover", TABLE), OBJECTS, RECS)
    rec = _Elicitor(new=[good])
    m = _mixture(tmp_path, reask=ReaskConfig(window=1000, scheduled_days=(3,),
                                             max_calls=1, new_class_triggers=False),
                 elicitor=rec)
    # Every original document says desk / desk / kitchen_table for the
    # laptop; the sightings say kitchen_table, so the statistical
    # particle and the TABLE document should both do well.
    for day in range(4):
        for hour in (8, 13, 19):
            m.update(_obs("laptop_1", "kitchen_table", day, hour))
    w = m.leaf_weights
    assert "p_0007" in w
    stat = [x for n, x in zip([p.name for p in m.particles], m.weights) if "Most" in n][0]
    # The newcomer is within a factor of 3 of the statistical particle
    # rather than buried at the (tiny) mean of the losers.
    assert w["p_0007"] > stat / 3
    assert w["p_0007"] > max(w.get("p_0001", 0.0), w.get("p_0002", 0.0))


def test_read_lines_parse_and_cap():
    from baselines.llm_hypotheses.longleaf import MAX_FETCH, read_ids
    text = "Let me see.\nREAD p_0001 p_0002, p_0003\nREAD: p_0004 p_0005 p_0006 p_0007 p_0008\n"
    got = read_ids(text)
    assert got[:3] == ["p_0001", "p_0002", "p_0003"] and len(got) == MAX_FETCH


def test_two_phase_revision_reads_then_writes(tmp_path):
    """Phase one sends the index (no documents); a READ reply gets the
    named documents in phase two; documents written in phase one skip
    phase two."""
    from baselines.llm_hypotheses.revise import LongLeafRevisionElicitor
    write_gate_pass_bank(tmp_path / "bank.jsonl", seed=0)
    episode = next(JsonlBank(tmp_path / "bank.jsonl").episodes())
    recs = list(episode.receptacle_ids)
    docs = [_doc(f"p_000{i}", f"d{i}", {"keys_shift": [
        {"days": "both", "from": 0, "to": 24, "at": recs[i], "chance": "usually"}]},
        check={"target": "keys_shift", "at": recs[i], "days": "both", "hour": 9, "if_seen": "right"})
        for i in range(3)]
    raws, _ = parse_documents(DELIMITER.join([""] + docs), episode.object_classes, recs)
    new_doc = _doc("p_0009", "d9 (fork of p_0001)", {"keys_shift": [
        {"days": "both", "from": 0, "to": 24, "at": recs[2], "chance": "usually"}]},
        check={"target": "keys_shift", "at": recs[2], "days": "both", "hour": 9, "if_seen": "right"})

    class _Client:
        def __init__(self): self.calls = []
        def generate(self, system, user, seed, temperature, max_tokens, reasoning_effort="medium", schema=None, keep_content=False):
            self.calls.append(user)
            reply = "READ p_0001 p_0002" if len(self.calls) == 1 else DELIMITER + "\n" + new_doc
            return {"payload": reply, "content": reply, "think": "t", "prompt_tokens": 1,
                    "completion_tokens": 1, "generation_seconds": 0.1, "finish_reason": "stop"}
    client = _Client()
    el = LongLeafRevisionElicitor(client, episode, anonymized=False, log_dir=tmp_path / "rev")
    report = {"day": 3, "trigger": "claim", "known_objects": dict(episode.object_classes),
              "library": [{"hypothesis_id": r["hypothesis_id"], "title": r["title"], "status": "live",
                           "weight": 0.3, "claims": [], "markdown": r["markdown"]} for r in raws],
              "rules_held": [], "rules_failed": [], "worst_objects": [], "uncovered_objects": [],
              "statistics": "", "object_table": [], "claims_against": [], "anomaly_bucket": [],
              "statistical_weight": 0.1}
    out = el(report, raws, None)
    assert len(client.calls) == 2
    assert "THE DOCUMENTS YOU ASKED TO READ" not in client.calls[0]
    assert "p_0001 — d1" in client.calls[1] and "p_0002 — d2" in client.calls[1]
    assert "p_0003 — d3" not in client.calls[1].split("THE DOCUMENTS YOU ASKED TO READ")[1]
    assert [d["hypothesis_id"] for d in out["new"]] == ["p_0009"]
    assert out["new"][0]["forked_from"] == "p_0001"
    # Index-only prompt is small: no document bodies in it.
    assert len(client.calls[0]) < len(client.calls[1])


def test_claim_against_a_weighted_document_fires_a_revision(tmp_path):
    rec = _Elicitor()
    m = _mixture(tmp_path, reask=ReaskConfig(window=1000, scheduled_days=(), max_calls=3,
                                             min_gap=2, new_class_triggers=False),
                 elicitor=rec)
    # The homebody document (laptop at desk all day) holds weight after
    # desk sightings; then two empty looks at the desk go against its
    # claim and the revision fires with trigger "claim" — but only once
    # min_gap sightings have accrued since the episode start.
    m.update(SenseResult(receptacle_id="desk", t=int(0 * DAY_SECONDS + 9 * H), contents=(), object_classes={}))
    m.update(SenseResult(receptacle_id="desk", t=int(0 * DAY_SECONDS + 11 * H), contents=(), object_classes={}))
    assert m.reask_events == []                     # against 2, but no sightings yet
    for day in range(2):
        m.update(_obs("laptop_1", "desk", day, 10))
    assert m.reask_events == []
    m.update(SenseResult(receptacle_id="desk", t=int(2 * DAY_SECONDS + 10 * H), contents=(), object_classes={}))
    m.update(SenseResult(receptacle_id="desk", t=int(2 * DAY_SECONDS + 12 * H), contents=(), object_classes={}))
    assert m.reask_events and m.reask_events[-1]["trigger"] == "claim"
    # A second call needs a full day as well as the sighting gap.
    m.update(SenseResult(receptacle_id="desk", t=int(2 * DAY_SECONDS + 14 * H), contents=(), object_classes={}))
    m.update(SenseResult(receptacle_id="desk", t=int(2 * DAY_SECONDS + 16 * H), contents=(), object_classes={}))
    for hour in (17, 18, 19):
        m.update(_obs("mug_1", "shelf", 2, hour))
    assert len(m.reask_events) == 1
    assert rec.calls[-1]["claims_against"]
    assert rec.calls[-1]["object_table"] and "found" in rec.calls[-1]["object_table"][0]


def test_chance_aliases_and_fork_inheritance():
    always = _doc("p_0011", "alias", {"laptop_1": [
        {"days": "both", "from": 0, "to": 24, "at": "desk", "chance": "always"},
        {"days": "weekday", "from": 9, "to": 17, "at": "OUT_OF_HOUSE", "chance": "mostly"}]})
    raw = parse_document(always, OBJECTS, RECS)
    assert [b["chance"] for b in raw["targets"]["laptop_1"]] == ["almost_always", "usually"]
    assert '"almost_always"' in raw["markdown"]
    # A fork that restates only one target inherits the rest (and the
    # claims) from its parent, and its stored markdown is complete.
    parent = _raws()[0]                                   # commuter: laptop + class:mug
    fork = _doc("p_0012", "commuter, mug on the table (fork of p_0001)",
                {"class:mug": [{"days": "both", "from": 0, "to": 24, "at": "kitchen_table", "chance": "usually"}]},
                claims=[])
    raw = parse_document(fork, OBJECTS, RECS, parents={"p_0001": parent})
    assert set(raw["targets"]) == {"laptop_1", "class:mug"}
    assert raw["targets"]["laptop_1"] == parent["targets"]["laptop_1"]
    assert raw["targets"]["class:mug"][0]["at"] == "kitchen_table"
    assert raw["claims"] == parent["claims"] and raw["forked_from"] == "p_0001"
    assert "inherited from p_0001" in raw["markdown"] and '"laptop_1"' in raw["markdown"]
    # Without the parent in hand the same fork fails loudly on the missing claims.
    with pytest.raises(Exception):
        parse_document(fork, OBJECTS, RECS)


def test_literal_away_tokens_are_accepted_in_the_anonymized_condition():
    from baselines.llm_hypotheses.longleaf import accept_literal_away_tokens
    rmap = {"OUT_OF_HOUSE": "receptacle_2", "ON_PERSON": "receptacle_3", "desk": "receptacle_9"}
    text = '"at": "OUT_OF_HOUSE"}, {"expect": "ON_PERSON"} and OUT_OF_HOUSE_x stays'
    out = accept_literal_away_tokens(text, rmap)
    assert '"at": "receptacle_2"' in out and '"expect": "receptacle_3"' in out
    assert "OUT_OF_HOUSE_x" in out            # whole words only
