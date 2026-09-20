# p_e5f6 — Hana's night shift, Priya's day job

Hana works a nursing or hospital shift 18:00–6:00 on weekdays. Priya works a standard 8:00–16:00 office job. The 18:00 walkthrough catches Hana at the threshold, about to leave for her night shift: her umbrella is at the entry floor (she's about to grab it), and her tablet and phone are at the desk because she's in the process of gathering them. Priya finished at 16:00 and is home; her keys, wallet, sunglasses, jacket, and shoes are at the entry simply because that is where she stores them (she is not leaving or arriving—she's been home two hours). On weekdays, Hana's phone, tablet, and umbrella are OUT_OF_HOUSE from 18:00 to 6:00. Priya's items never leave the house on a typical weekday (she works nearby or from home on Wed/Fri). The dog is home with Priya during Hana's shift. What sets this apart: Hana's tablet and phone are OUT_OF_HOUSE 18:00–23:00 on weekdays while Priya's keys are IN the house the same window. What would refute it: finding Hana's tablet in the house at 20:00 on a Tuesday, or finding Priya's keys out of the house at 12:00 on a Monday.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is out of the house on weekday evenings (night shift)",
   "target": "tablet_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 18,
   "to": 23
  },
  {
   "claim": "Priya's keys are in the house on weekday midday",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Hana's umbrella is out of the house on weekday nights",
   "target": "umbrella_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 18,
   "to": 24
  },
  {
   "claim": "Priya's wallet is at the entry table on weekday afternoons",
   "target": "wallet_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 16,
   "to": 22
  }
 ],
 "targets": {
  "tablet_hana": [
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
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   }
  ],
  "umbrella_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "shoes_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "notebook_hana": [
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
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "OUT_OF_HOUSE",
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
  "tablet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "bedroom_floor_b2",
    "chance": "sometimes"
   }
  ]
 }
}
```
