#!/usr/bin/env python3
"""
expand_scene_pool.py — expand the qualified-scene pool for the upcoming
E1-E4 experiment suite beyond scene 102343992's 9 frozen labels (see
embodied/experiment_config.py — that scene alone can't supply the
>=100-questions-per-stratum bar E1-E4 need).

Per-scene pipeline, in order, cheapest first:

  1. Reachability pre-flight (embodied.reachability.check_reachability_invariant)
     — pure scene-geometry check under the frozen NavMeshConfig, no LLM call.
     A scene that fails is skipped before any generation is spent on it.
  2. Multi-day generation (scripts/gen_dataset.py) — 4 train days (day 0..3,
     one call with default n_days=1 for day 0 + one call with day=1,
     n_days=3 for days 1-3) + 1 eval day (day 4, its own call so it lands in
     its own _day4 folder) — mirroring exactly how 102343992's 5
     generation_out/ folders were produced (verified: the day-0 folder has
     no _day suffix, which only happens when a run_batch call's own
     n_days==1 — see pipeline.run_batch's docstring — so day 0 must have
     been its own single-day call, separate from the call that produced
     days 1-4 with a suffix on every folder including the first of that
     call).

     Profile is assigned per scene, not hardcoded to "family_with_kids" —
     the E1-E4 pool needs real household-type diversity (see
     generation/persona/profiles.py's HOUSEHOLD_PROFILES), not N copies of
     one family structure. Resolution order per scene (see
     _resolve_profile()): (a) a scene already carrying generation_out/
     folders under some profile (102343992 frozen, 102344022/102344049
     pre-probed, or anything else already in progress before this profile-
     diversification pass existed) keeps that profile — switching a
     household mid-scene would just create a second, unrelated household
     for the same house, not "continue" the first one, since persona is
     keyed by household_id = f"{scene_id}_{household_type}"; (b) otherwise
     a fresh scene gets a deterministic hash-of-scene_id pick from
     HOUSEHOLD_PROFILES, stable across resumed runs and independent of
     candidate-list order (so growing the pool later doesn't reshuffle
     already-assigned scenes the way a running round-robin index would).
  3. Qualified-label count — embodied.sampling.qualify_labels()'s
     two-property rule (exists at patrol_start, every historical anchor
     slot reachable), via compute_frozen_labels.compute_qualifying_labels(),
     generalized from that script's scene-102343992-only pattern to take
     scene/eval_folder/train_folders as parameters (see that module).
  4. M3 state-change stratum (scripts/generate_state_stratum.py) — a
     deterministic, no-LLM/no-habitat_sim second pass over each folder
     (generation/pipeline.py's build_manifest() call doesn't itself set
     include_state_changes=True, so location-only generation never
     produces this stratum on its own). Writes <folder>_state siblings,
     never modifies the location folders qualify_scene_labels/
     FROZEN_LABELS read — a folder whose merged state+location trace
     fails trace_validate is reported and left unwritten, not forced.

State is checkpointed to a JSON file (--state) after every stage of every
scene, so an interrupted run resumes without repeating a reachability check
or a generation call already recorded done (scripts/gen_dataset.py's own
--cache-dir separately caches raw per-call LLM responses keyed by seed —
this state file is one level up, tracking which *stages* completed, so a
resumed run doesn't even re-invoke gen_dataset.py for a scene already fully
generated). "Generated" itself now means more than file existence — see
_folder_ready()'s trace_validate check, added after two pre-probed scenes'
day-0 folders turned out to predate this session's manifest.py
trace-integrity fixes and were sitting on disk with real hard-invariant
violations that a bare existence check would never have caught.

Two Python environments are involved, invoked as separate stages — this
script itself must run under the one with habitat_sim (e.g. the
`explore-eqa` conda env), since steps 1 and 3 import it in-process; step 2
(scripts/gen_dataset.py) needs vllm instead, which explore-eqa does not
have, so it is always run as a subprocess under _GEN_PYTHON (plain
python3 — confirmed to have vllm and not habitat_sim in this environment).

Usage:
    # Modest first batch (pipeline sanity check before scaling up)
    /home/oliver/miniconda3/envs/explore-eqa/bin/python \\
        dynamic_home_eqa/scripts/expand_scene_pool.py --n 9

    # Specific scenes
    ... expand_scene_pool.py --scenes 102344094 102344115

    # Reachability only, no generation (fast triage across many scenes)
    ... expand_scene_pool.py --n 30 --skip-generation
"""
from __future__ import annotations

