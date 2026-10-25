variant | fixes (non-lost, of 30) | harms (route returned in lost window, of 15) | correct in lost window
---|---|---|---
as_logged | 0 | 0 | 15
current | 0 | 0 | 15
A_trail | 6 | 0 | 15
B_tiers | 16 | 13 | 2
C_tiers_trail | 26 | 13 | 2
C2_thinblocks_trail | 20 | 10 | 5
D_C+snap | 28 | 14 | 1
E_droplive | 27 | 13 | 2
C + lost gate (hypothetical: fallbacks/trail skipped while lost) | 26 | 0 if the lost flag fires, else 13 | -
lost-window ids: 69,70,71,72,73,74,75,76,77,78,79,80,81,82,83
C harms (ids): 69,70,72,73,74,75,76,77,78,79,80,82,83
C non-lost still failing (ids): 46,47,66,67
