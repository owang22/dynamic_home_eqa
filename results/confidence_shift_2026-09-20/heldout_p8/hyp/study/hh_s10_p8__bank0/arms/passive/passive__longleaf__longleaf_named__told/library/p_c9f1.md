# p_c9f1 — tablet_omar migrates to the bedroom desk in the early afternoon before Omar's shift

Omar works afternoon-to-night shifts (roughly 13:40–23:00 on weekdays). In the early afternoon, before he leaves, he sits at the bedroom desk (desk_b1) to check messages, plan his shift, or do a quick work session on the tablet. The patrol at 16:00 on weekdays caught the tablet at desk_b1 once out of four passes (the other three at the nightstand), and the "worst objects" section records two instances on day 6 at 16:00 where the mixture predicted the nightstand but the tablet was at the desk.

This document differs from p_f3a7, p_a3d7, p_a7f3, and p_9c2b, all of which pin the tablet to the nightstand for the entire 14–17 h or 9–17 h window and have each lost two claim points. It also differs from p_e5f6 and p_d4e9, which place the tablet at the kitchen chair in the morning. The evidence at 08:00 (nightstand x2, chair x1, dresser x1) shows the morning position is genuinely mixed, but the 16:00 desk_b1 sighting is the specific gap the nightstand-only documents miss.

The prediction: tablet_omar is at the bedroom desk on weekdays from 14:00 to 18:00 with "sometimes" probability (Omar's pre-shift desk time), and at the nightstand overnight (00:00–08:00) where it charges. On weekends the tablet stays at the nightstand through the morning.

What would refute this: if the robot finds the tablet at the nightstand on three or more consecutive 16:00 weekday passes with no desk sighting, the afternoon desk-migration is a one-off and the nightstand is the true resting spot all day.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom desk at 16:00 on a weekday during his pre-shift planning",
   "target": "tablet_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 02:00 on a weekday, charging overnight",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 10:00 on a Saturday morning before he leaves for errands",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13,
    "at": "chair_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
