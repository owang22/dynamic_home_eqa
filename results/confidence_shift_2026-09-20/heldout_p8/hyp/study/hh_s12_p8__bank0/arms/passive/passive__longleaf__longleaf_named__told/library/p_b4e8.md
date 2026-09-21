# p_b4e8 — Full commuter; Priya's desk_b1 anchor all day

Elena is a full-time office commuter with no work-from-home days. Every weekday from roughly 8 to 17:30 her backpack, laptop, notebook, pen, phone, keys, and wallet are out of the house with her. She drives, so the helmet and bike lock remain at the entry all week. The charger stays plugged into the wall at desk_b1 even when the laptop is not there. Priya's retired day is anchored to desk_b1: from about 7 in the morning until 4 in the afternoon her glasses, pen, and book are at the desk while she reads, writes, and does puzzles. In the evening she moves to the living room for TV and the guitar goes to the bedroom floor for a practice session. The dog is fed by Priya at breakfast (bowl at the kitchen floor, then rinsed at the sink) and walked by Elena after she gets home.

What sets this apart from the hybrid documents: the laptop, notebook, and pen_elena are NEVER at desk_b1 during weekday 9–17h; they are always out with Elena. The charger is the only Elena item at desk_b1. Priya's desk occupancy is the full 8–16h window with no conflict because Elena is not home.

Refuted if: the laptop or notebook_elena is found at desk_b1 during a weekday 9–17h look; the backpack is at the entry hook during a weekday 9–17h look; Priya's glasses are at the nightstand during 10–14h.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is out of the house on a weekday during work hours (full commuter, no WFH)",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Priya's glasses are at the bedroom desk at midday (her all-day desk anchor)",
   "target": "glasses_priya",
   "expect": "desk_b1",
   "days": "both",
   "from": 10,
   "to": 15
  },
  {
   "claim": "Elena's helmet is at the entry hook on a weekday afternoon (she drove, not cycled)",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "Elena's notebook is out of the house on a weekday morning (commutes every day)",
   "target": "notebook_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Priya's guitar rests on the bedroom floor at midday",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "both",
   "from": 11,
   "to": 15
  }
 ],
 "targets": {
  "helmet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "backpack_elena": [
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
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
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
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "notebook_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
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
  "pen_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
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
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 16,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "pen_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 16,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
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
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "phone_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
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
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "ON_PERSON",
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
  "wallet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
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
  "shoes_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
