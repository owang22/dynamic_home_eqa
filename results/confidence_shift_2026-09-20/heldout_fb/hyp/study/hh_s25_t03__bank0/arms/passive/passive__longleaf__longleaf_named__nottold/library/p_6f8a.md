# p_6f8a — Overnight kitchen: used dishes rest in the sink and dish rack, not put away

The household does a minimal overnight kitchen reset. Several items that are used during the day end up in the sink or dish rack overnight (00:00–07:00) rather than being returned to their daytime resting spots. Specifically: Marco's glass is at the counter or sink (not the cupboard); the snack bowl is in the kitchen sink (not the coffee table or cupboard); the spatula is in the dish rack (not the drawer); and Marco's water bottle is in the dish rack (not the desk). This "lazy overnight" pattern is distinct from p_3d8b which places the snack bowl in the sink but does not cover the glass, spatula, or water bottle. What sets this apart: a coordinated overnight position for four kitchen items in the sink/dish-rack/counter zone. What would refute it: any of these four items sighted at its daytime resting spot (cupboard, coffee table, drawer, desk) during the 00:00–06:00 window.

```json
{
 "claims": [
  {
   "claim": "Marco's glass is at the kitchen counter overnight after being used at dinner",
   "target": "glass_marco",
   "expect": "counter_k1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "The snack bowl is in the kitchen sink overnight",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "The spatula is in the dish rack overnight after the evening cooking",
   "target": "spatula_shared",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Marco's water bottle is in the dish rack overnight",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 0,
   "to": 7
  }
 ],
 "targets": {
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