import argparse
import dataclasses
import glob
import hashlib
import json
import pathlib
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.config import NavMeshConfig
from dynamic_home_eqa.embodied.reachability import check_reachability_invariant
from dynamic_home_eqa.generation.persona import HOUSEHOLD_PROFILES
from dynamic_home_eqa.scripts.compute_frozen_labels import compute_qualifying_labels
from dynamic_home_eqa.scripts.generate_state_stratum import (
    build_state_stratum_for_folder, discover_folders as discover_state_folders,
)
from dynamic_home_eqa.trace_validate import validate as validate_trace

HSSD_DIR = "/mnt/nvme/oliver/robot/datasets/moving-eqa/scene_datasets/hssd-hab"

# Plain python3 in this environment resolves to a base conda env with vllm
# installed and no habitat_sim — the inverse of the interpreter this script
# itself must run under. Hardcoded (not sys.executable) because this script
# runs under explore-eqa, and sys.executable there is the wrong interpreter
# for the generation subprocess.
_GEN_PYTHON = "/home/oliver/miniconda3/bin/python3"
_GEN_SCRIPT = _DYNAMIC_EQA / "scripts" / "gen_dataset.py"

_ALREADY_DONE = {"102343992"}  # fully generated + frozen; not a candidate

# Already ran qualify_scene.py under the current (fixed) navmesh config by
# hand before this script existed — both PASS. Recorded here so this script
# doesn't repeat the check, per the task instruction not to redo it.
_PRE_VERIFIED_REACHABLE: dict[str, str] = {
    "102344022": "22/22 rooms+anchors reachable (pre-verified via qualify_scene.py, island 0)",
    "102344049": "21/21 rooms+anchors reachable (pre-verified via qualify_scene.py, island 0)",
}

_N_TRAIN_DAYS = 4  # days 0..3 -> train_folders; day 4 -> eval_folder
_PATROL_START = 6.0  # matches experiment_config.FROZEN_PATROL_START


def _assign_profile(scene_id: str) -> str:
    """Deterministic profile pick for a scene with no generation_out/ data
    yet — hash(scene_id) mod len(HOUSEHOLD_PROFILES), not a running
    round-robin counter, so it's stable regardless of what order scenes are
    processed in or how many more get added to the pool later (a counter
    would reshuffle every previously-assigned scene's profile the moment
    the candidate list's length or order changed between runs)."""
    digest = hashlib.sha256(scene_id.encode()).digest()
    idx = int.from_bytes(digest[:8], "little") % len(HOUSEHOLD_PROFILES)
    return HOUSEHOLD_PROFILES[idx]


def _detect_existing_profile(scene_id: str, out_dir: pathlib.Path) -> Optional[str]:
    """If this scene already has any generation_out/ folder on disk (frozen
    102343992, the 2 pre-probed scenes, or anything else generated before
    this profile-diversification pass existed), keep using that profile —
    switching profiles mid-scene wouldn't "continue" it, it'd start a
    second, unrelated household for the same house (household_id includes
    the profile string, so every downstream seed would change too)."""
    for profile in HOUSEHOLD_PROFILES:
        base = f"{scene_id}_{profile}"
        if (out_dir / base).exists() or any(out_dir.glob(f"{base}_day*")):
            return profile
    return None


def discover_candidate_scenes(exclude: set[str]) -> list[str]:
    """Same glob pattern as scripts/gen_dataset.py's _ALL_SCENES."""
    all_scenes = sorted(
        pathlib.Path(p).name.split(".scene_instance.json")[0]
        for p in glob.glob(f"{HSSD_DIR}/scenes-uncluttered/*.scene_instance.json")
    )
    return [s for s in all_scenes if s not in exclude]


