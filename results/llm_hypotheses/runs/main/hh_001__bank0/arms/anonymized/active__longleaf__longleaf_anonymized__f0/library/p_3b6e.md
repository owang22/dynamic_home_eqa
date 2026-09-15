# p_3b6e — object_25 has moved to the secondary shelf (receptacle_15) during the day

The mixture has been misplacing object_25 in the midday hours. On day 13, looks at 12:00 and 14:00 found object_25 at receptacle_15 (the secondary shelf), not at receptacle_13 (the bedroom shelf) or receptacle_21 (where the statistical model places it as the modal location). The per-object data shows object_25 is mostly at receptacle_21 (10/14 sighted days, 37 sightings, 3 distinct receptacles), but during weekday 09:00–17:00 looks at receptacle_21, it was found only 3 times out of 7, meaning it is at receptacle_21 less than half the time during the work stretch.

This document proposes that object_25 has been relocated to receptacle_15 (the secondary shelf) during the waking day (08:00–20:00), with receptacle_21 as its overnight parking spot. The two day-13 sightings at receptacle_15 (12:00 and 14:00) support this. The object is likely a personal item (a notebook, a small electronic device) that the resident now keeps at the secondary shelf for easy access during the day rather than at the bedroom shelf or the receptacle_21 location.

This document is distinct from p_7c3e (which does not target object_25) and from p_e9a4 (which places object_1 at receptacle_8 during weekday afternoon but does not address object_25). It also differs from the statistical model, which defaults to receptacle_21. What would refute this document: object_25 found at receptacle_21 during 10:00–16:00 on two or more weekday occasions, or object_25 found at receptacle_13 (the bedroom shelf) during the day.

```json
{
 "claims": [
  {
   "claim": "object_25 (personal item) is at the secondary shelf (receptacle_15) during weekday midday 10-16h",
   "target": "object_25",
   "expect": "receptacle_15",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "object_25 (personal item) is at the secondary shelf (receptacle_15) during weekday afternoon 12-18h",
   "target": "object_25",
   "expect": "receptacle_15",
   "days": "weekday",
   "from": 12,
   "to": 18
  },
  {
   "claim": "object_34 (storage item) is at the secondary shelf (receptacle_21) during weekday work hours",
   "target": "object_34",
   "expect": "receptacle_21",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_4 (kitchen item) is on the kitchen shelf (receptacle_18) all day",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "object_25": [
   {
    "days": "both",
    "from": 8,
    "to": 20,
    "at": "receptacle_15",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
    "chance": "sometimes"
   }
  ],
  "object_34": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
    "chance": "usually"
   }
  ],
  "object_4": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_18",
    "chance": "almost_always"
   }
  ],
  "object_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
    "chance": "almost_always"
   }
  ]
 }
}
```
