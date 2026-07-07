"""
Tests for scripts/scene_validation.py's shared "load a folder and validate
it" helper (Suite Buildout phase A's contamination-audit primitive).
"""
from __future__ import annotations

import json
import pathlib

from dynamic_home_eqa.scripts.scene_validation import validate_folder, validate_folders


def _write_folder(tmp_path: pathlib.Path, name: str, changes: list[dict], traces: list[dict]) -> None:
    d = tmp_path / name
    d.mkdir()
    (d / "manifest.json").write_text(json.dumps({"changes": changes}))
    (d / "generation_result.json").write_text(json.dumps({"traces": traces}))


_TRACES = [{"occupant_name": "Alex", "activities": [
    {"activity": "resting", "location": "kitchen", "start": 0.0, "end": 24.0},
]}]


def test_validate_folder_reports_ok_for_clean_data(tmp_path):
    _write_folder(tmp_path, "clean_day", [
        {"t": 1.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
    ], _TRACES)
    report = validate_folder(tmp_path, "clean_day")
    assert report.ok


def test_validate_folder_reports_failure_for_corrupted_data(tmp_path):
    _write_folder(tmp_path, "bad_day", [
        {"t": 1.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "from_semantic": "x", "to_semantic": "x"},
    ], _TRACES)
    report = validate_folder(tmp_path, "bad_day")
    assert not report.ok
    assert report.no_ops == 1


def test_validate_folders_covers_every_requested_folder(tmp_path):
    _write_folder(tmp_path, "day_a", [
        {"t": 1.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
    ], _TRACES)
    _write_folder(tmp_path, "day_b", [
        {"t": 1.0, "label": "vase_1", "change_type": "move_existing",
         "object_category": "vase", "from_semantic": "x", "to_semantic": "x"},
    ], _TRACES)
    reports = validate_folders(tmp_path, ["day_a", "day_b"])
    assert set(reports.keys()) == {"day_a", "day_b"}
    assert reports["day_a"].ok
    assert not reports["day_b"].ok
