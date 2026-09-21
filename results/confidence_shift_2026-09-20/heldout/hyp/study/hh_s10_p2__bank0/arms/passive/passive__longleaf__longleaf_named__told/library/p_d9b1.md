# p_d9b1 — Omar's tablet moves to the bedroom desk before his afternoon shift

Omar has started leaving his tablet at desk_b1 rather than the nightstand before he heads out to his afternoon-to-night shift. The recent patrol passes show tablet_omar at desk_b1 ten times since the last call (e.g. day 6 16:00), where the mixture had predicted nightstand_b1. The cumulative sightings still show nightstand_b1 as the most common spot (3× at 14:00, 3× at 16:00), but the desk_b1 sightings (1× at 14:00, 1× at 16:00 in the aggregate, 10× recently) indicate a shift in habit: Omar sets the tablet on the desk where he does his evening gaming and study, and it stays there while he is at work from roughly 13:30 to 23:00.

This document differs from p_a3d7, p_3d7e, and p_5f4b (all of which place the tablet at nightstand_b1 during the 12–16 h and 19–22 h weekday windows) by putting it at desk_b1 in the 13–22 h weekday window. The morning break (10:00, kitchen_table_k1) and the overnight rest (nightstand_b1, 0–10 h) are retained from the parent documents.

Refutation: if the robot finds tablet_omar at nightstand_b1 at both the 14:00 and 16:00 passes on three consecutive weekdays, the desk pattern has reverted.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom desk during his work shift on weekdays (he left it there before going out)",
   "target": "tablet_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 13,
   "to": 17
  },
  {
   "claim": "Omar's tablet is at the bedroom desk during his evening gaming on weekdays (he picks it up from the desk, not the nightstand)",
   "target": "tablet_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Omar's tablet is at the kitchen table during his 10:00 morning coffee on weekdays",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9.5,
   "to": 10.5
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
    "from": 9.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "dresser_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
