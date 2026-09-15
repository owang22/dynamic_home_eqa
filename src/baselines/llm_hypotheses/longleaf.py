"""treeLongLeaf: a LIBRARY of long, self-contained hypotheses.

Where the flat / graph / tree arms hold a handful of "rest + moves"
programs, this arm holds many markdown documents, each a full weekly
model of the home (:mod:`baselines.beliefs.timetable_hypothesis`), kept
as files a person or a model can read, and weighted by the same
sighting-likelihood mixture. A revision adds documents; nothing is
edited or deleted. A document whose weight sits under the floor for
days is RETIRED — dropped from the particle set but kept in the library
with its last weight — and a later revision may revive it by id.

Document format (one ``.md`` per hypothesis)::

    # p_3f1a — <one-line title: what this hypothesis says>

    <prose: who lives here and how the week runs; what this hypothesis
    predicts that the others do not; what would refute it>

    ```json
    {"distinguishing_check": {"target": ..., "at": ..., "days": ...,
                              "hour": ..., "if_seen": ...},
     "targets": {"<object id or class:name>": [<blocks in priority order>]}}
    ```

The prose is the model's; the fenced JSON is what the converter runs.
:func:`parse_documents` splits a response on :data:`DELIMITER`, checks
each document in the caller's vocabulary and returns raw dicts
(``hypothesis_id``, ``title``, ``prose``, ``markdown``, ``targets``,
``distinguishing_check``) that :class:`~baselines.beliefs.
timetable_hypothesis.TimetableBelief` accepts as ``hypothesis_raw``.
"""

from __future__ import annotations

import copy
import json
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.beliefs.hypothesis_program import HypothesisValidationError
from baselines.beliefs.timetable_hypothesis import parse_timetable
from baselines.llm_hypotheses.assumption_graph import LEAF_ID_RE, new_leaf_id
from baselines.llm_hypotheses.prompt import (anonymize_hypothesis,
                                             deanonymize_hypothesis)

DELIMITER = "=== HYPOTHESIS ==="
"""Line that separates documents in one model reply."""
MIN_ELICITED = 8
TARGET_ELICITED = (12, 20)
"""What the installation prompt asks for."""
REVISION_TARGET = (3, 8)
MAX_LIBRARY = 40
"""Hard cap on live + retired documents (a revision beyond it is
rejected whole)."""
AWAY_TOKENS = ("OUT_OF_HOUSE", "ON_PERSON")
_HEADING = re.compile(r"^#\s*(p_[0-9a-f]{4})?\s*[—–-]?\s*(.*)$", re.M)
_FORK = re.compile(r"\(\s*fork(?:ed)?\s+of\s+(p_[0-9a-f]{4})\s*\)", re.I)
_FENCE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.S)
_REVIVE = re.compile(r"^\s*REVIVE:?\s+(p_[0-9a-f]{4})", re.M)
_READ = re.compile(r"^\s*READ:?\s+((?:p_[0-9a-f]{4}[\s,]*)+)", re.M)
MAX_FETCH = 6
"""Documents a revision may ask to read in full before writing."""
CLAIM_TRIGGER_WEIGHT = 0.1
"""A live document at or above this weight whose claims have gone net
against it since the last call fires a revision."""
CLAIM_TRIGGER_AGAINST = 2


def split_documents(text: str) -> List[str]:
    parts = [p.strip() for p in text.split(DELIMITER)]
    return [p for p in parts if p and "```" in p]


