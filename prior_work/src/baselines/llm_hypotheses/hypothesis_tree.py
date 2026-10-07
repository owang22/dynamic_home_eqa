"""The hypothesis tree: refinement of hypothesis particles by labelled
children (Phase 3 of the graph arm).

The graph arm (:mod:`baselines.llm_hypotheses.assumption_graph`) crossed
named assumptions into a grid of leaves and asked the model to edit the
grid. The tree replaces the grid with REFINEMENT: every node is a full
hypothesis; a child is its parent plus a delta, carries every label of
its parent plus at least one of its own, and competes with its parent as
an ordinary particle. Nothing is ever edited in place — a revision can
only add a child under a node or add a new root — so a node's body, and
with it its mixture weight, survives every revision untouched.

Node (what the file holds; a root has ``rest``, a child has
``rest_overrides``)::

    {"node_id": "p_a41c", "parent": null | "p_xxxx",
     "labels": ["solo", "works_away"], "rationale": "...",
     "distinguishing_prediction": "...",
     "distinguishing_check": {"target", "at", "days", "hour", "if_seen"},
     "rest": {...}                     # roots only
     "rest_overrides": {...},          # children: stated-rest changes
     "activities": [...],              # root: all; child: the ones added
     "moves_changed": [{"activity": <inherited name>, "moves": [...]}]}

A node's particle is its MATERIALIZED body (:meth:`HypothesisTree.
materialize`): walk root -> node; start from the root's rest and
activities; at each child apply its ``rest_overrides``, append its
``activities``, then apply its ``moves_changed`` to the activity it
names. A ``rest_overrides`` entry changes only the stated rest, which
the converter treats as a decaying pseudo-count
(:data:`~baselines.beliefs.hypothesis_program.REST_PRIOR_COUNT`); it can
never override what the sightings say.

Parser rules, per node in file order (a node that fails is dropped with
its reason, as ``parse_graph`` does):

1. ``node_id`` is opaque ``p_`` + 4 hex; a bad or duplicate id is
   replaced and the substitution recorded.
2. ``parent`` is null or a kept node written earlier in the file.
3. ``labels`` is a non-empty list of short free-text strings naming no
   object or receptacle id; a child's label set strictly contains its
   parent's; two nodes never share a label set.
4. A root carries ``rest`` and no ``rest_overrides``; a child the other
   way round. ``moves_changed`` names an inherited activity. Activity
   names are unique along the path.
5. The materialized body passes :func:`~baselines.beliefs.
   hypothesis_program.parse_hypothesis` against the tables.

Caps: :data:`MAX_NODES` nodes; an elicitation gives :data:`MIN_ROOTS` to
:data:`MAX_ROOTS` roots and nothing else.

Operations (:func:`apply_operations`) are exactly two, ``add_child`` and
``add_root``; a response containing anything else is rejected whole and
every operation in it is listed in ``rejected``.
"""

from __future__ import annotations

import copy
import dataclasses
import re
from typing import (Any, Dict, Iterable, List, Mapping, Optional, Sequence,
                    Set, Tuple)

from baselines.beliefs.hypothesis_program import (HypothesisValidationError,
                                                  _rest_pairs,
                                                  parse_hypothesis)
from baselines.llm_hypotheses.assumption_graph import (LEAF_ID_RE,
                                                       PREMISE_SYNONYMS,
                                                       new_leaf_id)

NODE_ID_RE = LEAF_ID_RE
MAX_NODES = 12
MIN_ROOTS = 3
MAX_ROOTS = 5
SETTLED_LABEL_WEIGHT = 0.9
"""Share of the node weight at which a label counts as settled (reported
as such in the revision prompt)."""
TREE_OPS = ("add_child", "add_root")
AWAY_TOKENS = ("OUT_OF_HOUSE", "ON_PERSON")
_ID_TOKEN = re.compile(r"[A-Za-z0-9_]+")


