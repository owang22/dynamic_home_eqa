# p_8e2f — Project-based home; desk items stay put all weekday (fork of p_c9f2)

This fork corrects the afternoon-shelf prediction for object_14 and object_24. The parent p_c9f2 claimed these items move from the desk (receptacle_12) to the storage shelf (receptacle_19) during weekday 13:00–17:00, but both claims have accumulated 5-against / 0-for since the last call. The per-object data confirms: object_14 was found at receptacle_12 twice during weekday 9–17h looks, and object_24 was found there three times. They do not leave the desk in the afternoon.

The revised model keeps the project-based framing (two adults, flexible work-from-home) but drops the afternoon relocation. object_14 and object_24 remain at the shared desk (receptacle_12) for the full weekday working stretch 08:00–18:00. The other objects that p_c9f2 placed at receptacle_19 in the afternoon (object_5, object_20, object_7) are revised to stay at their respective home locations (receptacle_21, receptacle_21, receptacle_19) rather than cycling. The kitchen, bathroom, bedroom, and living-room routines are unchanged.

What changed from p_c9f2: object_14 and object_24 no longer move to receptacle_19 in the afternoon; object_5, object_20, object_7 lose their afternoon receptacle_19 blocks. What would refute this fork: object_14 or object_24 found at receptacle_19 during weekday 13:00–17:00.

```json
{
 "claims": [
  {
   "claim": "object_14 (desk item) stays at the desk (receptacle_12) for the full weekday working stretch 8-18h",
   "target": "object_14",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_24 (desk item) stays at the desk (receptacle_12) for the full weekday working stretch 8-18h",
   "target": "object_24",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_4 (kitchen item) is on the kitchen shelf (receptacle_18) all day, not the counter",
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
  "object_24": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
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
  "object_20": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
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
