"""Intraclass correlation per activity, estimated from ATUS + CASAS.

See README.md in this package for the method, the crosswalk, the guardrails,
and the known biases. The identity:

    ATUS  (many persons x 1 day)     -> sigma2_total = between + within
    CASAS (few persons x many days)  -> sigma2_within
    ICC = 1 - sigma2_within / sigma2_total
"""
