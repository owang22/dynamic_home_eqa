"""
Tests for llm_prior/pseudo_counts.py — L1 T1's Dirichlet pseudo-count
interface. Pure logic plus the committed L0 cache (no live model calls,
per L0/L1's shared "no live LLM calls in pytest" rule).
"""
from __future__ import annotations

import pathlib

import pytest

from dynamic_home_eqa.embodied.posterior import HierarchicalStat, shrink_hierarchical_with_llm
from dynamic_home_eqa.llm_prior.cache import EliciationCache
from dynamic_home_eqa.llm_prior.pseudo_counts import (
    elicited_distribution_to_pseudo_counts,
    elicited_pseudo_counts_from_cache,
    to_hierarchical_stat,
)

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent
_CACHE_DIR = _DYNAMIC_EQA / "llm_prior_cache"
_MANIFEST_DIR = _DYNAMIC_EQA / "results" / "reports" / "l0_manifests"

pytestmark = pytest.mark.skipif(
    not _CACHE_DIR.exists(), reason="L0 elicitation cache not present (run llm_prior/elicit.py first)"
)


class TestElicitedDistributionToPseudoCounts:
    def test_pseudo_counts_sum_to_concentration(self):
        dist = {"a": 0.5, "b": 0.3, "c": 0.2}
        result = elicited_distribution_to_pseudo_counts(
            dist, concentration=10.0, key="test", model_id="m", mode="verbalized", prompt_hash="h",
        )
        assert sum(result.pseudo_counts.values()) == pytest.approx(10.0)

    def test_normalizes_an_unnormalized_input_distribution(self):
        dist = {"a": 2.0, "b": 2.0}  # sums to 4, not 1
        result = elicited_distribution_to_pseudo_counts(
            dist, concentration=8.0, key="test", model_id="m", mode="verbalized", prompt_hash="h",
        )
        assert result.pseudo_counts["a"] == pytest.approx(4.0)
        assert result.pseudo_counts["b"] == pytest.approx(4.0)

    def test_concentration_zero_gives_all_zero_pseudo_counts(self):
        dist = {"a": 0.7, "b": 0.3}
        result = elicited_distribution_to_pseudo_counts(
            dist, concentration=0.0, key="test", model_id="m", mode="verbalized", prompt_hash="h",
        )
        assert all(v == 0.0 for v in result.pseudo_counts.values())

    def test_negative_concentration_raises(self):
        with pytest.raises(ValueError):
            elicited_distribution_to_pseudo_counts(
                {"a": 1.0}, concentration=-1.0, key="test", model_id="m", mode="verbalized", prompt_hash="h",
            )

    def test_zero_sum_distribution_raises(self):
        with pytest.raises(ValueError):
            elicited_distribution_to_pseudo_counts(
                {"a": 0.0, "b": 0.0}, concentration=5.0, key="test", model_id="m", mode="verbalized", prompt_hash="h",
            )


class TestToHierarchicalStat:
    def test_value_is_the_normalized_probability(self):
        dist = {"a": 3.0, "b": 1.0}  # normalizes to 0.75/0.25
        pc = elicited_distribution_to_pseudo_counts(dist, concentration=20.0, key="k", model_id="m", mode="mode", prompt_hash="h")
        stat = to_hierarchical_stat(pc, "a")
        assert stat.value == pytest.approx(0.75)
        assert stat.weight == pytest.approx(20.0)

    def test_concentration_zero_gives_weight_zero_do_no_harm_stat(self):
        pc = elicited_distribution_to_pseudo_counts({"a": 1.0, "b": 1.0}, concentration=0.0, key="k", model_id="m", mode="mode", prompt_hash="h")
        stat = to_hierarchical_stat(pc, "a")
        assert stat.weight == 0.0
        # value is documented irrelevant at weight=0, but must not be NaN/inf
        assert stat.value == 0.0

    def test_unknown_state_raises(self):
        pc = elicited_distribution_to_pseudo_counts({"a": 1.0}, concentration=5.0, key="k", model_id="m", mode="mode", prompt_hash="h")
        with pytest.raises(KeyError):
            to_hierarchical_stat(pc, "not_a_real_state")

    def test_plugs_directly_into_shrink_hierarchical_with_llm_do_no_harm_floor(self):
        # End-to-end check that concentration=0 really is inert once
        # wired through to the actual backoff function, not just at the
        # pseudo_counts layer in isolation.
        pc = elicited_distribution_to_pseudo_counts({"a": 0.9, "b": 0.1}, concentration=0.0, key="k", model_id="m", mode="mode", prompt_hash="h")
        llm_stat = to_hierarchical_stat(pc, "a")
        scene = HierarchicalStat(value=0.2, weight=4.0)
        profile = HierarchicalStat(value=0.5, weight=8.0)
        global_ = HierarchicalStat(value=0.8, weight=200.0)
        from dynamic_home_eqa.embodied.posterior import shrink_hierarchical
        assert shrink_hierarchical_with_llm(scene, profile, global_, llm_stat) == pytest.approx(
            shrink_hierarchical(scene, profile, global_)
        )

    def test_plugs_directly_into_zero_data_limit(self):
        pc = elicited_distribution_to_pseudo_counts({"a": 0.9, "b": 0.1}, concentration=50.0, key="k", model_id="m", mode="mode", prompt_hash="h")
        llm_stat = to_hierarchical_stat(pc, "a")
        scene = HierarchicalStat(value=999.0, weight=0.0)
        profile = HierarchicalStat(value=999.0, weight=0.0)
        global_ = HierarchicalStat(value=999.0, weight=0.0)
        assert shrink_hierarchical_with_llm(scene, profile, global_, llm_stat) == pytest.approx(0.9)


class TestElicitedPseudoCountsFromCache:
    def test_reads_real_committed_cache_and_scales_correctly(self):
        cache = EliciationCache(_CACHE_DIR)
        manifest = __import__("json").loads((_MANIFEST_DIR / "l0_manifest_qwen.json").read_text())
        target = next(t for t in manifest["targets"] if t["axis"] == "location")
        support = tuple(target["support"])
        letters = tuple(target["location_prior"]["option_letters"])
        pc = elicited_pseudo_counts_from_cache(
            cache, manifest["model_id"], "verbalized", target["location_prior"]["verbalized"],
            support, letters, concentration=12.0, key=target["key"],
        )
        assert sum(pc.pseudo_counts.values()) == pytest.approx(12.0)
        assert set(pc.pseudo_counts) == set(support)

    def test_raises_parse_failure_on_bad_prompt_hash(self):
        from dynamic_home_eqa.llm_prior.scoring import ParseFailure

        cache = EliciationCache(_CACHE_DIR)
        with pytest.raises(ParseFailure):
            elicited_pseudo_counts_from_cache(
                cache, "nonexistent-model", "verbalized", "nonexistent-hash",
                ("a", "b"), ("A", "B"), concentration=5.0, key="k",
            )
