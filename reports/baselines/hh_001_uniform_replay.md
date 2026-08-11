# Off-policy belief replay

Run: `smoke_results/baselines_hh001_uniform`. Cell = full-state belief accuracy of the
column's belief model on the observation stream the row's agent
generated (tour + scripted sightings + that agent's senses).
Columns separate belief quality from data; rows separate data
quality from belief.

| stream from \ belief | last_observation | most_frequent | timetable |
|---|---|---|---|
| LastObservation+FixedSchedule(k=6.0h,n_rot=4) | 0.713 | 0.750 | 0.737 |
| LastObservation+NeverSense | 0.704 | 0.702 | 0.704 |
| LastObservation+SequentialSearch | 0.668 | 0.680 | 0.685 |
| MostFrequentLocation+FixedSchedule(k=6.0h,n_rot=4) | 0.713 | 0.750 | 0.737 |
| MostFrequentLocation+NeverSense | 0.704 | 0.702 | 0.704 |
| MostFrequentLocation+SequentialSearch | 0.715 | 0.716 | 0.723 |
| TimetableLookup(bin=1h,days=all)+FixedSchedule(k=6.0h,n_rot=4) | 0.713 | 0.750 | 0.737 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 0.704 | 0.702 | 0.704 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 0.723 | 0.723 | 0.733 |

Column spread at fixed row = belief-model differences on identical
data. Row spread at fixed column = data-collection differences
under an identical belief.
