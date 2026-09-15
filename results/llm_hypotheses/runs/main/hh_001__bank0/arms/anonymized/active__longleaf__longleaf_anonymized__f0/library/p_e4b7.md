# p_e4b7 — Bedroom appliance; object_11 lives at the bedroom shelf, not the kitchen

This document is a targeted revision of the kitchen-shelf model. The dominant documents (p_b2d9, p_a7e3) place object_11 on the kitchen storage shelf (receptacle_18) alongside object_4, but the mixture's worst-object list shows object_11 was predicted at receptacle_18 and actually found at receptacle_13 on two occasions (day 2, 05:00). The per-object data confirms: object_11 is "mostly receptacle_18 (1/2 sighted days; 2 receptacles; 5 sightings)" and the weekday 9–17h looks at receptacle_18 found it 0 times and found nothing 2 times. This strongly suggests object_11 does not belong on the kitchen shelf.

The revised model: object_11 is a small personal appliance (a hair dryer, a compact iron, or a bedside humidifier) that lives on the bedroom shelf at receptacle_13, near object_18 and object_25 (other personal items). It is used in the morning or evening and returned to receptacle_13. The kitchen shelf (receptacle_18) holds only object_4. Everything else follows the standard home-based couple routine: object_15 and object_16 on the counter, the desk items at receptacle_12 in the morning, nothing leaves the house.

What sets this apart: object_11 at receptacle_13 instead of receptacle_18. What would refute it: object_11 found at receptacle_18 during 08:00–18:00 on any day, or object_11 found at receptacle_4 (the counter).

```json
{
 "claims": [
  {
   "claim": "object_11 (personal appliance) is at the bedroom shelf (receptacle_13), not the kitchen shelf, during the day",
   "target": "object_11",
   "expect": "receptacle_13",
   "days": "both",
   "from": 8,
   "to": 20
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
   "claim": "object_15 (kitchen item) is on the active counter (receptacle_4) during the day",
   "target": "object_15",
   "expect": "receptacle_4",
   "days": "both",
   "from": 7,
   "to": 21
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
    "from": 0,
    "to": 24,
    "at": "receptacle_13",
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
  ],
  "object_18": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_13",
    "chance": "almost_always"
   }
  ]
 }
}
```
