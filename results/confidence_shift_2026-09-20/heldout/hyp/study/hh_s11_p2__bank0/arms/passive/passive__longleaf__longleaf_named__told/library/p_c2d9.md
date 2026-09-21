# p_c2d9 — Weekend Entry: Hook, Shoe Rack, and Table

On weekends the entry-area objects shift from their weekday positions. Hana's handbag, which on weekdays sits on the entry floor or entry table in the morning and the entry table in the afternoon, stays on the entry hook all day on weekends—she's not packing it for a commute. Her jacket is on the entry floor in the morning, moves to the shoe rack in the afternoon (she's been in and out for errands), and returns to the hook in the evening. Her hat follows a similar pattern: hook in the morning, shoe rack in the afternoon. Priya's jacket is on the hook in the morning and the shoe rack in the afternoon. The scarf stays on the hook all day. Keys and wallets for both residents stay on the entry table. Priya's sunglasses stay on the entry table. The dog leash stays on the entry hook all day (no morning walk on weekends, or the walk is brief and the leash returns quickly). Hana's pen, which on weekdays is scattered around the entry area in the morning, is at her desk all day on weekends (she's working or reading at the desk). Hana's shoes are on the shoe rack in the morning and on the entry floor in the evening (she's been out). Priya's shoes stay on the shoe rack.

This document differs from p_9d2b (handbag at entry table weekday morning), p_3b8d (keys and jacket out of house for walk), and p_f3a1 (handbag at entry floor because home sick) by placing the entry set in its weekend resting spots. It would be refuted if the handbag is found at the entry table or floor, the keys are out of the house, or the pen is at the entry area on a weekend.

```json
{
 "claims": [
  {
   "claim": "Hana's handbag is on the entry hook, not the entry table or floor, on the weekend",
   "target": "handbag_hana",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Priya's jacket is on the shoe rack in the weekend afternoon, not the entry hook",
   "target": "jacket_priya",
   "expect": "shoe_rack_e1",
   "days": "weekend",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Hana's pen is at her desk all day on the weekend, not in the entry area",
   "target": "pen_hana",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Priya's keys are on the entry table all day on the weekend, not out of the house",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Hana's hat is on the shoe rack in the weekend afternoon",
   "target": "hat_hana",
   "expect": "shoe_rack_e1",
   "days": "weekend",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 16,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "hat_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "scarf_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "keys_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "pen_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "shoes_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "umbrella_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "doormat_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