@dataclass
class ScenePoolEntry:
    scene_id:         str
    reachable:        Optional[bool] = None
    reach_summary:    str = ""
    profile:          str = ""  # resolved once (see _resolve_profile), then frozen for this scene
    generated:        bool = False
    gen_error:        str = ""
    qualified_labels: Optional[list[str]] = None
    n_candidates:     Optional[int] = None
    state_generated:  bool = False  # M3 state-change stratum (scripts/generate_state_stratum.py)
    state_error:      str = ""

    def qualified_count(self) -> Optional[int]:
        return None if self.qualified_labels is None else len(self.qualified_labels)


def _entry_from_dict(d: dict) -> ScenePoolEntry:
    return ScenePoolEntry(**d)


def load_state(path: pathlib.Path) -> dict[str, ScenePoolEntry]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    return {k: _entry_from_dict(v) for k, v in raw.items()}


def save_state(path: pathlib.Path, state: dict[str, ScenePoolEntry]) -> None:
    payload = {k: dataclasses.asdict(v) for k, v in state.items()}
    path.write_text(json.dumps(payload, indent=2))


def _folder_names(scene_id: str, profile: str) -> tuple[str, tuple[str, ...], str]:
    """(day0_folder, train_folders incl. day0, eval_folder) for this scene —
    mirrors 102343992_family_with_kids{,_day1,_day2,_day3,_day4}/ exactly,
    just with scene's assigned profile in place of the literal
    "family_with_kids"."""
    base = f"{scene_id}_{profile}"
    day0 = base
    train_folders = (day0,) + tuple(f"{base}_day{d}" for d in range(1, _N_TRAIN_DAYS))
    eval_folder = f"{base}_day{_N_TRAIN_DAYS}"
    return day0, train_folders, eval_folder


def _run_gen_dataset(scene_id: str, profile: str, day: int, n_days: int, out_dir: pathlib.Path, cache_dir: str, model: str) -> None:
    cmd = [
        _GEN_PYTHON, str(_GEN_SCRIPT),
        "--scenes", scene_id,
        "--profile", profile,
        "--day", str(day),
        "--n-days", str(n_days),
        "--out", str(out_dir),
        "--cache-dir", cache_dir,
        "--model", model,
    ]
    # Streamed line-by-line (not subprocess.run(capture_output=True), which
    # buffers everything until the child exits) and flushed immediately —
    # if this subprocess or its parent gets killed mid-generation, whatever
    # ran before the kill stays on disk in the log instead of vanishing
    # with the child's unread pipe buffer (see main()'s line_buffering note
    # for the sibling half of this same failure mode).
    proc = subprocess.Popen(
        cmd, cwd=str(_REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
    )
    lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="", flush=True)
        lines.append(line)
    returncode = proc.wait()
    output = "".join(lines)
    if returncode != 0:
        raise RuntimeError(f"gen_dataset.py exited {returncode}: {output[-2000:]}")
    # gen_dataset.py reports per-scene errors as "[ERROR] ..." lines but
    # still exits 0 (see pipeline.run_batch's try/except) — treat that as a
    # generation failure too, since the expected folder never gets written.
    if "[ERROR]" in output:
        raise RuntimeError(f"gen_dataset.py reported an error: "
                            f"{[l for l in output.splitlines() if '[ERROR]' in l]}")


def _scene_fully_generated(scene_id: str, profile: str, out_dir: pathlib.Path) -> bool:
    """Results-first batch: this used to check file existence only,
    bypassing _folder_ready's trace_validate check entirely — generate_
    scene() calls this FIRST and returns immediately if it says True, so a
    folder whose files exist but fail trace_validate (e.g. 102344049's
    day0, corrupted since before this session's manifest.py fixes) never
    even reached the folder-by-folder _folder_ready check below that was
    specifically built to catch and regenerate it. Confirmed in practice:
    102344049's day0 failed trace_validate ([FAIL], chain_breaks=4,
    re_inserts=26, no_ops=31, unattended=26) in every expand_scene_pool
    run across this project's history, because this function reported the
    scene "fully generated" before that check ever ran. Delegating to
    _folder_ready for every folder closes the hole — existence alone is
    never sufficient, the same standing rule _folder_ready's own
    docstring already states."""
    _day0, train_folders, eval_folder = _folder_names(scene_id, profile)
    return all(_folder_ready(out_dir, folder) for folder in train_folders + (eval_folder,))


