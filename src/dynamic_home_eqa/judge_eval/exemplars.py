"""
Few-shot exemplar block for the strict judge (Phase 2.2).

Builds a small set of worked examples from the held-out EXEMPLAR subset —
each a real candidate line with its human band converted to a score and a
one-line rationale — that gets prepended to the strict judge prompt. The
block is passed to score_realism_batch as a string; its content hash is
folded into the judge stage tag there, so a changed exemplar set splits the
cache cleanly (no leakage: EXEMPLAR candidates are never in EVAL).
"""
from __future__ import annotations

from .labels import Candidate

# Human band -> the score an exemplar teaches (mid of each strict band).
_BAND_SCORE = {3: 0.9, 2: 0.6, 1: 0.3, 0: 0.05}
_BAND_GLOSS = {
    3: "typical — exactly what someone doing this would do",
    2: "plausible but less common",
    1: "contrived — you'd need a story",
    0: "no believable connection to the activity",
}


def select_exemplars(exemplar_pool: list[Candidate], n: int = 6) -> list[Candidate]:
    """Pick up to n exemplars spanning the bands, guaranteed to include a
    dinner-laptop case (the archetype the base judge over-scores). Deterministic
    (sorted by id)."""
    pool = sorted(exemplar_pool, key=lambda c: c.candidate_id)
    picked: list[Candidate] = []
    # one dinner-laptop first
    dl = [c for c in pool if c.is_dinner_laptop]
    if dl:
        picked.append(dl[0])
    # then spread across bands (3,2,1,0 cycling) without repeats
    by_band: dict[int, list[Candidate]] = {0: [], 1: [], 2: [], 3: []}
    for c in pool:
        by_band[c.human_band].append(c)
    idx = {b: 0 for b in by_band}
    while len(picked) < n and any(idx[b] < len(by_band[b]) for b in by_band):
        for b in (3, 2, 1, 0):
            if len(picked) >= n:
                break
            while idx[b] < len(by_band[b]):
                c = by_band[b][idx[b]]
                idx[b] += 1
                if c not in picked:
                    picked.append(c)
                    break
    return picked[:n]


def _rationale(c: Candidate) -> str:
    note = (c.notes or "").strip()
    if note:
        return note
    return _BAND_GLOSS[c.human_band]


def build_exemplar_block(exemplar_pool: list[Candidate], n: int = 6) -> str:
    """The text block prepended to the strict judge prompt."""
    picked = select_exemplars(exemplar_pool, n)
    lines = [
        "Worked examples — score new candidates on the same scale a careful "
        "human used here (object relation anchor @ activity — score — why):",
    ]
    for c in picked:
        score = _BAND_SCORE[c.human_band]
        lines.append(
            f"  {c.object_category} {c.target_relationship} {c.target_anchor} "
            f"@ {c.activity} — {score:.2f} — {_rationale(c)}"
        )
    return "\n".join(lines)
