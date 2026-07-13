"""
judge_eval — instrumentation for measuring realism-judge quality against a
human-labeled candidate set (prompting-infrastructure Phase 1).

labels  : load the human-labeled CSV, split into EVAL / EXEMPLAR (no leakage).
metrics : Spearman correlation, band separation, 4-band confusion, disagreements.
harness : score the EVAL set under a judge configuration and write a report.
"""