def _folder_ready(out_dir: pathlib.Path, folder: str) -> bool:
    """A folder counts as ready only if its manifest also passes
    trace_validate — existence alone isn't enough. Caught in practice: two
    pre-probed scenes' day-0 folders (102344022, 102344049) predated this
    session's manifest.py trace-integrity fixes and were sitting on disk
    with real hard-invariant violations (chain breaks, re-inserts, no-ops,
    unattended events) that file-existence checks alone would never catch
    — a folder existing says nothing about whether *this* run's pipeline
    code produced it. Re-running gen_dataset.py on a folder that fails
    this check overwrites it (pipeline.run_batch always writes
    unconditionally) using the cached LLM responses' raw text but current
    manifest-building code, so it's a real fix, not just a re-download."""
    d = out_dir / folder
    gr, mf = d / "generation_result.json", d / "manifest.json"
    if not (gr.exists() and mf.exists()):
        return False
    try:
        result   = json.loads(gr.read_text())
        manifest = json.loads(mf.read_text())
        report = validate_trace(manifest["changes"], result["traces"])
    except Exception:
        return False  # unreadable/malformed — treat the same as not-ready
    return report.ok


def generate_scene(scene_id: str, profile: str, out_dir: pathlib.Path, cache_dir: str, model: str) -> None:
    day0, train_folders, eval_folder = _folder_names(scene_id, profile)
    if _scene_fully_generated(scene_id, profile, out_dir):
        return  # resumed run — already on disk (e.g. the 2 pre-probed scenes' day 0)
    # Day 0 alone: a lone call with the default n_days=1 produces the
    # no-suffix folder (see module docstring).
    if not _folder_ready(out_dir, day0):
        _run_gen_dataset(scene_id, profile, day=0, n_days=1, out_dir=out_dir, cache_dir=cache_dir, model=model)
    # Days 1..N_TRAIN_DAYS (train days 1..3 + eval day 4) in one call so
    # every folder in it gets a suffix, including the first (day 1).
    #
    # Checked per-folder, not just eval_folder: a single bad day inside this
    # call (pipeline.run_batch's own per-day try/except lets one failure
    # skip that day's folder without aborting the rest — e.g. 102344022's
    # day 2 hit a malformed-JSON output that exhausted retries, but day
    # 4 == eval_folder still got written) must not read as "this call is
    # done" just because the *last* folder happens to exist. Re-running is
    # cheap for the days that already succeeded — gen_dataset.py's own
    # seed-keyed response cache (--cache-dir) replays their LLM calls
    # instantly — so this only spends real generation time on the gap.
    remaining_days_folders = train_folders[1:] + (eval_folder,)
    if not all(_folder_ready(out_dir, f) for f in remaining_days_folders):
        _run_gen_dataset(scene_id, profile, day=1, n_days=_N_TRAIN_DAYS, out_dir=out_dir, cache_dir=cache_dir, model=model)
    if not _scene_fully_generated(scene_id, profile, out_dir):
        raise RuntimeError(f"generation for {scene_id} did not produce all expected folders "
                            f"({train_folders + (eval_folder,)})")


def qualify_scene_labels(scene_id: str, profile: str, out_dir: pathlib.Path) -> tuple[list[str], int]:
    _day0, train_folders, eval_folder = _folder_names(scene_id, profile)
    results = compute_qualifying_labels(
        scene=scene_id,
        eval_folder=eval_folder,
        train_folders=train_folders,
        patrol_start=_PATROL_START,
        out_dir=out_dir,
    )
    qualifying = sorted(r.label for r in results if r.qualifies)
    return qualifying, len(results)


