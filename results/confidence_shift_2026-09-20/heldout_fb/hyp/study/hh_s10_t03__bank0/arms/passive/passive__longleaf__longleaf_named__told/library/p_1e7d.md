# p_1e7d — Omar's 23:00 post-shift drink: glass at the kitchen counter

Omar arrives home at approximately 23:00 on weekdays after his night shift. The evidence shows his glass at counter_k1 at 23:00 (×3) and at dish_rack_k1 (×1) during the same pass. This is his late-night water or tea, drunk standing at the counter rather than seated at the kitchen table. His plate and mug may be at the kitchen table for a quick bite (as p_5e19 predicts), but the glass specifically is at the counter — he fills it from the tap or the kettle and drinks it there before heading to bed.

This document is narrow: it only addresses glass_omar during the 23:00–24:00 window on weekdays. It sets itself apart from p_5e19 (which places his mug and plate at the kitchen table but is silent on the glass) and from the general class:glass block in other documents (which puts glasses at the cupboard or kitchen table). The glass is at the COUNTER, not the table, during his post-shift drink.

What would refute it: glass_omar at the kitchen table or dining table at 23:00 on a weekday; glass_omar at the nightstand at 23:00 (implying he went straight to bed without a drink).

```json
{
 "claims": [
  {
   "claim": "Omar's glass is at the kitchen counter at 23:00 on a weekday (his post-shift drink)",
   "target": "glass_omar",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Omar's glass is in the dish rack at 23:30 on a weekday (after he has finished his drink)",
   "target": "glass_omar",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 23.5,
   "to": 24
  }
 ],
 "targets": {
  "glass_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 23.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23.5,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 15.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
