# p_c5d1 — Hana's Midnight Kitchen; Glass and Snacks at the Counter After Her Shift

Hana (resident_1) comes home from her night shift at 23:00. Rather than going straight to bed, she heads to the kitchen for a late snack and a drink. The 23:00 pass catches glass_hana at counter_k1 ×2 (plus sink_k1 and cupboard_k1 in the same pass, suggesting she is mid-routine: getting a glass, filling it, putting the other away). The snack_bowl_shared is at counter_k1 ×2 at 23:00. By 03:00 the robot finds Hana still in the kitchen (resident_1 in kitchen), while Priya (resident_2) is already in bedroom_2. Hana's phone is at nightstand_b1 by 23:00 (she set it down when she came in) and remains there.

What sets this apart from p_789a (which places cooking at midnight with pan and knife on the counter): this document has no cooking, just a glass of water and a snack. The pan and knife are not at the counter at 23:00 in the sightings. What would refute it: a look at counter_k1 at 23:30 that finds the pan or knife, or a look at nightstand_b1 at 00:30 that finds no phone.

Hana's entry items (handbag, hat, jacket, scarf, pen, wallet, water bottle) are left at the entry area when she comes in at 23:00 and remain there through the 03:00 pass.

```json
{
 "claims": [
  {
   "claim": "Hana's glass is on the kitchen counter during her post-shift late snack",
   "target": "glass_hana",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Hana's glass is on the kitchen counter just after midnight",
   "target": "glass_hana",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 0,
   "to": 0.5
  },
  {
   "claim": "The snack bowl is on the kitchen counter during Hana's late-night snack",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "The snack bowl is on the kitchen counter just after midnight",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 0,
   "to": 0.5
  },
  {
   "claim": "Hana's phone is on her nightstand after she has come home from her shift",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 2
  },
  {
   "claim": "The remote is on the living room floor during the early-morning hours when Hana was watching TV",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 2.5,
   "to": 3.5
  }
 ],
 "targets": {
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 0.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0.5,
    "to": 3,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "cupboard_k1",
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
