# p_d6a3 — Marco's glasses: desk in the morning, nightstand at night

Marco keeps his reading glasses at the nightstand overnight, but in the morning he takes them to the desk where he journals and reads. The 00:00 and 08:00 weekday patrols show a split between nightstand and desk (2 at nightstand, 1 at desk, 1 at bed), consistent with the glasses being in transition. By 16:00 they've moved to the coffee table or bathroom (he's done with the desk). The worst-objects list flags "predicted nightstand_b1, actually desk_b1" twice since the last call, confirming the desk is the active morning spot. This document predicts desk_b1 for glasses_marco during the 06:00–10:00 weekday window. If the robot consistently finds the glasses at the nightstand during that window, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "Marco's glasses are at the desk during his morning journaling",
   "target": "glasses_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 6,
   "to": 10
  },
  {
   "claim": "Marco's glasses are at the nightstand in the evening",
   "target": "glasses_marco",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 18,
   "to": 23
  },
  {
   "claim": "Marco's glasses are at the nightstand on the weekend morning",
   "target": "glasses_marco",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 6,
   "to": 12
  }
 ],
 "targets": {
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 10,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
