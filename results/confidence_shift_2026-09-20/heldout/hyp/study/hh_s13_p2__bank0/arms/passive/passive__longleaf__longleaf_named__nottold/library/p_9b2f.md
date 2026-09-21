# p_9b2f — Dish Rack Bottle: Hana's water bottle lives at dish_rack_k1

The per-object evidence and the "worst objects" list both point to the same correction: water_bottle_hana's resting place is dish_rack_k1, not entry_hook_e1 (as p_a3f1 and p_d3e8 claim) and not sink_k1 (as the statistical model predicted four times wrong). The clock-hour sightings show the bottle at dish_rack_k1 at 00:00, 02:00, 04:00, 06:00, 08:00, 18:00, and 22:00. At 20:00 it appears at kitchen_table_k1 (Hana is having a drink during TV). During work hours it is OUT_OF_HOUSE with Hana. The bottle is washed and dried at the dish rack, then left there rather than being carried back to the entry or the sink.

What sets this apart: at 22:00 on a weekday, water_bottle_hana is at dish_rack_k1 (not entry_hook_e1, not sink_k1). At 20:00 it is at kitchen_table_k1. What would refute it: water_bottle_hana at entry_hook_e1 at 22:00 on a weekday, or at sink_k1 at 22:00.

```json
{
 "claims": [
  {
   "claim": "Hana's water bottle is at the dish rack at 22:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Hana's water bottle is at the kitchen table at 20:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Hana's water bottle is out of the house at noon on a weekday",
   "target": "water_bottle_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
