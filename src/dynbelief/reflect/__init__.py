"""Reflective memory: an online LLM agent that curates diagnostic evidence from the
daily event stream into a persistent memory file (top-3 persona hypotheses with
probabilities + selected evidence), whose hypothesis ENTROPY gates how strongly the
LLM's belief is injected into the Bayesian (classical) model at query time."""
