# results/llm_hypotheses — layout

One current run, one archive, and the inputs/caches the tools need. Nothing else.

```
runs/main/hh_001__bank0/         THE run that counts (hh_001, timeline seed 0, bank seed 0,
                               post-leak-fix world; every number quoted comes from here)
  README.md                    headline table, what each arm is, caveats
  figures/                     tables.md, leak_report.md, the png figures, elicitation cost
  arms/active/                 arms that matter: the robot senses (24 looks/day)
  arms/passive/                fixed patrol, no policy — secondary
  arms/anonymized/             the name-ablation condition, either protocol — tertiary
  arms/incomplete/             stopped or broken arms, kept only for their logs
archive/                       everything superseded, grouped by why it is superseded:
  leaky_runs_2026-09-13_14/    phases 0-2: prompts named the tour-unseen (= carried) objects
  pre_ownerdrift_2026-09-13/   world before owner-room drift + forgetfulness (incl. banks, tl1/tl2)
  round2_2026-09-12/           earlier round's prompt notes and arm logs
  leak_check_scrambled/        the scrambled-content control
hypotheses/<condition>/tl0_bank0_clean/   what the LLM wrote on day 0 (inputs to the arms)
logs/<condition>/tl0_bank0_clean/         the elicitation exchange (prompt, thinking, repair)
anonymization/                 token cross-reference tables for the anonymized condition
cache/                         every LLM reply, keyed by request hash (opaque; do not browse)
```

Rules that keep it this way:
- New runs land in `runs/main/<household>__bank<seed>/` with arms already grouped (`run_tour_start.py` does it).
- A superseded run moves into `archive/<reason_date>/`; never a sibling directory with a suffix.
- `preTravelFix/` at the repo root is the older archive of the pre-travel-fix world; it predates this layout.

Reading an arm: `per_question.jsonl.gz` (truth, distribution, senses per question),
`diagnostics.json` (re-ask events, graph traces, final weights; for the log reader every
decision with its reason), `provenance.json`, and for re-asking arms `revisions/` with
every LLM exchange. Log-reader arms also carry `notes/` and, when stopped early, `calls/`.
