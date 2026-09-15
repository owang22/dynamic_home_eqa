# p_c8f1 — object_19 shuttles from the storage shelf to the living room in the evening

The mixture has been misplacing object_19 in the mid-afternoon and evening. On day 11, looks at 14:00 and 18:00 found object_19 at receptacle_10 (the living room), not at receptacle_19 (the storage shelf) or receptacle_13 (the bedroom shelf) where the mixture predicted it. The per-object data shows object_19 is mostly at receptacle_19 (7/13 sighted days) but has 6 distinct receptacles and 46 sightings, indicating significant movement. During weekday 09:00–17:00 looks at receptacle_19, it was found only 4 times out of 11, meaning it is at the shelf less than half the time during the work stretch.

This document proposes a two-phase daily cycle for object_19: it is at receptacle_19 (the storage shelf) during the morning and early afternoon (07:00–14:00), then moves to receptacle_10 (the living room) for the late afternoon and evening (14:00–22:00). This matches the day-11 sightings at 14:00 and 18:00. The object is likely a reference book or decorative item that is consulted at the shelf in the morning and brought to the living room for evening reading or display.

This document is distinct from p_b8e2 (which does not target object_19) and from p_8e2f (which also does not target object_19). It also differs from p_d4a9, which places object_14 at receptacle_15 in the evening but does not address object_19. What would refute this document: object_19 found at receptacle_19 during 15:00–20:00 on two or more weekday occasions, or object_19 found at receptacle_13 (the bedroom shelf) during the evening.

```json
{
 "claims": [
  {
   "claim": "object_19 (storage item) is at the storage shelf (receptacle_19) during weekday morning 7-12h",
   "target": "object_19",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 7,
   "to": 12
  },
  {
   "claim": "object_19 (storage item) is at the living room (receptacle_10) during weekday evening 15-21h",
   "target": "object_19",
   "expect": "receptacle_10",
   "days": "weekday",
   "from": 15,
   "to": 21
  },
  {
   "claim": "object_26 (living room item) is at the living room (receptacle_10) during weekday evening 15-21h",
   "target": "object_26",
   "expect": "receptacle_10",
   "days": "weekday",
   "from": 15,
   "to": 21
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
  "object_19": [
   {
    "days": "both",
    "from": 7,
    "to": 14,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 22,
    "at": "receptacle_10",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "sometimes"
   }
  ],
  "object_26": [
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
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