def _report_line(e: ScenePoolEntry) -> str:
    reach = "PASS" if e.reachable else ("FAIL" if e.reachable is False else "UNKNOWN")
    parts = [f"SCENE={e.scene_id}", f"REACH={reach}"]
    if e.reachable is False:
        parts.append(f"reason=[{e.reach_summary}]")
    if e.reachable:
        if e.profile:
            parts.append(f"PROFILE={e.profile}")
        if e.gen_error:
            parts.append("GEN=ERROR")
            parts.append(f"gen_error=[{e.gen_error}]")
        elif e.generated:
            parts.append("GEN=DONE")
            if e.qualified_labels is not None:
                parts.append(f"LABELS={e.qualified_count()}/{e.n_candidates}")
                parts.append(f"labels={','.join(e.qualified_labels) if e.qualified_labels else '-'}")
            if e.state_error:
                parts.append("STATE=ERROR")
                parts.append(f"state_error=[{e.state_error}]")
            elif e.state_generated:
                parts.append("STATE=DONE")
        else:
            parts.append("GEN=PENDING")
    return "  ".join(parts)


def main() -> None:
    # Line-buffer stdout even when redirected to a file/pipe (the default is
    # full block buffering in that case) — a run that gets killed out from
    # under us (session/container recycle, not caught by any try/except
    # here) must not lose the progress lines already "printed" but still
    # sitting in an unflushed buffer. Cost: the ~9.5 hour gap in run #1
    # where the orchestrator process died silently with a 0-byte log,
    # leaving only the on-disk generation_out/ folders and no record of
    # why — see the state file / this script's git history for that
    # incident. This does not explain the death itself (most likely an
    # external process/session teardown — memory was fine, host uptime
    # showed no reboot, no OOM in dmesg), only makes the *next* one legible.
    sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=9,
                     help="Number of new candidate scenes to process, beyond the 2 "
                          "already-probed ones which are always included (default: 9)")
    ap.add_argument("--scenes", nargs="+", default=None,
                     help="Explicit candidate scene ids (overrides --n discovery)")
    ap.add_argument("--out", default=str(_DYNAMIC_EQA / "generation_out"))
    ap.add_argument("--cache-dir", default="/tmp/dynamic-home-eqa-gen-cache")
    # NOT generation.llm_client.DEFAULT_MODEL ("Qwen/Qwen3-14B-Instruct") —
    # that model id does not exist on the Hub (confirmed: HF API 401) and
    # is not what's cached locally. "Qwen/Qwen3-14B-AWQ" is the model
    # actually cached under HF_HOME and is the production model used
    # elsewhere in this repo (agents/llm_agent.py's MODEL_14B,
    # scripts/compare_agents.py's _DEFAULT_MODEL) — passed explicitly here
    # rather than relying on gen_dataset.py's own default.
    ap.add_argument("--model", default="Qwen/Qwen3-14B-AWQ")
    ap.add_argument("--state", default=str(_DYNAMIC_EQA / "generation_out" / "_expand_scene_pool_state.json"))
    ap.add_argument("--skip-generation", action="store_true",
                     help="Reachability pre-flight only, no generation/qualification "
                          "(fast triage across many candidate scenes)")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out)
    state_path = pathlib.Path(args.state)
    state = load_state(state_path)

    if args.scenes:
        candidates = list(args.scenes)
    else:
        pool = discover_candidate_scenes(exclude=_ALREADY_DONE)
        # Always include the 2 pre-probed scenes first, then top up to --n
        # with fresh candidates never touched before.
        pre_probed = [s for s in ("102344022", "102344049") if s in pool]
        fresh = [s for s in pool if s not in pre_probed and s not in state]
        candidates = pre_probed + fresh[: max(0, args.n)]

    print(f"Candidates this run: {len(candidates)} -> {candidates}")
    print()

    for scene_id in candidates:
        entry = state.get(scene_id, ScenePoolEntry(scene_id=scene_id))

        if entry.reachable is None:
            if scene_id in _PRE_VERIFIED_REACHABLE:
                entry.reachable = True
                entry.reach_summary = _PRE_VERIFIED_REACHABLE[scene_id]
            else:
                result = check_reachability_invariant(scene_id, NavMeshConfig())
                entry.reachable = result.ok
                entry.reach_summary = result.summary()
            state[scene_id] = entry
            save_state(state_path, state)
            print(_report_line(entry))

        if not entry.reachable:
            continue
        if args.skip_generation:
            continue

        if not entry.profile:
            entry.profile = _detect_existing_profile(scene_id, out_dir) or _assign_profile(scene_id)
            state[scene_id] = entry
            save_state(state_path, state)
            print(_report_line(entry))

        # Re-verify on disk rather than trusting a saved entry.generated=True
        # blindly — caught in practice: 102344049's state said generated=True
        # from before this session's manifest.py trace-integrity fixes
        # landed, but its day-0 folder was actually stale/corrupted
        # (trace_validate hard-invariant violations); a boolean cached from
        # an earlier, now-invalid definition of "ready" must not stop this
        # from being caught and regenerated on the next run.
        if not entry.generated or not _scene_fully_generated(scene_id, entry.profile, out_dir):
            try:
                generate_scene(scene_id, entry.profile, out_dir, args.cache_dir, args.model)
                entry.generated = True
                entry.gen_error = ""
                # Underlying data changed (or is being verified fresh) —
                # anything computed from the old data is stale too.
                entry.qualified_labels = None
                entry.n_candidates = None
                entry.state_generated = False
                entry.state_error = ""
            except Exception as e:  # noqa: BLE001 - report and move to next scene
                entry.generated = False
                entry.gen_error = str(e)
            state[scene_id] = entry
            save_state(state_path, state)
            print(_report_line(entry))

        if entry.generated and entry.qualified_labels is None:
            try:
                qualifying, n_candidates = qualify_scene_labels(scene_id, entry.profile, out_dir)
                entry.qualified_labels = qualifying
                entry.n_candidates = n_candidates
            except Exception as e:  # noqa: BLE001
                entry.gen_error = f"label qualification failed: {e}"
            state[scene_id] = entry
            save_state(state_path, state)
            print(_report_line(entry))

        # M3 state-change stratum second pass (scripts/generate_state_stratum.py)
        # — deterministic, no LLM/habitat_sim, so this always runs once
        # location generation is clean (entry.generated only becomes True
        # once every folder passes trace_validate — see _folder_ready).
        # Non-destructive: writes <folder>_state siblings, never touches
        # the location folders qualify_scene_labels/FROZEN_LABELS read.
        if entry.generated and not entry.state_generated and not entry.state_error:
            try:
                folders = discover_state_folders(out_dir, scene_id, entry.profile)
                failures = [f for f in folders if not build_state_stratum_for_folder(scene_id, out_dir, f)]
                if failures:
                    entry.state_error = f"trace_validate failed on merged state+location for: {failures}"
                else:
                    entry.state_generated = True
            except Exception as e:  # noqa: BLE001
                entry.state_error = f"state stratum generation failed: {e}"
            state[scene_id] = entry
            save_state(state_path, state)
            print(_report_line(entry))

    print()
    print("=" * 70)
    print("Final report:")
    n_pass = sum(1 for e in state.values() if e.reachable)
    n_fail = sum(1 for e in state.values() if e.reachable is False)
    n_gen  = sum(1 for e in state.values() if e.generated)
    n_state = sum(1 for e in state.values() if e.state_generated)
    total_labels = sum(e.qualified_count() or 0 for e in state.values() if e.qualified_count() is not None)
    for scene_id in candidates:
        print(_report_line(state[scene_id]))
    print(f"\nReachability: {n_pass} pass / {n_fail} fail / {len(state)} checked total")
    print(f"Generated: {n_gen}")
    print(f"State stratum generated: {n_state}")
    print(f"Total qualified labels across pool (this run's scenes): {total_labels}")


if __name__ == "__main__":
    main()
