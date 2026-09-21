# p_c37d — p_t4n9 — Weekend Evening Baking: Counter Active After 18:00, Not Afternoon

The weekend baking session in this household happens in the evening, not the afternoon as p_d1e6 and p_8c4d predict. The evidence: on Saturday the spatula appears on counter_k1 at 18:00 (two sightings) and the kitchen knife on counter_k1 at 22:00. The baking tray and mixing bowl are both at pantry_shelf_k1 at 03:00 (resting) and show no weekend counter sightings in the 09:00–16:00 window. The claims in p_d1e6 that the mixing bowl and knife are on the counter during "Yuki's weekend afternoon baking" (13:30–15:00) have just taken three strikes each since the last call.

Instead, the midday window (09:00–16:00) is when meals are served at the kitchen table: bowls appear at 09:00–10:00, plates at 13:00–16:00. The actual baking prep and cooking occupy the 18:00–22:00 window, when the spatula, knife, and presumably the tray and mixing bowl migrate to the counter. Marco's water bottle is at the dish rack overnight and at the kitchen table by 19:00, consistent with an evening meal or snack while baking.

What would refute this: a weekend sighting of the baking tray or mixing bowl on the counter between 09:00 and 16:00, or the spatula/knife on the counter before 17:00.

```json
{
 "claims": [
  {
   "claim": "The spatula is on the kitchen counter at 18:00 on a weekend during the evening baking session",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The kitchen knife is on the kitchen counter at 22:00 on a weekend, still in use from baking",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The mixing bowl is on the pantry shelf at 11:00 on a weekend, not yet in use for baking",
   "target": "mixing_bowl_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Yuki's plate is at the kitchen table at 14:00 on a weekend during the midday meal",
   "target": "plate_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 13,
   "to": 15
  }
 ],
 "targets": {
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:plate": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 17,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "class:bowl": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
