# p_4e7c — Hana's Entry Set Stays Home; Handbag on the Hook (fork of p_9d2b)

The parent document p_9d2b got the phone pattern right but made a systematic error: it sent Hana's keys, handbag, shoes, jacket, hat, and scarf all OUT_OF_HOUSE from 13:40 to 23:00. The sightings flatly contradict this. During 14:00–22:00 on weekdays, the robot finds the handbag at entry_table_e1, the keys at entry_table_e1, the shoes at shoe_rack_e1, and the jacket/hat/scarf at entry_hook_e1 — every single hour. None of these items leave the house. Hana apparently takes only her phone to work (or works in a way that doesn't require her home key set, bag, or outerwear to travel).

The second error: the handbag's morning resting spot is entry_hook_e1 (2 of 4 sightings per hour, 00:00–12:00), not entry_table_e1 (only 1 of 4). The parent's claim "handbag at entry_table_e1, weekday 8–13h" accumulated 18 against and 3 for over the full log, and another 6 against since the last call. The hook is the correct receptacle.

The water bottle is the most mobile object in the entry set: on weekdays it is split across four receptacles (entry_floor, entry_hook, entry_table, counter) in the early morning, shifts to coffee_table_l1 in the early afternoon, and ends at dish_rack_k1 in the evening. No single block captures it well; I give it a multi-block pattern with "sometimes" chance throughout.

What changed from the parent: (1) handbag moved from entry_table_e1 to entry_hook_e1; (2) all OUT_OF_HOUSE blocks for keys, handbag, shoes, jacket, hat, and scarf removed — they stay in the entry area all day; (3) water bottle given a multi-location weekday pattern instead of a single entry_floor_e1 block; (4) scarf given a secondary wardrobe_b1 block.

What would refute this: handbag_hana found at entry_table_e1 during 8:00–12:00 on a weekday (would mean the parent was right); any of the entry items found OUT_OF_HOUSE during 14:00–22:00; the phone found at the nightstand during 9:00–17:00.

```json
{
 "claims": [
  {
   "claim": "Hana's handbag is on the entry hook in the weekday morning, not on the entry table",
   "target": "handbag_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 8,
   "to": 12
  },
  {
   "claim": "Hana's keys stay at the entry table in the weekday afternoon; they do not leave the house",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 20
  },
  {
   "claim": "Hana's shoes stay on the shoe rack in the weekday afternoon; they do not leave the house",
   "target": "shoes_hana",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 14,
   "to": 20
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
   "claim": "Hana's scarf is on the entry hook in the weekday morning, not in the wardrobe",
   "target": "scarf_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 8,
   "to": 12
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
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 22,
    "at": "entry_table_e1",
    "chance": "sometimes"
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
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 14,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "rarely"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "rarely"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
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
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "hat_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
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
    "chance": "sometimes"
   }
  ],
  "scarf_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "wardrobe_b1",
    "chance": "rarely"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "sometimes"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_floor_e1",
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
