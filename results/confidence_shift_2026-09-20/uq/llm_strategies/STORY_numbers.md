# Numbers behind STORY.md — regenerated Tue 22 Sep 2026 07:32

Windows: lead = days 9-13 (settled end of the lead-up), 14-16 (first sick days), 17-23 (rest of the spell), 24-26 (first
days back), 27-31 (rest of the return). Accuracy in %, pooled over households. A window with fewer than 10 answers prints –.

## Counters on the one-person-sick population (10 households)

| method | lead 9-13 | 14-16 | 17-23 | 24-26 | 27-31 | claimed conf. lead → 14-16 |
|---|---|---|---|---|---|---|
| timetable, 3-day memory | 81 | 58 | 86 | 60 | 77 | 46 → 37 |
| timetable, never forgets | 82 | 51 | 70 | 78 | 80 | 61 → 51 |
| timetable, 1-day memory | 79 | 65 | 87 | 66 | 77 | 28 → 26 |
| most frequent, 3-day | 63 | 43 | 78 | 32 | 64 | 48 → 41 |
| hedge over memory lengths | 81 | 58 | 77 | 76 | 80 | 59 → 40 |
| 3-day timetable + change alarm | 81 | 64 | 88 | 64 | 77 | 45 → 32 |
| last seen | 47 | 57 | 57 | 50 | 51 | 98 → 98 |

## LLM memories on the one-person-sick population

| arm | done | lead 9-13 | 14-16 | 17-23 | 24-26 | 27-31 | cold 17-23 | cold 24-26 | stated conf. lead → 14-16 | lead-cal. gap 14-16 | ask% / miss% 14-16 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LLM, long-context memory · no message | finished, 1371 questions, hh 1-3 | 74 | 61 | 71 | 72 | 76 | 49 | 54 | 91 → 88 | +16 | 34 / 28 |
| LLM, long-context memory · start + end messages | finished, 1371 questions, hh 1-3 | 74 | 72 | 83 | 74 | 74 | 82 | 56 | 91 → 87 | +3 | 30 / 23 |
| LLM, long-context memory · start message | finished, 1371 questions, hh 1-3 | 74 | 72 | 83 | 60 | 67 | 82 | 37 | 91 → 87 | +3 | 30 / 23 |
| LLM, naive memory (buffer) · no message | finished, 4130 questions, hh 1-10 | 78 | 58 | 66 | 74 | 77 | 41 | 58 | 88 → 87 | +15 | 55 / 28 |
| LLM, naive memory (buffer) · start + end messages | finished, 4130 questions, hh 1-10 | 78 | 71 | 83 | 70 | 75 | 78 | 50 | 88 → 85 | +0 | 41 / 18 |
| LLM, naive memory (buffer) · start message | finished, 4130 questions, hh 1-10 | 78 | 71 | 83 | 62 | 72 | 78 | 38 | 88 → 85 | +0 | 41 / 18 |
| LLM, reflection notes · no message | finished, 4130 questions, hh 1-10 | 73 | 66 | 78 | 70 | 72 | 62 | 51 | 81 → 81 | +4 | 43 / 19 |
| LLM, reflection notes · start + end messages | finished, 2001 questions, hh 1-5 | 75 | 68 | 76 | 67 | 72 | 63 | 49 | 83 → 80 | +10 | 31 / 18 |
| LLM, reflection notes · start message | finished, 2001 questions, hh 1-5 | 75 | 68 | 76 | 69 | 71 | 63 | 52 | 83 → 80 | +10 | 31 / 18 |
| LLM, retrieval memory · no message | finished, 4130 questions, hh 1-10 | 81 | 56 | 64 | 76 | 82 | 43 | 62 | 88 → 85 | +17 | 58 / 31 |
| LLM, retrieval memory · start + end messages | finished, 4130 questions, hh 1-10 | 81 | 68 | 80 | 74 | 79 | 67 | 59 | 88 → 82 | +1 | 42 / 20 |
| LLM, retrieval memory · start message | finished, 4130 questions, hh 1-10 | 81 | 68 | 80 | 58 | 69 | 67 | 50 | 88 → 82 | +1 | 42 / 20 |
| LLM, 7-day routine notes · no message | finished, 4130 questions, hh 1-10 | 60 | 58 | 63 | 61 | 62 | 25 | 38 | 86 → 87 | +5 | 67 / 31 |
| LLM, 7-day routine notes · start + end messages | finished, 4130 questions, hh 1-10 | 60 | 62 | 68 | 62 | 63 | 37 | 38 | 86 → 83 | -2 | 62 / 22 |
| LLM, 7-day routine notes · start message | finished, 4130 questions, hh 1-10 | 60 | 62 | 68 | 55 | 58 | 37 | 27 | 86 → 83 | -2 | 62 / 22 |

