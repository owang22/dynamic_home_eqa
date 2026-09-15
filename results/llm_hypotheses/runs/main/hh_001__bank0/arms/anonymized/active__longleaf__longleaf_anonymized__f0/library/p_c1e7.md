# p_c1e7 — Home-based couple; object_3 is a mobile personal item centred on the entryway (fork of p_b2d9)

This fork of p_b2d9 corrects the placement of object_3. The parent (and many other documents) put object_3 at receptacle_7, but that block failed at 0.20 on 38 sightings across p_b2d9, p_e6c1, p_a7e3, p_e4b7, p_3a7d, p_5c1b, p_d4a9, and p_7f3a. The per-object data shows object_3 is mostly at receptacle_11 (the entryway) on 10 of 26 sighted days, with 6 distinct receptacles—making it one of the most mobile objects in the house. During weekday 9–17h, looks at receptacle_11 found it only 4 of 15 times, so it is at the entryway roughly a quarter of the time during work hours. The remaining sightings are spread across 5 other receptacles, suggesting object_3 is a bag, wallet, or personal accessory that the resident carries around the house and occasionally takes out.

What changed from the parent: object_3 is moved from receptacle_7 to receptacle_11 as its base location, with "sometimes" confidence reflecting its high mobility (6 receptacles). No weekday-specific override is added because the object does not show a clear time-of-day pattern at any single location. What would refute this fork: object_3 found at receptacle_7 on 3+ separate occasions, or object_3 consistently found at a single non-entryway receptacle (other than receptacle_11) during a specific time window on 5+ occasions.

_(targets the fork left unstated are inherited from p_b2d9)_

```json
{
 "claims": [
  {
   "claim": "object_3 (personal item) is at the entryway (receptacle_11) during the evening",
   "target": "object_3",
   "expect": "receptacle_11",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "object_4 (kitchen item) is stored on the kitchen shelf (receptacle_18), not the counter, all day",
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
