# v1 runs (2026-09-21 15:30-19:10) — weekday-only timestamps, superseded
Prompts rendered sightings as "Fri 10:40" (no day index), so over 32 days the model could not tell which week a
sighting came from (it wrote "the 10:40 sighting is in the future relative to the current time" on day 18).
Kept as a record; all reported numbers come from the dated-prompt runs one level up. Findings that held here and
should be re-checked there: naive buffer learns 37->85, breaks to 53 on day 14, re-learns slowly (63% sick-stage
vs 78% for the 3-day-half-life counter), no return drop; told helps in the spell (+7) and hurts on the return (-6)
because the sick messages read as still current; free-form nightly notes never learn (58 | 62 | 54).
