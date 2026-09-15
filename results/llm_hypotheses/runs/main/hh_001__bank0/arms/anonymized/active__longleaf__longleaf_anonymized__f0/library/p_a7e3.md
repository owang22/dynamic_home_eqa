# p_a7e3 — Home-based couple; morning desk, afternoon shelf (fork of p_b2d9)

This is a fork of p_b2d9 that adjusts the afternoon placement of object_14. The parent document placed object_14 at the shared desk (receptacle_12) for the full 08:00–18:00 weekday window, but the recent claim tally (2 against since last call, 0 for) and the per-object statistics (found at receptacle_12 on only 1 of 2 sighted days; 2-for-2-against in the 9–17h window) indicate the item is not at the desk all afternoon. The revised model: both residents work from home in focused morning blocks (08:00–12:00), then put their materials away on the storage shelf at receptacle_19 from midday onward. The rest of the household routine is unchanged: object_4 stays on the kitchen shelf (receptacle_18) all day, object_15 and object_16 remain on the active counter (receptacle_4), nothing ever leaves the house, and the bathroom and bedroom items are static.

What changed from the parent: the object_14 block is split into a morning block (weekday 8–12 at receptacle_12) and an afternoon block (weekday 12–18 at receptacle_19). The claim is narrowed to the morning window. What would refute this fork: object_14 found at receptacle_12 during 13:00–17:00 on a weekday, or object_14 found at receptacle_19 during 08:00–11:00 on a weekday.

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
   "claim": "object_14 (desk item) is at the shared desk (receptacle_12) during weekday morning work hours only",
   "target": "object_14",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 8,
   "to": 12
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
    "from": 8,
    "to": 12,
    "at": "receptacle_12",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 12,
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
  "object_24": [
   {
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "receptacle_19",
    "chance": "sometimes"
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
