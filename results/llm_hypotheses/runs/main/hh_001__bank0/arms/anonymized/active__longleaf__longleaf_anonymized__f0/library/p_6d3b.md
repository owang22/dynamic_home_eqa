# p_6d3b — object_18 shifts from the secondary shelf (receptacle_15) to the bedroom shelf (receptacle_13) overnight

object_18 is a personal item (class_16, shared with object_17) that occupies the secondary shelf at receptacle_15 during the waking day. The per-object data confirms: it is at receptacle_15 on 19 of 26 sighted days, and during weekday 9–17h looks at receptacle_15 found it 9 of 12 times. However, the mixture's worst-objects list for this call shows object_18 was predicted at receptacle_15 but actually found at receptacle_13 twice on day 25 at 00:00. This indicates an overnight relocation: the resident moves object_18 from the secondary shelf to the bedroom shelf (receptacle_13) as part of a bedtime routine, and brings it back in the morning. The object has only 2 distinct receptacles, consistent with a simple day/night split.

What sets this apart: no existing document models object_18's overnight shift. p_b2d9 and its forks do not include object_18 in their targets at all, so the robot falls back to raw statistics. This document explicitly models the 22:00–06:00 window at receptacle_13. What would refute it: object_18 found at receptacle_15 between 22:00 and 06:00 on 3+ occasions, or object_18 found at a third receptacle (other than 15 and 13) on 3+ occasions.

```json
{
 "claims": [
  {
   "claim": "object_18 (personal item) is at the secondary shelf (receptacle_15) during weekday work hours",
   "target": "object_18",
   "expect": "receptacle_15",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_18 (personal item) is at the bedroom shelf (receptacle_13) during the late-night hours",
   "target": "object_18",
   "expect": "receptacle_13",
   "days": "both",
   "from": 22,
   "to": 24
  },
  {
   "claim": "object_18 (personal item) is at the bedroom shelf (receptacle_13) during the early morning hours",
   "target": "object_18",
   "expect": "receptacle_13",
   "days": "both",
   "from": 0,
   "to": 6
  },
  {
   "claim": "object_18 (personal item) is at the secondary shelf (receptacle_15) on weekends during the day",
   "target": "object_18",
   "expect": "receptacle_15",
   "days": "weekend",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "object_18": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_15",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "receptacle_13",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "receptacle_13",
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
  "object_4": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_18",
    "chance": "almost_always"
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
  ]
 }
}
```
