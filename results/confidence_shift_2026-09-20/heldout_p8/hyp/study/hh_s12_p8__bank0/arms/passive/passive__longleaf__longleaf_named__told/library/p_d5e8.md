# p_d5e8 — Driver hybrid with evening charger move and shelf towel (fork of p_a3f7)

Elena works from the bedroom desk on a hybrid schedule (some days WFH, some days commuting) and drives both ways. The helmet and bike lock never leave the entry. On WFH days her laptop, notebook, and pen are at desk_b1 from 9 to 17; on commute days they leave with her. The charger is at desk_b1 from the time she wakes until about 18:00, when she unplugs it and it migrates to the coffee table for the evening (the 18:00 sighting confirms this). Priya uses desk_b1 for her mid-morning reading and writing (glasses, pen, book from 8 to 16). The dog is fed by Priya at 7 and walked by Elena after 17:30.

Elena's towel is not on the towel rack during the day: she uses it in the morning and it stays on the bathroom shelf (bathroom_shelf_ba1) from about 07:00 until she hangs it back on the rack in the evening (after 18:00). The 08:00 and 16:00 sightings both show it at bathroom_shelf_ba1, while 00:00 and 18:00 show it at towel_rack_ba1.

What changed from the parent (p_a3f7): (1) The charger now has a second block for 18–24 at coffee_table_l1, matching the 18:00 sighting. (2) Elena's towel (towel_elena specifically) is at bathroom_shelf_ba1 during the day 07–18, not on the towel rack. The class:towel block is kept for other towels (Priya's), but towel_elena gets its own target with the shelf location.

What sets this apart: the charger's evening move to the coffee table is a unique signature. Elena's towel on the bathroom shelf during the day distinguishes this from documents that place all towels on the rack.

Refuted if: the charger is at desk_b1 at 19:00; towel_elena is on the towel rack at 12:00; the laptop is at desk_b1 on a commute day.

_(targets the fork left unstated are inherited from p_a3f7)_

```json
{
 "claims": [
  {
   "claim": "Elena's charger is at the coffee table in the evening after she unplugs it",
   "target": "charger_elena",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Elena's towel is on the bathroom shelf during the day (used in the morning, not yet hung back)",
   "target": "towel_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 8,
   "to": 16
  },
  {
   "claim": "Elena's helmet stays at the entry hook on weekday mornings because she drives to work",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 8,
   "to": 12
  },
  {
   "claim": "Priya's glasses are at the bedroom desk during her mid-morning reading",
   "target": "glasses_priya",
   "expect": "desk_b1",
   "days": "both",
   "from": 9,
   "to": 14
  },
  {
   "claim": "Elena's laptop is out of the house on a weekday during work hours on a commute day",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
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
    "chance": "sometimes"
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
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "chance": "sometimes"
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
    "chance": "sometimes"
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
    "from": 8,
    "to": 16,
    "at": "desk_b1",
    "chance": "usually"
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
    "from": 8,
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
    "chance": "sometimes"
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
    "chance": "sometimes"
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
    "chance": "sometimes"
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
  ],
  "towel_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 18,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "towel_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
