# p_f4a9 — object_21 parks at the storage shelf overnight; object_20 stays put (fork of p_c2e8)

The parent (p_c2e8) captured the daytime split: object_28 at the desk, object_21 at the storage shelf. But the overnight evidence has sharpened. The mixture's worst-objects report shows object_21 predicted at receptacle_12 but actually at receptacle_19 on day 16 at 04:00, and object_20 predicted at receptacle_12 but actually at receptacle_19 on day 16 at 06:00. Meanwhile, p_c2e8's own block "object_21 at receptacle_19 held (0.55 on 54 sightings)" confirms the storage-shelf occupancy is substantial.

**What changed from the parent:** I have added an explicit overnight block (00:00–08:00) placing object_21 at receptacle_19, and a daytime block (08:00–20:00) placing it at receptacle_12. For object_20, the parent's implicit assumption that it visits the desk in the morning is contradicted: p_a3f7's claim "object_20 at receptacle_12, weekday 7-9h" has only 6 for and 14 against. I now place object_20 at receptacle_19 for the full day. object_28 remains at the desk during work hours as in the parent.

What sets this apart: between 00:00 and 08:00, object_21 is at receptacle_19, not receptacle_12. object_20 is at receptacle_19 all day, not at the desk. What would refute it: object_21 sighted at receptacle_12 during 01:00–06:00, or object_20 sighted at receptacle_12 during 07:00–12:00 on multiple days.

_(targets the fork left unstated are inherited from p_c2e8)_

```json
{
 "claims": [
  {
   "claim": "object_21 (desk item) is at the storage shelf (receptacle_19) during the overnight hours 0-8, not at the desk",
   "target": "object_21",
   "expect": "receptacle_19",
   "days": "both",
   "from": 0,
   "to": 8
  },
  {
   "claim": "object_21 (desk item) is at the shared desk (receptacle_12) during weekday work hours 9-17",
   "target": "object_21",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_20 (storage item) stays at the storage shelf (receptacle_19) all day, not at the desk",
   "target": "object_20",
   "expect": "receptacle_19",
   "days": "both",
   "from": 6,
   "to": 22
  },
  {
   "claim": "object_28 (living room item) is at the shared desk (receptacle_12) during weekday work hours",
   "target": "object_28",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
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
    "from": 8,
    "to": 20,
    "at": "receptacle_18",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
    "days": "weekday",
    "from": 8,
    "to": 20,
    "at": "receptacle_12",
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
  "object_21": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 20,
    "at": "receptacle_12",
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
  ],
  "object_20": [
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
