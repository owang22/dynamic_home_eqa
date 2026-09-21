# p_a9d2 — Weekend: baking, guitar practice, yoga, and the dog walk

Marco and Yuki live together. On weekends Marco is off work. He does errands around midday and is home the rest of the day. His hobbies include baking, yoga, journaling, and calls with family. Yuki is retired, home most of the day, with a late-morning walk. Her hobbies are baking and guitar. She looks after the dog.

On a typical weekend: in the late morning (10:00–12:00) Yuki takes the dog for a walk, so the leash leaves the entry hook. In the afternoon (13:00–16:00) the couple bakes together: the baking tray, mixing bowl, spatula, and kitchen knife come out to the counter or kitchen table. The guitar is on the couch in the morning and moves to the bedroom floor for Yuki's afternoon practice (15:00–17:00). Marco does yoga in the early morning (6:00–7:30) with the mat on the living room floor. Marco journals at the desk. Marco's work kit (backpack, jacket, keys, phone, wallet, shoes, sunglasses, notebook, water bottle) is at home in the entry area all day—nothing goes to work on a weekend.

This document predicts that on weekends the kitchen is in active baking use in the afternoon, the guitar is in the bedroom for practice, the yoga mat is on the living room floor in the morning, and Marco's going-out items are all present in the house. The "sometimes" chances reflect that not every weekend involves baking or that the exact hours shift.

What would refute it: If on a weekend afternoon the baking tray is still in the pantry, the guitar is still on the couch (not in the bedroom), and the yoga mat is still in the wardrobe (not on the floor), this document is wrong. If Marco's backpack or keys are out of the house on a weekend, the "nothing travels" claim fails.

```json
{
 "claims": [
  {
   "claim": "The baking tray is at the kitchen table during weekend afternoon baking",
   "target": "baking_tray_shared",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "The guitar is on the bedroom floor during Yuki's weekend afternoon practice",
   "target": "guitar_yuki",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 15,
   "to": 17
  },
  {
   "claim": "The yoga mat is on the living room floor during Marco's weekend morning yoga",
   "target": "yoga_mat_marco",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 6,
   "to": 7.5
  },
  {
   "claim": "Marco's backpack is at the entry hook on the weekend (not out at work)",
   "target": "backpack_marco",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "guitar_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 17,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 6,
    "to": 7.5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "journal_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "backpack_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "jacket_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "phone_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
