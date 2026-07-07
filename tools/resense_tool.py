"""
ResenseTool — PARTNR PerceptionTool that spends one budget token to refresh
the WorldGraph from a running PerceptionSim instance.

Usage inside a PARTNR episode:
    tool = ResenseTool(budget=BudgetTracker(total=10), sim=perception_sim)
    fresh_wg = tool.run(region="kitchen")

The tool is intentionally thin: all budget logic (should I resense?) lives in
the LLM agent (llm_agent.py).  ResenseTool only executes the resense once the
agent has decided to do so.

Integration sketch
------------------
1. PARTNR episode loop creates a BudgetTracker with the session budget.
2. LLMAgent.act() returns Decision(kind=RESENSE).
3. Caller checks budget_tracker.can_resense() and calls tool.run(region).
4. WorldGraph returned; caller passes it to make_observation() and re-queries
   the LLM (ANSWER path).

This mirrors the two-phase design in agents/harness.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from habitat_llm.world_model.world_graph import WorldGraph


# ---------------------------------------------------------------------------
# Budget tracker (session-level pool shared across questions)
# ---------------------------------------------------------------------------

@dataclass
class BudgetTracker:
    total:   int
    _spent:  int = field(default=0, init=False)

    @property
    def remaining(self) -> int:
        return self.total - self._spent

    def can_resense(self) -> bool:
        return self._spent < self.total

    def spend(self) -> bool:
        if self.can_resense():
            self._spent += 1
            return True
        return False


# ---------------------------------------------------------------------------
# Resense tool
# ---------------------------------------------------------------------------

class ResenseTool:
    """Spend one budget token and return a fresh WorldGraph snapshot.

    In standalone mode (no PerceptionSim), ``sim=None`` and the tool simply
    returns None so the harness falls back to SceneState replay.

    Args:
        budget: Session-level BudgetTracker.
        sim:    A PerceptionSim-like object with a ``get_world_graph()`` method,
                or any object with a ``get_observations(region)`` method.
                Pass None to operate in standalone mode (no Habitat-sim).
    """

    name = "resense"
    description = (
        "Re-observe a region of the house to get a fresh WorldGraph snapshot. "
        "Costs 1 budget token from the shared session budget."
    )

    def __init__(
        self,
        budget: BudgetTracker,
        sim=None,
    ) -> None:
        self.budget = budget
        self._sim   = sim

    def run(self, region: str = "") -> Optional["WorldGraph"]:
        """Spend one budget token and return a fresh WorldGraph (or None).

        Args:
            region: Hint for which part of the house to observe (ignored in
                    simple sim implementations; used for logging / future
                    partial-observation sims).

        Returns:
            Fresh WorldGraph, or None if budget exhausted or sim unavailable.
        """
        if not self.budget.can_resense():
            return None
        self.budget.spend()
        if self._sim is None:
            return None
        return _query_sim(self._sim, region)

    @property
    def remaining_budget(self) -> int:
        return self.budget.remaining


def _query_sim(sim, region: str) -> Optional["WorldGraph"]:
    """Pull a fresh WorldGraph from the sim object.

    Tries common PARTNR PerceptionSim API shapes:
      sim.get_world_graph()            → WorldGraph
      sim.observations.world_graph     → WorldGraph
      sim.get_observations(region)     → object with .world_graph
    """
    # Prefer direct get_world_graph() (habitat_llm.perception.PerceptionSim)
    if hasattr(sim, "get_world_graph"):
        try:
            return sim.get_world_graph()
        except Exception:
            pass
    # Attribute-style access (some wrappers)
    if hasattr(sim, "observations") and hasattr(sim.observations, "world_graph"):
        return sim.observations.world_graph
    # get_observations() style (older PARTNR versions)
    if hasattr(sim, "get_observations"):
        try:
            obs = sim.get_observations(region)
            return getattr(obs, "world_graph", None)
        except Exception:
            pass
    return None


# ---------------------------------------------------------------------------
# PARTNR PerceptionTool subclass (optional, import-guarded)
# ---------------------------------------------------------------------------

def _make_partnr_tool_class():
    """Factory that creates ResenseTool as a PARTNR PerceptionTool subclass.

    Returns None if habitat_llm is not importable (standalone mode).
    """
    try:
        from habitat_llm.tools.perception_tool import PerceptionTool
    except ImportError:
        return None

    class ResensePerceptionTool(PerceptionTool):
        """PARTNR-native wrapper around ResenseTool.

        Registered as a PerceptionTool so it can be wired into PARTNR's
        tool-calling interface alongside FindObjectTool, FindRoomTool, etc.
        """

        name        = ResenseTool.name
        description = ResenseTool.description

        def __init__(self, budget: BudgetTracker, **kwargs) -> None:
            super().__init__(**kwargs)
            self._inner = ResenseTool(budget=budget, sim=None)

        def _set_sim(self, sim) -> None:
            self._inner._sim = sim

        def run(self, query: str = "", **_) -> str:
            """Execute resense and return a human-readable summary string.

            Returns the worldgraph description or a budget-exhausted message.
            """
            region = query.strip() or ""
            wg     = self._inner.run(region=region)
            if wg is None:
                if self._inner.budget.remaining == 0:
                    return "Resense failed: budget exhausted."
                return "Resense failed: perception sim unavailable."
            try:
                return wg.get_world_descr()
            except Exception:
                return f"Fresh observation acquired (budget remaining: {self._inner.budget.remaining})."

    return ResensePerceptionTool


# Expose at module level; None if habitat_llm not installed
ResensePerceptionTool = _make_partnr_tool_class()
