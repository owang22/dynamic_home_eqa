#!/usr/bin/env python3
"""
llm_prior/elicit.py — L0's elicitation script. The ONLY module in this
project that may make a live LLM call for the L0 phase (llm_prior/
client.py provides the model wrapper; this script is the one caller of
it). Every response is written through llm_prior.cache.EliciationCache
before anything downstream reads it — scoring, tests, and the report all
read the cache, never call a model directly.

For each ElicitationTarget (llm_prior/targets.py) and each mode
(mcq_logprob, verbalized, sample_count), builds the mode's prompt
(llm_prior/prompts.py), computes its hash, and either reuses a cached
response or calls the model and caches the result. k=20 for sample_count,
temperature=0/fixed seed everywhere a mode allows it, per L0's own
elicitation-mode rules.

Requires network (first run, to download an ungated model if not already
present) and a local GPU (vLLM). Run from any environment with the vllm
package (a plain venv is fine — this does not need habitat_sim, unlike
the embodied-agent scripts elsewhere in this repo).
"""
from __future__ import annotations

import hashlib
import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.llm_prior.cache import EliciationCache
from dynamic_home_eqa.llm_prior.client import PHI3_CROSS_FAMILY, QWEN_GENERATOR, LLMPriorClient, ModelSpec
from dynamic_home_eqa.llm_prior import prompts
from dynamic_home_eqa.llm_prior.targets import ElicitationTarget, enumerate_targets, render_persona, render_room_inventory

_CACHE_DIR = _DYNAMIC_EQA / "llm_prior_cache"
_MANIFEST_DIR = _DYNAMIC_EQA / "results" / "reports" / "l0_manifests"
_SAMPLE_COUNT_K = 20
_SEED = 0

MODES = ("mcq_logprob", "verbalized", "sample_count")


def _code_hash() -> str:
    h = hashlib.sha256()
    module_dir = pathlib.Path(__file__).parent
    for name in sorted(p.name for p in module_dir.glob("*.py")):
        h.update((module_dir / name).read_bytes())
    return h.hexdigest()[:16]


def _elicit_location(client: LLMPriorClient, cache: EliciationCache, target: ElicitationTarget,
                      persona_text: str, room_text: str) -> dict:
    system, user, letters = prompts.location_mcq_prompt(persona_text, room_text, target.key, target.time_bin, target.support)
    h_mcq = prompts.prompt_hash("location_mcq", system, user)
    if not cache.has(client.spec.model_id, h_mcq, "mcq_logprob", _SEED):
        raw = client.mcq_logprob(system, user, letters, seed=_SEED)
        cache.put(client.spec.model_id, h_mcq, "mcq_logprob", _SEED, prompt=user, raw_response=raw)

    verb_system, verb_user = prompts.location_verbalized_prompt(persona_text, room_text, target.key, target.time_bin, target.support)
    h_verb = prompts.prompt_hash("location_verbalized", verb_system, verb_user)
    if not cache.has(client.spec.model_id, h_verb, "verbalized", _SEED):
        raw = client.verbalized(verb_system, verb_user, seed=_SEED)
        cache.put(client.spec.model_id, h_verb, "verbalized", _SEED, prompt=verb_user, raw_response=raw)

    sample_combined, sample_letters = prompts.location_sample_prompt(persona_text, room_text, target.key, target.time_bin, target.support)
    h_sample = prompts.prompt_hash("location_sample", sample_combined)
    if not cache.has(client.spec.model_id, h_sample, "sample_count", _SEED):
        system_s, user_s, _ = prompts.location_mcq_prompt(persona_text, room_text, target.key, target.time_bin, target.support)
        raw = client.sample_count(system_s, user_s, sample_letters, k=_SAMPLE_COUNT_K, seed=_SEED)
        cache.put(client.spec.model_id, h_sample, "sample_count", _SEED, prompt=sample_combined, raw_response=raw)

    return {"mcq_logprob": h_mcq, "verbalized": h_verb, "sample_count": h_sample, "option_letters": letters}


