# p_3a9f — Retired couple; object_26 reads at receptacle_20 in the weekday afternoon (fork of p_7c3e)

Two retired adults live here, home all day, waking around 07:30 and sleeping around 21:30. Almost nothing leaves the house. The objects are extremely stable except for one shift: object_26 (a reading item, class_23) is carried from the main living-room spot (receptacle_10) to the secondary reading nook (receptacle_20) once the morning is over. On weekdays the couple settles into the nook around 13:00 for their long afternoon reading, and object_26 goes with them. On weekends the routine is looser and object_26 stays at receptacle_10 for the full waking day.

**What changed from the parent:** The parent placed object_26 at receptacle_10 for the full 09:00–21:00 window on all days with "almost_always" confidence. Since the last call, four looks at receptacle_10 in that window found nothing, and the overall weekday 9–17 record is 6 found / 6 empty—far too even for "almost_always." The object's two known receptacles are receptacle_10 and receptacle_20. I have split the weekday afternoon (13–21h) to receptacle_20 and kept the weekday morning (9–13h) and all weekend hours at receptacle_10. The claim for object_26 now targets the weekday-afternoon location.

What sets this apart from p_7c3e: on weekday afternoons, object_26 is at receptacle_20, not receptacle_10. What would refute it: object_26 sighted at receptacle_10 on a weekday between 14:00 and 20:00, or object_26 not found at receptacle_20 on a weekday afternoon.

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
   "claim": "object_26 (living room item) is at the secondary reading nook (receptacle_20) during weekday afternoon reading",
   "target": "object_26",
   "expect": "receptacle_20",
   "days": "weekday",
   "from": 13,
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
    "from": 13,
    "to": 21,
    "at": "receptacle_20",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13,
    "at": "receptacle_10",
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
