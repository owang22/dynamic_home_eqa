# p_7a3e — The Kitchen Table Morning; Both Residents Eat Together at 08:00–09:30

Hana and Priya share a weekday breakfast at the kitchen table. Priya, back from her morning walk by 07:30, sets out her bowl, mug, and tablet at kitchen_table_k1 around 08:00. Hana, still home before her 13:40 departure, joins at the same table around 08:30–09:00 with her own bowl and plate. The tablet_hana that p_b8c2 and p_a1b2 place at desk_b1 is instead seen four times at kitchen_table_k1 at 09:00; her "morning work" or reading happens at the kitchen table, not the bedroom desk. The notebook_hana stays at desk_b1 (confirmed 2/2 days) but is not the active tool during breakfast.

This document sets itself apart by predicting that BOTH residents' personal tableware converges on kitchen_table_k1 in the 07:30–10:00 window, and that tablet_hana is at the kitchen table (not desk_b1) during that same window. If the robot finds bowl_priya and bowl_hana simultaneously at kitchen_table_k1 in the 8–9 AM window, this document is strongly supported. If both bowls are found in the cupboard during that window, the document is refuted.

The dog food bag is on the counter or floor during the 08:00 feeding (Priya feeds the dog before or during breakfast), consistent with the 08:00 sightings at counter_k1 and floor_k_k1.

```json
{
 "claims": [
  {
   "claim": "Priya's bowl is at the kitchen table during weekday breakfast",
   "target": "bowl_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9.5
  },
  {
   "claim": "Hana's bowl is at the kitchen table during weekday breakfast",
   "target": "bowl_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Hana's tablet is at the kitchen table, not the desk, during her morning block",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8.5,
   "to": 12
  },
  {
   "claim": "Priya's mug is at the kitchen table during weekday breakfast",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9.5
  }
 ],
 "targets": {
  "bowl_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "tablet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "bowl_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
