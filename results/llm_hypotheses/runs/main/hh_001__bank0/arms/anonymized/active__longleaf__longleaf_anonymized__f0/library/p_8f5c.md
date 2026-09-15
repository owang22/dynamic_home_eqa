# p_8f5c — object_32 is a mobile kitchen item; absent from receptacle_18 during weekday work hours

Object_32 (class_32) is mostly seen at receptacle_18 (11/18 sighted days, 61%), but weekday 9-17h looks at receptacle_18 found it 0 times while 14 looks found nothing. It has 6 distinct receptacles across only 34 sightings, making it one of the most mobile objects in the house. No existing document addresses object_32's weekday work-hours absence from receptacle_18.

This document hypothesizes that object_32 is a small kitchen item (perhaps a spice container, small utensil, or condiment bottle) that is stored on the kitchen shelf (receptacle_18) on weekends and weekday mornings, but is taken to the active counter (receptacle_4) or used at the desk (receptacle_12) during the weekday work stretch when residents prepare meals or snacks at the desk. Its high mobility (6 receptacles) suggests it is handled frequently and left in various spots.

This document is distinct from the kitchen-shelf documents (p_b2d9, p_a7e3) which do not cover object_32, and from the commuter documents which do not address it. The keys (object_2) remain at receptacle_11 24/7.

What would refute this document: object_32 sighted at receptacle_18 during weekday 10:00-14:00 on two or more occasions; object_32 sighted out of the house at any time.

```json
{
 "claims": [
  {
   "claim": "object_32 (class_32 item) is NOT at receptacle_18 during weekday work hours 9-16h",
   "target": "object_32",
   "expect": "receptacle_4",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "object_32 (class_32 item) is at receptacle_18 on weekends during the day 8-18h",
   "target": "object_32",
   "expect": "receptacle_18",
   "days": "weekend",
   "from": 8,
   "to": 18
  },
  {
   "claim": "object_32 (class_32 item) is at receptacle_18 during weekday early morning 6-9h, before work begins",
   "target": "object_32",
   "expect": "receptacle_18",
   "days": "weekday",
   "from": 6,
   "to": 9
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
    "at": "receptacle_4",
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
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
    "chance": "almost_always"
   }
  ],
  "object_34": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
    "chance": "almost_always"
   }
  ]
 }
}
```
