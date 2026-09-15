# p_4f8c — Home-based couple; object_14 and object_17 mobile during weekday work hours (fork of p_b2d9)

This fork of p_b2d9 addresses two blocks that have failed repeatedly. First, object_14 at the desk (receptacle_12) during weekday 8–18h has now accumulated 9 for vs 18 against, and the most recent call added 2 more against. The per-object data confirms: during weekday 9–17h, looks at receptacle_12 found object_14 only 7 of 19 times (37%). The item is at the desk on 14 of 24 sighted days overall, but it is clearly not a fixed desk-resident during weekday work hours. It is likely a shared reference book or tablet that one resident pulls to the desk in the morning, uses for an hour or two, then sets aside on a secondary surface. Second, object_17 was placed at receptacle_8 (bedroom shelf) in the parent, but that block failed at 0.10 on 46 sightings across multiple documents. The per-object data shows object_17 is mostly at receptacle_12 (14/26 days), with 9 distinct receptacles—far more mobile than the parent assumed.

What changed from the parent: (1) object_14's weekday 8–18 "almost_always" block at receptacle_12 is replaced with a "sometimes" block for weekday 9–17, acknowledging it is at the desk only about a third of the time during work hours. The base "usually" block at receptacle_12 covers weekends and weekday evenings. (2) object_17 is moved from receptacle_8 to receptacle_12 (its most common location), with a "sometimes" modifier during weekday 9–17h. (3) The object_14 claim is narrowed to weekends, where the item is more reliably at the desk. What would refute this fork: object_14 found at receptacle_12 on 5+ consecutive weekday 9–17h looks (it would be back to a fixed desk resident), or object_17 found at receptacle_8 on 3+ occasions.

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
   "claim": "object_14 (desk item) is at the shared desk (receptacle_12) on weekends during the day",
   "target": "object_14",
   "expect": "receptacle_12",
   "days": "weekend",
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
    "at": "receptacle_11",
    "chance": "sometimes"
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_12",
    "chance": "sometimes"
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
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_12",
    "chance": "sometimes"
   }
  ]
 }
}
```
