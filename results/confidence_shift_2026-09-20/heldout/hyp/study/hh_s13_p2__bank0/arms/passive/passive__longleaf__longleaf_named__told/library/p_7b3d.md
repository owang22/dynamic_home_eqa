# p_7b3d — Desk is Home: Laptop and Pen Rest at desk_b1 (fork of p_c9e5)

The parent document (p_c9e5) set the default resting spot for laptop_hana and pen_hana at entry_hook_e1, with a "sometimes" desk_b1 block for 18–22 h. The evidence contradicts this. Across all night and evening passes (00, 02, 04, 06, 18, 20, 22 h), the laptop is at desk_b1 two-thirds of the time and at entry_hook_e1 one-third. The pen is even more consistently at desk_b1 (2/3 at every single pass including 20:00, where the parent predicted a 50/50 split but the data shows 2/1). The "mixture's worst objects" list confirms: "laptop_hana: predicted entry_hook_e1, actually desk_b1 — 4x" and "pen_hana: predicted entry_hook_e1, actually desk_b1 — 3x."

The parent's 50/50 evening split for the laptop is also overstated. At 20:00 the split is 1/1 (one pass entry_hook, one pass desk), but at 18:00 and 22:00 it is 2/1 in favour of desk. The laptop's home is the desk; the entry hook is where it occasionally ends up on a rushed evening.

What changed from the parent: (1) laptop_hana default changed from entry_hook_e1 to desk_b1; the 18–22 h block is now entry_hook_e1 at "sometimes" (the minority case); (2) pen_hana default changed from entry_hook_e1 to desk_b1; the 18–22 h block is now entry_hook_e1 at "sometimes"; (3) charger_hana unchanged (already correct at desk_b1); (4) water bottle, jacket, keys, guitar, remote, and plate blocks unchanged from parent.

What would refute this fork: if the laptop is at entry_hook_e1 at 00:00, 02:00, AND 04:00 on the same night (three consecutive night passes at the hook with zero at the desk), the "desk is home" claim is wrong. If the pen is at entry_hook_e1 at 02:00, the correction is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at desk_b1 at 02:00 (night resting spot)",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Hana's pen is at desk_b1 at 02:00 (night resting spot)",
   "target": "pen_hana",
   "expect": "desk_b1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Hana's water bottle is at the kitchen table at 20:00 on a weekday (dinner)",
   "target": "water_bottle_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Hana's laptop is out of the house at noon on a weekday",
   "target": "laptop_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "charger_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "pen_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
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
    "from": 8,
    "to": 17.5,
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
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "class:plate": [
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
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