def _elicit_dynamics(client: LLMPriorClient, cache: EliciationCache, target: ElicitationTarget,
                      persona_text: str, room_text: str) -> dict:
    is_state = target.axis == "state"
    system, user, letters = prompts.dynamics_mcq_prompt(persona_text, room_text, target.key, target.time_bin, is_state)
    h_mcq = prompts.prompt_hash("dynamics_mcq", system, user)
    if not cache.has(client.spec.model_id, h_mcq, "mcq_logprob", _SEED):
        raw = client.mcq_logprob(system, user, letters, seed=_SEED)
        cache.put(client.spec.model_id, h_mcq, "mcq_logprob", _SEED, prompt=user, raw_response=raw)

    verb_system, verb_user = prompts.dynamics_verbalized_prompt(persona_text, room_text, target.key, target.time_bin, is_state)
    h_verb = prompts.prompt_hash("dynamics_verbalized", verb_system, verb_user)
    if not cache.has(client.spec.model_id, h_verb, "verbalized", _SEED):
        raw = client.verbalized(verb_system, verb_user, seed=_SEED)
        cache.put(client.spec.model_id, h_verb, "verbalized", _SEED, prompt=verb_user, raw_response=raw)

    sample_combined, sample_letters = prompts.dynamics_sample_prompt(persona_text, room_text, target.key, target.time_bin, is_state)
    h_sample = prompts.prompt_hash("dynamics_sample", sample_combined)
    if not cache.has(client.spec.model_id, h_sample, "sample_count", _SEED):
        system_s, user_s, _ = prompts.dynamics_mcq_prompt(persona_text, room_text, target.key, target.time_bin, is_state)
        raw = client.sample_count(system_s, user_s, sample_letters, k=_SAMPLE_COUNT_K, seed=_SEED)
        cache.put(client.spec.model_id, h_sample, "sample_count", _SEED, prompt=sample_combined, raw_response=raw)

    return {"mcq_logprob": h_mcq, "verbalized": h_verb, "sample_count": h_sample, "option_letters": letters}


def run_elicitation(spec: ModelSpec, out_dir: pathlib.Path) -> pathlib.Path:
    """Per L0's own spec, "Location prior" (categorical P(slot_type)) and
    "Dynamics prior" (stay-probability / flip-rate) are NOT one-per-axis
    alternatives — dynamics applies to BOTH location categories (stay-
    probability) and state variables (flip-rate); only the location prior
    is location-axis-specific (state variables don't have "slot types").
    An earlier version of this function called _elicit_location XOR
    _elicit_dynamics per target's axis, silently never eliciting a
    location category's own dynamics prior at all — found via report.py's
    "n_parse_failures=36 (every location target)" and fixed here: every
    location target gets BOTH; every state target gets dynamics only."""
    targets = enumerate_targets(out_dir, FROZEN)
    result = json.loads((out_dir / FROZEN.train_folders[0] / "generation_result.json").read_text())
    persona_text = render_persona(result["persona"])
    # L0 rerun fix: every location-axis category being asked about must be
    # named as present in the household, or the model reasonably (and, in
    # v1, verifiably) infers "not in inventory -> OUTSIDE" — see
    # render_room_inventory's own docstring.
    known_categories = tuple(sorted({t.key for t in targets if t.axis == "location"}))
    room_text = render_room_inventory(FROZEN.scene, known_categories=known_categories)

    client = LLMPriorClient(spec)
    index: list[dict] = []
    cache = EliciationCache(_CACHE_DIR)
    for target in targets:
        dynamics_hashes = _elicit_dynamics(client, cache, target, persona_text, room_text)
        entry = {
            "axis": target.axis, "key": target.key, "time_bin": target.time_bin,
            "support": list(target.support), "dynamics_prior": dynamics_hashes,
        }
        if target.axis == "location":
            entry["location_prior"] = _elicit_location(client, cache, target, persona_text, room_text)
        index.append(entry)
        print(f"  {target.axis}/{target.key}/t{target.time_bin}: cached")

    _MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = _MANIFEST_DIR / f"l0_manifest_{spec.family}.json"
    manifest_path.write_text(json.dumps({
        "model_id": spec.model_id, "family": spec.family, "provider": spec.provider,
        "quantization": spec.quantization, "is_generator_family": spec.is_generator_family,
        "prompt_version": prompts.PROMPT_VERSION, "code_hash": _code_hash(),
        "sample_count_k": _SAMPLE_COUNT_K, "seed": _SEED,
        "n_targets": len(targets), "targets": index,
    }, indent=2))
    return manifest_path


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", choices=("qwen", "phi3"), required=True)
    args = ap.parse_args()

    spec = QWEN_GENERATOR if args.model == "qwen" else PHI3_CROSS_FAMILY
    out_dir = _DYNAMIC_EQA / "generation_out"
    print(f"Eliciting with {spec.model_id} ({spec.family}, {'same' if spec.is_generator_family else 'cross'}-family)")
    manifest_path = run_elicitation(spec, out_dir)
    print(f"\nWrote {manifest_path}")


if __name__ == "__main__":
    main()
