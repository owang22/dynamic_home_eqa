# p_4a7c — Hana's Kitchen Table Morning; Tablet Walks the Room Before She Leaves

Hana is home on weekday mornings and works from the kitchen table, not the bedroom desk. The robot's passes confirm the tablet at kitchen_table_k1 six times at 09:00 on weekdays, then at coffee_table_l1 at 10:00, and back at nightstand_b1 by 12:00. Her mug follows the same path: cupboard in the pre-dawn, kitchen table at 09:00, coffee table from 10:00 through 17:00, back to the cupboard by 18:00. The notebook, by contrast, is a fixed object at desk_b1 (7/7 days, single receptacle) — it never leaves the desk. Hana leaves for her afternoon-to-night shift at roughly 13:40 and returns around 23:00. She does not take the tablet or notebook with her; they stay in the house. What she carries out is limited to keys, wallet, handbag, jacket, and shoes, all of which are seen at the entry area in the pre-dawn passes and are absent during her working hours.

This document sets itself apart from p_b8c2 (which places the tablet at desk_b1 in the morning — contradicted by 10 "against" sightings) and from p_a3f7 (which is silent on the tablet's morning location). The distinguishing prediction is the tablet's two-stop morning migration: kitchen table first, then coffee table, then nightstand. If the tablet is found at desk_b1 during the 08:00–12:00 weekday window, this document is refuted.

What would refute it: a weekday sighting of tablet_hana at desk_b1 between 08:00 and 12:00, or a weekday sighting of mug_hana at desk_b1 in the same window.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table during her weekday morning work block",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Hana's tablet is at the coffee table during her weekday mid-morning break",
   "target": "tablet_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Hana's mug is at the kitchen table during her weekday morning work block",
   "target": "mug_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Hana's notebook stays at her desk all day and all week",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Hana's keys are out of the house during her weekday work shift",
   "target": "keys_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "cupboard_k1",
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
    "from": 10,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.67,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "wallet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.67,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "class:dog_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
