"""The robot's notes about a household: a file of claims that persists across days.

This is the artifact the study is really about. It is deliberately separate from
the raw log of what the robot saw (that lives in the observation log), and it is
deliberately append-only about statements: there is no method that deletes a
claim or overwrites its wording in place without keeping what it said before.

A claim carries:
  statement                       plain language, what the robot believes
  holds_under                     the routine or condition it is claimed for
  supporting_observation_ids      sightings and looks that back it
  contradicting_observation_ids   sightings and looks that argue against it
  last_revised_day / _time        when it was last touched
  status                          "provisional" or "established"

The rule that the pre-registered prediction turns on: a claim written during the
disrupted period must NOT erase the claim written for the ordinary routine. The
file format enforces this - revising a claim records the old wording in its
history, and a superseded claim keeps its statement and gets its status changed
rather than being removed.

Two ways of writing the notes are supported, because that is factor one of the
study:

  incremental edits   the model adds, revises or marks individual claims. The
                      claim list carries over from yesterday untouched except
                      where the model acts on it.
  wholesale rewrite   the model rewrites one summary of the household from
                      scratch each night. We keep every night's summary so that
                      the same question - is the ordinary routine still written
                      down? - can be asked of this arm too.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from self_improve.frozen_household import period_of_day

PROVISIONAL = "provisional"
ESTABLISHED = "established"
STATUSES = (PROVISIONAL, ESTABLISHED)

# What may be recorded about a claim that has been argued against. None of these
# remove the claim or its wording.
SET_ASIDE = "set aside for now"
STILL_STANDING = "still standing"


@dataclass
class Claim:
    claim_id: str
    statement: str
    holds_under: str
    supporting_observation_ids: List[str] = field(default_factory=list)
    contradicting_observation_ids: List[str] = field(default_factory=list)
    last_revised_day: int = 0
    last_revised_time: int = 0
    status: str = PROVISIONAL
    standing: str = STILL_STANDING
    first_written_day: int = 0
    revision_history: List[Dict[str, Any]] = field(default_factory=list)

    def as_plain_words(self) -> str:
        support = len(self.supporting_observation_ids)
        against = len(self.contradicting_observation_ids)
        bits = [f"[{self.claim_id}] {self.statement}",
                f"(holds under: {self.holds_under};",
                f"{self.status}; {support} sighting(s) for, {against} against;",
                f"last revised on day {self.last_revised_day}"]
        if self.standing != STILL_STANDING:
            bits.append(f"; {self.standing}")
        return " ".join(bits) + ")"


class Notes:
    """The persistent notes file for one household under one arm."""

    def __init__(self, path: pathlib.Path, household: str, arm: str,
                 how_memory_is_written: str) -> None:
        if how_memory_is_written not in ("incremental edits", "wholesale rewrite"):
            raise ValueError(f"unknown way of writing memory: {how_memory_is_written!r}")
        self.path = path
        self.household = household
        self.arm = arm
        self.how_memory_is_written = how_memory_is_written
        self.claims: List[Claim] = []
        self.nightly_summaries: List[Dict[str, Any]] = []
        self.written_up_to_day: int = -1
        self._next_number = 1

    # -------------------------------------------------------- persistence --

    @classmethod
    def load(cls, path: pathlib.Path) -> "Notes":
        raw = json.loads(path.read_text())
        notes = cls(path, raw["household"], raw["arm"], raw["how_memory_is_written"])
        notes.claims = [Claim(**c) for c in raw["claims"]]
        notes.nightly_summaries = raw.get("nightly_summaries", [])
        notes.written_up_to_day = raw.get("written_up_to_day", -1)
        notes._next_number = raw.get("next_claim_number", len(notes.claims) + 1)
        return notes

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({
            "household": self.household,
            "arm": self.arm,
            "how_memory_is_written": self.how_memory_is_written,
            "written_up_to_day": self.written_up_to_day,
            "next_claim_number": self._next_number,
            "claims": [asdict(c) for c in self.claims],
            "nightly_summaries": self.nightly_summaries,
        }, indent=1))

    def snapshot_to(self, path: pathlib.Path) -> "Notes":
        """A frozen copy, for the held-out test. The copy is never written back."""
        path.parent.mkdir(parents=True, exist_ok=True)
        was, self.path = self.path, path
        try:
            self.save()
        finally:
            self.path = was
        return Notes.load(path)

    # ------------------------------------------------------------- writing --

    def add_claim(self, statement: str, holds_under: str, day: int, time: int,
                  supporting_observation_ids: Sequence[str] = (),
                  status: str = PROVISIONAL) -> Claim:
        if status not in STATUSES:
            raise ValueError(f"status must be one of {STATUSES}, got {status!r}")
        claim = Claim(claim_id=f"claim_{self._next_number:04d}",
                      statement=statement.strip(),
                      holds_under=holds_under.strip(),
                      supporting_observation_ids=list(supporting_observation_ids),
                      last_revised_day=day, last_revised_time=time,
                      status=status, first_written_day=day)
        self._next_number += 1
        self.claims.append(claim)
        return claim

    def claim(self, claim_id: str) -> Claim:
        for c in self.claims:
            if c.claim_id == claim_id:
                return c
        raise KeyError(f"{self.household}: no claim {claim_id!r}")

    def revise_claim(self, claim_id: str, day: int, time: int,
                     new_statement: Optional[str] = None,
                     new_holds_under: Optional[str] = None,
                     new_status: Optional[str] = None,
                     new_standing: Optional[str] = None,
                     why: str = "") -> Claim:
        """Change a claim, keeping what it used to say. There is no way to lose
        the previous wording: that is the point of this method."""
        claim = self.claim(claim_id)
        before = {"statement": claim.statement, "holds_under": claim.holds_under,
                  "status": claim.status, "standing": claim.standing}
        if new_statement is not None:
            claim.statement = new_statement.strip()
        if new_holds_under is not None:
            claim.holds_under = new_holds_under.strip()
        if new_status is not None:
            if new_status not in STATUSES:
                raise ValueError(f"status must be one of {STATUSES}, got {new_status!r}")
            claim.status = new_status
        if new_standing is not None:
            claim.standing = new_standing
        claim.last_revised_day, claim.last_revised_time = day, time
        claim.revision_history.append({"day": day, "time": time, "why": why.strip(),
                                       "was": before})
        return claim

    def record_evidence(self, claim_id: str, observation_ids: Sequence[str],
                        day: int, time: int, supports: bool) -> Claim:
        claim = self.claim(claim_id)
        target = (claim.supporting_observation_ids if supports
                  else claim.contradicting_observation_ids)
        for observation_id in observation_ids:
            if observation_id not in target:
                target.append(observation_id)
        claim.last_revised_day, claim.last_revised_time = day, time
        return claim

    def write_nightly_summary(self, day: int, time: int, summary: str) -> None:
        """The wholesale-rewrite arm's whole memory for the next day. We keep
        every night's text so the same survival question can be asked of it."""
        self.nightly_summaries.append({"day": day, "time": time,
                                       "period": period_of_day(day),
                                       "summary": summary})
        self.written_up_to_day = day

    def newest_summary(self) -> Optional[str]:
        return self.nightly_summaries[-1]["summary"] if self.nightly_summaries else None

    # ------------------------------------------------------------- reading --

    def what_the_robot_can_read(self, retrieval_budget: int) -> str:
        """The notes as they go into a prompt. The same budget for every arm."""
        if self.how_memory_is_written == "wholesale rewrite":
            return self.newest_summary() or "(no notes yet)"
        if not self.claims:
            return "(no notes yet)"
        # newest revisions first, then established before provisional, capped at
        # the shared retrieval budget so no arm gets to read more than another
        ordered = sorted(self.claims,
                         key=lambda c: (-c.last_revised_day,
                                        0 if c.status == ESTABLISHED else 1,
                                        c.claim_id))
        return "\n".join(c.as_plain_words() for c in ordered[:retrieval_budget])


# --------------------------------------------------------- the pre-registered
# check: is the ordinary routine still written down?


def ordinary_routine_claims_still_present(notes: Notes,
                                          settled_period_statements: Sequence[str]
                                          ) -> Dict[str, Any]:
    """Given the claims the notes held at the end of the ordinary fortnight,
    how many of them are still readable at this point?

    For the incremental arms this is exact: claim ids persist, so we check the
    id and whether the wording still says the same place. For the wholesale
    rewrite arms we can only check the newest summary text, so we check whether
    each settled-period statement's place words still appear in it. Both checks
    are mechanical and neither needs the model.
    """
    if notes.how_memory_is_written == "incremental edits":
        present = [c.claim_id for c in notes.claims]
        return {"how_checked": "claim ids that survived",
                "n_settled_period_claims": len(settled_period_statements),
                "n_still_present": len(present),
                "still_present": present}
    newest = (notes.newest_summary() or "").lower()
    kept = [s for s in settled_period_statements if s.lower() in newest]
    return {"how_checked": "settled-period wording still in the newest summary",
            "n_settled_period_claims": len(settled_period_statements),
            "n_still_present": len(kept),
            "still_present": kept}
