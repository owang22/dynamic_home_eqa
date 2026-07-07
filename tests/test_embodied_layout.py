"""
Enforces embodied/ground_truth.py's core safety property by inspection, not
just convention: EmbodiedWorld, BeliefStore, and every DecisionPolicy must
never import it, or an agent could trivially "cheat" the resense-vs-answer
decision this whole phase exists to study. runner.py (scoring code) and
question.py (the question generator, which needs the current true anchor
to build non-degenerate distractors — see its module docstring) are the
two modules allowed to; policies only ever see question.options, never
question-generation-time ground truth.
"""
from __future__ import annotations

import ast
import pathlib

_EMBODIED_DIR = pathlib.Path(__file__).parent.parent / "embodied"

_FORBIDDEN_IMPORTERS = [
    "world.py", "sensor.py", "belief.py", "policy.py", "types.py", "config.py", "scoring.py",
]
_ALLOWED_IMPORTERS = ["runner.py", "question.py"]


def _imported_module_names(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
    return names


def test_ground_truth_module_exists():
    assert (_EMBODIED_DIR / "ground_truth.py").is_file()


def test_forbidden_modules_never_import_ground_truth():
    offenders = []
    for filename in _FORBIDDEN_IMPORTERS:
        path = _EMBODIED_DIR / filename
        assert path.is_file(), f"expected {path} to exist"
        imports = _imported_module_names(path)
        if any("ground_truth" in name for name in imports):
            offenders.append(filename)
    assert not offenders, f"modules that must not import ground_truth but do: {offenders}"


def test_allowed_modules_do_import_ground_truth():
    for filename in _ALLOWED_IMPORTERS:
        path = _EMBODIED_DIR / filename
        assert path.is_file(), f"expected {path} to exist"
        imports = _imported_module_names(path)
        assert any("ground_truth" in name for name in imports), (
            f"{filename} is designated scoring/generation code — expected it to import ground_truth"
        )