class TreeValidationError(ValueError):
    def __init__(self, problems: Sequence[str]) -> None:
        super().__init__("; ".join(problems))
        self.problems: Tuple[str, ...] = tuple(problems)


# ------------------------------------------------------------------ tree

@dataclasses.dataclass
class HypothesisTree:
    """Nodes in file order (parents before children)."""

    nodes: List[Dict[str, Any]]

    # ---------------------------------------------------------- structure

    def node_ids(self) -> List[str]:
        return [str(n["node_id"]) for n in self.nodes]

    def node(self, node_id: str) -> Dict[str, Any]:
        for n in self.nodes:
            if n["node_id"] == node_id:
                return n
        raise KeyError(node_id)

    def has(self, node_id: str) -> bool:
        return any(n["node_id"] == node_id for n in self.nodes)

    def roots(self) -> List[Dict[str, Any]]:
        return [n for n in self.nodes if n.get("parent") is None]

    def children(self, node_id: str) -> List[Dict[str, Any]]:
        return [n for n in self.nodes if n.get("parent") == node_id]

    def path(self, node_id: str) -> List[Dict[str, Any]]:
        """Root first, ``node_id`` last."""
        out = [self.node(node_id)]
        while out[0].get("parent") is not None:
            out.insert(0, self.node(out[0]["parent"]))
        return out

    def depth(self, node_id: str) -> int:
        return len(self.path(node_id)) - 1

    def max_depth(self) -> int:
        return max((self.depth(i) for i in self.node_ids()), default=0)

    def subtree_ids(self, node_id: str) -> List[str]:
        """``node_id`` and every descendant, parents first."""
        out = [node_id]
        i = 0
        while i < len(out):
            out += [c["node_id"] for c in self.children(out[i])]
            i += 1
        return out

    def labels(self, node_id: str) -> Tuple[str, ...]:
        return tuple(str(l) for l in self.node(node_id).get("labels", ()))

    def all_labels(self) -> List[str]:
        seen: List[str] = []
        for n in self.nodes:
            for l in n.get("labels", ()):
                if l not in seen:
                    seen.append(str(l))
        return seen

    # ------------------------------------------------------ materialize

    def materialize(self, node_id: str) -> Dict[str, Any]:
        """The full hypothesis body of one node: the converter's input.
        ``hypothesis_id`` is the node id, so the particle names itself
        after the node and the mixture can key weights on it."""
        rest: Dict[str, str] = {}
        activities: List[Dict[str, Any]] = []
        for n in self.path(node_id):
            if n.get("parent") is None:
                rest = dict(_rest_pairs(n.get("rest")))
                activities = copy.deepcopy(list(n.get("activities", ())))
                continue
            rest.update(dict(_rest_pairs(n.get("rest_overrides"))))
            activities += copy.deepcopy(list(n.get("activities", ())))
            for change in n.get("moves_changed", ()) or ():
                name = str(change.get("activity", ""))
                hit = [a for a in activities if a.get("name") == name]
                if not hit:
                    raise TreeValidationError(
                        [f"node {node_id}: moves_changed names activity "
                         f"{name!r}, which no ancestor provides"])
                hit[0]["moves"] = copy.deepcopy(list(change.get("moves", ())))
        node = self.node(node_id)
        return {"hypothesis_id": node_id, "node_id": node_id,
                "labels": list(node.get("labels", ())),
                "rationale": str(node.get("rationale", "")),
                "distinguishing_prediction": str(
                    node.get("distinguishing_prediction", "")),
                "distinguishing_check": copy.deepcopy(
                    node.get("distinguishing_check")),
                "rest": rest, "activities": activities}

    def bodies(self) -> List[Dict[str, Any]]:
        return [self.materialize(i) for i in self.node_ids()]

    # ------------------------------------------------------------- edits

    def remove_node(self, node_id: str) -> List[Dict[str, Any]]:
        """Drop one node and re-parent its children so that every
        child's MATERIALIZED body is unchanged: the removed node's delta
        is folded into each child (a child of a removed root becomes a
        root holding its materialized rest and activities). Labels are
        kept as they are. Returns one row per re-parented child."""
        victim = self.node(node_id)
        parent_id = victim.get("parent")
        rows = []
        for child in self.children(node_id):
            before = self.materialize(child["node_id"])
            if parent_id is None:
                child["rest"] = before["rest"]
                child["activities"] = before["activities"]
                child.pop("rest_overrides", None)
                child.pop("moves_changed", None)
                child["parent"] = None
            else:
                child["parent"] = parent_id
                merged = dict(_rest_pairs(victim.get("rest_overrides")))
                merged.update(dict(_rest_pairs(child.get("rest_overrides"))))
                child["rest_overrides"] = merged
                child["activities"] = (
                    copy.deepcopy(list(victim.get("activities", ())))
                    + list(child.get("activities", ())))
                child["moves_changed"] = (
                    copy.deepcopy(list(victim.get("moves_changed", ()) or ()))
                    + list(child.get("moves_changed", ()) or ()))
            rows.append({"child": child["node_id"], "new_parent": parent_id,
                         "labels": list(child.get("labels", ()))})
        self.nodes = [n for n in self.nodes if n["node_id"] != node_id]
        return rows

    def remove_subtree(self, node_id: str) -> List[str]:
        ids = self.subtree_ids(node_id)
        self.nodes = [n for n in self.nodes if n["node_id"] not in ids]
        return ids

    # --------------------------------------------------------------- io

    def copy(self) -> "HypothesisTree":
        return HypothesisTree(nodes=copy.deepcopy(self.nodes))

    def to_json(self) -> Dict[str, Any]:
        return {"nodes": copy.deepcopy(self.nodes)}

    @classmethod
    def from_json(cls, payload: Mapping[str, Any]) -> "HypothesisTree":
        return cls(nodes=copy.deepcopy(list(payload.get("nodes", ()))))


