# p_de90 — p_8k2m — Marco's desk items are stowed or on-person during work; charger travels with phone

Marco and Omar both work from home at their respective desks from 9 to 5:30 on weekdays. Marco's desk (desk_b1) holds his notebook, pen, and a few small items that stay visible on the surface. However, the robot's repeated looks at desk_b1 during the 9–17 window find the laptop, charger, and glasses absent far more often than present. The most parsimonious explanation: Marco works with the laptop lid closed (driving an external display or simply having the screen face him at an angle the camera misses), his phone-and-charger pair is on his person or in a pocket while he works, and his reading glasses are on his face. The notebook and pen remain on the desktop because they are flat, open, and in the camera's line of sight.

This hypothesis differs from p_a1b2 and p_a3f7, which place laptop_marco at desk_b1 with high confidence during 9–17h and have accumulated 12–15 "against" counts. Here the laptop block is downgraded to "sometimes" (it is at the desk but often not detected), the charger is placed ON_PERSON during work hours, and the glasses are "rarely" visible at the desk. The charger's overnight and evening sightings at desk_b1 (03:00, 17:00, 18:00) and its 23:00 sighting at bedroom_floor_b1 are preserved.

This document is refuted if the robot finds charger_marco at a fixed receptacle (not ON_PERSON) during 9–17h, or if laptop_marco is consistently sighted at a location other than desk_b1 during work hours.

```json
{
 "claims": [
  {
   "claim": "Marco's charger is on his person during weekday work hours because he carries his phone",
   "target": "charger_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's laptop is at his desk in the early morning before the work day begins",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 6,
   "to": 9
  },
  {
   "claim": "Marco's notebook is on his desk during the full work window",
   "target": "notebook_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's glasses are on the nightstand in the evening after work",
   "target": "glasses_marco",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 19,
   "to": 22
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
    "at": "desk_b1",
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
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
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
    "at": "desk_b1",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
