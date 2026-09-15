# p_9b2d — Object_21 moved to storage shelf; object_28 stays in living room (fork of p_c2e8)

This fork corrects the object_28 prediction while keeping the object_21 relocation. The parent p_c2e8 claimed both object_28 and object_21 were swapped: object_28 to the desk (receptacle_12) and object_21 to the storage shelf (receptacle_19). The object_21 claim held (0.51 on 24 sightings) and the worst-objects list confirms object_21 was found at receptacle_19 three times recently (day 8 07:00, day 8 06:00). However, the object_28 claim has failed badly: 2-for / 9-against. The per-object data shows object_28 is at receptacle_10 (living room) on 6 of 9 sighted days, and weekday 9-17h looks at receptacle_10 found it 4 times versus 2 empty. Object_28 never left the living room.

The revised model: only object_21 moved (from desk to storage shelf, perhaps a project item completed and shelved). Object_28 remains in the living room (receptacle_10) as a decorative or leisure item. The rest of the house follows the standard home-based couple routine: object_4 on the kitchen shelf, object_15 and object_16 on the counter, object_2 and object_35 at the entryway. Nothing leaves the house.

What changed from p_c2e8: object_28's target is receptacle_10 (living room) instead of receptacle_12 (desk); the object_28 claim now expects receptacle_10. What would refute this fork: object_28 found at receptacle_12 during weekday 09:00–17:00 on two or more occasions.

```json
{
 "claims": [
  {
   "claim": "object_28 (living room item) remains in the living room (receptacle_10) during weekday work hours",
   "target": "object_28",
   "expect": "receptacle_10",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_21 (desk item) is now at the storage shelf (receptacle_19) during weekday work hours",
   "target": "object_21",
   "expect": "receptacle_19",
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_17": [
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
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
  "object_21": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_5": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_6": [
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_9": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_12": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_23": [
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
