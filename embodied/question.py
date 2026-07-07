"""
question.py — MCQ question generation.

Builds a fixed option set per question at arrival time: the target's
current anchor, prior anchors from its own day history (the stale-memory
trap distractor — the exact scenario a resense is supposed to catch), a
category-plausible anchor the target never visited that day, and a
contentful "not in the house" option when this category is ever seen
outdoor/away in the training data.

correct_index is set at generation time from the target's CURRENT truth,
but the option set itself is what's fixed — if the object moves again
before the agent finally answers, the scorer (runner.py) re-derives which
option index is correct at report time from true_anchor(), not this
module. If report-time truth isn't among the fixed options at all,
scoring.brier_score treats every answer neutrally (see that module) rather
than this one silently fabricating a plausible-looking but wrong option to
paper over it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..env.deltas import Change
from ..rooms import slot_room
from .belief import DecayModel
from .ground_truth import true_anchor
from .policy import classify_hazard

NOT_IN_HOUSE = "OUTSIDE"


@dataclass(frozen=True)
class MCQQuestion:
    label:                 str
    category:              str
    stem:                  str
    options:               tuple[str, ...]
    correct_index:         Optional[int]     # at GENERATION time; runner re-derives at report time
    asked_t:               float
    hazard_class:          str
    distractor_provenance: tuple[str, ...]   # parallel to options
    # M3 (state-change dynamics): "location" (default, generate_mcq_question
    # above) or "state" (generate_state_question below). label/category are
    # the belief-store keys a state question uses — synthetic
    # f"{real_label}::{variable}" / f"{real_category}::{variable}" strings
    # (see posterior.py's module docstring) — so underlying_label/
    # state_variable carry the REAL identity ground-truth scoring needs
    # (runner._score branches on question_type to call true_state with
    # these instead of true_anchor with .label).
    question_type:         str = "location"
    underlying_label:      Optional[str] = None
    state_variable:        Optional[str] = None


def category_anchor_history(train_manifests: list[dict]) -> dict[str, set[str]]:
    """{category: {anchor, ...}} — every to_semantic anchor ever seen for
    each category across the given (train) manifests' changes. The source
    for "a category-plausible anchor the target never visited today":
    plausible because some real instance of that category really was
    placed there at some point, not an arbitrary guess."""
    history: dict[str, set[str]] = {}
    for manifest in train_manifests:
        for c in manifest.get("changes", []):
            history.setdefault(c["object_category"], set()).add(c["to_semantic"])
    return history


def categories_ever_outdoor(train_manifests: list[dict]) -> set[str]:
    """Categories whose to_semantic ever resolved to a non-indoor room
    (rooms.slot_room returns None or "outdoor") across the given
    manifests — the source of truth for whether "not in the house" is
    even a plausible option for this category."""
    categories: set[str] = set()
    for manifest in train_manifests:
        for c in manifest.get("changes", []):
            room = slot_room(c["to_semantic"])
            if room is None or room == "outdoor":
                categories.add(c["object_category"])
    return categories


def _label_history_up_to(changes: list[Change], label: str, t: float) -> list[str]:
    """Distinct to_semantic anchors this label visited, in chronological
    order, up to (and including) time t."""
    events = sorted((c for c in changes if c.instance_id == label and c.t <= t), key=lambda c: c.t)
    visited: list[str] = []
    for e in events:
        if e.to_semantic and e.to_semantic not in visited:
            visited.append(e.to_semantic)
    return visited


def generate_mcq_question(
    label: str,
    category: str,
    asked_t: float,
    initial_state,
    changes: list[Change],
    anchor_history: dict[str, set[str]],
    outdoor_categories: set[str],
    decay_models: dict[str, DecayModel],
    n_options: int = 4,
) -> MCQQuestion:
    current_truth = true_anchor(label, asked_t, initial_state, changes)
    visited_today = _label_history_up_to(changes, label, asked_t)

    options: list[str] = []
    provenance: list[str] = []

    def _add(anchor: Optional[str], kind: str) -> None:
        if anchor and anchor not in options:
            options.append(anchor)
            provenance.append(kind)

    _add(current_truth, "target")

    # The stale-memory trap: the anchor immediately before the current one.
    if len(visited_today) >= 2:
        _add(visited_today[-2], "prior_history")

    # Another anchor from the label's own history, if one remains unused.
    for anchor in visited_today:
        if anchor not in options:
            _add(anchor, "prior_history")
            break

    # A category-plausible anchor the target never visited today.
    plausible = sorted(anchor_history.get(category, set()) - set(visited_today))
    for anchor in plausible:
        if anchor not in options:
            _add(anchor, "category_plausible")
            break

    # Fill remaining slots with further category-plausible anchors before
    # ever repeating a provenance kind's exhausted source.
    for anchor in plausible:
        if len(options) >= n_options:
            break
        _add(anchor, "category_plausible")

    if category in outdoor_categories:
        _add(NOT_IN_HOUSE, "not_in_house")

    # Shuffle deterministically (seeded by label + asked_t, not by which
    # entry is correct) — construction always appended the current truth
    # first, so an unshuffled list would put the correct answer at index 0
    # every time, a positional leak the blind-baseline test exists to
    # catch. Shuffling here, once, means correct_index below is computed
    # against the final order actually exposed to a policy.
    import random as _random
    rng = _random.Random(f"{label}:{asked_t:.6f}")
    order = list(range(len(options)))
    rng.shuffle(order)
    options = [options[i] for i in order]
    provenance = [provenance[i] for i in order]

    correct_index = options.index(current_truth) if current_truth is not None and current_truth in options else None
    hazard = classify_hazard(category, decay_models)
    stem = f"Where is the {category} tracked as {label!r} right now?"

    return MCQQuestion(
        label=label, category=category, stem=stem, options=tuple(options),
        correct_index=correct_index, asked_t=asked_t, hazard_class=hazard,
        distractor_provenance=tuple(provenance),
    )


@dataclass(frozen=True)
class TargetSpec:
    """One referenced instance within a MultiObjectQuestion — the same
    resolvable shape a single-object MCQQuestion carries (options/
    correct_index/distractor_provenance/hazard_class), so each target can
    be scored independently and identically to how single-object
    questions already work: re-deriving truth from true_anchor() at
    report time, per label, exactly as runner.py already does."""
    label:                 str
    category:              str
    options:               tuple[str, ...]
    correct_index:         Optional[int]
    distractor_provenance: tuple[str, ...]
    hazard_class:          str


@dataclass(frozen=True)
class MultiObjectQuestion:
    """D2: a question stem referencing 2-3 instances at once (E3's own
    IV — opportunistic routing among referenced instances — needs
    multiple genuinely independent targets to route between; a single-
    target question can never exercise that decision). Each target is
    independently report-time resolvable (see TargetSpec) — there is no
    combined/joint option set, deliberately: scoring an instance's
    location doesn't depend on any other referenced instance's location,
    so bundling them into one combinatorial option set would only make
    scoring harder to interpret for no added test coverage.

    hazard_class is the MAX over targets.hazard_class ("volatile" if any
    referenced instance is volatile, else "stable") — the question is
    only as easy as its hardest-to-track referenced instance.
    """
    stem:         str
    targets:      tuple[TargetSpec, ...]   # 2-3 entries
    asked_t:      float
    hazard_class: str
    n_targets:    int
    question_type: str = "location"


def generate_multi_object_question(
    labels: tuple[str, ...],
    categories: dict[str, str],
    asked_t: float,
    initial_state,
    changes: list[Change],
    anchor_history: dict[str, set[str]],
    outdoor_categories: set[str],
    decay_models: dict[str, DecayModel],
    n_options: int = 4,
) -> MultiObjectQuestion:
    """Builds one TargetSpec per label by reusing generate_mcq_question's
    own per-instance option/distractor/hazard construction unchanged (no
    duplicated logic — each target is exactly what a single-object
    question for that label would have produced), then bundles them.

    labels must have 2 or 3 distinct entries — the range D2 specs
    ("stems referencing 2-3 instances"); this is enforced, not silently
    clamped, since a 1-target or 4+-target call is a caller bug, not a
    valid degenerate case of this function.
    """
    if not (2 <= len(labels) <= 3):
        raise ValueError(f"generate_multi_object_question needs 2-3 labels, got {len(labels)}: {labels}")
    if len(set(labels)) != len(labels):
        raise ValueError(f"generate_multi_object_question needs distinct labels, got duplicates in {labels}")

    targets = []
    for label in labels:
        category = categories[label]
        sub = generate_mcq_question(
            label=label, category=category, asked_t=asked_t,
            initial_state=initial_state, changes=changes,
            anchor_history=anchor_history, outdoor_categories=outdoor_categories,
            decay_models=decay_models, n_options=n_options,
        )
        targets.append(TargetSpec(
            label=label, category=category, options=sub.options,
            correct_index=sub.correct_index, distractor_provenance=sub.distractor_provenance,
            hazard_class=sub.hazard_class,
        ))

    combined_hazard = "volatile" if any(t.hazard_class == "volatile" for t in targets) else "stable"
    stem = "Where are the " + ", ".join(f"{t.category} tracked as {t.label!r}" for t in targets) + " right now?"

    return MultiObjectQuestion(
        stem=stem, targets=tuple(targets), asked_t=asked_t,
        hazard_class=combined_hazard, n_targets=len(targets),
    )


def generate_state_question(
    label: str,
    category: str,
    variable: str,
    asked_t: float,
    initial_state,
    changes: list[Change],
    decay_models: dict[str, DecayModel],
) -> MCQQuestion:
    """M3 (state-change dynamics): a question about `label`'s current
    value of `variable` (e.g. power, door — env/deltas.py's
    STATE_VARIABLES) instead of its current location.

    Unlike generate_mcq_question, the option set needs no distractor
    construction: STATE_VARIABLES' domain is small and closed (typically 2
    values), so every legal value is an option, not a sampled subset. label/
    category on the returned MCQQuestion are the synthetic belief-store
    keys (f"{label}::{variable}" / f"{category}::{variable}" — see
    posterior.py's module docstring); underlying_label/state_variable carry
    the real identity runner._score needs to call true_state.
    """
    from ..env.deltas import STATE_VARIABLES
    from .ground_truth import true_state

    current_truth = true_state(label, variable, asked_t, initial_state, changes)
    options = list(STATE_VARIABLES[variable]["values"])

    import random as _random
    rng = _random.Random(f"{label}:{variable}:{asked_t:.6f}")
    order = list(range(len(options)))
    rng.shuffle(order)
    options = [options[i] for i in order]

    correct_index = options.index(current_truth) if current_truth is not None and current_truth in options else None
    hazard = classify_hazard(f"{category}::{variable}", decay_models)
    stem = f"What is the current {variable} state of the {category} tracked as {label!r}?"

    return MCQQuestion(
        label=f"{label}::{variable}", category=f"{category}::{variable}", stem=stem,
        options=tuple(options), correct_index=correct_index, asked_t=asked_t, hazard_class=hazard,
        distractor_provenance=tuple("state_domain" for _ in options),
        question_type="state", underlying_label=label, state_variable=variable,
    )
