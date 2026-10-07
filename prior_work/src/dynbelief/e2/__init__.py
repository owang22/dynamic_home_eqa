"""E2 — one-shot LLM-elicited prior: help vs harm.

Does a one-shot LLM prior help where the population prior fits (typical) and
hurt where it does not (atypical)? Arms share the identical filter + rate
family; only the PRIOR differs:
  P0    uninformative (== the C-arm as run)
  Pllm  LLM-elicited prior (elicit.py; gpt-5.4-mini / gpt-5.5 only, never Claude)
  Porc  oracle-parameter prior (machinery control; must help everywhere)

Injection is MAP regularization / pseudo-observations toward the elicited
parameters with equivalent-sample-size kappa in {1, 7, 28} days (inject.py) —
never initialization-only (one day of real data would overwrite it).
"""