## Three confidence channels + honest sets on the model's own answer (bounded day list, 3 households)

**LLM, naive memory (buffer) · no message** — 3 households, 309 questions

| day | n | accuracy | verbalized | agreement | token prob. | MCQ acc. | set coverage | set size /10 |
|---|---|---|---|---|---|---|---|---|
| 13 | 45 | 82 | 84 | 84 | 77 | 0 | 100 | 10.0 |
| 14 | 48 | 48 | 86 | 87 | 75 | 0 | 92 | 7.3 |
| 15 | 48 | 54 | 82 | 75 | 75 | 0 | 92 | 4.9 |
| 20 | 48 | 71 | 82 | 82 | 77 | 0 | 88 | 4.6 |
| 24 | 44 | 80 | 88 | 86 | 74 | 0 | 91 | 4.9 |
| 25 | 38 | 82 | 90 | 92 | 73 | 0 | 95 | 4.5 |
| 30 | 38 | 76 | 88 | 88 | 72 | 0 | 82 | 4.7 |

**LLM, retrieval memory · no message** — 3 households, 309 questions

| day | n | accuracy | verbalized | agreement | token prob. | MCQ acc. | set coverage | set size /10 |
|---|---|---|---|---|---|---|---|---|
| 13 | 45 | 80 | 86 | 91 | 76 | 0 | 100 | 10.0 |
| 14 | 48 | 50 | 85 | 93 | 75 | 0 | 92 | 7.4 |
| 15 | 48 | 40 | 84 | 91 | 75 | 0 | 94 | 4.9 |
| 20 | 48 | 75 | 85 | 85 | 76 | 0 | 88 | 4.1 |
| 24 | 44 | 84 | 87 | 88 | 74 | 0 | 89 | 4.8 |
| 25 | 38 | 84 | 86 | 88 | 73 | 0 | 95 | 4.7 |
| 30 | 38 | 71 | 87 | 90 | 72 | 0 | 84 | 4.8 |

## Shared-memory interference (one person sick, everyone's things asked; the workshop session's partial-shift arms)

| arm | households | whose things | lead 9-13 | 14-16 | 17-23 | 24-26 | 27-31 |
|---|---|---|---|---|---|---|---|
| LLM, naive memory (buffer) · no message | 6 | the sick person's | 84 | 59 | 70 | 80 | 78 |
| LLM, naive memory (buffer) · no message | 6 | everyone else's | 71 | 71 | 71 | 72 | 74 |
| LLM, naive memory (buffer) · no message | 6 | everyone else's, cold | 67 | 71 | 69 | 71 | 72 |
| LLM, naive memory (buffer) · start message | 6 | the sick person's | 84 | 76 | 86 | 74 | 77 |
| LLM, naive memory (buffer) · start message | 6 | everyone else's | 71 | 74 | 71 | 68 | 73 |
| LLM, naive memory (buffer) · start message | 6 | everyone else's, cold | 67 | 75 | 70 | 64 | 70 |
| LLM, 7-day routine notes · no message | 6 | the sick person's | 70 | 60 | 68 | 74 | 69 |
| LLM, 7-day routine notes · no message | 6 | everyone else's | 60 | 56 | 53 | 56 | 65 |
| LLM, 7-day routine notes · no message | 6 | everyone else's, cold | 48 | 48 | 44 | 44 | 55 |
| LLM, 7-day routine notes · start message | 6 | the sick person's | 70 | 68 | 73 | 66 | 66 |
| LLM, 7-day routine notes · start message | 6 | everyone else's | 60 | 57 | 52 | 55 | 61 |
| LLM, 7-day routine notes · start message | 6 | everyone else's, cold | 48 | 50 | 42 | 40 | 51 |


## Paired told-vs-untold contrasts (per household, told minus no message)