def parse_document(text: str, object_classes: Mapping[str, str],
                   receptacle_ids: Sequence[str],
                   taken: Sequence[str] = (),
                   unsensable: Sequence[str] = (),
                   parents: Optional[Mapping[str, Mapping[str, Any]]] = None
                   ) -> Dict[str, Any]:
    """One markdown document -> raw dict. Raises
    :class:`HypothesisValidationError` with the offending strings.
    A fork (``(fork of p_xxxx)`` in the heading) with ``parents`` given
    inherits every target and claim of its parent it does not restate:
    "copy it whole and change what the evidence points at" then works
    whether the model reprints the whole json block or only the changed
    entries; the stored markdown gets the merged block so the file is
    complete on its own."""
    heading = _HEADING.search(text)
    if heading is None:
        raise HypothesisValidationError(
            "document must start with a `# p_xxxx — title` heading", ["#"])
    given = heading.group(1) or ""
    title = heading.group(2).strip()
    fork = _FORK.search(title)
    forked_from = fork.group(1) if fork else None
    if fork:
        title = (title[:fork.start()] + title[fork.end():]).strip()
    fence = _FENCE.search(text)
    if fence is None:
        raise HypothesisValidationError(
            "document must end with one ```json block", ["```json"])
    try:
        payload = json.loads(fence.group(1))
    except json.JSONDecodeError as err:
        raise HypothesisValidationError(f"json block: {err.msg}",
                                        [fence.group(1)[:60]])
    if not isinstance(payload, Mapping):
        raise HypothesisValidationError("json block must be an object", ["{"])
    prose = text[heading.end():fence.start()].strip()
    hypothesis_id = (given if LEAF_ID_RE.match(given) and given not in taken
                     else new_leaf_id(taken, f"{given}|{title}|{len(taken)}"))
    targets = copy.deepcopy(dict(payload.get("targets") or {}))
    claims = copy.deepcopy(list(payload.get("claims") or []))
    inherited = False
    parent = (parents or {}).get(forked_from) if forked_from else None
    if parent is not None:
        merged = copy.deepcopy(dict(parent.get("targets") or {}))
        merged.update(targets)
        inherited = len(merged) > len(targets)
        targets = merged
        if not claims:
            claims = copy.deepcopy(list(parent.get("claims") or []))
    raw = {"hypothesis_id": hypothesis_id, "title": title, "prose": prose,
           "forked_from": forked_from, "targets": targets, "claims": claims,
           "distinguishing_check": copy.deepcopy(
               payload.get("distinguishing_check"))}
    for c in raw["claims"]:
        c.pop("chance", None)               # a stray field, seen in replies
    if not raw["claims"]:
        raise HypothesisValidationError(
            "document needs a non-empty `claims` list (what it predicts "
            "that a look can settle)", ["claims"])
    _normalize_chances(raw["targets"])
    parse_timetable(raw, object_classes, receptacle_ids, unsensable=unsensable)
    body = text[heading.end():fence.start()].lstrip("\n").rstrip()
    lineage = f" (fork of {forked_from})" if forked_from else ""
    block = json.dumps({"claims": raw["claims"], "targets": raw["targets"]},
                       indent=1)
    note = (f"\n\n_(targets the fork left unstated are inherited from "
            f"{forked_from})_" if inherited else "")
    raw["markdown"] = (f"# {hypothesis_id} — {title}{lineage}\n\n{body}{note}"
                       f"\n\n```json\n{block}\n```\n")
    return raw


CHANCE_ALIASES = {"always": "almost_always", "almost always": "almost_always",
                  "often": "usually", "mostly": "usually", "frequently": "usually",
                  "occasionally": "sometimes", "seldom": "rarely",
                  "never": "rarely", "rare": "rarely"}
"""Chance words the model reaches for, mapped onto the four labels the
converter knows. Deterministic and logged in the stored block (which
carries the mapped label), never a guess about ids."""


def _normalize_chances(targets: Mapping[str, Any]) -> None:
    for blocks in targets.values():
        if not isinstance(blocks, list):
            continue
        for b in blocks:
            if isinstance(b, Mapping) and "chance" in b:
                c = str(b["chance"]).strip().lower().replace("-", "_")
                b["chance"] = CHANCE_ALIASES.get(c, CHANCE_ALIASES.get(
                    c.replace("_", " "), c))


