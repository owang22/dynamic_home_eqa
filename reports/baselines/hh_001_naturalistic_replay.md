# Off-policy belief replay

Run: `smoke_results/baselines_hh001_naturalistic`. Cell = full-state belief accuracy of the
column's belief model on the observation stream the row's agent
generated (tour + scripted sightings + that agent's senses).
Columns separate belief quality from data; rows separate data
quality from belief.

| stream from \ belief | last_observation | most_frequent | timetable |
|---|---|---|---|
| LastObservation+FixedSchedule(k=6.0h,n_rot=4) | 0.703 | 0.745 | 0.736 |
| LastObservation+NeverSense | 0.693 | 0.692 | 0.691 |
| LastObservation+SequentialSearch | 0.720 | 0.723 | 0.726 |
| MostFrequentLocation+FixedSchedule(k=6.0h,n_rot=4) | 0.703 | 0.745 | 0.736 |
| MostFrequentLocation+NeverSense | 0.693 | 0.692 | 0.691 |
| MostFrequentLocation+SequentialSearch | 0.644 | 0.670 | 0.667 |
| TimetableLookup(bin=1h,days=all)+FixedSchedule(k=6.0h,n_rot=4) | 0.703 | 0.745 | 0.736 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 0.693 | 0.692 | 0.691 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 0.704 | 0.712 | 0.707 |

Column spread at fixed row = belief-model differences on identical
data. Row spread at fixed column = data-collection differences
under an identical belief.