def is_tree_payload(payload: Any) -> bool:
    return isinstance(payload, Mapping) and "nodes" in payload


# --------------------------------------------------------------- parsing

@dataclasses.dataclass
class TreeParseResult:
    tree: Optional[HypothesisTree]
    dropped: List[Dict[str, Any]]
    substitutions: List[Dict[str, Any]]
    problems: List[str]


def _label_list(raw: Any) -> Optional[List[str]]:
    if not isinstance(raw, (list, tuple)) or not raw:
        return None
    out = []
    for l in raw:
        s = str(l).strip()
        if not s:
            return None
        out.append(s)
    return out


def _leaked_ids(texts: Iterable[str], ids: Set[str]) -> List[str]:
    out = []
    for text in texts:
        out += [tok for tok in _ID_TOKEN.findall(str(text)) if tok in ids]
    return sorted(set(out))


def parse_tree(raw: Mapping[str, Any], object_classes: Mapping[str, str],
               receptacle_ids: Sequence[str], enforce_caps: bool = True,
               roots_only: bool = False,
               unsensable: Sequence[str] = ()) -> TreeParseResult:
    """Validate a tree payload against the household vocabulary (module
    rules 1-5, then the caps). ``roots_only`` is the elicitation's
    contract: every node a root, :data:`MIN_ROOTS`-:data:`MAX_ROOTS` of
    them."""
    problems: List[str] = []
    if not isinstance(raw, Mapping) or not isinstance(raw.get("nodes"), list):
        return TreeParseResult(None, [], [], ["payload must be an object "
                                              "with a `nodes` list"])
    ids = set(object_classes) | set(receptacle_ids)
    kept: List[Dict[str, Any]] = []
    dropped: List[Dict[str, Any]] = []
    substitutions: List[Dict[str, Any]] = []
    label_sets: Dict[Tuple[str, ...], str] = {}
    tree = HypothesisTree(nodes=kept)

    def drop(index: int, node: Any, error: str, bad: Sequence[str] = ()):
        dropped.append({"index": index, "node": node, "error": error,
                        "bad_strings": sorted(set(bad))})

    for index, node in enumerate(raw["nodes"]):
        if not isinstance(node, Mapping):
            drop(index, node, "node must be an object")
            continue
        body = copy.deepcopy(dict(node))
        given = str(body.get("node_id", body.get("leaf_id",
                                                 body.get("hypothesis_id", ""))))
        taken = {n["node_id"] for n in kept}
        if not NODE_ID_RE.match(given) or given in taken:
            assigned = new_leaf_id(taken, f"{given}|{index}|"
                                   f"{body.get('labels')}")
            substitutions.append({"index": index, "given": given,
                                  "assigned": assigned,
                                  "reason": ("duplicate" if given in taken
                                             else "not an opaque p_xxxx id")})
            body["node_id"] = assigned
        else:
            body["node_id"] = given
        for k in ("leaf_id", "hypothesis_id"):
            body.pop(k, None)
        parent = body.get("parent")
        parent = None if parent in (None, "", "null") else str(parent)
        body["parent"] = parent
        if parent is not None and parent not in taken:
            drop(index, body, f"parent {parent!r} is unknown or was dropped",
                 [parent])
            continue
        if roots_only and parent is not None:
            drop(index, body, "the installation tree holds roots only")
            continue
        labels = _label_list(body.get("labels"))
        if labels is None:
            drop(index, body, "`labels` must be a non-empty list of strings")
            continue
        leaked = _leaked_ids(labels + [body.get("rationale", "")], ids)
        if leaked:
            drop(index, body, "labels and rationale must name no object or "
                              "receptacle id", leaked)
            continue
        body["labels"] = labels
        if parent is not None:
            parent_labels = set(tree.labels(parent))
            if not parent_labels < set(labels):
                drop(index, body, f"a child's labels must contain every "
                                  f"label of its parent {parent} plus at "
                                  f"least one more")
                continue
            if "rest" in body:
                drop(index, body, "a child carries `rest_overrides`, and its "
                                  "root carries `rest`")
                continue
        else:
            if "rest_overrides" in body or "moves_changed" in body:
                drop(index, body, "a root carries `rest` and `activities`; "
                                  "`rest_overrides` and `moves_changed` "
                                  "belong to a child")
                continue
            if body.get("rest") is None:
                body["rest"] = {}
        key = tuple(sorted(labels))
        if key in label_sets:
            drop(index, body, f"same label set as node {label_sets[key]}")
            continue
        kept.append(body)
        try:
            materialized = tree.materialize(body["node_id"])
            names = [a.get("name") for a in materialized["activities"]]
            if len(names) != len(set(names)):
                raise TreeValidationError(
                    [f"activity names repeat along the path: "
                     f"{sorted(n for n in names if names.count(n) > 1)}"])
            parse_hypothesis(materialized, object_classes, receptacle_ids,
                             unsensable=unsensable)
        except HypothesisValidationError as err:
            kept.pop()
            drop(index, body, str(err), list(err.bad_strings))
            continue
        except (TreeValidationError, TypeError, ValueError, KeyError) as err:
            kept.pop()
            drop(index, body, str(err))
            continue
        label_sets[key] = body["node_id"]

    if not kept:
        problems.append("no valid nodes")
    n_roots = len(tree.roots())
    if roots_only and enforce_caps and not MIN_ROOTS <= n_roots <= MAX_ROOTS:
        problems.append(f"{n_roots} roots; the installation tree needs "
                        f"{MIN_ROOTS} to {MAX_ROOTS}")
    if enforce_caps and len(kept) > MAX_NODES:
        problems.append(f"{len(kept)} nodes exceeds the cap of {MAX_NODES}")
    return TreeParseResult(tree if not problems else None, dropped,
                           substitutions, problems)


