# p_5e1c — Omar's glasses follow a morning path: nightstand, bathroom, desk

Omar's reading glasses (glasses_omar) trace a clear weekday morning path visible in the patrol data. They rest at nightstand_b1 overnight (sighted there at 03:00), move to bathroom_shelf_ba1 around 07:00 (sighted there twice at 07:00, consistent with a morning grooming or shaving routine), and then go to desk_o1 for the workday (sighted there at 18:00, presumably returned after work ends or left there in the evening). Marco's glasses (glasses_marco) follow a simpler pattern: they are at desk_b1 during the day (sighted at 03:00 and 09:00) and move to nightstand_b1 in the evening (sighted there at 18:00).

This document is distinct from the existing "class:glasses at nightstand_b1" blocks that held up in several documents, because it captures the intra-day movement (bathroom at 7, desk at work) rather than just the overnight resting spot. It explains why the mixture's worst-object list shows glasses_omar predicted at desk_o1 but actually at nightstand_b1 (03:00) and at bathroom_shelf_ba1 (07:00).

What would refute it: a weekday look at bathroom_shelf_ba1 around 07:00 that does not find Omar's glasses, or a sighting of glasses_omar at a fourth receptacle.

```json
{
 "claims": [
  {
   "claim": "Omar's glasses are on the bathroom shelf during his weekday morning routine",
   "target": "glasses_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Omar's glasses are at his desk during weekday work hours",
   "target": "glasses_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's glasses are at his desk during weekday work hours",
   "target": "glasses_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
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
    "from": 7,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
