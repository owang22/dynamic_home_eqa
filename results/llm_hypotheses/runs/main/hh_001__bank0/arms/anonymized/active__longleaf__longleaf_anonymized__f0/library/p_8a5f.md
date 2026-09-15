# p_8a5f — object_32 is a mobile kitchen item; absent from the kitchen shelf during weekday work hours

object_32 (class_32) is at the kitchen shelf (receptacle_18) on 11 of 18 sighted days, but during weekday 9–17h it is NEVER found there: 0 of 14 looks at receptacle_18 found it. This is the strongest "absence" signal in the current evidence set. p_8f5c predicted it at receptacle_4 (the counter) during 9–16h, but that claim scored 0 for / 17 against, ruling out the counter as well. With 6 distinct receptacles, object_32 is a mobile item—possibly a cutting board, serving platter, or small appliance—that is used in the kitchen in the morning and evening but moved to a different room (living room, dining area, or a secondary surface) during the midday work block. The p_8f5c weekend claim (receptacle_18, 6 for / 5 against) and early-morning claim (receptacle_18, 4 for / 15 against) suggest it returns to the kitchen shelf on weekends and very early weekday mornings.

What sets this apart: no existing document models object_32's complete absence from receptacle_18 during weekday 9–17h. p_8f5c is the closest but pins it to receptacle_4, which the evidence refutes. This document leaves the weekday 9–17h location open (no specific block), allowing the robot's own sighting statistics to fill in, while anchoring the object at receptacle_18 for weekends and weekday evenings. What would refute it: object_32 found at receptacle_18 during weekday 10:00–16:00 on 3+ separate days, or object_32 consistently found at a single non-kitchen receptacle during 9–17h on 5+ occasions (which would justify a more specific block).

```json
{
 "claims": [
  {
   "claim": "object_32 (class_32 item) is at the kitchen shelf (receptacle_18) on weekends during the day",
   "target": "object_32",
   "expect": "receptacle_18",
   "days": "weekend",
   "from": 8,
   "to": 18
  },
  {
   "claim": "object_32 (class_32 item) is at the kitchen shelf (receptacle_18) during weekday evening after work",
   "target": "object_32",
   "expect": "receptacle_18",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "object_4 (kitchen item) is on the kitchen shelf (receptacle_18) all day, not the counter",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "object_32": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_18",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_18",
    "chance": "rarely"
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
  ]
 }
}
```