def validate_tree(tree: HypothesisTree, object_classes: Mapping[str, str],
                  receptacle_ids: Sequence[str],
                  unsensable: Sequence[str] = ()) -> List[str]:
    """Whole-tree check after operations: every problem and every node
    the parser would drop counts."""
    result = parse_tree(tree.to_json(), object_classes, receptacle_ids,
                        unsensable=unsensable)
    problems = list(result.problems)
    for row in result.dropped:
        problems.append(f"node {row['node'].get('node_id', '?')}: "
                        f"{row['error']}"
                        + (f" {row['bad_strings']}" if row["bad_strings"]
                           else ""))
    for row in result.substitutions:
        problems.append(f"node id {row['given']!r} is not opaque")
    return problems


def truncate_roots(tree: HypothesisTree) -> Tuple[HypothesisTree, List[str]]:
    """Deterministic cut when a repaired elicitation still overshoots:
    keep the first :data:`MAX_ROOTS` roots."""
    out = tree.copy()
    roots = out.roots()
    notes: List[str] = []
    if len(roots) > MAX_ROOTS:
        cut = [r["node_id"] for r in roots[MAX_ROOTS:]]
        notes.append(f"dropped roots {cut}")
        for node_id in cut:
            out.remove_subtree(node_id)
    return out, notes


