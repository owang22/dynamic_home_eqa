# p_7e4c — Home-based couple; object_14 parked at storage shelf during work day (fork of p_b2d9)

This fork corrects the object_14 prediction. The parent p_b2d9 placed object_14 at the shared desk (receptacle_12) for weekday 08:00–18:00, but the claim has now accumulated 3-against / 0-for since the last call (7 against, 2 for total). The per-object data confirms: object_14 was found at receptacle_12 on only 4 of 7 sighted days and has 5 distinct receptacles, meaning it is frequently elsewhere. The "weekday 9-17h looks at receptacle_12" tally shows 2 found / 5 empty—object_14 is not reliably at the desk during the work stretch.

The revised model: object_14 (a reference notebook or project binder) is pulled from the desk in the morning and parked at the storage shelf (receptacle_19) during the active work hours 09:00–17:00 on weekdays. It returns to the desk in the evening for review. Everything else in the parent's model is unchanged: object_4 on the kitchen shelf, object_15 and object_16 on the counter, object_2 and object_35 at the entryway, bathroom items at receptacle_6, bedroom items at receptacle_8. Nothing leaves the house.

What changed from p_b2d9: object_14's weekday block now targets receptacle_19 instead of receptacle_12, and the window narrows to 09:00–17:00. What would refute this fork: object_14 found at receptacle_12 during weekday 10:00–16:00 on two or more occasions.

```json
{
 "claims": [
  {
   "claim": "object_4 (kitchen item) is stored on the kitchen shelf (receptacle_18), not the counter, all day",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_15 (kitchen item) is on the active counter (receptacle_4) during weekday work hours",
   "target": "object_15",
   "expect": "receptacle_4",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_14 (desk item) is parked at the storage shelf (receptacle_19) during weekday work hours, not at the desk",
   "target": "object_14",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_2 (keys) is always in the house because both residents work from home",
   "target": "object_2",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "object_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_35": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_3": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_7",
    "chance": "almost_always"
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
  "object_11": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_18",
    "chance": "usually"
   }
  ],
  "object_15": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_4",
    "chance": "usually"
   }
  ],
  "object_16": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_4",
    "chance": "usually"
   }
  ],
  "object_14": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "sometimes"
   }
  ],
  "object_24": [
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
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
  "object_17": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_8",
    "chance": "almost_always"
   }
  ]
 }
}
```
