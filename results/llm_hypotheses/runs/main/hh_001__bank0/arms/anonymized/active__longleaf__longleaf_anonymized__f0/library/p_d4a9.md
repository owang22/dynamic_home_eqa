# p_d4a9 — Evening reorganization at 21:00; objects shift to night storage

The worst-objects list since the last call shows a cluster of sightings at 22:00 and 00:00 where objects are at locations different from their daytime homes: object_14 and object_17 at receptacle_15 (day 2, 22:00); object_19 and object_21 at receptacle_8 (day 2, 22:00); object_15 at receptacle_19 (day 2, 22:00); object_23 and object_25 at receptacle_21 (day 2, 22:00); object_12 and object_32 at receptacle_22 (day 3, 00:00); object_10 at receptacle_17 (day 3, 00:00). This is not random: it is a deliberate evening tidy-up. Around 21:00, the residents put away the day's work materials. Desk items (object_14, object_17, object_19) go to a secondary shelf at receptacle_15 or the bedroom at receptacle_8. The counter item object_15 gets shelved at receptacle_19. The storage-shelf items (object_12, object_23, object_25, object_10) get redistributed to receptacle_21, receptacle_22, and receptacle_17 for the night.

By 06:00 the next morning, everything is back at its daytime location. The weekday 09:00–17:00 window is unaffected: objects are where the standard home-based couple model puts them. This document only modifies the 21:00–06:00 overnight window.

What sets this apart: it is the only document that predicts objects at receptacle_15, receptacle_21, receptacle_22, and receptacle_17 during 21:00–06:00. What would refute it: object_14 found at receptacle_12 (not receptacle_15) during 22:00–23:00 on a weekday, or object_15 found at receptacle_4 (not receptacle_19) during 22:00–23:00.

```json
{
 "claims": [
  {
   "claim": "object_14 (desk item) is at the secondary shelf (receptacle_15) during the evening after 21:00 on weekdays",
   "target": "object_14",
   "expect": "receptacle_15",
   "days": "weekday",
   "from": 21,
   "to": 24
  },
  {
   "claim": "object_15 (kitchen item) is shelved at the storage unit (receptacle_19) during the evening after 21:00",
   "target": "object_15",
   "expect": "receptacle_19",
   "days": "both",
   "from": 21,
   "to": 24
  },
  {
   "claim": "object_17 (desk item) is at the secondary shelf (receptacle_15) during the evening after 21:00 on weekdays",
   "target": "object_17",
   "expect": "receptacle_15",
   "days": "weekday",
   "from": 21,
   "to": 24
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
  "object_14": [
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "receptacle_15",
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
  "object_15": [
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
  "object_17": [
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "receptacle_15",
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
  "object_19": [
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "receptacle_8",
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
  "object_21": [
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "receptacle_8",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_15",
    "chance": "usually"
   }
  ],
  "object_23": [
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "receptacle_21",
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
  "object_25": [
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "receptacle_21",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_13",
    "chance": "usually"
   }
  ],
  "object_12": [
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "receptacle_22",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
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
  ]
 }
}
```
