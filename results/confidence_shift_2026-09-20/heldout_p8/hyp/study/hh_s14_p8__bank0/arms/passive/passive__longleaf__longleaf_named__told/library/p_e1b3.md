# p_e1b3 — Weekend: corrected resting spots (fork of p_a9d2)

Marco and Yuki live together. On weekends Marco is off work, does errands around midday, and is home the rest of the day. Yuki is retired, home most of the day, with a late-morning walk. She looks after the dog.

This fork corrects several weekend resting spots that the parent document (p_a9d2) got wrong or did not cover. The notebook is in the wardrobe on weekends, not the entry hook: Marco stores his work notebook away when he is not going to work, and all three weekend passes (00:00, 08:00, 16:00) show wardrobe_b1. The blanket is on the bed on weekends, not the couch: the couple sleeps in the bed and the blanket stays there through the day (all three weekend passes show bed_b1, while weekdays show couch_l1). Marco's glass is at the nightstand in the weekend morning — he keeps his drinking glass by the bed on weekends, whereas on weekdays it is in the cupboard or at the kitchen table.

The backpack is at the entry hook on weekends, but the 16:00 pass sometimes shows entry_floor_e1 instead, so the chance stays "usually" rather than "almost_always." The guitar, baking, yoga, and dog-walk routines from the parent are retained unchanged.

This document differs from p_a9d2 in that (1) notebook_marco's weekend resting spot is wardrobe_b1 instead of entry_hook_e1; (2) blanket_shared is added with bed_b1 on weekends; (3) glass_marco is added with nightstand_b1 on weekend mornings. The parent's backpack claim scored 2 against and 0 for on the weekend, partly because the backpack drifts to the entry floor; this fork keeps the entry-hook prediction but with a lower confidence label.

What would refute it: If on a weekend the notebook is at the entry hook, the blanket is on the couch, or the glass is in the cupboard in the morning, this document is wrong. If the guitar is not on the bedroom floor during the 15–17 h practice window, the practice prediction fails.

_(targets the fork left unstated are inherited from p_a9d2)_

```json
{
 "claims": [
  {
   "claim": "Marco's notebook is in the wardrobe on the weekend (not at the entry hook)",
   "target": "notebook_marco",
   "expect": "wardrobe_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The blanket is on the bed on the weekend (not on the couch)",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
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
   "claim": "Marco's glass is at the nightstand during the weekend morning",
   "target": "glass_marco",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 0,
   "to": 12
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
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
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
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
