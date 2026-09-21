# p_1f9a — Saturday 8AM: The House Sleeps, Kitchen Untouched

The Saturday 08:00 pass is the clearest evidence of the weekend sleep-in. Both residents are still in their bedrooms at 8:00 on Saturday (resident_1 in bedroom_1, resident_2 in bedroom_2), compared to weekdays when Priya is already in the kitchen and Hana is out at work. The house is in a pre-activity rest state: no one has touched the kitchen, the bathroom, or the living room yet.

This means the kitchen objects are in their overnight resting spots. Hana's mug is in cupboard_k1 (not at the sink or on the counter as it might be on a weekday morning after a quick coffee). Priya's mug is at dish_rack_k1, where it was put away after the previous evening's use. The snack bowl is also at dish_rack_k1. Hana's water bottle is at dish_rack_k1. Priya's bowl is in cupboard_k1. All of these are confirmed by the 08:00 Saturday pass.

Hana's laptop and pen are at entry_hook_e1, where they were dumped the previous evening (Friday 18:00) and have not been moved because she is still in bed. Her charger is at desk_b1, where it was left overnight. Her phone is at nightstand_b1, within reach of the bed. Priya's phone is at nightstand_b2.

The living room is also undisturbed: the blanket is already on the armchair (Priya's weekend spot), the remote is on the coffee table, the guitar is on the bedroom floor, the puzzle box is on the bookshelf. Nothing has been set out for a morning activity because no one has woken up yet.

This document differs from p_e5f0 in that it does NOT claim brunch at 11:00–13:00 or guitar playing at 14:00–17:00. It focuses on the 7:00–10:00 window when the house is genuinely quiet. It differs from p_7f3a (and its fork p_3b7e) by emphasising the kitchen resting spots at this specific hour rather than the full-day pattern.

What would refute this: finding Hana's mug on the kitchen table at 8:00 on a Saturday, finding Priya in the kitchen at 8:00 on a Saturday, or finding Hana's laptop at desk_b1 at 8:00 on a Saturday.

```json
{
 "claims": [
  {
   "claim": "Hana's mug is in the cupboard at 8:00 on a Saturday because no one has had coffee yet",
   "target": "mug_hana",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 7,
   "to": 10
  },
  {
   "claim": "Priya's mug is at the dish rack at 8:00 on a Saturday, put away from the previous evening",
   "target": "mug_priya",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 7,
   "to": 10
  },
  {
   "claim": "The snack bowl is at the dish rack at 8:00 on a Saturday, not on the counter or coffee table",
   "target": "snack_bowl_shared",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 7,
   "to": 10
  },
  {
   "claim": "Hana's water bottle is at the dish rack at 8:00 on a Saturday",
   "target": "water_bottle_hana",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 7,
   "to": 10
  }
 ],
 "targets": {
  "mug_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
