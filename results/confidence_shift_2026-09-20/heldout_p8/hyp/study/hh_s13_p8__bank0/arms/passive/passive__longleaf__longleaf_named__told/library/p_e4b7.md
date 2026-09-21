# p_e4b7 — Weekend Kitchen Reset: Dish Rack and Cupboard Replace the Sink

On weekdays, several kitchen objects rest at sink_k1 between uses: Priya's mug, the snack bowl, and Hana's water bottle all cycle through the sink as they are washed and set down. On weekends, this pattern shifts. The Saturday 00:00 and 08:00 passes show a different resting configuration: Priya's mug is at dish_rack_k1 (not sink_k1), the snack bowl is at dish_rack_k1 (not sink_k1), and Hana's water bottle is at dish_rack_k1 (not sink_k1). By 16:00, the mug and snack bowl have moved to cupboard_k1, and the water bottle remains at dish_rack_k1.

This makes sense in the context of the weekend sleep-in: on a weekday morning, the kitchen is active by 7:00 (Priya making tea, Hana grabbing a glass of water), so objects are at the sink mid-wash. On a Saturday morning, the kitchen is untouched until 10:00 or later, so the objects are in their fully-put-away spots: the dish rack (just dried, not yet returned to the cupboard) or the cupboard (fully stored).

Priya's bowl is at cupboard_k1 on all three Saturday passes, not at sink_k1 as it sometimes is on weekdays. Hana's mug is at cupboard_k1 on all three Saturday passes. The glasses (both residents') are at sink_k1 on weekends, consistent with their weekday resting spot.

This document is distinct from p_1f9a (Saturday 8AM sleep-in) in that it covers the full weekend day rather than just the morning, and it focuses specifically on the kitchen resting spots. It differs from p_e5f0 in that it does not assert brunch at 11:00–13:00; the 16:00 pass shows plates and mugs back in the cupboard or at the kitchen table, not a midday meal in progress.

What would refute this: finding Priya's mug at sink_k1 on a Saturday morning, finding the snack bowl at sink_k1 on a Saturday, or finding Hana's water bottle at sink_k1 on a weekend.

```json
{
 "claims": [
  {
   "claim": "Priya's mug is at the dish rack on a Saturday morning, not at the sink",
   "target": "mug_priya",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 7,
   "to": 12
  },
  {
   "claim": "The snack bowl is at the dish rack on a Saturday morning, not at the sink",
   "target": "snack_bowl_shared",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 7,
   "to": 12
  },
  {
   "claim": "Hana's water bottle is at the dish rack on a Saturday afternoon, not at the sink",
   "target": "water_bottle_hana",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "Priya's bowl is in the cupboard on a Saturday afternoon, not at the sink",
   "target": "bowl_priya",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 12,
   "to": 18
  }
 ],
 "targets": {
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
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
  ],
  "mug_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ]
 }
}
```
