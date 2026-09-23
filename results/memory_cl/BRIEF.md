# Brief: memory and continual learning in a shifting household

You are taking over a new strand of an ongoing project. Read this whole file before touching anything.

## The setting

A home robot answers "where is X?" while people are using things. It sees one patrol round at 03:00,
and ten minutes after every question it is told the true location — clean, ground-truth feedback, every
time. Ten simulated households run an ordinary routine for two weeks; then one resident is off sick for
ten days and their things move (desk → couch, coffee table); then eight days back to normal.
Everything is frozen and reproducible: `configs/frozen_regime_2026-09-21_person.yaml`.

Belief models under test: timetable counters at several forgetting rates, Perpetua* (survival-time
model), and five language-model memories (recency buffer, retrieval, nightly routine table, reflection,
long-context) on a local vLLM Qwen3.8-27B. Never spend money on a hosted API.

## What is already established (do not re-derive)

1. Everything learns the stationary routine well (~80%) and breaks at the shift.
2. **The counters re-learn the new routine inside the spell (+31 points); the language memories barely
   move (+10).** Ten days of daily ground-truth correction teach them little.
3. **One sentence — "she is home sick today" — is worth more than that entire week of corrections**:
   +6.3 points the same day, +14.6 by the next, sustained +12 to +17.
4. **A stale sentence costs.** All four told arms sit below their untold twins a week after the return.
5. **The never-forgets counter is the only method the return does not hurt** (+2.6 where the adaptive
   ones lose 24-34). Plasticity buys the new regime and costs the old one.
6. **Retrieval inherits the failure mode of its index**: it correlates with the never-forgets counter at
   +0.90 because it retrieves same-time-of-day sightings across all history. Choosing the retrieval key
   is choosing which disruption you will fail on.
7. Uncertainty: no method's confidence is usable at the shift; declining only pays for Perpetua*, whose
   confidence tracks the AGE of its evidence rather than the regularity of the past.

The unifying claim: **none of these memories represents how long what it knows stays true** — neither a
sighting nor a sentence carries a validity window.

## Your question

Why does clean, daily, ground-truth feedback fail to teach a language memory a new routine?

First measurement, which needs no GPU and may already be running when you start — check with the
coordinator before duplicating it: on the saved logs, separate **retention** from **generalisation**.
After the robot is told where an object actually was, (a) is it right about THAT object at THAT hour the
next day, and (b) is it right about a DIFFERENT object moved by the same regime change? If retention is
high and generalisation near zero, "feedback taught it nothing" becomes "it memorises corrections and
never infers the rule" — a much sharper claim, and one that says what to build.

Then, in rough priority:
- Does the answer differ by memory kind? The buffer should retain and not generalise by construction;
  reflection writes itself notes, so it is the one that COULD generalise. Does it?
- Does generalisation appear at all with more feedback, or is it flat in the amount of feedback?
- Is the failure at write time or read time — does the memory contain the corrections and fail to
  retrieve them, or never record them? For retrieval and the buffer you can check the prompt directly.

## How to work here

- **Ownership.** You own `results/memory_cl/` and nothing else. `dynamic-home-eqa-0a` owns the story page,
  the figures and the long-context extension run; `dynamic-home-eqa-5a` owns the workshop draft. Do not
  write outside your directory, and never edit `src/situation_sim/` beyond config knobs.
- **The server is shared.** Check what is running before launching anything; long-context prompts are
  prefill-heavy and starve everything else. Announce before you take more than three streams.
- **Sanity-check every run in its first minute.** Emit an output assay when an arm finishes — answer
  distribution, share of identical consecutive outputs, share on any single option, per-letter histogram
  for choice formats, share of mass on a catch-all option. A degenerate arm has cost this project a
  night's GPU time twice. A suspiciously constant metric is a bug until proven otherwise.
- **Statistics.** Report a per-household paired difference with its standard error and n, never a pooled
  figure that mixes household sets. Call an effect detected at twice its standard error; below six
  households use the stricter "bigger than the spread" bar and say which you used. Where several arms
  move the same way and none clears alone, the unanimity is the finding.
- **Write predictions before runs land**, in `results/memory_cl/EXPECTATIONS.md`, and record whether they
  held. Three predictions were refuted this way today and each refutation was worth more than the guess.
- **Numbers in prose drift.** Compute them from the data, or check them against it before writing.

Report to the coordinator (`dynamic-home-eqa-37`) rather than acting alone on anything that changes a
claim, and say what you measured before saying what it means.
