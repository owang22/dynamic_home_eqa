# p_7a3c — Marco's laptop is on his lap; glasses on his face; notebook stays on the desk

Marco works from desk_b1, but his working posture explains the 12 empty looks at the desk during 9–17 h: the laptop sits in his lap (ON_PERSON), his glasses are on his face, and the charger is plugged into the laptop in his hands. What *does* rest on the desk surface is the notebook (8 sightings, block held at 0.98) and the pen (6 sightings, 3 confirmed during the window). After 17:00 the laptop, charger, and glasses return to desk_b1, and by 23:00 the laptop is on the bedroom floor (charging overnight). This document separates from p_a1b2 and p_a3f7, which place the laptop *on* the desk and have accumulated 10–13 "against" tallies from empty desk looks. It also refines p_7f2a, which wrongly puts the notebook ON_PERSON as well; the notebook clearly stays on the desk.

What would refute this: a look at desk_b1 during 9–17 h that finds the laptop, charger, or glasses sitting on the surface (not in a resident's hands); or a look at a resident that shows them *not* carrying the laptop while at the desk.

```json
{
 "claims": [
  {
   "claim": "Marco's laptop is in his hands while he works, not on the desk surface",
   "target": "laptop_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's charger is with the laptop in his hands during work",
   "target": "charger_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's notebook remains on the desk surface during work hours",
   "target": "notebook_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's glasses are on his face during work, not on the desk",
   "target": "glasses_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ],
  "charger_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "pen_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
