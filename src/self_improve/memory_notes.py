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
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, NamedTuple, Optional, Sequence

from self_improve.frozen_household import period_of_day

PROVISIONAL = "provisional"
ESTABLISHED = "established"
STATUSES = (PROVISIONAL, ESTABLISHED)

# What may be recorded about a claim that has been argued against. None of these
# remove the claim or its wording.
class MemoryIsFull(Exception):
    """The working memory has no room. Handed back to the model, not swallowed."""


SET_ASIDE = "set aside for now"
STILL_STANDING = "still standing"
# A claim whose content was taken into another claim. It keeps its wording and its
# history and stops being shown, which is how two notes become one without a delete.
FOLDED_IN = "folded into another claim"

# The three ways of writing the notes. The third is the second plus two things: it is
# told, each night, which of its notes helped and which misled when the robot answered
# that day, and it may fold two notes into one or mark one a repeat of another. Both of
# those come from the method in arxiv 2510.04618 (Zhang et al., "Agentic Context
# Engineering"), whose Reflector reads task outcomes and whose Curator makes itemised
# edits with a step that stops the store growing without bound. The second arm has
# neither, which is why it is the third arm and not a reworded second one.
WHOLESALE_REWRITE = "wholesale rewrite"
INCREMENTAL_EDITS = "incremental edits"
TOLD_IF_IT_WAS_RIGHT = "claim store told if it was right"
# The fourth way, added 2026-09-25. The robot reads its own observation record when it is
# asked, so its notes are forbidden from saying where anything is and hold what a record
# cannot: when people are where, what moves with what, what changed, where to look first.
# The reason, measured: of 1,906 claims the other claim stores wrote, 91% named a place
# and 0.3% mentioned any time, condition or change - and answering straight from the
# record with no model beats all of them by about 25 points outside the disrupted window.
THE_LOG_AND_THE_ROUTINE = "the log and notes about the routine"
# The fifth way, added 2026-09-25: MemGPT (Packer et al.). A small working memory of fixed
# size that is always in front of the model, plus an unbounded archive that is only reached
# by searching it, and the model moves things between the two itself. It is the only
# published system in our survey that bounds WRITING, and it bounds it by refusing a write
# that would overflow rather than by a constant nobody chose.
A_WORKING_MEMORY_AND_AN_ARCHIVE = "a small working memory and an archive"
WAYS_OF_WRITING = (WHOLESALE_REWRITE, INCREMENTAL_EDITS, TOLD_IF_IT_WAS_RIGHT,
                   THE_LOG_AND_THE_ROUTINE, A_WORKING_MEMORY_AND_AN_ARCHIVE)

# How big the working memory is. Anchored on something real rather than chosen: the
# wholesale-rewrite arm's whole nightly summary averages about 1,500 characters on the
# cells measured on 2026-09-24, so a working memory of 1,200 is a little smaller than one
# of those summaries. That makes "what this model can keep in front of it" comparable to
# "what the summarising arm keeps", which is the comparison the number has to serve.
WORKING_MEMORY_CHARACTERS = 1200


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
    # Only the third way of writing notes fills these in. They stay at zero and empty
    # for the other two, so every line either of those arms writes is unchanged.
    # MemGPT only. Whether this note is in the small working memory that is always shown,
    # or in the archive that is only reached by searching. False for every other arm.
    in_working_memory: bool = False
    # When it crossed between the working memory and the archive, oldest first, as
    # {"day", "time", "into_working_memory"}. WITHOUT THIS A SNAPSHOT CANNOT BE REBUILT:
    # the flag was flipped with no day recorded, so a snapshot of an earlier day carried
    # whichever notes were in working memory at the END of the run. Found by the research
    # agent; the check that was meant to catch it could not, because rebuilding at the LAST
    # day is the one case where the end state and that day's state agree.
    moved_between_memory_and_archive: List[Dict[str, Any]] = field(default_factory=list)
    times_it_helped: int = 0
    times_it_misled: int = 0
    what_it_taught: List[Dict[str, Any]] = field(default_factory=list)
    folded_into: Optional[str] = None
    folded_in_from: List[str] = field(default_factory=list)

    def as_plain_words(self) -> str:
        """How an existing note is shown back to the model.

        ONE LINE PER THING, AND THE REASON MATTERS. This used to be one line with
        everything after "(holds under: " run together with semicolons, and the model
        copied that whole run-on string INTO the `holds_under` field of the notes it then
        wrote: real values from 2026-09-25 include
        "Day 1-2, 09:00-16:00; provisional; 12 sighting(s) for, 0 against; last revised on
        day 2". Across three arms that field has never once held a condition - 99% said
        "current" in the first two, MemGPT put observation ids in it, and this arm put the
        rendering back. Three different failures of one field is a fault in how it is
        presented, not three coincidences. Labelled lines cannot be imitated into a single
        field value.
        """
        support = len(self.supporting_observation_ids)
        against = len(self.contradicting_observation_ids)
        lines = [f"[{self.claim_id}] {self.statement}",
                 f"    when it is true: {self.holds_under or 'not said'}"]
        tail = [f"{support} sighting(s) support it", f"{against} argue against it",
                f"written or last changed on day {self.last_revised_day}", self.status]
        if self.standing != STILL_STANDING:
            tail.append(self.standing)
        if self.times_it_helped or self.times_it_misled:
            tail.append(f"it has helped {self.times_it_helped} time(s) and misled "
                        f"{self.times_it_misled}")
        lines.append("    " + " | ".join(tail))
        return "\n".join(lines)


