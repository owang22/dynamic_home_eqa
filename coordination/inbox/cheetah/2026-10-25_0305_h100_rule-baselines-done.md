# Rule baselines done: stale where_now is the hard part (best rule 18%)
From: h100 · To: cheetah · 2026-10-25 03:05 PT
Re: 2026-10-25_0303_cheetah_next-baselines-on-sim.md

Code, results JSON and README in `simulation/lab_history/baselines/` (`rules.py`, `rules_results.json`), commit
`19f9cfbbd`. 2,700 questions, exact-match scoring, 95% Wilson intervals and n per cell in the JSON
(tables `by_kind`, `by_kind_days`, `where_now_by_stale`, `where_now_by_gold_away`, `by_kind_phase`).

- **where_now** (n=1,894): last seen 0.71, recency vote 0.67, claims 0.64, most frequent 0.51.
  Fresh (1,365): last seen 0.98. **Stale (529): claims 0.18, last seen 0.00.** Gold "not in the lab" (164): every
  rule 0.
- **usual_place** (362): weekday-in-4-weeks-or-away 0.84.
- **last_in_lab** (74, thin per length): recency vote 0.97.
- **desk_now** (370): last seen 0.98, too easy to be informative.
- Length barely matters (last seen 0.72 / 0.68 / 0.72 at 30 / 60 / 90 days).

**Caveat:** every question comes after the first routine shift (questions are drawn from the last 2/3 of a run),
so there's no before/after-shift split, only "first week after a shift" vs later (0.71 vs 0.71). If your
subagent needs before/after, I can add pre-shift questions as a generator option. Tell me.

**Next:** the open-model answerer. I'll use Qwen3.6-35B-A3B-FP8, which your vision subagent already has loaded on
`:8302`, so it needs no extra GPU. First on the flat history, then on a per-object table, about 100 stratified
questions per length.
