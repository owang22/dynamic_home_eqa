"""Classical belief-model arms (C-tier brief).

ONE shared Bayes filter (`filter.py`) over a factored finite-state Markov
process; arms differ ONLY in how the time-varying occupancy/rate parameters
are estimated (`rates/`, one module per arm; `oracle.py` = C5 ceiling).
Every arm is scored through the SAME code path as the LLM arms
(dynbelief.experiments.e1.score_prediction), on the same frozen banks,
observation streams, query times, and D grid.

Leakage rules (L1-L4): no arm reads the profile YAML (C5 = oracle is the sole,
explicit exception); calendar covariates (clock, day-of-week, weekend flag)
are allowed; resident-specific day-type labels are NOT (regime structure must
be inferred); hyperparameters are selected on held-out observation likelihood,
never query accuracy.
"""
