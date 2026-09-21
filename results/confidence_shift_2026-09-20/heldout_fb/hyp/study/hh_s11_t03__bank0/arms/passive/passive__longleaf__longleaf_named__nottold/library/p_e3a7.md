# p_e3a7 — The 03:00 Snapshot; Hana in the Kitchen, Priya in Bedroom, Entry Items Scattered

This document captures the specific 03:00 weekday state confirmed by the resident looks: Hana (resident_1) is in the kitchen, Priya (resident_2) is in bedroom_2. Hana came home at 23:00, left her coat, bag, hat, scarf, pen, wallet, and water bottle at the entry area, and has been up since — watching TV (remote on floor_l_l1, blanket on armchair_l1) and then moving to the kitchen for a late snack or drink. Priya went to bed around 22:00 and is asleep in bedroom_2.

The entry items are scattered between entry_floor_e1 and entry_hook_e1: handbag, hat, jacket, scarf, pen, wallet, and water_bottle_hana all appear at one of these two spots at 03:00. This is the "just came home and dumped everything" pattern.

What sets this apart: most documents do not specify the 03:00 resident locations or the entry-item scatter. This document predicts the remote on the living room floor (not the TV stand) and the blanket on the armchair (not the coffee table) at 02:30–03:30, reflecting active TV use before Hana moved to the kitchen. What would refute it: a look at tv_stand_l1 at 03:00 that finds the remote, or a look at coffee_table_l1 at 03:00 that finds the blanket.

```json
{
 "claims": [
  {
   "claim": "The remote is on the living room floor at 3 AM during Hana's post-shift TV",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 2.5,
   "to": 3.5
  },
  {
   "claim": "The blanket is on the armchair at 3 AM during Hana's post-shift TV",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 2.5,
   "to": 3.5
  },
  {
   "claim": "Hana's handbag is on the entry floor after she has come home from her shift",
   "target": "handbag_hana",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Hana's handbag is on the entry floor in the early morning after her shift",
   "target": "handbag_hana",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 0,
   "to": 4
  },
  {
   "claim": "Hana's phone is on her nightstand after she has come home",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Hana's phone is on her nightstand in the early morning after her shift",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 3
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 2,
    "to": 4,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 2,
    "to": 5,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "couch_l1",
    "chance": "sometimes"
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
  "hat_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
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
  "scarf_hana": [
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
  "wallet_hana": [
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
  "water_bottle_hana": [
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
