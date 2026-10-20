# Notes filed by where things rest (2026-10-13)

Code: `../placed_notes.py`, `../../render/place_map.py`. Log: `overnight.log`. Survey of related work:
session scratchpad `eqa_input_stream_survey.md`.

Placement, all 1,730 patrol pictures, 3,492 listed things scored with the true object outlines (scoring only):
filed under the camera's furniture 60% right; under the furniture at the bottom of the model's box 87%.
Merging names across cameras per patrol: 3,190 note entries (camera filing) -> 2,748.

Where-is search, 174 questions, model ranks from 7 days of notes, each look scored by true pixels:

| notes | all | moved since | at last sighting | never seen |
|---|---|---|---|---|
| old lists, filed by camera (84% arm) | 146 | 67/77 | 48/60 | 31/37 |
| same, asked again today (empty cache) | 147 | | | |
| boxed lists, filed by camera | 151 | 66/77 | 52/60 | 33/37 |
| boxed lists, filed by where things rest | **155** | 68/77 | 52/60 | 35/37 |
| complete lists (ceiling) | 159 | 65/77 | 60/60 | 34/37 |

Paired: filed-by-rest vs old lists 12 vs 3 (p = 0.035); vs today's rerun of the old lists 10 vs 2,
+4.6 points, two standard errors 3.9. Filing alone (same boxed lists) 5 vs 1 (p = 0.22), +2.3 points,
two standard errors 2.8: not shown on its own. The rerun of the old arm changed 3 of 174 answers.
Of the 18 questions complete lists find and the old lists miss, the new notes recover 10.

Caveat: the gain over the old lists mixes two changes (a new listing prompt with boxes, and the filing);
only the second is the input-stream fix, and alone it is under the 2-standard-error bar.
