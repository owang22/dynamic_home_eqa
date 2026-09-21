# p_5f8a — Weekend kitchen: sink-side morning prep, not table baking

On weekend mornings the kitchen is used for light breakfast preparation rather than the full baking session that p_a9d2 predicts for the afternoon. The cutting board is in the cupboard (not the kitchen table) in the morning: the weekend 00:00 and 08:00 passes show it split between kitchen_table_k1 and cupboard_k1, and the mixture's worst-objects list flags the kitchen_table prediction as wrong on day 5. By the afternoon the cutting board moves to the counter.

The pan and kitchen knife are at the sink in the morning, not in the drawer or cupboard. This suggests a quick wash-and-prep at the sink for breakfast, rather than a full cooking setup at the counter. The serving dish is also in the sink in the morning, consistent with dishes being washed after a weekend breakfast. The baking tray stays in the pantry through the morning and does not come out to the kitchen table until the afternoon (if at all).

The shopping bag is sometimes on the counter (not just the pantry) on weekends, suggesting a recent grocery trip or items being unpacked. Yuki's water bottle is on the counter in the morning (not the dish rack), where she fills it before her late-morning walk.

This document differs from p_a9d2 in that the morning kitchen items are at the sink and cupboard, not the kitchen table. It differs from p_e5a1 (weekend kitchen: snack bowl on counter, baking at table) in that the morning prep is sink-side and the baking tray does not come out until the afternoon.

What would refute it: If on a weekend morning the cutting board is at the kitchen table, the pan is in the cupboard (not the sink), and the baking tray is at the kitchen table, this document is wrong. If the shopping bag is always in the pantry and never on the counter, the grocery-trip prediction fails.

```json
{
 "claims": [
  {
   "claim": "The cutting board is in the cupboard during weekend morning prep",
   "target": "cutting_board_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 0,
   "to": 12
  },
  {
   "claim": "The pan is at the kitchen sink during weekend morning prep",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekend",
   "from": 0,
   "to": 12
  },
  {
   "claim": "The kitchen knife is at the kitchen sink during weekend morning prep",
   "target": "kitchen_knife_shared",
   "expect": "sink_k1",
   "days": "weekend",
   "from": 0,
   "to": 12
  },
  {
   "claim": "The baking tray stays in the pantry during weekend morning",
   "target": "baking_tray_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 0,
   "to": 12
  }
 ],
 "targets": {
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 18,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
