"""
Human-labeled judge candidate set: load, validate, and split.

The labeled CSV is the Phase-1a deliverable returned by the human — one row
per candidate with a corrected `band` (0-3) plus full context. This module
loads it into typed records, splits it deterministically into EVAL and
EXEMPLAR subsets (EXEMPLAR is reserved for Phase-2 few-shot and is
permanently excluded from every metric), and persists the split so every
harness run scores the exact same EVAL set.
"""
from __future__ import annotations

import csv
import dataclasses
import json
import pathlib
import random
from typing import Optional


@dataclasses.dataclass(frozen=True)
class Candidate:
    candidate_id: str
    scene: str
    occupant: str
    activity: str
    start: float
    end: float
    object_category: str
    target_relationship: str
    target_anchor: str
    room: str
    reason: str
    assumed_from: str
    judge_score: float          # the strict-judge score at label-set build time
    machine_band: int           # band mapped from that score (machine suggestion)
    flag: str
    human_band: int             # the corrected `band` column — ground truth
    notes: str

    @property
    def is_dinner_laptop(self) -> bool:
        """A candidate on the electronics-at-the-eating-surface archetype the
        exemplar set must include."""
        return self.flag.startswith("obvious-negative: electronics")


def _parse_time_window(tw: str) -> tuple[float, float]:
    # "8.5-9.0h" -> (8.5, 9.0)
    core = tw.strip().rstrip("h")
    a, b = core.split("-")
    return float(a), float(b)


def load_labeled_csv(path: pathlib.Path) -> list[Candidate]:
    rows = list(csv.DictReader(path.open()))
    out: list[Candidate] = []
    errors: list[str] = []
    for r in rows:
        band_raw = (r.get("band") or "").strip()
        if band_raw not in {"0", "1", "2", "3"}:
            errors.append(f"{r.get('candidate_id')}: band={band_raw!r} not in 0-3")
            continue
        start, end = _parse_time_window(r["time_window"])
        out.append(Candidate(
            candidate_id=r["candidate_id"],
            scene=r["scene"],
            occupant=r["occupant"],
            activity=r["activity"],
            start=start,
            end=end,
            object_category=r["object_category"],
            target_relationship=r["target_relationship"],
            target_anchor=r["target_anchor"],
            room=r["room"],
            reason=r["reason"],
            assumed_from=r.get("assumed_from", ""),
            judge_score=float(r["judge_score"]),
            machine_band=int(r["machine_band"]),
            flag=r.get("flag", ""),
            human_band=int(band_raw),
            notes=r.get("notes", ""),
        ))
    if errors:
        raise ValueError("labeled CSV has unlabeled/invalid bands:\n  " + "\n  ".join(errors))
    return out


def split_eval_exemplar(
    cands: list[Candidate], seed: int, n_exemplar: int = 12,
) -> tuple[list[Candidate], list[Candidate]]:
    """Stratified split by human band. EXEMPLAR gets ~n_exemplar candidates
    spread across bands (so few-shot can show every band) and is guaranteed
    to contain at least one dinner-laptop case (Phase 2.2 requires it). The
    rest are EVAL. Deterministic in `seed`."""
    rng = random.Random(seed)
    by_band: dict[int, list[Candidate]] = {0: [], 1: [], 2: [], 3: []}
    for c in cands:
        by_band[c.human_band].append(c)
    for b in by_band:
        by_band[b].sort(key=lambda c: c.candidate_id)  # stable pre-shuffle order
        rng.shuffle(by_band[b])

    per_band = max(1, n_exemplar // 4)
    exemplar: list[Candidate] = []
    for b in (0, 1, 2, 3):
        exemplar.extend(by_band[b][:per_band])

    # Guarantee a dinner-laptop exemplar (prefer a low human band — a clear
    # negative teaches the judge the case it currently gets wrong).
    if not any(c.is_dinner_laptop for c in exemplar):
        dl = sorted(
            (c for c in cands if c.is_dinner_laptop),
            key=lambda c: (c.human_band, c.candidate_id),
        )
        if dl:
            pick = dl[0]
            # swap in for an existing exemplar of the same band (else append)
            same_band = [c for c in exemplar if c.human_band == pick.human_band]
            if same_band:
                exemplar[exemplar.index(same_band[-1])] = pick
            else:
                exemplar.append(pick)

    exemplar_ids = {c.candidate_id for c in exemplar}
    eval_set = [c for c in cands if c.candidate_id not in exemplar_ids]
    return eval_set, exemplar


def write_split(
    eval_set: list[Candidate], exemplar: list[Candidate], seed: int,
    out_dir: pathlib.Path, source_csv: pathlib.Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "seed": seed,
        "source_csv": str(source_csv),
        "eval_ids": sorted(c.candidate_id for c in eval_set),
        "exemplar_ids": sorted(c.candidate_id for c in exemplar),
        "n_eval": len(eval_set),
        "n_exemplar": len(exemplar),
    }
    (out_dir / "split_manifest.json").write_text(json.dumps(manifest, indent=2))


def load_split(
    labeled_csv: pathlib.Path, manifest_path: pathlib.Path,
) -> tuple[list[Candidate], list[Candidate]]:
    """Reload the exact EVAL / EXEMPLAR sets recorded in the manifest."""
    manifest = json.loads(manifest_path.read_text())
    by_id = {c.candidate_id: c for c in load_labeled_csv(labeled_csv)}
    eval_set = [by_id[i] for i in manifest["eval_ids"] if i in by_id]
    exemplar = [by_id[i] for i in manifest["exemplar_ids"] if i in by_id]
    return eval_set, exemplar
