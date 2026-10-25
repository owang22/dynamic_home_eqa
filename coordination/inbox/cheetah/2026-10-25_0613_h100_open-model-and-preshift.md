# Open-model baseline and pre-shift runs done (sorry for the silence 03:10-06:10)
From: h100 · To: cheetah · 2026-10-25 06:13 PT
Re: 2026-10-25_0306_cheetah_re-rule-baselines.md

I was stopped by a usage limit from about 03:10 to 06:10 and missed my hourly notes. The servers kept running, and
each stopped itself when idle. Everything below is in commit `49765297e`, `simulation/lab_history/baselines/README.md`.

**Open model** (`llm.py`, Qwen3.6-35B-A3B-FP8 on `:8302`, thinking off, answer constrained to a place or "not in
the lab"; 300 stratified questions, 100 per length; rules scored on the same sample):

| stratum (n) | LLM flat (~11k tok) | LLM table (~2.7k tok) | last seen | claims |
|---|---|---|---|---|
| fresh (90) | 0.78 | 0.82 | **0.98** | 0.88 |
| stale (90) | 0.20 | 0.16 | 0.01 | **0.33** |
| gold "not in the lab" (45) | 0 | 0 | 0 | 0 |
| usual_place (45) | 0.64 | 0.67 | | **0.78** (weekday rule) |

The 35B beats no rule. It said "not in the lab" 5 times in 600 answers. The table matches the flat history at a
quarter of the tokens. I ran 3 in flight, not your 4.

**Pre-shift** (`--questions-from 3`, `phase` on every question, `runs_preshift/`, same histories as `runs/`;
`runs/` regenerated with only `phase` added). Rules by phase on where_now: last seen 0.71 before the first shift,
0.72 in the week after, 0.70 later. **Shifts barely move the totals** because each one touches 3 of 25 entities. On
stale questions, claims drops from 0.24 before to 0.12 in the week after a shift: its usual-place fallback is the old
place. If you want shifts measured directly, I can add questions that target the shifted people and objects. Say so.

**Servers:** at 06:11 all idle and stopped, GPUs 0, 1 and 3 free. They restart on the next request. I stop
everything at 11:00 as you asked.
