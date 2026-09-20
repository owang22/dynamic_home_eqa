# Open questions and assumptions

## Things that look wrong or surprising and were not resolved

1. **Weekends are the easy days, not the hard ones.** Pooled over 20 households, every classical agent is
   *more* accurate on Saturday/Sunday than on weekdays, and abstains less. The reason is in the truth mix:
   OUT_OF_HOUSE truths are 11-13% of questions on weekdays and 1-2% on weekends (people leave the house with
   their things on workdays), and every classical agent gets OUT_OF_HOUSE wrong (0-9%, Markov1 34% by coin
   flip). So the "weekend shift" that the brief expects to show up as a drop shows up as a rise. The routine
   shift the generator produces (guests, illness, weekend schedules) moves objects between in-house spots, and
   a 4-hourly patrol sees those moves before they are asked about. The per-truth-type tables in the report
   are the honest view; a curve that only looks at in-house spot truths is flat at ~89% for everyone.

2. **No learning curve for the classical agents.** Wednesday to Friday is flat (79-80% at 4 h patrol, look
   off). At this patrol density every belief's answer is dominated by the last sighting: a spot seen 4 h ago
   is not refuted by anything, and the base pipeline's negative-evidence half-life (24 h) barely suppresses
   a spot seen empty 1-4 h ago (factor 0.03-0.11) — but it suppresses every other spot by the same factor, so
   the last-seen spot still wins. Belief differences reach the answer (LastObservation and Markov1 disagree on
   19 of 224 seed-0 questions; traced one by hand, see problems_found.md), but they are small: the week of
   history is not long enough for frequency or timetable statistics to outvote a fresh sighting. I did not
   change any belief; that would be tuning.

3. **The 95% ceiling is exceeded by construction, not by a leak.** With a look at the belief's top room
   ("look top"), LastObservation reaches 96-98% on weekend days: residents are home, objects stay in the
   house, and a look at the last-seen room confirms. The look reads only the chosen room's contents at the
   question instant, through the same `Episode.receptacle_contents` the harness uses for paid senses; the
   ON_PERSON pseudo-room is excluded (problems_found.md #2). I checked for leaks in the prompts (leak_check,
   0 hits) and by reading the runner; I found none.

4. **The one-step VoI look is nearly useless for a confident belief** (problems_found.md #3): it finds the
   object in ~50% of looks vs 87% for a look at the top room. This is the rule the brief specified; I report
   both.

5. **The LLM (Qwen3.8-27B, no thinking) almost never asks for the look** (about 5% of questions) and states
   0.95 confidence on nearly everything, including questions where a full patrol just found the object in
   no room. Its accuracy is at the level of last-seen. It also fails OUT_OF_HOUSE questions (1-3 of 18 on
   seed 0) although the prompt says "full patrol, not found in any room". I did not tune the prompt beyond
   fixing the two presentation bugs in problems_found.md; a stronger model or thinking mode would be the next
   thing to try.

6. **Told vs not told is nearly identical on seed 0** (192 vs 192, 188 vs 189 right). The message is in the
   prompt (verified: 224/224 told prompts carry it from the shift day's first question, 0/224 not-told
   prompts do). The model does not use it. Pooled numbers over more households are in the report.

7. **Routine-summary notes get truncated.** The notes prompt asks for at most 350 words, the model often
   writes more, and max_tokens = 900 cuts some notes mid-list (seed 0: 3 of 8 notes so far hit the cap).
   The head (residents, main objects) survives. Left as is to keep prompts identical across households.

8. **Perpetua / Perpetua\*** are the only slow agents (~450 s per hourly bank vs seconds for the others),
   never abstain (top probability always high), and score 4-6 points under last-seen. They were run in a
   second pass; if the 1 h / 2 h banks are missing for them in the tables, that pass had not finished.

## Underspecified in the brief, and what I assumed

- **Patrol schedule:** one pass at every multiple of `patrol_hours` after the walkthrough (00:00, 04:00, ...
  for 4 h), all rooms listed at the same instant. Night passes are included; they are mostly uninformative
  but keep the schedule regular.
- **Walkthrough:** Tuesday 18:00, as `initial_tour` sightings plus a `room_visit` per room carrying only
  the empty spots (the existing convention), so the walkthrough's exclusions reach the beliefs.
- **"Observation rows with source scripted":** the bank uses the loader's `room_visit` rows (which the loader
  turns into one scripted sense result per spot, with residents present), because a full listing needs the
  empties, and a plain `observation` row cannot carry emptiness.
- **Questions:** 32 per scored day, object uniform over non-fixture objects, minute uniform in 07:00-23:00,
  seeded by `patrol_questions:<seed>`. Fixtures (lamp, doormat, ...) are excluded as "not movable".
- **Abstain for classical agents** is applied at summary time from the logged top probability (it changes
  nothing downstream), so one run serves all three thresholds. The LLM's confidence-threshold route is
  treated the same way; its outright ABSTAIN answers are a separate column.
- **Score:** right +1, wrong -1, abstain 0, reported as "mean score" per agent; per-day scores are in the
  per-day tables as abstain rate and answered accuracy.
- **Shift days:** Saturday, Sunday, plus scored days with a `guest_visit` or `sick_day` event (the
  generator's other events — rain, laundry, late work, grocery delivery — are not "major"). Day 0 (Tuesday,
  the walkthrough day) is never a shift day because it is not scored. At the current event rates 17 of 20
  households have a major event on a scored day, so the rates were **not** raised.
- **Hint messages:** one dated sentence per shift day, written from the event type (never the internal cause
  name): "It's the weekend, so we're off our usual routine and around the house more." / "We have friends
  coming over this evening." / "<Name> is home sick today." Several sentences are joined when a day has
  several. The told arm sees every message dated on or before the current day.
- **Resident intro card:** name, an age band drawn from the role (students early twenties, retired
  sixties/seventies, workers late twenties to early fifties; the generator has no ages), occupation from the
  role, one weekday and one weekend sentence from the role's schedule template, hobbies, and who looks after
  the pet. Bedroom is in the card data but not printed.
- **ON_PERSON (with resident):** the LLM may answer `ON_PERSON:<name>`; the name is recorded
  (`on_person_resident`) and the answer is scored as ON_PERSON. Classical agents answer plain ON_PERSON.
- **Room-level answer:** not asked for. The brief's schema list ("ranked locations, confidence, and if a look
  is taken, the room. Nothing else.") leaves no field for it, so nothing is recorded.
- **Look for the LLM:** two calls when a look is requested (first answer with `look_room`, then the look
  result appended and a final answer). The first answer is logged as `answer_before_look`.
- **Memory for the summary agent** also gets the compact "not found" lines for the queried object (a full
  patrol that missed it), on top of the notes and the last 3 sightings; without it the agent could not know
  the object had left since its last sighting.
- **Budget:** no hosted calls at all (local vLLM Qwen/Qwen3.8-27B on :8300); `hosted_spend.py` was not
  exercised because there was nothing to price. Token counts are logged per arm in `llm/*/stats.json` and
  `llm_stats.json`.
- **Households for the LLM:** seed 0 first, then seeds 1-9 at 4 h patrol, then a density check
  (1 h and 8 h, seeds 0-4, look on only). Whatever had finished by the morning is in the report; the run
  logs say which.
