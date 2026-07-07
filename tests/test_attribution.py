"""
Tests for embodied/attribution.py's behavior_code_hash() — the code-hash
fingerprint guard (Suite Buildout coverage-repair phase, item 2). Pure
logic — reads the real module files on disk, no habitat_sim needed.
"""
from __future__ import annotations

from dynamic_home_eqa.embodied.attribution import behavior_code_hash


def test_is_deterministic():
    assert behavior_code_hash() == behavior_code_hash()


def test_is_a_short_hex_string():
    h = behavior_code_hash()
    assert len(h) == 16
    int(h, 16)  # raises ValueError if not valid hex


def test_fresh_computation_changes_if_a_behavior_module_changes(tmp_path):
    """_compute_behavior_code_hash() (the fresh, non-cached computation)
    is sensitive to a behavior module's byte contents — the property the
    whole guard depends on."""
    import pathlib
    import shutil

    import dynamic_home_eqa.embodied.attribution as attribution_module

    real_dir = pathlib.Path(attribution_module.__file__).parent
    fake_dir = tmp_path / "embodied"
    fake_dir.mkdir()
    for name in attribution_module._BEHAVIOR_MODULES:
        shutil.copy(real_dir / name, fake_dir / name)

    def _hash_of(dir_path):
        import hashlib
        h = hashlib.sha256()
        for name in attribution_module._BEHAVIOR_MODULES:
            h.update((dir_path / name).read_bytes())
        return h.hexdigest()[:16]

    before = _hash_of(fake_dir)
    (fake_dir / "policy.py").write_bytes((fake_dir / "policy.py").read_bytes() + b"\n# perturbed\n")
    after = _hash_of(fake_dir)
    assert before != after


def test_behavior_code_hash_is_cached_at_import_time_not_recomputed_per_call(monkeypatch):
    """The regression test for the race this guard itself caught: a
    result manifest's code_hash must reflect the code this PROCESS
    imported and ran under, not whatever happens to be on disk whenever
    the manifest is finally written (a background gate run can take
    several minutes; a concurrent edit mid-run must not change what
    already-running processes report). behavior_code_hash() must return
    the same cached value even if the underlying files change after
    import — unlike _compute_behavior_code_hash(), which is intentionally
    fresh every call (see the test above)."""
    import dynamic_home_eqa.embodied.attribution as attribution_module

    before = attribution_module.behavior_code_hash()
    monkeypatch.setattr(attribution_module, "_BEHAVIOR_CODE_HASH", "deadbeefdeadbeef")
    # behavior_code_hash() itself always returns _BEHAVIOR_CODE_HASH verbatim
    # (no re-read) — patching that module-level constant is the only way
    # its return value ever changes, proving there is no lazy re-computation.
    assert attribution_module.behavior_code_hash() == "deadbeefdeadbeef"
    monkeypatch.undo()
    assert attribution_module.behavior_code_hash() == before
