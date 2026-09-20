# Problems found (in order)

Each entry: symptom, cause, what changed.

1. **Symptom:** the simulator could not produce a Tuesday-start 8-day episode; `situation.py` cycled a fixed
   five-day list (Wednesday..Sunday) with `d % 5`, so day 5 would have been "Wednesday" again.
   **Cause:** the generator was written for the 5-day human quiz.
   **Change:** `situation_sim/situation.py` gained a 7-day `WEEK` and a `day0` parameter (`weekday_of`);
   `run.py --day0 Tuesday --days 8`. The default (`Wednesday`, 5 days) is byte-identical to before
   (checked by regenerating seed 0 with and without the change).

2. **Symptom:** the free look could target the pseudo-room `person_check`: the sim header maps `ON_PERSON` to
   room `person_check`, and `EpisodeContext.sensable_receptacle_ids` includes `ON_PERSON`. In the first
   seed-0 run the VoI argmax chose `person_check` once, and a look there would have returned every object
   carried by anyone (pockets, which the protocol says are never seen).
   **Cause:** the room map from the sim is reused as the look map without filtering the answer tokens.
   **Change:** `patrol/run.py` builds the room map from spots only (`ON_PERSON`, `OUT_OF_HOUSE` excluded);
   the LLM driver does the same. Looks never touch pockets.

3. **Symptom:** the VoI look almost never looked where the belief was (LastObservation's look found the object
   in 41% of questions while a look at the argmax room finds it 87% of the time).
   **Cause:** not a bug: one-step VoI over rooms is `p(R) + max_{s not in R} p(s) - max(p)`; for a belief that
   is already 98% sure, every room's VoI is a few floor units and the room with the most spots (most floor
   mass) wins. The brief asked for argmax VoI with no threshold, so that is what `look voi` is.
   **Change:** added a second look mode `top` (look at the room holding the argmax; the room with the most
   mass when the argmax is ON_PERSON/OUT_OF_HOUSE) and ran every agent under `off`, `voi` and `top`. The report
   shows all three; the `voi` numbers are the brief's rule, `top` is the sanity comparison.

4. **Symptom (LLM prompts, read by hand):** the "spots where it was NOT" list omitted the object's own
   last-seen spot at later patrols, so a patrol that found the hook empty after the shoes left was hidden from
   the model; the list was also a 37-line dump of every spot per patrol.
   **Cause:** a filter I wrote to avoid listing the sighting spot at the sighting instant also dropped it at
   every later instant; and the exclusions were not grouped.
   **Change:** exclusions strictly after the last sighting are kept for every spot; they are printed one line
   per instant ("full patrol, not found in any room", "entry (all spots)", or single spots).

5. **Symptom (LLM prompts):** the routine-summary agent's daily notes came back as `{"notes": "..."}` JSON,
   and the day-0 movement list contained all 60 walkthrough sightings as "not seen before -> spot".
   **Cause:** the shared system prompt says "answer with JSON only"; the walkthrough instant was logged as
   movement.
   **Change:** the notes prompt has its own plain-text system line; the walkthrough instant is not a movement
   (its full listing is given to the notes prompt separately).

6. **Symptom:** same-instant exclusions were listed right next to the sighting ("Wed 04:00: entry_table_e1"
   then "Wed 04:00: every other spot"), pure noise.
   **Change:** only listings strictly later than the last sighting are shown.

7. **Symptom:** 11 of the 120 LLM arm runs at 4 h patrol had no `run_log.jsonl`; the driver logs show
   `FileNotFoundError: ... llm_cache/<hash>.tmp -> <hash>.json`.
   **Cause:** a race in the prompt cache. The told and not-told arms of one household build byte-identical
   prompts until the first shift day, so two threads asked the server the same prompt at the same time,
   both wrote `<hash>.tmp`, and the second rename failed. The exception ended that arm's thread; the driver
   then re-raised it and stopped reporting, so nothing retried.
   **Change:** the temp file carries the thread id and a failed replace is ignored (the other thread's
   identical completion is already in place); an arm failure is now reported and counted instead of aborting
   the driver. The 11 arms were rerun (`run_llm_missing.sh`), mostly as cache replays. The density check
   (1 h / 8 h banks) was already running on the old code when this was found; any arm it lost was rerun
   the same way.

8. **Symptom:** the first launch of the sweep ran 240 jobs at 20 processes and starved the vLLM server of
   CPU (load 22 on 24 cores) while Perpetua/Perpetua* took ~450 s per hourly bank each (every other belief:
   seconds).
   **Change:** the sweep was split into a fast-belief pass over everything and a Perpetua pass
   (`--beliefs ... --suffix _perpetua`, 12 workers), the finished full logs were split by belief so nothing
   was recomputed, and everything long-running was moved into a tmux session (`overnight`) with resumable
   queue scripts (`run_classical_queue.sh`, `run_llm_queue.sh`). Results are byte-identical across the
   restart (checked: rebuilt bank and rerun log compared with `cmp`; LLM arms replayed from the cache with
   `calls 0`).

9. **Symptom:** one rerun arm (hh_s5, naive, not told, look on) failed with `JSONDecodeError: Extra data`
   while reading a cache entry.
   **Cause:** the same race as #7 left one cache file with two completions concatenated (both threads wrote
   the same `.tmp` before the rename). The cache reader assumed every file is valid JSON.
   **Change:** scanned the cache (1 corrupt file of ~30k), deleted it, reran the arm. The per-thread temp
   name from #7 prevents a recurrence.
