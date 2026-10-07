# v2 runs (2026-09-21 19:04-19:32) — dated timestamps but weekday names shown; superseded
The F1 calendar runs the weekday routine on every day (bank day_kinds all "weekday"), yet these prompts named
Saturdays/Sundays and the resident cards described a weekend routine, so the LLM reasoned "it is Saturday, she
sleeps in" on days 5-6, 12-13, 19-20, 26-27 (cold-question accuracy dipped 20-25 points on those days for the LLM arms
only). Fixed in llm.py by FLAT_WEEK (no weekday names, cards without the weekend sentence, messages dated "Day 19:").
Partial results kept for reference (naive through day ~17 on s3-s5; routine/routine7/summary through day ~5-9).
Observation that motivated the cold/warm split: on sick day 1 the buffer LLM is wrong on the FIRST question about
each object and right on the later ones by recency ("the most recent sighting at 09:05 today places the book at the
coffee table"). Cold = first question about an object that day.
