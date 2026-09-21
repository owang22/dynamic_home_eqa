# p_c8b3 — Morning Kitchen: Breakfast at the Table, the Dog's Bowl, and Yuki's Tablet

The weekday morning in this house runs in a sequence between 06:30 and 09:30. Yuki feeds the dog first (around 07:00, food bag on the kitchen floor, bowl on the counter while it is being filled). She then sits at the kitchen table with her tablet for reading around 07:30–08:30. Marco has his breakfast at the kitchen table around 08:30–09:30: his bowl and mug come out of the cupboard to the table. Around the same time (08:30–09:30) Marco takes his shower, and his glasses go to the bathroom shelf. By 09:30 the kitchen table is cleared and dishes go back to the cupboard.

What sets this apart: this document specifically places Marco's bowl and mug at the kitchen table during 08:30–09:30 (the p_7b3e document has the bowl at 8–9h, which the sightings do not support — the 09:00 pass shows the bowl at the table, not at 08:00). It also places the dog bowl at the counter (not the floor) during 07:30–08:30 while it is being filled, and Yuki's tablet at the kitchen table at 08:00.

What would refute it: if the bowl and mug are found in the cupboard at 09:00; if the dog bowl is on the floor at 08:00; if the tablet is at the nightstand at 08:00; if the glasses are at the nightstand at 09:00.

```json
{
 "claims": [
  {
   "claim": "Marco's bowl is at the kitchen table during his weekday breakfast",
   "target": "bowl_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8.5,
   "to": 9.5
  },
  {
   "claim": "Marco's mug is at the kitchen table during his weekday breakfast",
   "target": "mug_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8.5,
   "to": 9.5
  },
  {
   "claim": "The dog bowl is on the kitchen counter during weekday morning feeding",
   "target": "dog_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  },
  {
   "claim": "Yuki's tablet is at the kitchen table during her weekday morning reading",
   "target": "tablet_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  }
 ],
 "targets": {
  "bowl_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 8.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "tablet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 9.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
