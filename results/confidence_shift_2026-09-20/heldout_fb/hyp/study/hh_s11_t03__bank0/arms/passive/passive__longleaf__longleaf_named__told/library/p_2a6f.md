# p_2a6f — The Sick Day Kitchen; No Shared Breakfast, Priya Eats Alone

On this sick-day Friday, the normal shared breakfast at the kitchen table does not happen. Hana is too unwell to come downstairs; she stays in bed. Priya may eat a light breakfast alone at the kitchen table around 08:00 or skip it entirely. The dog still gets its morning feeding at 07:00–08:00, with the dog food bag on the kitchen floor (sighted there 4 times at 08:00 on normal days). Priya's bowl and mug may appear at the kitchen table briefly for her solo meal, but Hana's bowl and plate stay in the cupboard or at the sink. The morning is quieter than usual: no Hana at the kitchen table with her tablet at 09:00, no shared fruit bowl being eaten. The fruit bowl stays on the kitchen table untouched.

This document differs from p_e8b2 and p_7a3e (which predict both residents at the kitchen table for breakfast, with Hana's bowl and plate there) by having only Priya present. It differs from the standard documents by the absence of Hana's objects in the kitchen in the morning. The dog food bag pattern is the same as normal days.

This document is refuted if Hana's bowl or plate is seen at the kitchen table between 07:00 and 10:00, or if Hana's tablet appears at the kitchen table in the morning (which would mean she is up and working despite being sick).

```json
{
 "claims": [
  {
   "claim": "Hana's bowl stays in the cupboard because she is too sick to eat breakfast at the table",
   "target": "bowl_hana",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 7,
   "to": 10
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the morning feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 7,
   "to": 8.5
  },
  {
   "claim": "Hana's plate stays at the sink on the sick day and does not go to the kitchen table for a meal",
   "target": "plate_hana",
   "expect": "sink_k1",
   "days": "both",
   "from": 7,
   "to": 14
  }
 ],
 "targets": {
  "bowl_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
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
    "from": 7,
    "to": 8.5,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