# ---------------------------------------------------------------- weights

def normalized_node_weights(tree: HypothesisTree,
                            weights: Mapping[str, float]) -> Dict[str, float]:
    """Node weights renormalized among the tree's nodes (statistical
    particles are simply absent from the map)."""
    raw = {i: max(0.0, float(weights.get(i, 0.0))) for i in tree.node_ids()}
    total = sum(raw.values())
    if total <= 0.0:
        n = len(raw) or 1
        return {i: 1.0 / n for i in raw}
    return {i: w / total for i, w in raw.items()}


def subtree_weights(tree: HypothesisTree,
                    weights: Mapping[str, float]) -> Dict[str, float]:
    norm = normalized_node_weights(tree, weights)
    return {i: sum(norm[j] for j in tree.subtree_ids(i))
            for i in tree.node_ids()}


def label_weights(tree: HypothesisTree,
                  weights: Mapping[str, float]) -> Dict[str, float]:
    """Share of the node weight carried by nodes holding each label."""
    norm = normalized_node_weights(tree, weights)
    out: Dict[str, float] = {l: 0.0 for l in tree.all_labels()}
    for n in tree.nodes:
        for l in n.get("labels", ()):
            out[str(l)] += norm[n["node_id"]]
    return out


def settled_labels(tree: HypothesisTree, weights: Mapping[str, float],
                   floor: float = SETTLED_LABEL_WEIGHT) -> Dict[str, float]:
    return {l: w for l, w in label_weights(tree, weights).items()
            if w >= floor}


# ------------------------------------------------------------ operations

@dataclasses.dataclass
class TreeOperationResult:
    """``tree`` is None when the response was rejected whole
    (``problems`` says why and ``rejected`` lists every operation with
    the reason); otherwise ``applied`` lists the new nodes."""

    tree: Optional[HypothesisTree]
    applied: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    problems: List[str] = dataclasses.field(default_factory=list)
    operations: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    rejected: List[Dict[str, Any]] = dataclasses.field(default_factory=list)


def _mapping(x: Any) -> Dict[str, Any]:
    return dict(x) if isinstance(x, Mapping) else {}


