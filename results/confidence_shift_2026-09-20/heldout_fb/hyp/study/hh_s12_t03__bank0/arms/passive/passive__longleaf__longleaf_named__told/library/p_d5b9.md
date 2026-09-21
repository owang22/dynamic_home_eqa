# p_d5b9 — Saturday midday: Elena's errands and the quiet kitchen

A narrower slice of the weekend: Saturday 12:00-15:00. Elena has gone out for errands (her stated weekend pattern: "errands around midday"). Priya is home, likely reading, having guitar, or tending the dog. The kitchen is quiet—no baking (that was morning), no cooking (dinner is hours away). The dog is with Priya. Elena's keys, wallet, and phone are out with her; her backpack may be on her person or at the entry. The shopping bag from a previous trip might still be at the counter.

What sets this apart: this is the one window on a weekend when an object IS out of the house (Elena's keys, wallet, phone, possibly water bottle). It also predicts the kitchen counter is clear of baking items (tray put back at 12) and the living room is calm (no TV yet, no friends yet). Priya's mug is at the kitchen table from her late breakfast, now empty.

Refutation: if Elena's keys or wallet are sighted in the house during Saturday 12-15, or if the baking tray is still at the counter at 13:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Elena's keys are out of the house during her Saturday midday errands",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 15
  },
  {
   "claim": "The baking tray is back on the pantry shelf by 13:00 on Saturday after morning baking is done",
   "target": "baking_tray_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 12.5,
   "to": 14
  },
  {
   "claim": "The dog toy is on the living-room floor during the Saturday midday when Priya is home with the dog",
   "target": "dog_toy_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Elena's wallet is out of the house during her Saturday midday errands",
   "target": "wallet_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 15
  }
 ],
 "targets": {
  "keys_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "wallet_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekend",
    "from": 12,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekend",
    "from": 12,
    "to": 16,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