Each cell is the mean across households ± its standard error, then n = households and the sd = how much those
households disagree. Since 22 Sept 07:25 an effect is claimed when |mean| >= 2 standard errors (Oliver's rule);
below 6 households the standard error is estimated from too few numbers to trust, so those rows keep the older
"bigger than the sd" floor. ✓ = claimed under whichever bar governs that row. Note the direction of the change:
at 6 households or more, clearing 1 sd implies clearing 2 se, so the new bar only ever adds claims.

| arm | window | all questions | cold questions |
|---|---|---|---|
| LLM, long-context memory · start + end messages | 14-16 | +11.1 ± 8.0 (n=3, sd 13.9) | +25.0 ± 15.7 (n=3, sd 27.1) |
| LLM, long-context memory · start + end messages | 17-23 | **+12.2 ± 2.6 (n=3, sd 4.6)** ✓ | **+31.8 ± 4.7 (n=3, sd 8.2)** ✓ |
| LLM, long-context memory · start + end messages | 24-26 | **+1.4 ± 0.7 (n=3, sd 1.2)** ✓ | +2.6 ± 4.9 (n=3, sd 8.4) |
| LLM, long-context memory · start + end messages | 27-31 | **-1.8 ± 0.4 (n=3, sd 0.6)** ✓ | **-2.7 ± 1.4 (n=3, sd 2.4)** ✓ |
| LLM, long-context memory · start message | 14-16 | +11.1 ± 8.0 (n=3, sd 13.9) | +25.0 ± 15.7 (n=3, sd 27.1) |
| LLM, long-context memory · start message | 17-23 | **+12.2 ± 2.5 (n=3, sd 4.4)** ✓ | **+31.9 ± 4.1 (n=3, sd 7.0)** ✓ |
| LLM, long-context memory · start message | 24-26 | -9.3 ± 8.6 (n=3, sd 14.8) | -17.2 ± 12.7 (n=3, sd 22.0) |
| LLM, long-context memory · start message | 27-31 | **-8.0 ± 3.2 (n=3, sd 5.6)** ✓ | **-23.9 ± 10.3 (n=3, sd 17.8)** ✓ |
| LLM, naive memory (buffer) · start + end messages | 14-16 | **+12.9 ± 3.0 (n=10, sd 9.5)** ✓ | **+23.5 ± 4.2 (n=10, sd 13.4)** ✓ |
| LLM, naive memory (buffer) · start + end messages | 17-23 | **+16.3 ± 3.6 (n=10, sd 11.3)** ✓ | **+36.3 ± 5.9 (n=10, sd 18.8)** ✓ |
| LLM, naive memory (buffer) · start + end messages | 24-26 | -3.6 ± 2.6 (n=10, sd 8.3) | -7.0 ± 5.4 (n=10, sd 17.0) |
| LLM, naive memory (buffer) · start + end messages | 27-31 | -3.0 ± 1.8 (n=10, sd 5.7) | -2.2 ± 4.3 (n=10, sd 13.6) |
| LLM, naive memory (buffer) · start message | 14-16 | **+12.9 ± 3.0 (n=10, sd 9.5)** ✓ | **+23.5 ± 4.2 (n=10, sd 13.4)** ✓ |
| LLM, naive memory (buffer) · start message | 17-23 | **+16.3 ± 3.6 (n=10, sd 11.3)** ✓ | **+33.3 ± 4.4 (n=18, sd 18.8)** ✓ |
| LLM, naive memory (buffer) · start message | 24-26 | **-7.0 ± 2.2 (n=18, sd 9.5)** ✓ | **-12.3 ± 3.9 (n=18, sd 16.5)** ✓ |
| LLM, naive memory (buffer) · start message | 27-31 | -2.8 ± 2.2 (n=18, sd 9.5) | -4.2 ± 3.9 (n=18, sd 16.5) |
| LLM, reflection notes · start + end messages | 14-16 | +4.6 ± 4.1 (n=5, sd 9.1) | +5.2 ± 6.2 (n=5, sd 13.9) |
| LLM, reflection notes · start + end messages | 17-23 | -5.5 ± 3.7 (n=5, sd 8.3) | -7.2 ± 7.5 (n=5, sd 16.8) |
| LLM, reflection notes · start + end messages | 24-26 | -8.0 ± 5.5 (n=5, sd 12.4) | -6.6 ± 7.1 (n=5, sd 15.9) |
| LLM, reflection notes · start + end messages | 27-31 | -6.7 ± 5.0 (n=5, sd 11.2) | -14.0 ± 7.2 (n=5, sd 16.1) |
| LLM, reflection notes · start message | 14-16 | +4.6 ± 4.1 (n=5, sd 9.1) | +5.2 ± 6.2 (n=5, sd 13.9) |
| LLM, reflection notes · start message | 17-23 | -5.5 ± 3.7 (n=5, sd 8.3) | -7.2 ± 7.5 (n=5, sd 16.8) |
| LLM, reflection notes · start message | 24-26 | -4.4 ± 4.2 (n=5, sd 9.5) | -3.0 ± 5.5 (n=5, sd 12.3) |
| LLM, reflection notes · start message | 27-31 | -4.5 ± 2.6 (n=5, sd 5.8) | **-15.6 ± 6.3 (n=5, sd 14.2)** ✓ |
| LLM, retrieval memory · start + end messages | 14-16 | **+12.1 ± 5.4 (n=10, sd 17.1)** ✓ | **+12.8 ± 3.9 (n=10, sd 12.3)** ✓ |
| LLM, retrieval memory · start + end messages | 17-23 | **+15.5 ± 5.3 (n=10, sd 16.7)** ✓ | **+24.6 ± 4.6 (n=10, sd 14.5)** ✓ |
| LLM, retrieval memory · start + end messages | 24-26 | -3.1 ± 2.3 (n=10, sd 7.3) | -3.5 ± 4.3 (n=10, sd 13.5) |
| LLM, retrieval memory · start + end messages | 27-31 | -3.6 ± 2.0 (n=10, sd 6.3) | **-4.9 ± 1.7 (n=10, sd 5.5)** ✓ |
| LLM, retrieval memory · start message | 14-16 | **+12.1 ± 5.4 (n=10, sd 17.1)** ✓ | **+12.8 ± 3.9 (n=10, sd 12.3)** ✓ |
| LLM, retrieval memory · start message | 17-23 | **+15.5 ± 5.3 (n=10, sd 16.7)** ✓ | **+24.6 ± 4.6 (n=10, sd 14.5)** ✓ |
| LLM, retrieval memory · start message | 24-26 | -13.1 ± 7.0 (n=10, sd 22.2) | -11.6 ± 9.1 (n=10, sd 28.9) |
| LLM, retrieval memory · start message | 27-31 | **-11.4 ± 3.6 (n=10, sd 11.3)** ✓ | **-21.2 ± 6.0 (n=10, sd 19.1)** ✓ |
| LLM, 7-day routine notes · start + end messages | 14-16 | **+3.3 ± 1.5 (n=10, sd 4.7)** ✓ | **+10.6 ± 4.4 (n=10, sd 13.8)** ✓ |
| LLM, 7-day routine notes · start + end messages | 17-23 | +4.8 ± 2.7 (n=10, sd 8.5) | +12.1 ± 6.5 (n=10, sd 20.4) |
| LLM, 7-day routine notes · start + end messages | 24-26 | -0.4 ± 3.1 (n=10, sd 9.8) | +0.2 ± 4.0 (n=10, sd 12.7) |
| LLM, 7-day routine notes · start + end messages | 27-31 | +0.2 ± 1.9 (n=10, sd 6.1) | +2.9 ± 3.9 (n=10, sd 12.4) |
| LLM, 7-day routine notes · start message | 14-16 | **+3.3 ± 1.5 (n=10, sd 4.7)** ✓ | **+10.6 ± 4.4 (n=10, sd 13.8)** ✓ |
| LLM, 7-day routine notes · start message | 17-23 | +4.8 ± 2.7 (n=10, sd 8.5) | +12.1 ± 6.5 (n=10, sd 20.4) |
| LLM, 7-day routine notes · start message | 24-26 | -4.1 ± 3.9 (n=10, sd 12.2) | -10.6 ± 5.8 (n=10, sd 18.3) |
| LLM, 7-day routine notes · start message | 27-31 | **-3.4 ± 1.5 (n=10, sd 4.7)** ✓ | **-8.9 ± 3.6 (n=10, sd 11.5)** ✓ |