def apply_operations(tree: HypothesisTree,
                     operations: Sequence[Mapping[str, Any]],
                     object_classes: Mapping[str, str],
                     receptacle_ids: Sequence[str],
                     unsensable: Sequence[str] = ()) -> TreeOperationResult:
    """Apply a revision's operations to a copy of ``tree``.

    ``add_child``: ``{parent, labels_added, delta: {activities_added,
    moves_changed, rest_overrides}, rationale, distinguishing_check,
    distinguishing_prediction}``. The child's labels are the parent's
    plus ``labels_added`` (at least one new label); the delta must
    change something; every id in it must be in ``object_classes`` /
    ``receptacle_ids`` (the known objects, never the inventory).

    ``add_root``: ``{body}`` with ``labels, rationale,
    distinguishing_check, rest, activities``; the label set must differ
    from every existing node's.

    Any other operation, any malformed operation, a cap overshoot, or a
    result that fails :func:`validate_tree` rejects the response WHOLE:
    ``tree`` is None and ``rejected`` carries every operation with the
    reason. Nothing is ever partially applied.
    """
    result = TreeOperationResult(tree=None)
    result.operations = [dict(op) if isinstance(op, Mapping) else {"op": op}
                         for op in operations]
    problems = result.problems
    if not operations:
        problems.append("no operations")
        return result
    kinds = [str(op.get("op", "")) if isinstance(op, Mapping) else ""
             for op in operations]
    unknown = [k for k in kinds if k not in TREE_OPS]
    if unknown:
        problems.append(f"unknown operation(s) {sorted(set(unknown))}; the "
                        f"operations are add_child and add_root")
    out = tree.copy()
    if not unknown:
        for index, op in enumerate(operations):
            kind = kinds[index]
            if kind == "add_child":
                problem = _add_child(out, op, object_classes, receptacle_ids,
                                     index, result.applied, unsensable)
            else:
                problem = _add_root(out, op, index, result.applied)
            if problem:
                problems.append(f"operation {index} ({kind}): {problem}")
        if len(out.nodes) > MAX_NODES:
            problems.append(f"{len(out.nodes)} nodes exceeds the cap of "
                            f"{MAX_NODES}")
        if not problems:
            problems += validate_tree(out, object_classes, receptacle_ids,
                                      unsensable=unsensable)
    if problems:
        reason = "response rejected whole: " + "; ".join(problems)
        result.rejected = [{"index": i, "op": kinds[i],
                            "parent": (op.get("parent") if isinstance(op, Mapping)
                                       else None),
                            "reason": reason}
                           for i, op in enumerate(operations)]
        result.applied = []
        return result
    result.tree = out
    return result


def _add_child(out: HypothesisTree, op: Mapping[str, Any],
               object_classes: Mapping[str, str],
               receptacle_ids: Sequence[str], index: int,
               applied: List[Dict[str, Any]],
               unsensable: Sequence[str] = ()) -> Optional[str]:
    parent = str(op.get("parent", ""))
    if not out.has(parent):
        return f"unknown parent {parent!r}"
    added = _label_list(op.get("labels_added"))
    if added is None:
        return "`labels_added` must be a non-empty list of strings"
    parent_labels = list(out.labels(parent))
    new = [l for l in added if l not in parent_labels]
    if not new:
        return (f"labels_added {added} adds nothing to the parent's labels "
                f"{parent_labels}")
    delta = _mapping(op.get("delta"))
    activities = list(delta.get("activities_added") or ())
    changes = list(delta.get("moves_changed") or ())
    overrides = delta.get("rest_overrides") or {}
    if not (activities or changes or overrides):
        return ("`delta` is empty; give activities_added, moves_changed or "
                "rest_overrides")
    if not isinstance(overrides, (Mapping, list, tuple)):
        return "`rest_overrides` must be a map of target -> receptacle"
    check = op.get("distinguishing_check")
    if not isinstance(check, Mapping) or not check:
        return "a child needs a `distinguishing_check`"
    node_id = new_leaf_id(out.node_ids(),
                          f"child|{parent}|{sorted(parent_labels + new)}|{index}")
    node = {"node_id": node_id, "parent": parent,
            "labels": parent_labels + new,
            "rationale": str(op.get("rationale", "")),
            "distinguishing_prediction": str(
                op.get("distinguishing_prediction", "")),
            "distinguishing_check": copy.deepcopy(dict(check)),
            "rest_overrides": copy.deepcopy(overrides),
            "activities": copy.deepcopy(activities),
            "moves_changed": copy.deepcopy(changes)}
    key = tuple(sorted(node["labels"]))
    for n in out.nodes:
        if tuple(sorted(n.get("labels", ()))) == key:
            return f"same label set as node {n['node_id']}"
    out.nodes.append(node)
    try:
        body = out.materialize(node_id)
        parse_hypothesis(body, object_classes, receptacle_ids,
                         unsensable=unsensable)
    except HypothesisValidationError as err:
        out.nodes.pop()
        return f"{err}"
    except (TreeValidationError, TypeError, ValueError, KeyError) as err:
        out.nodes.pop()
        return f"{err}"
    applied.append({"op": "add_child", "node_id": node_id, "parent": parent,
                    "labels_added": new, "labels": node["labels"],
                    "activities_added": [str(a.get("name", ""))
                                         for a in activities],
                    "moves_changed": [str(c.get("activity", ""))
                                      for c in changes],
                    "rest_overrides": len(dict(_rest_pairs(overrides)))
                    if isinstance(overrides, (Mapping, list, tuple)) else 0})
    return None


