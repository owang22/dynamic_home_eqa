# p_5e7c — Retired couple; object_3 is a mobile personal item parked at receptacle_20 during the weekday day

Two retired adults are home all day. Most objects in this house are fixed, but object_3 (class_3, a personal item) is the exception: it is a small bag or pouch that one resident carries from room to room. In the early morning (06:00–09:00) it hangs at the entryway hook (receptacle_11) while the resident gets ready for the day. From 09:00 through 17:00 on weekdays it is parked at the secondary shelf or hook in the living room (receptacle_20), within reach while the resident reads or works at the desk. In the evening (17:00–22:00) it returns to receptacle_11. On weekends the pattern is looser; object_3 lingers at receptacle_11 for most of the day.

The rest of the household matches the retired-couple baseline: keys (object_2) and object_35 are always at receptacle_11; bathroom items (object_13, object_27, object_31) are fixed at receptacle_6; the kitchen shelf (receptacle_18) holds object_4 and object_11 during waking hours; the counter (receptacle_4) holds object_15 and object_16. Nothing leaves the house.

What sets this apart: object_3 is at receptacle_20 during weekday 09:00–17:00, not at receptacle_11. The parent documents either do not specify object_3 or assume it stays at the entryway. What would refute it: object_3 sighted at receptacle_11 on a weekday between 10:00 and 16:00, or object_3 not found at receptacle_20 on multiple weekday afternoons.

```json
{
 "claims": [
  {
   "claim": "object_3 (personal item) is at the secondary living-room shelf (receptacle_20) during weekday work hours, not at the entryway",
   "target": "object_3",
   "expect": "receptacle_20",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_3 (personal item) is at the entryway (receptacle_11) during the early morning 6-9",
   "target": "object_3",
   "expect": "receptacle_11",
   "days": "both",
   "from": 6,
   "to": 9
  },
  {
   "claim": "object_2 (keys) is always in the house at the entryway because the retired couple rarely goes far",
   "target": "object_2",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "object_13 (bathroom item) is at the bathroom sink at all hours",
   "target": "object_13",
   "expect": "receptacle_6",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "object_3": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_20",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "receptacle_11",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 22,
    "at": "receptacle_11",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 17,
    "at": "receptacle_11",
    "chance": "sometimes"
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
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
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
  ]
 }
}
```
