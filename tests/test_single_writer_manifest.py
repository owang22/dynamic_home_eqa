"""
VoI validation batch, item 3: single-writer manifest enforcement.

embodied/attribution.py's write_result_manifest is the one function that
should ever construct a milestone result manifest (stamping fingerprint
and code_hash). The coverage-repair phase found two gate scripts
(embodied_m2_gate.py, embodied_m3_gate.py) bypassing it by merging several
rerun_frozen_e0 calls' temp files into a final manifest via their own
separate json.dumps — silently omitting code_hash. This test greps every
.py file in the repo for the manifest-construction shape (both
'"milestone":' and '"fingerprint":' as dict-literal keys, the same shape
write_result_manifest itself produces) outside attribution.py, so a new
script that writes its own manifest fails this test rather than relying
on review to catch it.

Pure text scan — no habitat_sim, no imports of the scanned modules needed.
"""
from __future__ import annotations

import pathlib

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()

# The one legitimate constructor of this manifest shape.
_CANONICAL_WRITER = _DYNAMIC_EQA / "embodied" / "attribution.py"

# Test fixtures legitimately construct synthetic manifest dicts to feed
# build_attribution_table.py's own fingerprint/code-hash checks — that is
# testing the READER, not a second writer in production code.
_ALLOWED_FIXTURES = {
    _DYNAMIC_EQA / "tests" / "test_build_attribution_table.py",
    pathlib.Path(__file__).resolve(),  # this file's own docstring/markers, not a real constructor
}

_MANIFEST_KEY_MARKERS = ('"milestone":', '"fingerprint":')


def _constructs_manifest_shape(path: pathlib.Path) -> bool:
    text = path.read_text()
    return all(marker in text for marker in _MANIFEST_KEY_MARKERS)


def _all_python_files() -> list[pathlib.Path]:
    return [
        p for p in _DYNAMIC_EQA.rglob("*.py")
        if "__pycache__" not in p.parts
    ]


def test_only_attribution_py_constructs_the_manifest_shape():
    offenders = [
        p for p in _all_python_files()
        if p != _CANONICAL_WRITER and p not in _ALLOWED_FIXTURES and _constructs_manifest_shape(p)
    ]
    assert offenders == [], (
        f"Found {len(offenders)} file(s) constructing a result-manifest-shaped dict "
        f"(both '\"milestone\":' and '\"fingerprint\":' as literal keys) outside "
        f"embodied/attribution.py's write_result_manifest: {offenders}. Route the final "
        f"write through attribution.write_result_manifest (or rerun_frozen_e0/"
        f"rerun_frozen_state_e0, which call it) instead of constructing the manifest "
        f"dict directly — see this test's own module docstring for why."
    )


def test_canonical_writer_itself_is_detected_by_the_marker_scan():
    """Sanity check on the detector itself: attribution.py must actually
    contain both markers, or the scan above would pass vacuously (nothing
    to exempt) without ever having tested anything."""
    assert _constructs_manifest_shape(_CANONICAL_WRITER)


def test_embodied_m2_and_m3_gates_no_longer_construct_their_own_manifest():
    """Regression test for the exact bug this item fixes: these two
    scripts used to merge rerun_frozen_e0's temp-file rows into a manifest
    via their own json.dumps, bypassing code_hash entirely."""
    for name in ("embodied_m2_gate.py", "embodied_m3_gate.py"):
        path = _DYNAMIC_EQA / "scripts" / name
        assert not _constructs_manifest_shape(path), f"{name} still constructs its own manifest dict"
