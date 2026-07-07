"""
JSON serialisation for EQA question batches.

Answer key travels with the questions in the prototype (correct_index included
per record).  Split it into a separate file only if/when the set is released.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .questions import MCQuestion


def question_to_dict(q: MCQuestion) -> dict:
    return {
        "prompt":        q.prompt,
        "options":       q.options,
        "correct_index": q.correct_index,
        "difficulty_bin": q.spec.difficulty_bin,
        "metadata":      q.metadata,
    }


def batch_to_json(
    questions: list[MCQuestion],
    path: Union[str, Path, None] = None,
) -> str:
    """Serialise a batch to JSON.  Writes to path if given; always returns the string."""
    by_bin: dict[str, int] = {}
    for q in questions:
        b = q.spec.difficulty_bin or "unset"
        by_bin[b] = by_bin.get(b, 0) + 1

    data = {
        "total":         len(questions),
        "by_difficulty": by_bin,
        "questions":     [question_to_dict(q) for q in questions],
    }
    text = json.dumps(data, indent=2)
    if path is not None:
        Path(path).write_text(text)
    return text


def batch_from_json(path: Union[str, Path]) -> dict:
    """Load a saved batch.  Returns the raw dict (questions under 'questions' key)."""
    return json.loads(Path(path).read_text())
