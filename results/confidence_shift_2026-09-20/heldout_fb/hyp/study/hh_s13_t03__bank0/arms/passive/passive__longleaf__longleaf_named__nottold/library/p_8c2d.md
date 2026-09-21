# p_8c2d — The 20:00 Transition: Dinner at the Kitchen Table, Then Coffee-Table TV

This document models the 19:30–21:00 window, which no existing document covers as a unified phase. The evidence: plate_hana is in the cupboard at 19:00 but on kitchen_table_k1 at 20:00 (×3); mug_hana is at kitchen_table_k1 at 18:00 and at coffee_table_l1 at 20:00 and 21:00; mug_priya is at coffee_table_l1 at 21:00 and 22:00 (×3); glass_priya is at coffee_table_l1 at 20:00 and 23:00, nightstand_b2 at 22:00 (×3); snack_bowl_shared is at counter_k1 at 19:00 (×3) and coffee_table_l1 at 21:00 (×2); blanket_shared is at couch_l1 at 18:00 (×2) and coffee_table_l1 at 21:00 (×2).

The pattern: dinner is served at the kitchen table around 19:30–20:00 (plates and mugs at the table). By 20:30–21:00, both residents have moved to the living room. The mugs and glasses migrate to the coffee table, the snack bowl moves from the counter to the coffee table, and the blanket shifts from the couch to the coffee table. The plates go back to the cupboard or sink by 21:00.

What sets this apart: it is the *only* document that explicitly models the 20:00–21:00 migration as a single phase, with the kitchen table as the dinner site (not the living room) and the coffee table as the TV site (not the couch). It differs from p_7d4e which focuses on the 21:00+ state but does not model the 20:00 dinner-at-the-table moment. It differs from p_2e9c (Dinner at the Kitchen Table) which places the plate at the table at 19:30; here the plate is at the table at 20:00 (the 19:00 sighting is still in the cupboard).

Refutation: plate_hana at kitchen_table_k1 at 19:00 on a weekday (dinner is earlier than 19:30), or mug_hana at kitchen_table_k1 at 21:00 (she has not moved to the living room yet).

```json
{
 "claims": [
  {
   "claim": "Hana's plate is on the kitchen table at 20:00 on a weekday (dinner in progress)",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 20.5
  },
  {
   "claim": "Hana's mug is on the coffee table at 21:00 on a weekday (moved to TV area)",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "Priya's mug is on the coffee table at 22:00 on a weekday (evening TV)",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the counter at 19:00 on a weekday (dinner side, not yet moved)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
  }
 ],
 "targets": {
  "plate_hana": [
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
    "from": 19.5,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
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
    "from": 19.5,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "from": 7,
    "to": 8.5,
    "at": "kitchen_table_k1",
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
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
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
    "from": 20,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
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
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