def parse_documents(text: str, object_classes: Mapping[str, str],
                    receptacle_ids: Sequence[str],
                    taken: Sequence[str] = (),
                    unsensable: Sequence[str] = (),
                    parents: Optional[Mapping[str, Mapping[str, Any]]] = None
                    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Every document in a reply: ``(valid raws, dropped rows)``.
    ``parents`` (id -> raw) lets forks inherit."""
    valid: List[Dict[str, Any]] = []
    dropped: List[Dict[str, Any]] = []
    ids = list(taken)
    pool = dict(parents or {})
    for index, doc in enumerate(split_documents(text)):
        try:
            raw = parse_document(doc, object_classes, receptacle_ids,
                                 taken=ids, unsensable=unsensable,
                                 parents=pool)
            pool[raw["hypothesis_id"]] = raw     # a fork of a fork in one reply
        except HypothesisValidationError as err:
            dropped.append({"index": index, "error": str(err),
                            "bad_strings": list(err.bad_strings),
                            "document": doc})
            continue
        except (TypeError, ValueError, KeyError) as err:
            dropped.append({"index": index, "error": repr(err),
                            "bad_strings": [], "document": doc})
            continue
        ids.append(raw["hypothesis_id"])
        valid.append(raw)
    return valid, dropped


def accept_literal_away_tokens(text: str, rmap: Mapping[str, str]) -> str:
    """In the anonymized condition the model sometimes writes the real
    away tokens (``OUT_OF_HOUSE`` / ``ON_PERSON``) inside a document
    instead of their anonymized ids. They name no object and carry no
    household information, so they are mapped onto their tokens before
    validation rather than sent back for repair."""
    for real in AWAY_TOKENS:
        if real in rmap:
            text = re.sub(rf"\b{real}\b", rmap[real], text)
    return text


def revive_ids(text: str) -> List[str]:
    """``REVIVE p_xxxx`` lines anywhere in a reply."""
    return sorted(set(_REVIVE.findall(text)))


def read_ids(text: str) -> List[str]:
    """``READ p_xxxx p_yyyy`` lines: the documents the model wants to see
    in full before writing (first :data:`MAX_FETCH`, in order)."""
    out: List[str] = []
    for group in _READ.findall(text):
        for i in re.findall(r"p_[0-9a-f]{4}", group):
            if i not in out:
                out.append(i)
    return out[:MAX_FETCH]


# -------------------------------------------------------- anonymization

def _as_hypothesis(raw: Mapping[str, Any]) -> Dict[str, Any]:
    """Shape a raw timetable dict like a program hypothesis so the
    existing id translators apply: targets become activities whose moves
    carry the block receptacles; claims become one more activity."""
    activities = [
        {"name": target, "moves": [{"target": target, "to": b.get("at")}
                                   for b in blocks]}
        for target, blocks in dict(raw.get("targets", {})).items()]
    activities.append({"name": "__claims__", "moves": [
        {"target": c.get("target"), "to": c.get("expect")}
        for c in (raw.get("claims") or [])]})
    return {"rest": {}, "activities": activities,
            "distinguishing_check": raw.get("distinguishing_check")}


def _translate(raw: Mapping[str, Any], fn) -> Dict[str, Any]:
    done = fn(_as_hypothesis(raw))
    out = dict(raw)
    targets: Dict[str, List[Dict[str, Any]]] = {}
    for act, (target, blocks) in zip(done["activities"][:-1],
                                     dict(raw.get("targets", {})).items()):
        new_target = act["moves"][0]["target"] if act["moves"] else target
        targets[new_target] = [dict(b, at=m["to"])
                               for b, m in zip(blocks, act["moves"])]
    out["targets"] = targets
    out["claims"] = [dict(c, target=m["target"], expect=m["to"])
                     for c, m in zip(raw.get("claims") or [],
                                     done["activities"][-1]["moves"])]
    if raw.get("distinguishing_check"):
        out["distinguishing_check"] = done["distinguishing_check"]
    return out


def deanonymize_document(raw: Mapping[str, Any], omap, rmap, cmap) -> dict:
    """Structured fields back to real ids; ``markdown``/``prose`` stay in
    the vocabulary the model wrote them in."""
    return _translate(raw, lambda b: deanonymize_hypothesis(b, omap, rmap, cmap))


def anonymize_document(raw: Mapping[str, Any], omap, rmap, cmap) -> dict:
    return _translate(raw, lambda b: anonymize_hypothesis(b, omap, rmap, cmap))


# ------------------------------------------------------------- library

def library_index(raws: Sequence[Mapping[str, Any]],
                  vocabulary: Mapping[str, str]) -> Dict[str, Any]:
    """The household file: the raw dicts (markdown included) plus the
    vocabulary the model was shown."""
    return {"format": "longleaf", "hypotheses": [dict(r) for r in raws],
            "vocabulary": dict(vocabulary)}


def is_longleaf_payload(payload: Any) -> bool:
    return isinstance(payload, Mapping) and payload.get("format") == "longleaf"


def write_library(directory, raws: Sequence[Mapping[str, Any]],
                  status: Optional[Mapping[str, Mapping[str, Any]]] = None) -> None:
    """One ``.md`` per hypothesis plus ``INDEX.md`` with weights and
    status when given."""
    import pathlib
    directory = pathlib.Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    rows = ["# Hypothesis library", "", "| id | title | forked from | status | weight |", "|---|---|---|---|---|"]
    for raw in raws:
        (directory / f"{raw['hypothesis_id']}.md").write_text(raw["markdown"])
        st = (status or {}).get(raw["hypothesis_id"], {})
        rows.append(f"| [{raw['hypothesis_id']}]({raw['hypothesis_id']}.md) | "
                    f"{raw.get('title', '')} | {raw.get('forked_from') or '-'} | "
                    f"{st.get('status', 'live')} | "
                    f"{st.get('weight', float('nan')):.3f} |")
    (directory / "INDEX.md").write_text("\n".join(rows) + "\n")


__all__ = ["AWAY_TOKENS", "CLAIM_TRIGGER_AGAINST", "CLAIM_TRIGGER_WEIGHT",
           "accept_literal_away_tokens",
           "DELIMITER", "MAX_FETCH", "MAX_LIBRARY", "MIN_ELICITED", "read_ids",
           "REVISION_TARGET", "TARGET_ELICITED", "anonymize_document",
           "deanonymize_document", "is_longleaf_payload", "library_index",
           "parse_document", "parse_documents", "revive_ids",
           "split_documents", "write_library"]
