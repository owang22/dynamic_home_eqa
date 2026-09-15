"""The tree arm's mixture: :class:`~baselines.beliefs.
llm_hypothesis_mixture.LLMHypothesisMixture` over the nodes of a
:class:`~baselines.llm_hypotheses.hypothesis_tree.HypothesisTree`.

Every node — root or child — is one particle holding its materialized
body; the mixture is flat over nodes and the weights are keyed on
``node_id``, so a revision (which only ADDS nodes) leaves every existing
particle's weight untouched and a new node enters at the mean log weight
after a full replay of the evidence log (the parent's ``_rebuild``).

What differs from the graph mixture:

* the file holds ``{"nodes": [...]}``; revisions arrive as a
  :class:`~baselines.llm_hypotheses.hypothesis_tree.TreeOperationResult`
  from an elicitor ``(report, tree, context) -> result``;
* pruning has two rules — a NODE whose weight sits under the floor for
  ``leaf_prune_days`` days is removed and its children re-parented with
  its delta folded in (their bodies unchanged); a SUBTREE whose summed
  weight sits under the floor for as long is removed whole. Never below
  :data:`~baselines.beliefs.llm_hypothesis_mixture.MIN_LEAVES_AFTER_PRUNE`
  nodes;
* the triggers are the scheduled day, the anomaly bucket and prediction
  quality, in that order, with one call type; the uncovered-bank trigger
  is off (``ReaskConfig.new_class_triggers=False`` from the driver);
* the report carries the tree (per node: parent, labels, weight, subtree
  weight, check history), the settled labels and the label weights;
* the policy hook is :meth:`label_distributions`: per label, the weight
  share of nodes carrying it and the predictive distributions of the
  nodes with and without it.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from baselines.beliefs.llm_hypothesis_mixture import (
    MIN_LEAVES_AFTER_PRUNE, LLMHypothesisMixture)
from baselines.llm_hypotheses.hypothesis_tree import (
    SETTLED_LABEL_WEIGHT, HypothesisTree, is_tree_payload, label_weights,
    normalized_node_weights, settled_labels, subtree_weights)
from baselines.types import DAY_SECONDS


class TreeHypothesisMixture(LLMHypothesisMixture):
    """Particles = tree nodes. See the module docstring."""

    def __init__(self, *args, **kwargs) -> None:
        self._tree: Optional[HypothesisTree] = None
        self._subtree_below_since: Dict[str, int] = {}
        self.reparent_log: List[Dict[str, Any]] = []
        self._tree_trace: Dict[int, Dict[str, Any]] = {}
        super().__init__(*args, **kwargs)

    @property
    def name(self) -> str:
        return self._label or f"TreeHypothesisMixture({self._dir.name})"

    def _load_payload(self, payload: Any) -> List[dict]:
        if not is_tree_payload(payload):
            raise ValueError(f"{self.name}: the household file is not a "
                             f"tree (no `nodes` list)")
        self._graph = None
        self._tree = HypothesisTree.from_json(payload)
        return self._tree.bodies()

    def reset(self, context) -> None:
        super().reset(context)
        self._subtree_below_since = {}
        self.reparent_log = []
        self._tree_trace = {}

    @property
    def has_structure(self) -> bool:
        return self._tree is not None

    @property
    def tree(self) -> Optional[HypothesisTree]:
        return self._tree

    # ------------------------------------------------------------- trace

    def update(self, evidence) -> None:
        super().update(evidence)
        if self._tree is None:
            return
        day = evidence.t // DAY_SECONDS
        weights = self.leaf_weights
        norm = normalized_node_weights(self._tree, weights)
        sub = subtree_weights(self._tree, weights)
        self._tree_trace[day] = {
            "n_nodes": len(self._tree.nodes),
            "max_depth": self._tree.max_depth(),
            "nodes": {i: {"weight": round(norm[i], 4),
                          "subtree": round(sub[i], 4),
                          "depth": self._tree.depth(i)}
                      for i in self._tree.node_ids()},
            "labels": {l: round(w, 4) for l, w in
                       label_weights(self._tree, weights).items()}}

    # ---------------------------------------------------------- revision

    def _apply_revision(self, report: Dict[str, Any], t: int, trigger: str,
                        event: Dict[str, Any]) -> bool:
        assert self._elicitor is not None and self._tree is not None
        result = self._elicitor(report, self._tree, self._context)
        tree = getattr(result, "tree", None)
        applied = list(getattr(result, "applied", []))
        changed = tree is not None and bool(applied)
        stamp = {"t": t, "day": t // DAY_SECONDS, "trigger": trigger,
                 "call_index": self.calls_made}
        if changed:
            self._tree = tree
            self._rebuild(self._tree.bodies())
            for op in applied:
                key = self._particle_key({"node_id": op["node_id"]})
                weight = self.leaf_weights.get(key)
                self.edit_log.append({**stamp, **op,
                                      "weight_at_creation": weight})
        event["problems"] = list(getattr(result, "problems", []))
        event["operations"] = len(getattr(result, "operations", []))
        rejected = list(getattr(result, "rejected", []))
        self.rejected_ops += [{**stamp, **r} for r in rejected]
        event["rejected"] = len(rejected)
        event["call_type"] = "revise"
        if trigger == "anomaly":
            event["anomaly_key"] = report.get("anomaly_firing")
        event["n_nodes_after"] = len(self._tree.nodes)
        return changed

    # ------------------------------------------------------------ pruning

    def _prune(self, t: int) -> None:
        """Subtree rule first, then node rule (module docstring)."""
        if self._tree is None or self._leaf_prune_days <= 0:
            return
        day = t // DAY_SECONDS
        weights = self.leaf_weights
        sub = subtree_weights(self._tree, weights)
        floor = self._leaf_weight_floor
        # The floor is on the MIXTURE weight (as for graph leaves); the
        # subtree sum is compared on the same scale.
        total_hyp = sum(weights.values())
        mixture_sub = {i: s * total_hyp for i, s in sub.items()}
        for node_id in self._tree.node_ids():
            if mixture_sub[node_id] < floor:
                self._subtree_below_since.setdefault(node_id, day)
            else:
                self._subtree_below_since.pop(node_id, None)
            if weights.get(node_id, 0.0) < floor:
                self._below_since.setdefault(node_id, day)
            else:
                self._below_since.pop(node_id, None)
        pruned: set = set()

        def live() -> int:
            return len(self._tree.nodes)

        # Subtrees, lowest summed weight first.
        ripe = [i for i, since in self._subtree_below_since.items()
                if day - since >= self._leaf_prune_days and self._tree.has(i)]
        for node_id in sorted(ripe, key=lambda i: mixture_sub[i]):
            if not self._tree.has(node_id):
                continue        # inside a subtree already removed
            ids = self._tree.subtree_ids(node_id)
            if live() - len(ids) < MIN_LEAVES_AFTER_PRUNE:
                continue
            removed = self._tree.remove_subtree(node_id)
            for i in removed:
                self.prune_log.append({
                    "t": t, "day": day, "leaf_id": i, "node_id": i,
                    "kind": "subtree", "root_of_subtree": node_id,
                    "weight": weights.get(i, 0.0),
                    "subtree_weight": mixture_sub[node_id],
                    "below_since_day": self._subtree_below_since.get(node_id)})
                pruned.add(i)
                self._subtree_below_since.pop(i, None)
        # Single nodes, lowest weight first; children re-parented.
        ripe = [i for i, since in self._below_since.items()
                if day - since >= self._leaf_prune_days and self._tree.has(i)]
        for node_id in sorted(ripe, key=lambda i: weights.get(i, 0.0)):
            if live() <= MIN_LEAVES_AFTER_PRUNE:
                break
            rows = self._tree.remove_node(node_id)
            self.prune_log.append({
                "t": t, "day": day, "leaf_id": node_id, "node_id": node_id,
                "kind": "node", "weight": weights.get(node_id, 0.0),
                "children_reparented": [r["child"] for r in rows],
                "below_since_day": self._below_since.get(node_id)})
            self.reparent_log += [{"t": t, "day": day, "removed": node_id, **r}
                                  for r in rows]
            pruned.add(node_id)
            self._subtree_below_since.pop(node_id, None)
        if not pruned:
            return
        self._remove_hypothesis_particles(pruned)
        # Re-parented children keep their materialized bodies, so their
        # particles and weights stand; the raw bodies are refreshed so
        # the node_id -> body map matches the tree.
        bodies = {b["node_id"]: b for b in self._tree.bodies()}
        self._raw_hypotheses = [dict(bodies[self._particle_key(h)])
                                for h in self._raw_hypotheses]

    # ------------------------------------------------------------- report

    def revision_report(self, t: int) -> Dict[str, Any]:
        from baselines.llm_hypotheses.prompt import per_object_statistics
        report = super().revision_report(t)
        if self._tree is None:
            return report
        weights = self.leaf_weights
        norm = normalized_node_weights(self._tree, weights)
        sub = subtree_weights(self._tree, weights)
        history: Dict[str, List[Dict[str, Any]]] = {}
        for row in self.check_outcomes:
            history.setdefault(row["leaf_id"], []).append(
                {"day": row["day"], "in_favour": row["in_favour"]})
        nodes = []
        for node in self._tree.nodes:
            i = node["node_id"]
            nodes.append({
                "node_id": i, "parent": node.get("parent"),
                "labels": list(node.get("labels", ())),
                "depth": self._tree.depth(i),
                "weight": norm[i], "subtree_weight": sub[i],
                "check_history": history.get(i, []),
                "rationale": str(node.get("rationale", "")),
                "distinguishing_check": node.get("distinguishing_check")})
        table = report["known_objects"]
        sightings = [(row["t"], row["object"], row["actual"])
                     for row in self._sighting_log]
        # Affirmative wording throughout (the prompt hygiene test greps
        # the rendered text for negations).
        report["uncovered_objects"] = [
            {**u, "summary": u["summary"].replace("never sighted",
                                                  "0 sightings so far")}
            for u in report["uncovered_objects"]]
        report.update({
            "tree_nodes": nodes,
            "label_weights": label_weights(self._tree, weights),
            "settled_labels": self.settled_labels,
            "settled_floor": (self._reask.settled_weight if self._reask
                              else SETTLED_LABEL_WEIGHT),
            "statistics": per_object_statistics(
                sorted(table), sightings, t,
                unsighted_label="0 sightings so far")})
        return report

    @property
    def settled_labels(self) -> Dict[str, float]:
        if self._tree is None:
            return {}
        floor = self._reask.settled_weight if self._reask else SETTLED_LABEL_WEIGHT
        return settled_labels(self._tree, self.leaf_weights, floor)

    # ------------------------------------------------------------- policy

    def label_distributions(self, object_id: str, t: int
                            ) -> Dict[str, Tuple[float, Dict[str, float],
                                                 Dict[str, float]]]:
        """For the policy: per label with weight strictly between 0 and
        1, ``(share, distribution of the nodes WITH the label,
        distribution of the nodes WITHOUT it)`` for ``object_id`` at
        ``t``. Node distributions are read once; nothing is perturbed."""
        if self._tree is None:
            return {}
        n_hyp = len(self._raw_hypotheses)
        dists = self.particle_distributions(object_id, t)[:n_hyp]
        weights = self.leaf_weights
        norm = normalized_node_weights(self._tree, weights)
        by_node = {self._particle_key(raw): d
                   for raw, d in zip(self._raw_hypotheses, dists)}
        out: Dict[str, Tuple[float, Dict[str, float], Dict[str, float]]] = {}
        for label in self._tree.all_labels():
            with_: Dict[str, float] = {}
            without: Dict[str, float] = {}
            share = 0.0
            for node in self._tree.nodes:
                i = node["node_id"]
                w = norm[i]
                bucket = with_ if label in node.get("labels", ()) else without
                if label in node.get("labels", ()):
                    share += w
                for rec, p in by_node.get(i, {}).items():
                    bucket[rec] = bucket.get(rec, 0.0) + w * p
            if share <= 0.0 or share >= 1.0:
                continue
            with_ = {r: p / share for r, p in with_.items()}
            without = {r: p / (1.0 - share) for r, p in without.items()}
            out[label] = (share, with_, without)
        return out

    # -------------------------------------------------------- diagnostics

    def tree_diagnostics(self) -> Dict[str, Any]:
        return {
            "is_tree": self._tree is not None,
            "tree_trace": {str(d): v for d, v in
                           sorted(self._tree_trace.items())},
            "edit_log": list(self.edit_log),
            "prune_log": list(self.prune_log),
            "reparent_log": list(self.reparent_log),
            "rejected_ops": list(self.rejected_ops),
            "check_outcomes": list(self.check_outcomes),
            "bucket_trace": list(self.bucket_trace),
            "weight_spread": self.weight_spread(),
            "settled_labels": self.settled_labels,
            "label_weights": (label_weights(self._tree, self.leaf_weights)
                              if self._tree else {}),
            "final_tree": self._tree.to_json() if self._tree else None,
            "leaf_weight_floor": self._leaf_weight_floor,
            "leaf_prune_days": self._leaf_prune_days}


__all__ = ["TreeHypothesisMixture"]
