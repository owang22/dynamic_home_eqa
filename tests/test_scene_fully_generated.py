"""
Regression test for scripts/expand_scene_pool.py's _scene_fully_generated
bug (Results-First batch, the one allowed must-fix): it used to check
file existence only, so generate_scene() would report a scene "fully
generated" and skip regeneration even when a folder's manifest failed
trace_validate — exactly what happened to 102344049's day0 (corrupted
since before this session's manifest.py fixes) in every expand_scene_pool
run across this project's history. _scene_fully_generated must delegate
to _folder_ready (which does call trace_validate) for every folder.

Pure logic — no habitat_sim needed (only reads JSON fixtures on disk).
"""
from __future__ import annotations

import json

from dynamic_home_eqa.scripts.expand_scene_pool import _scene_fully_generated


def _write_folder(out_dir, name, changes, traces):
    d = out_dir / name
    d.mkdir(parents=True)
    (d / "manifest.json").write_text(json.dumps({"changes": changes}))
    (d / "generation_result.json").write_text(json.dumps({"traces": traces}))


def test_false_when_a_folder_is_missing(tmp_path):
    assert not _scene_fully_generated("999999", "family_with_kids", tmp_path)


def test_false_when_a_folders_manifest_fails_trace_validate(tmp_path, monkeypatch):
    import dynamic_home_eqa.scripts.expand_scene_pool as module

    # _folder_names produces (day0, train_folders, eval_folder); stub it so
    # this test only needs one folder, independent of the real naming
    # scheme, and independent of any change to that scheme in the future.
    monkeypatch.setattr(module, "_folder_names", lambda scene_id, profile: ("day0", ("day0",), "day0"))

    def fake_folder_ready(out_dir, folder):
        return False  # simulates a manifest that exists but fails trace_validate

    monkeypatch.setattr(module, "_folder_ready", fake_folder_ready)
    (tmp_path / "day0").mkdir()
    assert not _scene_fully_generated("999999", "family_with_kids", tmp_path)


def test_true_only_when_every_folder_passes_folder_ready(tmp_path, monkeypatch):
    import dynamic_home_eqa.scripts.expand_scene_pool as module

    monkeypatch.setattr(module, "_folder_names", lambda scene_id, profile: ("day0", ("day0", "day1"), "day1"))
    monkeypatch.setattr(module, "_folder_ready", lambda out_dir, folder: True)
    assert _scene_fully_generated("999999", "family_with_kids", tmp_path)


def test_delegates_to_folder_ready_not_bare_existence(tmp_path, monkeypatch):
    """The exact regression: files exist (would pass a bare-existence
    check) but _folder_ready reports not-ready (trace_validate failed) —
    _scene_fully_generated must follow _folder_ready's verdict, not the
    files' mere presence."""
    import dynamic_home_eqa.scripts.expand_scene_pool as module

    monkeypatch.setattr(module, "_folder_names", lambda scene_id, profile: ("day0", ("day0",), "day0"))
    monkeypatch.setattr(module, "_folder_ready", lambda out_dir, folder: False)

    d = tmp_path / "day0"
    d.mkdir()
    (d / "manifest.json").write_text("{}")
    (d / "generation_result.json").write_text("{}")

    assert not _scene_fully_generated("999999", "family_with_kids", tmp_path)
