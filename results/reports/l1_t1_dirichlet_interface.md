# L1 T1: Dirichlet pseudo-count interface for the LLM prior

**DO-NO-HARM CHECK (math-level, not yet a belief-store ablation — that's
T2): PASS.** `concentration=0` is verified, by direct test against the
real backoff function (not just at the pseudo-count layer in isolation),
to make `shrink_hierarchical_with_llm` produce results identical to
`shrink_hierarchical` (the existing, LLM-free 3-level backoff) to
floating-point precision. A concentration=0 LLM prior is mathematically
inert, not merely small. The zero-data limit is also verified exactly:
a cell with zero real events anywhere in the pool backs off to precisely
the LLM's elicited value, for any concentration greater than zero.

## What was built

**`embodied/posterior.py`: `shrink_hierarchical_with_llm`.** Extends the
existing 3-level D1 backoff (`shrink_hierarchical`: scene -> profile ->
global) with a 4th, bottom level: the global level now backs off toward
an explicit LLM `HierarchicalStat` first, instead of implicitly bottoming
out at whatever Laplace-smoothed cross-category average the pooled
statistics happened to produce. No new smoothing math — reuses the same
`_shrink` weighted-average primitive every other level already uses.
`llm.weight` IS the concentration parameter: it plays exactly the role
`prior_strength` plays at the other two backoff steps, just localized to
the one step where the LLM prior enters.

**`llm_prior/pseudo_counts.py`: L0-to-D1 plumbing.**
`elicited_distribution_to_pseudo_counts` scales a normalized elicited
distribution by a chosen concentration into Dirichlet pseudo-counts
(`alpha_i = concentration * p_i`); `to_hierarchical_stat` reads one
state's pseudo-count back out as a `HierarchicalStat` ready to plug into
`shrink_hierarchical_with_llm`; `elicited_pseudo_counts_from_cache` does
the full path from a committed L0 cache entry to pseudo-counts in one
call. No new elicitation modes, no new model calls — parsing is done by
`llm_prior.scoring.parse_location_distribution_from_cache`, factored out
of `llm_prior/report.py`'s own scoring pass (previously a private,
report-only function) so T1 and L0's scoring read the identical parse of
the identical cached response, not two copies that could drift apart.

## Verified properties (unit tests, `tests/test_transition_kernel.py` +
`tests/test_llm_prior_pseudo_counts.py`)

| property | test | result |
|---|---|---|
| pseudo-counts normalize (sum to concentration) | `test_pseudo_counts_sum_to_concentration` | pass |
| unnormalized input distributions are normalized first | `test_normalizes_an_unnormalized_input_distribution` | pass |
| concentration=0 -> all-zero pseudo-counts | `test_concentration_zero_gives_all_zero_pseudo_counts` | pass |
| concentration=0 -> backoff identical to LLM-free 3-level (do-no-harm floor) | `test_zero_concentration_is_the_do_no_harm_floor`, `test_plugs_directly_into_shrink_hierarchical_with_llm_do_no_harm_floor` | pass |
| zero real data -> backoff equals LLM value exactly, any concentration>0 | `test_zero_global_weight_falls_back_exactly_to_llm_value`, `test_zero_global_weight_limit_holds_at_any_positive_concentration`, `test_plugs_directly_into_zero_data_limit` | pass |
| higher concentration monotonically pulls result toward the LLM value | `test_higher_concentration_pulls_the_backed_off_value_closer_to_llm` | pass |
| abundant real data resists even a high-concentration LLM prior | `test_strong_global_weight_stays_close_to_its_own_value_regardless_of_llm` | pass |
| fully degenerate input (no data, no prior) fails loudly | `test_both_global_and_llm_weight_zero_raises_rather_than_silently_guessing` | pass (raises `ZeroDivisionError`) |
| reading a real committed L0 cache entry produces a valid, correctly-scaled result | `test_reads_real_committed_cache_and_scales_correctly` | pass |
| a missing/bad cache entry raises `ParseFailure`, not a silent default | `test_raises_parse_failure_on_bad_prompt_hash` | pass |

19 new tests total (7 in `test_transition_kernel.py`, 12 in
`test_llm_prior_pseudo_counts.py`), all passing; 525 project-wide.

## What this does not yet do

This is the interface only — no belief store, gate script, or policy
reads `shrink_hierarchical_with_llm` or `llm_prior/pseudo_counts.py` yet.
T2 wires this into the actual D1 fitting path and runs the first
belief-store-level do-no-harm ablation (strong cells unchanged within
noise) plus the cold-cell comparison against uniform. Choosing a real
operating-point concentration is also T2's job, not this one — every test
here uses illustrative concentration values (10, 20, 50, ...) to exercise
the math, not a value validated against real held-out accuracy.

**Traceability:** pure Python and math, no code_hash/fingerprint
dependency of its own (the cache-reading test uses whatever
`l0_manifest_qwen.json`/`llm_prior_cache/` currently hold, traced back to
L0's own `code_hash`/`prompt_version` in that manifest). Reproduce:
`python -m pytest tests/test_transition_kernel.py tests/
test_llm_prior_pseudo_counts.py`.
