"""C0 — last-observation, no dynamics. Belief = point mass on the last seen
receptacle, forever. The floor / "memory parroting" reference.

Implemented as the degenerate rate model: rate ≡ 0 (nothing ever refreshes),
occupancy = uniform (used only when there is no observation to condition on).
The shared Filter with rate 0 keeps the post-update point mass unchanged —
no bespoke prediction path (core architecture requirement)."""
from __future__ import annotations


class C0LastObs:
    name = "C0_lastobs"

    def __init__(self, candidates: list[str]):
        self.candidates = list(candidates)

    def fit(self, observation_history: list[dict]) -> None:
        pass                                       # nothing to fit

    def occupancy(self, object_id: str, receptacle_id: str, t: int) -> float:
        return 1.0 / len(self.candidates)

    def rate(self, object_id: str, receptacle_id: str, t: int) -> float:
        return 0.0

    def estimator_for(self, object_id: str) -> str:
        return "point_mass"
