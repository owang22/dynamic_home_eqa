# p_a7c3 — Hana's Kitchen Table Morning; Notebook at Desk, Tablet at the Table

Hana (resident_1) works afternoon-to-night shifts, home in the morning. This hypothesis refines the morning routine: her **tablet** is at the **kitchen table** during her work-and-snack block, not at desk_b1. The evidence is now strong: five sightings of tablet_hana at kitchen_table_k1 on weekday mornings (09:00 ×4, 10:00 ×1), while notebook_hana sits at desk_b1 on all three sighted days. She eats her morning bowl at the same kitchen table, then transitions to the desk for the notebook-only tasks before leaving at 13:40. Priya (resident_2) is retired, home all day, with a morning walk and afternoon errands; she anchors the kitchen and the dog.

What sets this apart from p_b8c2 and p_a1b2: those place the tablet at desk_b1 in the morning, which the sightings contradict (5 against). This document places the tablet at kitchen_table_k1 and the notebook at desk_b1 simultaneously. What would refute it: a weekday 9–12 h look at kitchen_table_k1 that finds no tablet, or a look at desk_b1 that finds the tablet.

Travelling objects: Hana takes her phone, keys, handbag, jacket, hat, scarf, water bottle, and pen out of the house at 13:40 on weekdays. Priya takes her keys, sunglasses, and the dog leash out for the morning walk (07:00–08:30) and afternoon errands (14:00–16:00). The dog leash and toy go out with Priya.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table during her weekday morning work block",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Hana's notebook remains at her desk during the weekday morning",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Hana's bowl is at the kitchen table during her weekday morning meal",
   "target": "bowl_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 10
  },
  {
   "claim": "Hana's phone is out of the house during her weekday shift",
   "target": "phone_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "weekday",
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
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 8.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "mug_hana": [
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
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
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
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "handbag_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
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
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
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
  ],
  "class:bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
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
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "floor_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 0.5,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "almost_always"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ]
 }
}
```
