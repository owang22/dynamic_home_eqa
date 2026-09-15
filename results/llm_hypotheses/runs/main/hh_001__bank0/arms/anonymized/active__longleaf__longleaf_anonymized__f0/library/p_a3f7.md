# p_a3f7 — One resident commutes; morning desk setup and afternoon parking added (fork of p_d6c3)

This fork of p_d6c3 adds three blocks that address the mixture's worst-object misses since the last call. The parent correctly identifies the commuter and the out-of-house cluster (object_6, object_7, object_11), but it says nothing about the morning and afternoon shuffles the robot has now caught:

- object_20 (a storage item, mostly at receptacle_19) was sighted at receptacle_12 (the desk) on day 11 at 08:00, twice. The mixture predicted receptacle_19 and was wrong.
- object_16 (a kitchen item, mostly at receptacle_4) was sighted at receptacle_12 on day 11 at 07:00, three times. The mixture predicted the counter and was wrong.
- object_24 (a desk item, mostly at receptacle_12) was sighted at receptacle_19 on day 9 at 15:00, three times. The mixture predicted receptacle_21 and was wrong.

The pattern: in the early morning (07:00–09:00) the work-from-home resident sets up the desk, pulling object_20 from the storage shelf and object_16 from the kitchen counter onto the desk. In the mid-afternoon (14:00–18:00) the work session winds down and object_24 is parked at the storage shelf (receptacle_19) rather than remaining at the desk.

What changed from p_d6c3: three new target entries (object_20, object_16, object_24) with morning/afternoon override blocks. The out-of-house claims for object_6, object_7, and object_11 are unchanged—the per-object data (9/11 empty looks at receptacle_19 for object_6 and object_7 during weekday 9-17h) still strongly supports absence. The two "against" sightings on each are consistent with one or two work-from-home days per week.

What would refute this fork: object_20 or object_16 sighted at receptacle_19 or receptacle_4 respectively during weekday 07:00–09:00 on two or more occasions; object_24 sighted at receptacle_12 during weekday 14:00–18:00 on two or more occasions.

```json
{
 "claims": [
  {
   "claim": "object_7 (small tool) is out of the house with the commuting resident during weekday work hours",
   "target": "object_7",
   "expect": "receptacle_2",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_6 (storage item) is out of the house with the commuting resident during weekday work hours",
   "target": "object_6",
   "expect": "receptacle_2",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_20 (storage item) is at the shared desk (receptacle_12) during weekday early morning setup hours 7-9",
   "target": "object_20",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "object_24 (desk item) is parked at the storage shelf (receptacle_19) during weekday afternoon wind-down 14-18h",
   "target": "object_24",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "object_6 (storage item) is back at the storage shelf (receptacle_19) on weekends during the day",
   "target": "object_6",
   "expect": "receptacle_19",
   "days": "weekend",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "object_6": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_7": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_11": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_18",
    "chance": "usually"
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
  "object_35": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
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
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "receptacle_12",
    "chance": "sometimes"
   },
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_24": [
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "receptacle_19",
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
  "object_28": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ],
  "object_20": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ]
 }
}
```
