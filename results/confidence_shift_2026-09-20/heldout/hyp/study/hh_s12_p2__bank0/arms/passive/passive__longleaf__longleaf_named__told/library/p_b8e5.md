# p_b8e5 — Evening settling: blanket on coffee table, remote on TV stand, dog fed

This document focuses on the evening window (19:00–23:00) when both residents are home and the household shifts from activity to rest. The pattern is consistent across the sighting log:

**Blanket (blanket_shared):** During the day (00:00–18:00) the blanket is at couch_l1 (2 of 3 passes) or coffee_table_l1 (1 of 3). But in the evening (20:00–22:00) the pattern flips: coffee_table_l1 x2, couch_l1 x1. The blanket is pulled from the couch to the coffee table for evening TV — it is draped over the coffee table or the person sitting in front of the TV. The mixture has been wrong 2 times predicting couch when the actual was coffee_table.

**Remote (remote_shared):** During the day the remote is at tv_stand_l1 (2 of 3) or coffee_table_l1 (1 of 3). In the evening (20:00–22:00) it is at tv_stand_l1 x2, coffee_table_l1 x1 — the remote returns to the TV stand after TV ends (around 21:30–22:00). At 22:00 it shifts to coffee_table_l1 x2, tv_stand_l1 x1, suggesting it is set down on the coffee table after the last viewing.

**Dog food bag (dog_food_bag_shared):** In the evening (20:00–22:00) the bag is at pantry_shelf_k1 x1, kitchen_table_k1 x1, floor_k_k1 x1. The dog is fed around 20:00 (after dinner), the bag is brought to the kitchen floor or table, and then returned to the pantry. The floor_k_k1 sighting represents the active feeding moment.

**Dog bowl (dog_bowl_shared):** Stays at floor_k_k1 all day (9/9 weekday midday looks). The dog eats from it at breakfast and dinner; the bowl is not moved.

What sets this hypothesis apart: it models the evening-specific shift of the blanket from couch to coffee table (a TV-viewing behavior), and the evening dog-feeding cycle that moves the food bag to the kitchen floor. No existing document captures the blanket's evening flip.

Refutation: if the blanket is at the couch on 8+ of 10 evening looks (20–22h); if the dog food bag is at the pantry on 8+ of 10 evening looks (20–22h); if the remote is at the coffee table on 8+ of 10 evening looks (20–21h).

```json
{
 "claims": [
  {
   "claim": "The blanket is on the coffee table during evening TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the evening feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The remote is on the TV stand during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20,
   "to": 21.5
  },
  {
   "claim": "The dog bowl is on the kitchen floor during the evening feeding",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "rarely"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ],
  "mug_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
