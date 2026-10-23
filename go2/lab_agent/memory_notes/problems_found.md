# Problems found (2026-10-23 overnight, memory)

- server.py `status()` (and so `--selftest`) GETs `/agent/status`. It is a GET, but tonight's rule is "never call
  /agent/*", so the selftest was run without status() tonight.
- 01:10 t1792710643153 (10-22 16:10) is a scrambled frame (decoder garbage); the chat had already noticed one. Worth a check for broken JPEG frames at index time.
- The describer names some fixed things inconsistently: the black water cooler is "water cooler"/"appliance" in
  only 9 of 19 pictures where it is plainly visible (else omitted, or "computer tower", "speaker"), the podium is
  "podium" in 5 of 21 (else "desk"/"cabinet"), the blue tape in 1 of 8. Word search and negative evidence both
  inherit this; picture embeddings do not.
- Qwen ranging: asked for all objects' distances in one list without reasons, it returns the same distance for
  every object (mode collapse under JSON schema, thinking off). Reason-first fields per object fix it.
- 2026-10-19 trail frames before 16:54: 526 of 1109 described pictures (47%) have the worse pre-fix poses.
- 01:20 server.py when(): 'YYYY-MM-DD' was always REFUSED (the ':' check ran first), so the selftest's people_seen(since='2026-10-19') failed. Fixed (formats tried first).
- Map poses on Thu 10-22 differ by up to ~3 m between passes 20 min apart (the grey-white backpack on the black
  tower: (2.85, 0.15) at 16:13, (0.27, 1.95) at 16:36). The console's map status tonight reads "placed by hand
  ... 21% fit ... unsure". Object positions from Thu inherit this; where_is shows the +- and the picture ids.
- "Covered by the field of view" is only ~45% reliable on the same day and ~10% across days (static objects are
  named in that share of covering pictures). Negative evidence therefore has to be weak; it is (MISS_LR >= 0.3,
  one count per 10-min visit). Better poses would help more than a better model.
- The describer sometimes lists 14-16 copies of a thing across the top edge of one picture (bottles, shoes).
  These become many bogus sightings. Not filtered yet (a cap per picture per kind would be easy).
- p1792710643153 / t1792710643153-style scrambled frames still get described and indexed ("black bag").
- web.py does not compute embeddings or distances for new pictures; search_memory embeds missing pictures on
  demand (fast, GPU), where_is asks Qwen for distances of at most the 8 newest unranged pictures (~25 s) and does
  the rest in a background thread. If the agent runs long without where_is calls, the backlog grows.
- server.py now keeps SigLIP on the GPU (~1.9 GB) once search_memory has run. It falls back to the CPU when less
  than 3 GB are free, and to word search if torch/open_clip fail.
