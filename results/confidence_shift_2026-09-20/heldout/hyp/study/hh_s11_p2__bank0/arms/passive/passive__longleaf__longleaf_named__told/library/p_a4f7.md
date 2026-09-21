# p_a4f7 — Hana's Handbag Lives on the Hook, Not the Table (fork of p_9d2b)

The parent document p_9d2b placed handbag_hana at entry_table_e1 in the weekday morning, but the per-object evidence now reads "mostly entry_hook_e1 (4/6 sighted days)" and the claim "handbag at entry table, weekday 8–13h" has accumulated **for 3, against 18**. The hourly sightings confirm it: from 00:00 through 12:00 the bag is at entry_hook_e1 in 2 of 4 passes, entry_floor_e1 in 1, and entry_table_e1 in 1. The hook is the dominant resting spot in the morning. After 13:40 the bag goes out with Hana (only 1 of 4 passes finds it at the table, the rest empty because it is OUT_OF_HOUSE). At 22:00 it returns to the hook.

This fork changes only the handbag blocks and its associated claim. Everything else in the parent — phone on person in the morning, out during the shift, back on the nightstand at 23:00; keys and wallet at the entry table; jacket, hat, scarf on the hook; shoes on the rack; guitar in the bedroom; notebook at the desk — stays exactly as written. The water-bottle early-morning block (entry_floor_e1, 6–10h) is also weakened: the sightings show the bottle split four ways (entry_floor, entry_hook, entry_table, counter) in that window, so the chance drops to "rarely."

What would refute this fork: handbag_hana found at entry_table_e1 in more than half of morning looks; the bag on the entry floor rather than the hook.

```json
{
 "claims": [
  {
   "claim": "Hana's handbag is on the entry hook in the weekday morning, not on the entry table",
   "target": "handbag_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 7,
   "to": 13
  },
  {
   "claim": "Hana's phone is not at her nightstand during her weekday morning; she carries it with her",
   "target": "phone_hana",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 8,
   "to": 12
  },
  {
   "claim": "Hana's keys are at the entry table in the weekday morning",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 8,
   "to": 13
  },
  {
   "claim": "Hana's handbag is back on the entry hook late at night after she returns from work",
   "target": "handbag_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 22,
   "to": 24
  }
 ],
 "targets": {
  "phone_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.67,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "rarely"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.67,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 18,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "hat_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "scarf_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
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
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
