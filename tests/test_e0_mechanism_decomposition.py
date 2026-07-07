"""
Tests for scripts/e0_mechanism_decomposition.py's transition classification:
distinguishing "wrong->right" (true discovery) from "wrong->abstain"
(selective abstention) is the whole point of the decomposition, so the
classify() truth table and the answer_immediately-baseline diffing in
decompose() are what must be verified.

Does not require habitat_sim (only reads/synthesizes result-row dicts).
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

_SCRIPT_PATH = pathlib.Path(__file__).parent.parent / "scripts" / "e0_mechanism_decomposition.py"


def _load_module():
    # Register in sys.modules before exec: the module's frozen dataclasses
    # resolve their (string, from __future__ import annotations) field
    # types via sys.modules[cls.__module__] at class-creation time, which
    # is None for a module loaded via spec_from_file_location alone.
    spec = importlib.util.spec_from_file_location("e0_mechanism_decomposition", _SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def module():
    return _load_module()


def _outcome(module, correct, abstained=False):
    return module.Outcome(correct=correct, abstained=abstained)


class TestClassify:
    def test_unchanged_right(self, module):
        assert module.classify(_outcome(module, True), _outcome(module, True)) == "unchanged_right"

    def test_unchanged_wrong(self, module):
        assert module.classify(_outcome(module, False), _outcome(module, False)) == "unchanged_wrong"

    def test_wrong_to_right_is_discovery(self, module):
        assert module.classify(_outcome(module, False), _outcome(module, True)) == "wrong_to_right"

    def test_wrong_to_abstain_is_selective_abstention(self, module):
        assert module.classify(_outcome(module, False), _outcome(module, None, abstained=True)) == "wrong_to_abstain"

    def test_right_to_abstain_is_a_regression(self, module):
        assert module.classify(_outcome(module, True), _outcome(module, None, abstained=True)) == "right_to_abstain"

    def test_right_to_wrong_is_a_regression(self, module):
        assert module.classify(_outcome(module, True), _outcome(module, False)) == "right_to_wrong"

    def test_baseline_abstained_is_its_own_bucket_not_a_flip(self, module):
        # The baseline itself never answered — there's nothing to call a
        # "flip", so this must not collapse into wrong_to_right/abstain.
        assert module.classify(
            _outcome(module, None, abstained=True), _outcome(module, True),
        ) == "baseline_abstained_right"


def _row(policy, wait_hours, label, correct, abstained=False, log=None):
    return {
        "policy": policy, "wait_hours": wait_hours, "label": label,
        "correct": correct, "abstained": abstained, "log": log or [],
    }


class TestDecompose:
    def test_flip_attributed_to_resense_anchor(self, module):
        rows = [
            _row("answer_immediately", 1.0, "book_1", correct=False),
            _row("always_resense", 1.0, "book_1", correct=True, log=[
                {"kind": "goto_resense", "anchor": "kitchen.counter"},
                {"kind": "answer", "correct": True},
            ]),
        ]
        records = module.decompose(rows)
        assert len(records) == 1
        rec = records[0]
        assert rec.policy == "always_resense"
        assert rec.transition == "wrong_to_right"
        assert rec.resense_anchors == ("kitchen.counter",)

    def test_no_baseline_trial_is_skipped_not_crashed(self, module):
        # answer_immediately never saw this label at this wait_hours (e.g.
        # not in current_instances() for that trial) — nothing to diff against.
        rows = [_row("decay_voi", 2.0, "vase_1", correct=True)]
        assert module.decompose(rows) == []

    def test_multiple_resense_anchors_all_attributed(self, module):
        rows = [
            _row("answer_immediately", 4.0, "keys_1", correct=False),
            _row("decay_voi", 4.0, "keys_1", correct=False, abstained=True, log=[
                {"kind": "goto_resense", "anchor": "living_room.shelf"},
                {"kind": "goto_resense", "anchor": "office.desk"},
            ]),
        ]
        records = module.decompose(rows)
        assert records[0].transition == "wrong_to_abstain"
        assert records[0].resense_anchors == ("living_room.shelf", "office.desk")


class TestSummarize:
    def test_counts_and_totals(self, module):
        rows = [
            _row("answer_immediately", 1.0, "book_1", correct=False),
            _row("always_resense", 1.0, "book_1", correct=True,
                 log=[{"kind": "goto_resense", "anchor": "kitchen.counter"}]),
            _row("answer_immediately", 1.0, "vase_1", correct=True),
            _row("always_resense", 1.0, "vase_1", correct=True),
        ]
        records = module.decompose(rows)
        summaries = module.summarize(records)
        assert len(summaries) == 1
        s = summaries[0]
        assert s["policy"] == "always_resense"
        assert s["wait_hours"] == 1.0
        assert s["counts"]["wrong_to_right"] == 1
        assert s["counts"]["unchanged_right"] == 1
        assert "book_1:kitchen.counter" in s["triggers"]["wrong_to_right"]
