# p_2c9d — Shopping bag: kitchen counter by day, pantry by night

The shared shopping bag is not a static object. During the day—roughly 8:00 to 17:00 on weekdays and 10:00 to 16:00 on weekends—it sits on the kitchen counter, where it is used to hold produce, bread, or other groceries that have been unpacked from the car but not yet put away. At night (03:00 passes) it is back in the pantry shelf, folded or emptied. The 7-for-7 weekday 9–17h looks at counter_k1 that found the bag confirm this is a daily pattern, not a one-off.

What sets this apart: no existing document in the library places the shopping bag on the counter during the day. The statistical model would put it at pantry_shelf_k1 (its 03:00 resting spot) for all hours, missing the daytime displacement. This document predicts the bag is on the counter at midday on both weekdays and weekends, and in the pantry only at night.

Refutation: if the shopping bag is sighted in the pantry shelf during a 9–17h weekday look, or if it is absent from the counter on 3 or more consecutive weekday midday passes, the daily-counter hypothesis fails.

```json
{
 "claims": [
  {
   "claim": "The shopping bag is on the kitchen counter at 12:00 on a weekday",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The shopping bag is in the pantry shelf at 03:00 on a weekday",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "The shopping bag is on the kitchen counter at 14:00 on a weekend",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 12,
   "to": 16
  }
 ],
 "targets": {
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 16,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