def _add_root(out: HypothesisTree, op: Mapping[str, Any], index: int,
              applied: List[Dict[str, Any]]) -> Optional[str]:
    body = _mapping(op.get("body"))
    if not body:
        return "`body` is required"
    labels = _label_list(body.get("labels"))
    if labels is None:
        return "`body.labels` must be a non-empty list of strings"
    key = tuple(sorted(labels))
    for n in out.nodes:
        if tuple(sorted(n.get("labels", ()))) == key:
            return f"same label set as node {n['node_id']}"
    node_id = new_leaf_id(out.node_ids(), f"root|{key}|{index}")
    node = {"node_id": node_id, "parent": None, "labels": labels,
            "rationale": str(body.get("rationale", "")),
            "distinguishing_prediction": str(
                body.get("distinguishing_prediction", "")),
            "distinguishing_check": copy.deepcopy(
                body.get("distinguishing_check")),
            "rest": copy.deepcopy(body.get("rest") or {}),
            "activities": copy.deepcopy(list(body.get("activities") or ()))}
    out.nodes.append(node)
    applied.append({"op": "add_root", "node_id": node_id, "labels": labels,
                    "activities_added": [str(a.get("name", ""))
                                         for a in node["activities"]]})
    return None


# ------------------------------------------------------------- recovery

def label_recovered(tree: Optional[HypothesisTree],
                    weights: Mapping[str, float],
                    premises: Mapping[str, str]
                    ) -> Dict[str, Optional[Dict[str, Any]]]:
    """Name-matched recovery of the bank's premises in the tree's
    labels: for each premise, the label whose text carries a
    synonym of the label value, with the share of node weight it holds
    (None when no label matches). Labels have no question attached, so
    the axis check the graph arm applied has nothing to read; a match is
    by label text alone and is reported as such."""
    out: Dict[str, Optional[Dict[str, Any]]] = {}
    if tree is None:
        return {p: None for p in premises}
    masses = label_weights(tree, weights)
    for premise, value in premises.items():
        needles = [value.lower().replace("_", " ")] + [
            s.lower() for s in PREMISE_SYNONYMS.get(value, ())]
        hit = None
        for label in tree.all_labels():
            hay = label.lower().replace("_", " ")
            if any(n in hay for n in needles):
                hit = {"label": label, "weight": masses.get(label, 0.0)}
                break
        out[premise] = hit
    return out


__all__ = [
    "AWAY_TOKENS", "HypothesisTree", "MAX_NODES", "MAX_ROOTS", "MIN_ROOTS",
    "NODE_ID_RE", "SETTLED_LABEL_WEIGHT", "TREE_OPS", "TreeOperationResult",
    "TreeParseResult", "TreeValidationError", "apply_operations",
    "is_tree_payload", "label_recovered", "label_weights",
    "normalized_node_weights", "parse_tree", "settled_labels",
    "subtree_weights", "truncate_roots", "validate_tree",
]
