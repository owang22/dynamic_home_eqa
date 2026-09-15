"""The assumption graph: shared premises over hypothesis particles.

The flat arm holds N independent hypotheses. The graph arm holds the
same kind of hypotheses as LEAVES of a two-level graph whose upper nodes
are ASSUMPTIONS — named latent facts about the household ("how many
people live here", "where is the primary resident on weekdays") each
with a small set of named VALUES. Every leaf carries a complete
``assumes`` map (one value per assumption), so a leaf is one cell of the
assumption grid, and the leaves' mixture weights ROLL UP to a weight per
assumption value.

Inference does not change: each leaf is still one particle in
:class:`~baselines.beliefs.hypothesis_mixture.HypothesisMixture`, still
validated by :func:`~baselines.beliefs.hypothesis_program.
parse_hypothesis`, and the mixture stays flat over leaves. The graph is
metadata that buys three things: weight rollup per assumption
(:func:`value_weight`, :func:`node_entropy`), edit SCOPING for revisions
(:func:`apply_operations` — leaves not mentioned stay byte-identical, so
their weights survive a rebuild; the LLM can neither delete a leaf nor
edit a rest map, and settled assumptions are closed to it), and assumption-targeted sensing
(:mod:`baselines.policies.assumption_disambiguation`).

Envelope (what the elicitation writes and the mixture loads)::

    {"assumptions": {<name>: {"question": str, "values": {<value>: str}}},
     "leaves": [{"leaf_id": "p_a41c", "assumes": {<name>: <value>},
                 ...the usual hypothesis body...}]}

Parser rules, enforced in this order; a leaf that fails any is dropped
with its offending strings recorded, as ``validate_hypotheses`` does:

1. ``leaf_id`` is opaque: ``p_`` plus 4 hex characters, NEVER derived
   from the assumption path. A path-like or duplicate id is replaced
   server-side and the substitution recorded.
2. Every key in ``assumes`` names an assumption; every value names one
   of its values.
3. Every assumption appears in every leaf's ``assumes``.
4. No two leaves share an ``assumes`` map.
5. The body passes :func:`parse_hypothesis` against the tables.

Caps: :data:`MAX_ASSUMPTIONS` assumptions, :data:`MAX_LEAVES` leaves.
Beyond them the envelope is rejected (for the repair round) and, if the
repair also overshoots, :func:`truncate_to_caps` cuts deterministically.
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import itertools
import re
from typing import (Any, Dict, Iterable, List, Mapping, Optional, Sequence,
                    Set, Tuple)

from baselines.beliefs.hypothesis_program import (HypothesisValidationError,
                                                  parse_hypothesis)
from baselines.policies.hypothesis_disambiguation import entropy

LEAF_ID_RE = re.compile(r"^p_[0-9a-f]{4}$")
MAX_ASSUMPTIONS = 3
MAX_LEAVES = 12
LIVE_FLOOR = 0.10
"""Rolled-up value weight at or above which a value counts as live for
the birth rule of ``add_assumption_value``."""

OPERATION_ORDER = ("add_assumption", "add_assumption_value", "edit_leaf",
                   "add_activity", "add_leaf")
"""Operations a revision may return, in application order. Leaf removal
is never an operation: leaves go only through the mixture's automatic
prune. ``add_activity`` appends one activity to a named leaf (the
diversify call's only way to touch an existing leaf)."""

REPAIR_OPS = frozenset({"edit_leaf", "add_activity", "add_assumption_value",
                        "add_leaf"})
"""A repair call edits what exists: ``add_activity`` is an ``edit_leaf``
that appends one activity, so it belongs here too (the model reaches
for it when new objects need a move)."""
DIVERSIFY_OPS = frozenset({"add_assumption", "add_assumption_value",
                           "add_leaf", "add_activity"})
ALL_OPS = frozenset(OPERATION_ORDER)
SETTLED_WEIGHT = 0.9
"""Rolled-up weight at which an assumption's top value makes the node
settled: reported as such and closed to operations."""

AWAY_TOKENS = ("OUT_OF_HOUSE", "ON_PERSON")


class GraphValidationError(ValueError):
    """The envelope, or an operation set, is not a valid graph.
    ``problems`` are human-readable; ``bad_strings`` feed the repair
    prompt verbatim."""

    def __init__(self, problems: Sequence[str],
                 bad_strings: Sequence[str] = ()) -> None:
        super().__init__("; ".join(problems))
        self.problems: Tuple[str, ...] = tuple(problems)
        self.bad_strings: Tuple[str, ...] = tuple(sorted(set(bad_strings)))


@dataclasses.dataclass(frozen=True)
class Assumption:
    name: str
    question: str
    values: Mapping[str, str]        # value name -> description


@dataclasses.dataclass
class AssumptionGraph:
    """Assumptions in declaration order plus leaf bodies in file order.
    Each leaf body carries ``leaf_id``, ``assumes`` and (set by the
    parser) ``hypothesis_id == leaf_id`` so
    :class:`~baselines.beliefs.hypothesis_program.HypothesisProgramBelief`
    names itself after the leaf without any change to that file."""

    assumptions: Dict[str, Assumption]
    leaves: List[Dict[str, Any]]

    # ---------------------------------------------------------- accessors

    def leaf_ids(self) -> List[str]:
        return [str(leaf["leaf_id"]) for leaf in self.leaves]

    def leaf(self, leaf_id: str) -> Dict[str, Any]:
        for leaf in self.leaves:
            if leaf["leaf_id"] == leaf_id:
                return leaf
        raise KeyError(leaf_id)

    def leaf_bodies(self) -> List[Dict[str, Any]]:
        """Deep copies with ``hypothesis_id`` pinned to ``leaf_id`` — what
        the mixture hands to the converter."""
        out = []
        for leaf in self.leaves:
            body = copy.deepcopy(leaf)
            body["hypothesis_id"] = body["leaf_id"]
            out.append(body)
        return out

    def copy(self) -> "AssumptionGraph":
        return AssumptionGraph(
            assumptions=dict(self.assumptions),
            leaves=[copy.deepcopy(leaf) for leaf in self.leaves])

    def to_json(self) -> Dict[str, Any]:
        return {"assumptions": {
                    name: {"question": a.question, "values": dict(a.values)}
                    for name, a in self.assumptions.items()},
                "leaves": [copy.deepcopy(leaf) for leaf in self.leaves]}

    @classmethod
    def from_json(cls, payload: Mapping[str, Any]) -> "AssumptionGraph":
        """Structural load of an already-validated envelope (the mixture's
        reset). No vocabulary check here — the leaf particles validate
        against the household tables when they reset."""
        assumptions = {
            str(name): Assumption(name=str(name),
                                  question=str(spec.get("question", "")),
                                  values={str(v): str(d) for v, d in
                                          dict(spec.get("values", {})).items()})
            for name, spec in dict(payload.get("assumptions", {})).items()}
        leaves = []
        for leaf in payload.get("leaves", ()):
            body = copy.deepcopy(dict(leaf))
            body["hypothesis_id"] = body["leaf_id"]
            leaves.append(body)
        return cls(assumptions=assumptions, leaves=leaves)


def is_graph_payload(payload: Any) -> bool:
    """Does a hypotheses file hold a graph envelope (vs the flat list)?"""
    return (isinstance(payload, Mapping) and "leaves" in payload
            and "assumptions" in payload)


# ------------------------------------------------------------------ ids

def new_leaf_id(existing: Iterable[str], seed_text: str) -> str:
    """A fresh opaque ``p_xxxx``: hashed from ``seed_text`` (deterministic
    across reruns) and bumped until it collides with nothing."""
    taken = set(existing)
    for salt in itertools.count():
        digest = hashlib.sha1(f"{seed_text}|{salt}".encode()).hexdigest()
        candidate = f"p_{digest[:4]}"
        if candidate not in taken:
            return candidate
    raise RuntimeError("unreachable")


def _assumes_key(assumes: Mapping[str, str]) -> Tuple[Tuple[str, str], ...]:
    return tuple(sorted((str(k), str(v)) for k, v in assumes.items()))


# --------------------------------------------------------------- parsing

@dataclasses.dataclass
class ParseResult:
    """``graph`` is None when the envelope as a whole is unusable
    (``problems`` says why); otherwise the kept leaves, plus every leaf
    dropped with its reason, and every leaf id the parser replaced."""

    graph: Optional[AssumptionGraph]
    dropped: List[Dict[str, Any]]
    substitutions: List[Dict[str, Any]]
    problems: List[str]

    @property
    def bad_strings(self) -> List[str]:
        out: List[str] = []
        for row in self.dropped:
            out.extend(row.get("bad_strings", ()))
        return sorted(set(out))


def _parse_assumptions(raw: Any, object_classes: Mapping[str, str],
                       receptacle_ids: Sequence[str],
                       enforce_caps: bool = True
                       ) -> Tuple[Dict[str, Assumption], List[str]]:
    problems: List[str] = []
    if not isinstance(raw, Mapping):
        return {}, ["`assumptions` must be an object mapping name -> "
                    "{question, values}"]
    ids = set(object_classes) | set(receptacle_ids)
    assumptions: Dict[str, Assumption] = {}
    for name, spec in raw.items():
        name = str(name)
        if not isinstance(spec, Mapping):
            problems.append(f"assumption {name!r}: must be an object")
            continue
        question = str(spec.get("question", "")).strip()
        values_raw = spec.get("values")
        if not question:
            problems.append(f"assumption {name!r}: missing `question`")
        if not isinstance(values_raw, Mapping) or len(values_raw) < 1:
            problems.append(f"assumption {name!r}: `values` must map at "
                            f"least one value name to a description")
            continue
        values = {str(v): str(d) for v, d in values_raw.items()}
        leaked = [tok for tok in _tokens(question)
                  + sum((_tokens(d) + _tokens(v) for v, d in values.items()),
                        [])
                  if tok in ids]
        if leaked:
            problems.append(
                f"assumption {name!r}: question/value text must not name "
                f"object or receptacle ids: {sorted(set(leaked))}")
        assumptions[name] = Assumption(name=name, question=question,
                                       values=values)
    if enforce_caps and len(assumptions) > MAX_ASSUMPTIONS:
        problems.append(f"{len(assumptions)} assumptions exceeds the cap of "
                        f"{MAX_ASSUMPTIONS}")
    return assumptions, problems


def _tokens(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9_]+", str(text))


def parse_graph(raw: Mapping[str, Any], object_classes: Mapping[str, str],
                receptacle_ids: Sequence[str],
                enforce_caps: bool = True,
                unsensable: Sequence[str] = ()) -> ParseResult:
    """Validate one envelope against the household vocabulary, applying
    the module's five rules per leaf in order, then the caps
    (``enforce_caps=False`` skips the caps so an over-sized but otherwise
    valid envelope can be cut with :func:`truncate_to_caps`)."""
    problems: List[str] = []
    if not isinstance(raw, Mapping) or "leaves" not in raw:
        return ParseResult(None, [], [], ["payload must be an object with "
                                          "`assumptions` and `leaves`"])
    assumptions, a_problems = _parse_assumptions(
        raw.get("assumptions", {}), object_classes, receptacle_ids,
        enforce_caps)
    problems += a_problems
    raw_leaves = raw.get("leaves")
    if not isinstance(raw_leaves, (list, tuple)):
        return ParseResult(None, [], [], problems + ["`leaves` must be a list"])
    if enforce_caps and len(raw_leaves) > MAX_LEAVES:
        problems.append(f"{len(raw_leaves)} leaves exceeds the cap of "
                        f"{MAX_LEAVES}")

    kept: List[Dict[str, Any]] = []
    dropped: List[Dict[str, Any]] = []
    substitutions: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()
    seen_assumes: Dict[Tuple[Tuple[str, str], ...], str] = {}
    for index, leaf in enumerate(raw_leaves):
        if not isinstance(leaf, Mapping):
            dropped.append({"index": index, "leaf": leaf, "bad_strings": [],
                            "error": "leaf must be an object"})
            continue
        body = copy.deepcopy(dict(leaf))
        # Rule 1: opaque id.
        given = str(body.get("leaf_id", body.get("hypothesis_id", "")))
        if not LEAF_ID_RE.match(given) or given in seen_ids:
            assigned = new_leaf_id(seen_ids, f"{given}|{index}|"
                                   f"{_assumes_key(body.get('assumes') or {})}")
            substitutions.append({"index": index, "given": given,
                                  "assigned": assigned,
                                  "reason": ("duplicate" if given in seen_ids
                                             else "not an opaque p_xxxx id")})
            body["leaf_id"] = assigned
        else:
            body["leaf_id"] = given
        body.pop("hypothesis_id", None)
        # Rule 2: assumes names known assumptions and values.
        assumes = body.get("assumes")
        if not isinstance(assumes, Mapping):
            dropped.append({"index": index, "leaf": body, "bad_strings": [],
                            "error": "missing or non-object `assumes`"})
            continue
        assumes = {str(k): str(v) for k, v in assumes.items()}
        bad = [k for k in assumes if k not in assumptions]
        bad += [f"{k}={v}" for k, v in assumes.items()
                if k in assumptions and v not in assumptions[k].values]
        if bad:
            dropped.append({"index": index, "leaf": body, "bad_strings": bad,
                            "error": "assumes names unknown assumptions or "
                                     "values"})
            continue
        # Rule 3: complete assignment.
        missing = [a for a in assumptions if a not in assumes]
        if missing:
            dropped.append({"index": index, "leaf": body,
                            "bad_strings": missing,
                            "error": "assumes must give a value for every "
                                     "assumption"})
            continue
        # Rule 4: unique cell.
        key = _assumes_key(assumes)
        if key in seen_assumes:
            dropped.append({"index": index, "leaf": body, "bad_strings": [],
                            "error": f"same assumes map as leaf "
                                     f"{seen_assumes[key]}"})
            continue
        # Rule 5: the body itself.
        body["assumes"] = assumes
        body["hypothesis_id"] = body["leaf_id"]
        try:
            parse_hypothesis(body, object_classes, receptacle_ids,
                             unsensable=unsensable)
        except HypothesisValidationError as err:
            dropped.append({"index": index, "leaf": body,
                            "bad_strings": list(err.bad_strings),
                            "error": str(err)})
            continue
        except (TypeError, ValueError, KeyError) as err:
            dropped.append({"index": index, "leaf": body, "bad_strings": [],
                            "error": repr(err)})
            continue
        seen_ids.add(body["leaf_id"])
        seen_assumes[key] = body["leaf_id"]
        kept.append(body)
    if not kept:
        problems.append("no valid leaves")
    graph = (AssumptionGraph(assumptions=assumptions, leaves=kept)
             if not problems else None)
    return ParseResult(graph, dropped, substitutions, problems)


def validate_graph(graph: AssumptionGraph, object_classes: Mapping[str, str],
                   receptacle_ids: Sequence[str],
                   unsensable: Sequence[str] = ()) -> List[str]:
    """Whole-graph check after operations: every problem AND every leaf
    the parser would drop counts (an operation set that leaves any leaf
    invalid is not applied)."""
    result = parse_graph(graph.to_json(), object_classes, receptacle_ids,
                         unsensable=unsensable)
    problems = list(result.problems)
    for row in result.dropped:
        problems.append(f"leaf {row['leaf'].get('leaf_id', '?')}: "
                        f"{row['error']}"
                        + (f" {row['bad_strings']}" if row["bad_strings"]
                           else ""))
    for row in result.substitutions:
        problems.append(f"leaf id {row['given']!r} is not opaque")
    return problems


def truncate_to_caps(graph: AssumptionGraph
                     ) -> Tuple[AssumptionGraph, List[str]]:
    """Deterministic cut used when the repair round still overshoots:
    keep the first :data:`MAX_ASSUMPTIONS` assumptions (stripping the
    rest from every leaf, then deduplicating cells), then the first
    :data:`MAX_LEAVES` leaves."""
    notes: List[str] = []
    names = list(graph.assumptions)
    keep = names[:MAX_ASSUMPTIONS]
    out = graph.copy()
    if len(names) > MAX_ASSUMPTIONS:
        notes.append(f"dropped assumptions {names[MAX_ASSUMPTIONS:]}")
        out.assumptions = {n: graph.assumptions[n] for n in keep}
        seen: Set[Tuple[Tuple[str, str], ...]] = set()
        leaves = []
        for leaf in out.leaves:
            leaf["assumes"] = {k: v for k, v in leaf["assumes"].items()
                               if k in keep}
            key = _assumes_key(leaf["assumes"])
            if key in seen:
                notes.append(f"dropped leaf {leaf['leaf_id']} (duplicate "
                             f"cell after assumption cut)")
                continue
            seen.add(key)
            leaves.append(leaf)
        out.leaves = leaves
    if len(out.leaves) > MAX_LEAVES:
        notes.append(f"dropped leaves "
                     f"{[l['leaf_id'] for l in out.leaves[MAX_LEAVES:]]}")
        out.leaves = out.leaves[:MAX_LEAVES]
    return out, notes


# ---------------------------------------------------------------- rollup

def normalized_leaf_weights(graph: AssumptionGraph,
                            leaf_weights: Mapping[str, float]
                            ) -> Dict[str, float]:
    """Weights of the graph's leaves renormalized among themselves.
    ``leaf_weights`` are the mixture's weights keyed by leaf id — the
    statistical particles are simply not in the map, so they are
    excluded from the rollup and keep their own weight outside it."""
    raw = {lid: max(0.0, float(leaf_weights.get(lid, 0.0)))
           for lid in graph.leaf_ids()}
    total = sum(raw.values())
    if total <= 0.0:
        n = len(raw) or 1
        return {lid: 1.0 / n for lid in raw}
    return {lid: w / total for lid, w in raw.items()}


def value_weights(graph: AssumptionGraph, leaf_weights: Mapping[str, float],
                  assumption: str) -> Dict[str, float]:
    """Rolled-up weight of every value of ``assumption`` (declared values
    with no leaf get 0)."""
    norm = normalized_leaf_weights(graph, leaf_weights)
    out = {v: 0.0 for v in graph.assumptions[assumption].values}
    for leaf in graph.leaves:
        v = leaf["assumes"][assumption]
        out[v] = out.get(v, 0.0) + norm[leaf["leaf_id"]]
    return out


def value_weight(graph: AssumptionGraph, leaf_weights: Mapping[str, float],
                 assumption: str, value: str) -> float:
    """Sum of normalized leaf weights with ``assumes[assumption] ==
    value``."""
    return value_weights(graph, leaf_weights, assumption).get(value, 0.0)


def node_entropy(graph: AssumptionGraph, leaf_weights: Mapping[str, float],
                 assumption: str) -> float:
    """Shannon entropy in nats over the assumption's value weights (the
    same ``entropy`` helper the flat disambiguation policy uses)."""
    return entropy(list(value_weights(graph, leaf_weights,
                                      assumption).values()))


def live_values(graph: AssumptionGraph, leaf_weights: Mapping[str, float],
                floor: float = LIVE_FLOOR) -> Dict[str, List[str]]:
    """Per assumption, the values whose rolled-up weight is at or above
    ``floor``, in declaration order."""
    return {a: [v for v, w in value_weights(graph, leaf_weights, a).items()
                if w >= floor]
            for a in graph.assumptions}


def assumption_summary(graph: AssumptionGraph,
                       leaf_weights: Mapping[str, float]
                       ) -> Dict[str, Dict[str, Any]]:
    """Per assumption: its question, each value's weight, the entropy."""
    return {a: {"question": graph.assumptions[a].question,
                "values": value_weights(graph, leaf_weights, a),
                "entropy": node_entropy(graph, leaf_weights, a)}
            for a in graph.assumptions}


# ------------------------------------------------------------ operations

@dataclasses.dataclass
class OperationResult:
    """Outcome of :func:`apply_operations`. ``graph`` is None when the
    set was rejected whole (``problems`` says why); ``applied`` lists
    what took effect, ``births`` the leaves created by
    ``add_assumption_value`` and ``skipped_births`` the combinations the
    birth rule declined with the reason."""

    graph: Optional[AssumptionGraph]
    applied: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    births: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    skipped_births: List[Dict[str, Any]] = dataclasses.field(
        default_factory=list)
    problems: List[str] = dataclasses.field(default_factory=list)
    operations: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    """The operations as received (real ids), for the edit log."""
    rejected: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    """Operations refused one by one (``op``, ``reason``, and what named
    them) while the rest of the set still applied."""

    @property
    def changed_leaf_ids(self) -> List[str]:
        """Leaves whose body differs after the set: edited, added, born.
        Everything else is byte-identical to before."""
        out: List[str] = []
        for row in self.applied:
            if row["op"] in ("edit_leaf", "add_leaf"):
                out.append(row["leaf_id"])
        out += [b["leaf_id"] for b in self.births]
        return out


def _body_from(op: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    body = op.get("body")
    return copy.deepcopy(dict(body)) if isinstance(body, Mapping) else None


def settled_assumptions(graph: AssumptionGraph,
                        leaf_weights: Mapping[str, float],
                        settled_weight: float = SETTLED_WEIGHT
                        ) -> Dict[str, str]:
    """Assumptions whose top value holds at least ``settled_weight`` of
    the rolled-up weight: ``{assumption: top value}``."""
    out: Dict[str, str] = {}
    for name in graph.assumptions:
        weights = value_weights(graph, leaf_weights, name)
        if not weights:
            continue
        top = max(weights, key=lambda v: weights[v])
        if weights[top] >= settled_weight:
            out[name] = top
    return out


def _rest_map(body: Mapping[str, Any]) -> Dict[str, str]:
    """The rest map as a plain dict, whichever shape it was written in."""
    from baselines.beliefs.hypothesis_program import _rest_pairs
    try:
        return dict(_rest_pairs(body.get("rest")))
    except HypothesisValidationError:
        return {"<unparseable>": str(body.get("rest"))[:60]}


def apply_operations(graph: AssumptionGraph,
                     operations: Sequence[Mapping[str, Any]],
                     leaf_weights: Mapping[str, float],
                     object_classes: Mapping[str, str],
                     receptacle_ids: Sequence[str],
                     live_floor: float = LIVE_FLOOR,
                     allowed_ops: Optional[Iterable[str]] = None,
                     settled: Optional[Mapping[str, str]] = None,
                     unsensable: Sequence[str] = ()) -> OperationResult:
    """Apply a revision's operations to a copy of ``graph``.

    Order: ``add_assumption``, ``add_assumption_value``, ``edit_leaf``,
    ``add_activity``, ``add_leaf``; births from ``add_assumption_value``
    are materialized last so a template leaf already carries any value
    the same response assigned it.

    Two kinds of refusal. The WHOLE set is rejected (``graph`` None, so
    the caller runs the repair round) when an operation is malformed or
    names something that does not exist, when an ``edit_leaf`` changes
    the leaf's ``rest`` (rest is fit from sightings and set once at
    tour start), when an ``add_assumption`` is not accompanied by
    ``edit_leaf`` operations covering every existing leaf, or when the
    result fails :func:`validate_graph` or the caps. Single operations
    are refused and listed in ``rejected`` while the rest still apply
    when their kind is outside ``allowed_ops`` (a removed ``drop_leaf``,
    or an edit in a diversify call) or when they touch an assumption in
    ``settled`` (add a value to it, or assign a leaf a non-settled
    value of it).

    Birth rule: a new value of assumption A is crossed only with LIVE
    values (rolled-up weight >= ``live_floor`` under the pre-operation
    weights) of every other assumption. Each born leaf is a copy of the
    best-weighted leaf sharing that combination, re-labelled; an
    ``add_leaf`` in the same response with the same ``assumes`` map takes
    precedence over the template.
    """
    result = OperationResult(graph=None)
    problems = result.problems
    allowed = set(allowed_ops) if allowed_ops is not None else set(ALL_OPS)
    settled = dict(settled or {})
    diversify = allowed == set(DIVERSIFY_OPS)
    if diversify:
        # A diversify call must add structure: an edit written to every
        # leaf cannot move relative weight, so a response made only of
        # add_activity does nothing. Reject it whole so the repair round
        # asks again; and one activity name may go to one leaf only.
        kinds = [str(op.get("op", "")) for op in operations
                 if isinstance(op, Mapping)]
        if not any(k in ("add_leaf", "add_assumption_value", "add_assumption")
                   for k in kinds):
            problems.append(
                "diversify call rejected: it must contain at least one "
                "add_leaf or add_assumption_value (an add_activity written "
                "to every leaf cannot move any weight)")
        names: Dict[str, List[str]] = {}
        for op in operations:
            if isinstance(op, Mapping) and op.get("op") == "add_activity" \
                    and isinstance(op.get("activity"), Mapping):
                names.setdefault(str(op["activity"].get("name", "")), []
                                 ).append(str(op.get("leaf_id")))
        for name, leaves in names.items():
            if len(leaves) > 1:
                problems.append(
                    f"diversify call rejected: activity {name!r} added to "
                    f"{len(leaves)} leaves {leaves}; one activity name may "
                    f"be added to at most one leaf per call")
        if problems:
            return result
    ops_by_kind: Dict[str, List[Mapping[str, Any]]] = {k: []
                                                       for k in OPERATION_ORDER}
    for index, op in enumerate(operations):
        kind = str(op.get("op", "")) if isinstance(op, Mapping) else ""
        if kind == "drop_leaf":
            result.rejected.append({"index": index, "op": kind,
                                    "leaf_id": op.get("leaf_id"),
                                    "reason": "drop_leaf is not an operation; "
                                              "leaves go only through the "
                                              "automatic prune"})
            continue
        if kind not in ops_by_kind:
            result.rejected.append({"index": index, "op": kind,
                                    "leaf_id": op.get("leaf_id"),
                                    "reason": f"unknown op {kind!r}; the "
                                              f"operations are "
                                              f"{', '.join(OPERATION_ORDER)}"})
            continue
        if kind not in allowed:
            result.rejected.append({"index": index, "op": kind,
                                    "leaf_id": op.get("leaf_id"),
                                    "reason": f"{kind} is not allowed in "
                                              f"this call"})
            continue
        touched = _settled_touched(op, settled)
        if touched:
            result.rejected.append({"index": index, "op": kind,
                                    "leaf_id": op.get("leaf_id"),
                                    "assumption": touched,
                                    "reason": f"assumption {touched!r} is "
                                              f"settled at "
                                              f"{settled[touched]!r} and "
                                              f"closed to operations"})
            continue
        ops_by_kind[kind].append(op)
    if problems:
        return result

    pre_weights = normalized_leaf_weights(graph, leaf_weights)
    pre_live = live_values(graph, leaf_weights, live_floor)
    pre_assumptions = list(graph.assumptions)
    out = graph.copy()
    existing_ids = set(out.leaf_ids())

    # add_assumption — with the coverage rule checked up front.
    for op in ops_by_kind["add_assumption"]:
        name = str(op.get("assumption", "")).strip()
        values = op.get("values")
        if not name or name in out.assumptions:
            problems.append(f"add_assumption: missing or duplicate name "
                            f"{name!r}")
            continue
        if not isinstance(values, Mapping) or not values:
            problems.append(f"add_assumption {name!r}: `values` must map "
                            f"value names to descriptions")
            continue
        covered = {str(e.get("leaf_id")) for e in ops_by_kind["edit_leaf"]
                   if isinstance(e.get("body"), Mapping)
                   and name in dict(e["body"].get("assumes") or {})}
        uncovered = sorted(existing_ids - covered)
        if uncovered:
            problems.append(
                f"add_assumption {name!r} rejected: no edit_leaf gives a "
                f"value for it on leaves {uncovered}")
            continue
        out.assumptions[name] = Assumption(
            name=name, question=str(op.get("question", "")),
            values={str(v): str(d) for v, d in values.items()})
        result.applied.append({"op": "add_assumption", "assumption": name,
                               "values": sorted(values)})
    if problems:
        return OperationResult(graph=None, problems=problems,
                               rejected=result.rejected)

    # add_assumption_value — recorded now, born last.
    pending_births: List[Tuple[str, str, str]] = []
    for op in ops_by_kind["add_assumption_value"]:
        name = str(op.get("assumption", ""))
        value = str(op.get("value", "")).strip()
        if name not in out.assumptions:
            result.rejected.append({
                "op": "add_assumption_value", "assumption": name,
                "reason": f"unknown assumption {name!r} (existing: "
                          f"{list(out.assumptions)}); a new assumption "
                          f"needs add_assumption with edit_leaf coverage"})
            continue
        if not value or value in out.assumptions[name].values:
            result.rejected.append({
                "op": "add_assumption_value", "assumption": name,
                "reason": f"missing or duplicate value {value!r}"})
            continue
        a = out.assumptions[name]
        out.assumptions[name] = Assumption(
            name=name, question=a.question,
            values={**a.values, value: str(op.get("description", ""))})
        result.applied.append({"op": "add_assumption_value",
                               "assumption": name, "value": value})
        pending_births.append((name, value, str(op.get("description", ""))))

    # edit_leaf — the id is the identity; the body is replaced whole;
    # rest must be byte-for-byte what the leaf already holds.
    for op in ops_by_kind["edit_leaf"]:
        leaf_id = str(op.get("leaf_id", ""))
        body = _body_from(op)
        if leaf_id not in existing_ids or body is None:
            problems.append(f"edit_leaf: unknown leaf {leaf_id!r} or missing "
                            f"body")
            continue
        stored = out.leaf(leaf_id)
        old_rest, new_rest = _rest_map(stored), _rest_map(body)
        if old_rest != new_rest:
            changed = sorted(k for k in set(old_rest) | set(new_rest)
                             if old_rest.get(k) != new_rest.get(k))
            problems.append(
                f"edit_leaf {leaf_id}: rest is fit from sightings and is "
                f"not editable; resubmit with the stored rest map "
                f"(changed keys: {changed})")
            continue
        body["leaf_id"] = leaf_id
        body["hypothesis_id"] = leaf_id
        out.leaves = [body if l["leaf_id"] == leaf_id else l
                      for l in out.leaves]
        result.applied.append({"op": "edit_leaf", "leaf_id": leaf_id})

    # add_activity — append one activity to a named leaf.
    for op in ops_by_kind["add_activity"]:
        leaf_id = str(op.get("leaf_id", ""))
        activity = op.get("activity")
        if leaf_id not in existing_ids or not isinstance(activity, Mapping):
            result.rejected.append({
                "op": "add_activity", "leaf_id": leaf_id,
                "reason": f"unknown leaf {leaf_id!r} or missing `activity`"})
            continue
        leaf = out.leaf(leaf_id)
        leaf["activities"] = list(leaf.get("activities", ())) + [
            copy.deepcopy(dict(activity))]
        result.applied.append({"op": "add_activity", "leaf_id": leaf_id,
                               "activity": str(activity.get("name", ""))})

    # add_leaf — a fresh cell; the id is kept when opaque and unused.
    added_cells: Dict[Tuple[Tuple[str, str], ...], str] = {}
    for op in ops_by_kind["add_leaf"]:
        body = _body_from(op)
        if body is None or not isinstance(body.get("assumes"), Mapping):
            result.rejected.append({
                "op": "add_leaf", "reason": "body with a complete `assumes` "
                                            "map is required"})
            continue
        given = str(body.get("leaf_id", ""))
        taken = set(out.leaf_ids())
        leaf_id = (given if LEAF_ID_RE.match(given) and given not in taken
                   else new_leaf_id(taken, f"add|{_assumes_key(body['assumes'])}"
                                           f"|{len(taken)}"))
        body["leaf_id"] = leaf_id
        body["hypothesis_id"] = leaf_id
        body["assumes"] = {str(k): str(v) for k, v in body["assumes"].items()}
        out.leaves.append(body)
        added_cells[_assumes_key(body["assumes"])] = leaf_id
        result.applied.append({"op": "add_leaf", "leaf_id": leaf_id,
                               "given_id": given})
    if problems:
        return OperationResult(graph=None, problems=problems,
                               rejected=result.rejected)

    # Births, against live values only.
    for name, value, description in pending_births:
        others = [a for a in out.assumptions if a != name]
        axes: List[List[str]] = []
        for other in others:
            if other in pre_assumptions:
                live = list(pre_live.get(other, []))
                dead = [v for v in out.assumptions[other].values
                        if v not in live]
                for v in dead:
                    result.skipped_births.append({
                        "new_value": f"{name}={value}",
                        "assumption": other, "value": v,
                        "weight": value_weight(graph, leaf_weights, other, v)
                        if v in graph.assumptions[other].values else 0.0,
                        "reason": f"below live floor {live_floor}"})
            else:
                # An assumption added in this same response has no
                # rolled-up weight yet: every value it declares is live.
                live = list(out.assumptions[other].values)
            axes.append(live)
        for combo in itertools.product(*axes) if axes else [()]:
            assumes = dict(zip(others, combo))
            assumes[name] = value
            key = _assumes_key(assumes)
            if key in added_cells or any(_assumes_key(l["assumes"]) == key
                                         for l in out.leaves):
                result.skipped_births.append({
                    "new_value": f"{name}={value}", "assumes": assumes,
                    "reason": "cell already supplied by an add_leaf"})
                continue
            template = _template_leaf(out, pre_weights, others, combo)
            if template is None:
                result.skipped_births.append({
                    "new_value": f"{name}={value}", "assumes": assumes,
                    "reason": "no leaf to copy as a template"})
                continue
            body = copy.deepcopy(template)
            leaf_id = new_leaf_id(out.leaf_ids(),
                                  f"birth|{key}|{template['leaf_id']}")
            body["leaf_id"] = leaf_id
            body["hypothesis_id"] = leaf_id
            body["assumes"] = assumes
            body["rationale"] = (f"[born from {template['leaf_id']} for "
                                 f"{name}={value}: {description}] "
                                 f"{template.get('rationale', '')}").strip()
            out.leaves.append(body)
            result.births.append({"leaf_id": leaf_id, "assumes": assumes,
                                  "template": template["leaf_id"],
                                  "new_value": f"{name}={value}"})

    if len(out.assumptions) > MAX_ASSUMPTIONS:
        problems.append(f"{len(out.assumptions)} assumptions exceeds the cap "
                        f"of {MAX_ASSUMPTIONS}")
    if len(out.leaves) > MAX_LEAVES:
        problems.append(f"{len(out.leaves)} leaves exceeds the cap of "
                        f"{MAX_LEAVES}")
    problems += validate_graph(out, object_classes, receptacle_ids,
                               unsensable=unsensable)
    if problems:
        return OperationResult(graph=None, applied=result.applied,
                               births=result.births,
                               skipped_births=result.skipped_births,
                               problems=problems, rejected=result.rejected)
    result.graph = out
    return result


def _settled_touched(op: Mapping[str, Any],
                     settled: Mapping[str, str]) -> Optional[str]:
    """The settled assumption an operation would touch, if any: adding a
    value to it, or giving a leaf a value of it other than the settled
    one (an add_leaf or edit_leaf that agrees with the settled value is
    fine)."""
    if not settled:
        return None
    kind = str(op.get("op", ""))
    if kind == "add_assumption_value" and op.get("assumption") in settled:
        return str(op["assumption"])
    body = op.get("body")
    if kind in ("add_leaf", "edit_leaf") and isinstance(body, Mapping):
        assumes = body.get("assumes") or {}
        for name, top in settled.items():
            if name in assumes and str(assumes[name]) != top:
                return name
    return None


def _template_leaf(graph: AssumptionGraph, weights: Mapping[str, float],
                   others: Sequence[str], combo: Sequence[str]
                   ) -> Optional[Dict[str, Any]]:
    """Best-weighted leaf agreeing with ``combo`` on ``others``; failing
    that, the best-weighted leaf overall (weight 0 for leaves born or
    added in this response)."""
    def weight(leaf: Mapping[str, Any]) -> float:
        return float(weights.get(leaf["leaf_id"], 0.0))
    matching = [l for l in graph.leaves
                if all(l["assumes"].get(a) == v for a, v in zip(others, combo))]
    pool = matching or list(graph.leaves)
    if not pool:
        return None
    return max(pool, key=weight)


# ------------------------------------------------------------- recovery

PREMISE_SYNONYMS: Mapping[str, Tuple[str, ...]] = {
    # composition
    "solo": ("solo", "single", "alone", "one adult", "one resident",
             "one person", "lives alone"),
    "couple": ("couple", "two adults", "partner", "pair", "two residents"),
    "family_with_children": ("family", "kid", "kids", "child", "children",
                             "toddler", "teen", "parent"),
    "roommates": ("roommate", "roommates", "flatmate", "housemate",
                  "students", "shared"),
    "multigenerational": ("multigenerational", "grandparent", "three "
                          "generations", "extended family", "elder"),
    "retired": ("retired", "retiree", "pensioner", "senior"),
    # work pattern
    "works_away": ("works away", "office", "commute", "out of the house",
                   "away on weekdays", "9 to 5", "leaves for work",
                   "works_away", "away_weekdays"),
    "works_from_home": ("works from home", "work from home", "remote",
                        "home office", "at the desk", "wfh", "works_from_home"),
    "shift_work": ("shift", "night shift", "rotating", "irregular",
                   "nights", "evenings out"),
    "opposite_schedules": ("opposite", "staggered", "different schedules",
                           "one home while the other"),
    "no_fixed_work": ("retired", "no fixed", "home most of the day",
                      "student", "gig", "irregular"),
}
"""How a ground-truth premise label (from the bank's ``premises``) is
recognised in the model's free-text assumption values. Deliberately
loose word matching over value NAME plus DESCRIPTION: the labels are
ours, the vocabulary is the model's."""


PREMISE_AXES: Mapping[str, Tuple[str, ...]] = {
    "composition": ("composition", "household", "size", "member", "people",
                    "person", "resident", "live", "who", "occupant",
                    "family", "partner", "roommate"),
    "work_pattern": ("work", "weekday", "presence", "schedule", "commute",
                     "office", "job", "shift", "daytime", "routine", "away",
                     "home during"),
}
"""Words an assumption's NAME or QUESTION must contain for it to count
as being about a given premise axis. A value that happens to read like
a work pattern under a household-size assumption is not a recovery of
the work-pattern premise."""


def premise_recovered(graph: Optional[AssumptionGraph],
                      premises: Mapping[str, str]) -> Dict[str, Optional[str]]:
    """For each ground-truth premise (``{"composition": "solo",
    "work_pattern": "works_away"}``), the ``assumption=value`` of the
    final graph that matches it, or None. A match needs BOTH: an
    assumption whose name or question is about that axis
    (:data:`PREMISE_AXES`), and a value of it whose name or description
    carries a synonym of the label."""
    out: Dict[str, Optional[str]] = {}
    for premise, label in premises.items():
        needles = [label.lower().replace("_", " ")] + [
            s.lower() for s in PREMISE_SYNONYMS.get(label, ())]
        axis_words = PREMISE_AXES.get(premise, (premise.replace("_", " "),))
        hit = None
        if graph is not None:
            for name, a in graph.assumptions.items():
                about = f"{name} {a.question}".lower().replace("_", " ")
                if not any(w in about for w in axis_words):
                    continue
                for value, description in a.values.items():
                    hay = f"{value} {description}".lower().replace("_", " ")
                    if any(n in hay for n in needles):
                        hit = f"{name}={value}"
                        break
                if hit:
                    break
        out[premise] = hit
    return out


def tv_distance(p: Mapping[str, float], q: Mapping[str, float]) -> float:
    """Total variation distance between two distributions over
    receptacles (missing keys are 0)."""
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


__all__ = [
    "Assumption", "AssumptionGraph", "GraphValidationError",
    "LEAF_ID_RE", "LIVE_FLOOR", "MAX_ASSUMPTIONS", "MAX_LEAVES",
    "OperationResult", "ParseResult", "apply_operations",
    "settled_assumptions", "REPAIR_OPS", "DIVERSIFY_OPS", "ALL_OPS",
    "SETTLED_WEIGHT", "AWAY_TOKENS",
    "assumption_summary", "is_graph_payload", "live_values",
    "new_leaf_id", "node_entropy", "normalized_leaf_weights",
    "parse_graph", "premise_recovered", "truncate_to_caps",
    "tv_distance", "validate_graph", "value_weight", "value_weights",
]
