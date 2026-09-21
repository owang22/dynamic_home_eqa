# p_a9d4 — Omar's glasses drift to the bedroom desk overnight

The mixture keeps predicting Omar's glasses at the nightstand, but the 03:00 passes show them at desk_b1 (1× out of 3) and the 09:00 passes show them at desk_b1 (2× out of 6). The worst-object list flags this directly: predicted nightstand_b1, actually desk_b1, 3 times (day 3, 03:00). Omar works until 23:00, so at 03:00 he is asleep; the glasses at the desk mean he left them there the evening before — perhaps reading or checking his phone at the desk before turning in. By 09:00, his pre-work morning, the glasses are split three ways: nightstand (2×), desk (2×), bathroom shelf (2×), reflecting him moving them around as he showers and gets ready. By 18:00 and 23:00 they are back at the nightstand for the night.

This document differs from the plain statistical model and from every existing hypothesis, none of which places the glasses at desk_b1. It does not compete with any document on the bathroom-shelf or nightstand resting spots; it adds the desk as a secondary overnight and morning location.

What would refute it: three or more 03:00 passes that find the glasses at the nightstand with zero at the desk, or a 09:00 pass that finds them only at the nightstand and bathroom shelf with no desk sighting.

```json
{
 "claims": [
  {
   "claim": "Omar's glasses are at the bedroom desk at 03:00 on a weekday (left there the evening before)",
   "target": "glasses_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Omar's glasses are at the bedroom desk at 09:00 on a weekday during his morning routine",
   "target": "glasses_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Omar's glasses are at the nightstand at 23:00 on a weekday (back for the night)",
   "target": "glasses_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 24
  }
 ],
 "targets": {
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 14,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 14,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 14,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
