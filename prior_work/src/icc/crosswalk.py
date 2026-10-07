"""The activity crosswalk: CASAS labels <-> ATUS codes <-> canonical ids.

This is the highest-risk artefact in the pipeline — if a reviewer distrusts
one number here, it is this one — so it lives as a versioned CSV with a
rationale per row (``crosswalk.csv``) rather than as a dict buried in a
loader. Every mapping decision, every deliberate exclusion, and every
known ambiguity is a readable row.

Columns:
  version         crosswalk version; bumped on any semantic change
  activity        canonical activity id used everywhere downstream
  measure         episode = start + summed duration + count;
                  event   = an instant derived from the episodes (a wake
                  time, a departure), carrying no duration. The distinction
                  matters for validation: two activities may read the same
                  raw episodes only if at most one of them counts their
                  MINUTES, otherwise the same minutes enter two variances
                  and they are not independent.
  casas_labels    pipe-separated raw CASAS labels (union over testbeds)
  atus_codes      pipe-separated ATUS code PREFIXES (2/4/6 digit)
  atus_home_only  1 = restrict the ATUS side to at-home records
  start_rule      first | last | none  (see schema.StartRule)
  merge_gap_min   join episodes separated by <= this many minutes before any
                  statistic is taken (0 = leave alone). Corrects sensor-vs-
                  self-report granularity; see schema.merge_episodes.
  status          include | exclude
  confidence      high | medium | low  — of the mapping, not of the estimate
  rationale       why this mapping, and what is known to be wrong with it
"""

from __future__ import annotations

import csv
import dataclasses
import hashlib
import pathlib
from typing import Dict, List, Tuple

from icc.schema import StartRule

CROSSWALK_PATH = pathlib.Path(__file__).with_name("crosswalk.csv")


@dataclasses.dataclass(frozen=True)
class Mapping:
    """One canonical activity and how each source expresses it."""

    version: int
    activity: str
    measure: str                   # "episode" | "event"
    casas_labels: Tuple[str, ...]
    atus_codes: Tuple[str, ...]
    atus_home_only: bool
    start_rule: StartRule
    merge_gap_min: float
    status: str
    confidence: str
    rationale: str

    @property
    def included(self) -> bool:
        return self.status == "include"

    @property
    def is_event(self) -> bool:
        return self.measure == "event"


def load(path: pathlib.Path = CROSSWALK_PATH) -> List[Mapping]:
    """Parse and validate the crosswalk; raises on any malformed row."""
    rows: List[Mapping] = []
    with open(path, newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            if r["status"] not in ("include", "exclude"):
                raise ValueError(f"{path}:{i}: bad status {r['status']!r}")
            if r["confidence"] not in ("high", "medium", "low"):
                raise ValueError(f"{path}:{i}: bad confidence")
            if r["measure"] not in ("episode", "event"):
                raise ValueError(f"{path}:{i}: bad measure {r['measure']!r}")
            if not r["rationale"].strip():
                raise ValueError(
                    f"{path}:{i}: every mapping needs a rationale — this file "
                    f"is the artefact reviewers audit")
            rows.append(Mapping(
                version=int(r["version"]), activity=r["activity"],
                measure=r["measure"],
                casas_labels=tuple(x for x in r["casas_labels"].split("|") if x),
                atus_codes=tuple(x for x in r["atus_codes"].split("|") if x),
                atus_home_only=r["atus_home_only"] == "1",
                start_rule=StartRule(r["start_rule"]),
                merge_gap_min=float(r["merge_gap_min"]),
                status=r["status"], confidence=r["confidence"],
                rationale=r["rationale"]))
    activities = [m.activity for m in rows]
    if len(set(activities)) != len(activities):
        raise ValueError(f"{path}: duplicate canonical activity ids")
    versions = {m.version for m in rows}
    if len(versions) != 1:
        raise ValueError(f"{path}: mixed versions {sorted(versions)} — bump "
                         f"every row together")
    # A CASAS label may feed at most ONE duration-bearing (episode) mapping:
    # otherwise the same minutes enter two variance estimates. Event
    # mappings may share episodes freely — they read an instant, not
    # minutes (e.g. `wake` and `sleep` both read the sleep episodes).
    seen: Dict[str, str] = {}
    for m in rows:
        if m.is_event:
            continue
        for lab in m.casas_labels:
            if lab in seen:
                raise ValueError(
                    f"{path}: CASAS label {lab!r} feeds two duration-bearing "
                    f"activities, {seen[lab]!r} and {m.activity!r} — the same "
                    f"minutes would enter two variances")
            seen[lab] = m.activity
    return rows


def version(path: pathlib.Path = CROSSWALK_PATH) -> int:
    return load(path)[0].version


def content_hash(path: pathlib.Path = CROSSWALK_PATH) -> str:
    """Hash of the crosswalk bytes — pinned in every output's provenance."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def included(path: pathlib.Path = CROSSWALK_PATH) -> List[Mapping]:
    return [m for m in load(path) if m.included]


def casas_index(path: pathlib.Path = CROSSWALK_PATH) -> Dict[str, str]:
    """raw CASAS label -> canonical activity (included mappings only)."""
    return {lab: m.activity for m in included(path) for lab in m.casas_labels}
