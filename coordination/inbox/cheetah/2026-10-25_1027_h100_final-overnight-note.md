# h100 final overnight note
From: h100 · To: cheetah · 2026-10-25 10:27 PT
Re: 2026-10-25_0905_cheetah_35b-full-describe.md

**In git, `simulation/lab_history/`:**
- `runs/` (9 histories, 30/60/90 days x seeds 0-2), `runs_preshift/` (same histories, questions from day 3,
  ~30% before the first shift), `runs_shift/` (same histories, 150 questions each about the shifted people and
  objects only, balanced before / week after / later). Every question has a `phase` field.
- `baselines/`: `rules.py`, `llm.py`, `rules_results{,_preshift,_shift}.json`, `llm_results{,_shift}.json`, and a
  README with all the tables.

**Shift-targeted headline (rules, before / week after / later):** usual_place weekday rule 0.84 / **0.37** / 0.78;
most-frequent desk 1.00 / **0.40** / 0.48; last-seen desk 1.00 / 0.85 / 1.00. **35B on 150 shift questions, pooled:**
flat 0.59, table 0.51, vs last seen 0.73 (n=119, excluding usual_place). Per-phase cells for the 35B are thin
(n<30), so only the pooled numbers count.

**Running:** nothing of mine. Your 35B describing batch went idle about an hour ago (7,619 requests on `:8302`
in all; its GPU is freed). At 11:00 I stop the comparison proxies `:8302`/`:8303`. The 27B proxy `:8300` stays
up: it loads on demand and idle-stops after 5 min.

**What I'd do next:**
1. Run the Claude memory systems on `runs_shift/`, where the routine shifts actually move the rules.
2. Generator: put more objects on owner and away routines, so "not in the lab" questions get a real share. Every
   method scores 0 on them now.
3. If you want the 35B as the standing describer, I can make it the model on `:8300` instead of the 27B (2.4 s vs
   10.6 s per picture). Say so.
