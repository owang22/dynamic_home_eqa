
## 14:24 P1 — the plain mixture martingale can never fire on a 28-day bank (found on hh_s0 sick_owner, first household)
Symptom: mart/mon agents on sick_owner hh_s0: max martingale per day 1, 1, then 0.000 for days 3-27; 0 fires although the
frozen timetable drops 100 -> 22% on day 14. Cause: a nonnegative martingale started at 1 over ~400 stationary questions
decays to ~1e-5 (its expectation is 1 but the mass sits on rare paths); a 100x rise from there needs more evidence than 5
sick days give. This is also why the previous agent's fb-bank runs never fired (0/72 shift days) — not "no cliff to
detect". Fix: the CUSUM e-detector of Shin, Ramdas, Rinaldo 2024 (each mixture grid point restarts at 1 whenever it drops
below 1; threshold 1/delta with delta 1e-3 because the guarantee is an average run length, not Ville's inequality).
Synthetic: false alarms 2/50 stationary streams of 1000 steps at 1000; mild shift (90 -> 50% accuracy) detected after a
median 21 questions (max 61). The plain martingale needed 24-237 steps on the same mild shift (threshold 100) and is kept
as `--detector mixture`. uq_synth.py extended with the cusum checks; EXPECTATIONS E3-E5 unchanged (fire day 14-15, lead
<= 2/10 households).

## 14:27 P2 — repeated questions count as repeated evidence (hand check of the hh_s0 day-19 fire)
The frozen-timetable monitor fired on day 19 (return) in hh_s0 on d19q28-q30: mug_yuki asked five times in a row during
evening_tv, minutes apart, truth sink_k1, p(truth) = 0.00 each time (the found-it feedback lands 10 min after the first
question, after all five). The detector saw five independent p-values of 0.001-0.013 for one error. Also on day 18
(rest_couch: water_bottle / mug / charger each asked 3-4 times). Fix: the detector steps only on questions that carry new
information — a repeat of the same object with no positive sighting of it since its previous question and the same truth
is logged (`dup: true`) but does not move the detector (`--no-dedupe` restores the old behaviour). The conformal agent
is left per-question, since coverage is scored per question.

## 14:38 P3 — LLM token-probability channel: the JSON-string schema makes "J) somewhere else" a tokenization artifact
First 6 rows of the day-13/14 test on sick_owner hh_s0: mcq_answer "other" with conf_token 0.00 in 4/6, while the greedy
JSON answer was right in 5/6. The cache shows why: with the letter forced to be a JSON string, Qwen's tokenizer has
merged tokens '"A' .. '"I' but not '"J'; the first token's top alternatives are '"' (-0.53) vs '"C' (-1.34) vs '"B'
(-2.09) ..., the bare quote wins greedily, and after a bare quote only J follows (-0.0). So the channel chose "somewhere
else" by tokenization, and letter_probs (first token only) read the letter mass for A-I but 0 for J. Fix: the
multiple-choice call is made without a schema ("Answer with the letter only", max_tokens 2) so the bare letter is the
first token; the first 6 rows moved to hh_s0_v1_quoted_letter_bug.jsonl; greedy and sample calls are cache hits.
