# p_c1f4 — Retired couple; object_26 at receptacle_20 on weekdays, receptacle_10 on weekends (fork of p_7c3e)

Two retired adults live here, home all day. Their weekday and weekend routines differ in one noticeable way: on weekdays the couple settles into the secondary reading nook (receptacle_20) for the long stretch from 09:00 to 21:00, and object_26 goes with them. On weekends they are more scattered, moving around the main living room (receptacle_10), and object_26 stays there. The weekday 9–17 record for object_26 at receptacle_10 is 6 found / 6 empty, which is consistent with the object being at receptacle_20 during those hours rather than receptacle_10.

**What changed from the parent:** The parent placed object_26 at receptacle_10 for 09:00–21:00 on both day types with "almost_always." Four recent claims went against, and the weekday 9–17 stats are a flat 50/50. I have split by day type: weekday 9–21 at receptacle_20, weekend 9–21 at receptacle_10. The chance on both is "usually" rather than "almost_always" to reflect the residual uncertainty. The claim now targets the weekday location.

What sets this apart from p_7c3e and from p_3a9f: the split is by day type, not by time of day. On a weekday, object_26 is at receptacle_20 from 09:00 onward; on a weekend it is at receptacle_10. What would refute it: object_26 at receptacle_10 on a weekday between 10:00 and 18:00, or object_26 at receptacle_20 on a weekend afternoon.

```json
{
 "claims": [
  {
   "claim": "object_2 (keys) is always in the house because the retired couple rarely goes far",
   "target": "object_2",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "object_26 (living room item) is at the secondary reading nook (receptacle_20) during weekday waking hours 9-21",
   "target": "object_26",
   "expect": "receptacle_20",
   "days": "weekday",
   "from": 9,
   "to": 21
  },
  {
   "claim": "object_4 (kitchen item) is stored on the kitchen shelf all day, not on the counter",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
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
  "object_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
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
  "object_26": [
   {
    "days": "weekday",
    "from": 9,
    "to": 21,
    "at": "receptacle_20",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
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
