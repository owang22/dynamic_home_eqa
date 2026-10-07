"""STAR-style indexed memory: an exact-match observation log with
spatial/semantic/temporal lookups (`indexed_observation_log`), prompt-text
recall tools over it (`recall_tools`), and the served-LLM glue for the
memory-loop policy (`serving`). See `policies/star_memory_loop.py` for the
policy that consumes these and `star_study.py` for the evaluation driver.
"""