class Notes:
    """The persistent notes file for one household under one arm."""

    def __init__(self, path: pathlib.Path, household: str, arm: str,
                 how_memory_is_written: str) -> None:
        if how_memory_is_written not in WAYS_OF_WRITING:
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

    def record_what_a_claim_did(self, claim_id: str, helped: bool, day: int,
                                question_about: str, what_it_taught: str = "") -> Claim:
        """The third format only: the robot answered a question with this claim in
        front of it and the answer was right, or it was wrong. Nothing about the
        claim's wording changes here - this is a tally beside it, so a later night
        can see which of its notes have been earning their line."""
        claim = self.claim(claim_id)
        if helped:
            claim.times_it_helped += 1
        else:
            claim.times_it_misled += 1
        claim.what_it_taught.append({"day": day, "about": question_about,
                                     "helped": helped,
                                     "what_it_taught": what_it_taught.strip()})
        return claim

    def fold_one_claim_into_another(self, keep_id: str, fold_in_id: str, day: int,
                                    time: int, new_statement: Optional[str] = None,
                                    why: str = "") -> Claim:
        """Two claims become one line without either wording being lost.

        The kept claim may be reworded (its old wording goes into its history, as
        with any revision) and inherits the other's evidence. The folded claim keeps
        its statement, its history and its evidence, gets a standing that says where
        it went, and stops being shown at answer time. Nothing is deleted, so the
        question "was the ordinary routine still written down" can still be asked of
        this arm - which is the reason the study never deletes a claim."""
        if keep_id == fold_in_id:
            raise ValueError(f"{self.household}: cannot fold {keep_id} into itself")
        keep, folded = self.claim(keep_id), self.claim(fold_in_id)
        if folded.folded_into is not None:
            raise ValueError(f"{self.household}: {fold_in_id} was already folded "
                             f"into {folded.folded_into}")
        for ids, target in ((folded.supporting_observation_ids,
                             keep.supporting_observation_ids),
                            (folded.contradicting_observation_ids,
                             keep.contradicting_observation_ids)):
            for observation_id in ids:
                if observation_id not in target:
                    target.append(observation_id)
        keep.times_it_helped += folded.times_it_helped
        keep.times_it_misled += folded.times_it_misled
        if new_statement:
            self.revise_claim(keep_id, day, time, new_statement=new_statement,
                              why=why or f"folded in {fold_in_id}")
        keep.folded_in_from.append(fold_in_id)
        self.revise_claim(fold_in_id, day, time, new_standing=FOLDED_IN,
                          why=why or f"folded into {keep_id}")
        folded.folded_into = keep_id
        keep.last_revised_day, keep.last_revised_time = day, time
        return keep

    # ------------------------------------- a working memory and an archive (MemGPT) --

    def working_memory(self) -> List[Claim]:
        """What is always in front of the model, oldest first so it reads as a document."""
        return [c for c in self.claims
                if c.in_working_memory and c.folded_into is None]

    def characters_in_working_memory(self) -> int:
        return sum(len(c.statement) + 1 for c in self.working_memory())

    def put_in_working_memory(self, claim_id: str, day: int = 0,
                              time: int = 0) -> Claim:
        """Move a note into the working memory, or refuse because it is full.

        Refusing is the mechanism, not an error to be avoided: MemGPT's working context is
        a fixed size and a write that would overflow it fails, which is what forces the
        model to decide what to evict. The caller hands the refusal back to the model.
        """
        claim = self.claim(claim_id)
        if claim.in_working_memory:
            return claim
        room_left = WORKING_MEMORY_CHARACTERS - self.characters_in_working_memory()
        if len(claim.statement) + 1 > room_left:
            raise MemoryIsFull(
                f"your working memory holds {self.characters_in_working_memory()} of "
                f"{WORKING_MEMORY_CHARACTERS} characters, so there is no room for this "
                f"note ({len(claim.statement)} characters). Move something out first.")
        claim.in_working_memory = True
        claim.moved_between_memory_and_archive.append(
            {"day": day, "time": time, "into_working_memory": True})
        return claim

    def take_out_of_working_memory(self, claim_id: str, day: int = 0,
                                   time: int = 0) -> Claim:
        """Move a note to the archive. It is not deleted and can be searched for."""
        claim = self.claim(claim_id)
        claim.in_working_memory = False
        claim.moved_between_memory_and_archive.append(
            {"day": day, "time": time, "into_working_memory": False})
        return claim

    def was_it_in_working_memory_on(self, claim: Claim, day: int) -> bool:
        """Which side of the working memory a note was on at the end of that day.

        The state after the last crossing on or before that day, and False if it had not
        crossed by then. This is what a rebuilt snapshot must use instead of the flag, which
        only ever describes the end of the run.
        """
        crossings = [m for m in claim.moved_between_memory_and_archive
                     if m["day"] <= day]
        if not crossings:
            return False
        newest = sorted(crossings, key=lambda m: (m["day"], m["time"]))[-1]
        return bool(newest["into_working_memory"])

    def search_the_archive(self, words: str, how_many: int = 10) -> List[Claim]:
        """The archive, searched. Word overlap, because there are no vectors here.

        Only notes NOT in the working memory are searched: the working memory is already
        in front of the model and returning it again would spend the search on what it can
        already see.
        """
        wanted = {w for w in (words or "").lower().replace("_", " ").split()
                  if len(w) > 2}
        scored = []
        for claim in self.claims:
            if claim.in_working_memory or claim.folded_into is not None:
                continue
            text = claim.statement.lower().replace("_", " ")
            hits = sum(1 for w in wanted if w in text)
            if hits:
                scored.append((hits, -claim.last_revised_day, claim))
        scored.sort(key=lambda row: (-row[0], row[1]))
        return [claim for _, _, claim in scored[:how_many]]

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

    def what_the_robot_can_read(self, read_budget_lines: Optional[int],
                                about_object: Optional[str] = None) -> "WhatWasRead":
        """The notes as they go into a prompt, through a window both formats share.

        The budget is the same number of lines for every arm, and it is set below
        one line per object for all but the smallest household. That single
        constraint is what makes the two formats architecturally different rather
        than differently prompted:

          the wholesale rewrite is ONE artifact, so to fit it must decide what to
          lose. It is told the limit when it writes, and truncated here if it
          overran anyway.

          the claim store keeps everything and decides what to SHOW, so it can put
          the claims about the object being asked about first and spend the rest of
          the budget on whatever else is most recent.

        Neither is given more lines than the other.

        `read_budget_lines=None` means NO LIMIT: every line the notes hold goes into
        the prompt. Added 2026-09-24 as a correction, not as an extra condition. Eight
        lines is fewer than the number of objects the robot is asked about in nine of
        the ten homes, it is a limit we imposed and cannot justify, and it shapes every
        number measured under it - so it is a confound on the question the study asks
        rather than a property of the memory. An int is still accepted and still
        behaves exactly as before, so no earlier number moves.

        NOTE FOR ANYONE READING A NO-LIMIT RESULT: removing the cap at READ time alone
        tests very little for the wholesale arm, because that arm's WRITING prompt also
        states the budget ("your notes must fit in N lines") - so its notes were
        composed under the constraint whatever the reader then does.
        `write_the_notes.rewrite_the_notes_wholesale` takes
        `say_the_notes_must_fit_a_budget=False` to remove that sentence too, and the two
        must be switched together or the result is uninterpretable. The claim-store
        writing prompt never mentioned a budget, so for that format the read-time
        change is the whole change.
        """
        no_limit = read_budget_lines is None
        if self.how_memory_is_written == "wholesale rewrite":
            available = summary_lines(self.newest_summary() or "")
            shown = available if no_limit else available[:read_budget_lines]
            return WhatWasRead(
                text="\n".join(shown) if shown else "(no notes yet)",
                n_lines_available=len(available), n_lines_shown=len(shown),
                budget_bit=(False if no_limit else len(available) > read_budget_lines),
                how_chosen=("the whole summary it keeps, with no length limit" if no_limit
                            else "the first lines of the one summary it keeps"))

        if self.how_memory_is_written == A_WORKING_MEMORY_AND_AN_ARCHIVE:
            # This arm does NOT get to read everything it holds. Its working memory is
            # always shown and its archive is only reached by searching, which is the whole
            # design: if the answer step read the archive for free, the working memory
            # would cost nothing to overflow and there would be no reason to manage it.
            working = self.working_memory()
            found = self.search_the_archive(about_object or "")
            shown = working + found
            if not shown:
                return WhatWasRead("(no notes yet)", 0, 0, False, "nothing written yet")
            text = "\n".join(
                ["Your working memory:"]
                + ([c.as_plain_words() for c in working] or ["(nothing in it)"])
                + ["", "Found in your archive by searching for what you were asked about:"]
                + ([c.as_plain_words() for c in found] or ["(the search found nothing)"]))
            return WhatWasRead(
                text=text,
                claim_ids_shown=tuple(c.claim_id for c in shown),
                n_lines_available=len([c for c in self.claims
                                       if c.folded_into is None]),
                n_lines_shown=len(shown), budget_bit=False,
                how_chosen="its working memory, plus its archive searched for the object "
                           "it was asked about")

        if not self.claims:
            return WhatWasRead("(no notes yet)", 0, 0, False, "nothing written yet")
        ordered = self.claims_in_reading_order(about_object)
        shown = ordered if no_limit else ordered[:read_budget_lines]
        return WhatWasRead(
            text="\n".join(c.as_plain_words() for c in shown),
            claim_ids_shown=tuple(c.claim_id for c in shown),
            n_lines_available=len(ordered), n_lines_shown=len(shown),
            budget_bit=(False if no_limit else len(ordered) > read_budget_lines),
            how_chosen=("every claim it holds, in reading order, with no length limit"
                        if no_limit else
                        "claims about the object asked about first, then the most "
                        "recently revised"))

    def claims_in_reading_order(self, about_object: Optional[str] = None) -> List[Claim]:
        """What the claim store chooses to show, best first.

        A claim that has been folded into another one is not shown: its content is
        in the claim that absorbed it, and showing both would spend two lines on one
        fact. It is still in the file.

        The third format orders by what a claim has done - times it helped minus
        times it misled - before recency, because that tally is the only thing it
        has that the second format does not. The other two formats are ordered
        exactly as before, so no number measured under them moves.
        """
        by_results = self.how_memory_is_written == TOLD_IF_IT_WAS_RIGHT
        def sort_key(claim: Claim):
            about_this_one = 0
            if about_object and about_object.lower() in claim.statement.lower():
                about_this_one = -1
            earned = (claim.times_it_misled - claim.times_it_helped) if by_results else 0
            return (about_this_one, earned, -claim.last_revised_day,
                    0 if claim.status == ESTABLISHED else 1, claim.claim_id)
        return sorted([c for c in self.claims if c.folded_into is None], key=sort_key)


class WhatWasRead(NamedTuple):
    """What actually went into a prompt, so the budget can be audited."""
    text: str
    n_lines_available: int
    n_lines_shown: int
    budget_bit: bool
    how_chosen: str
    # Which claims those lines were, when the notes are a claim store. Empty for the
    # wholesale arm, which has no ids. The third format needs this: it can only ask
    # "did this note help" about the notes that were actually in front of the robot.
    claim_ids_shown: tuple = ()


def summary_lines(summary: str) -> List[str]:
    """A summary split into the same unit a claim is measured in: one fact a line.

    The model writes either one fact per line or one fact per sentence, so we
    split on both and drop the blanks. Counting in a shared unit is what lets one
    budget bind on a free-text summary and on a list of claims alike.
    """
    out: List[str] = []
    for line in (summary or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) < 200:
            out.append(line)
            continue
        out.extend(part.strip() for part in re.split(r"(?<=[.;])\s+", line)
                   if part.strip())
    return out


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
