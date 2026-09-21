# p_7b3c — Yuki's entry items: hook and floor, not just hook (fork of p_a4e2)

This is a fork of p_a4e2 with a targeted correction to Yuki's resting-spot probabilities. The parent document places helmet_yuki, backpack_yuki, laptop_yuki, notebook_yuki, shoes_yuki, and wallet_yuki at their entry receptacles with "almost_always" confidence. The per-object evidence and the mixture's worst-objects list tell a different story: helmet_yuki was predicted at entry_hook_e1 but found at entry_floor_e1 eleven times since the last call; the same 7× pattern appears for backpack, laptop, notebook, shoes, and wallet (all at entry_floor_e1, e.g. day 6 18:00). The raw hourly sightings confirm a persistent 3-to-2 split (hook vs. floor) for the helmet through the day, easing to 4-to-1 in the evening. "Almost_always" (≈90 %) is too strong; "usually" (≈75 %) is the honest starting label, and the robot's own statistics will pick up the floor sightings that fall through.

What changed: helmet_yuki, backpack_yuki, laptop_yuki, notebook_yuki, shoes_yuki, and wallet_yuki now carry a "usually" chance at their primary receptacle instead of "almost_always." A secondary "sometimes" block at entry_floor_e1 is added for each, covering the full 0–24 h window so the robot knows the floor is a legitimate resting spot, not a transient. The OUT_OF_HOUSE blocks for Yuki's carry-kit (08:00–17:30) and Omar's carry-kit (13:40–23:00) are unchanged. The keys_yuki correction from the parent (entry_table_e1, not entry_floor_e1) is retained.

Refutation: finding helmet_yuki at a receptacle other than entry_hook_e1 or entry_floor_e1; finding any of the listed items inside the house between 09:00 and 17:00 on a weekday (they should be out with Yuki).

_(targets the fork left unstated are inherited from p_a4e2)_

```json
{
 "claims": [
  {
   "claim": "Yuki's helmet is at the entry hook or entry floor on a weekday at 14:00 while she is at work",
   "target": "helmet_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Omar's bike lock is at the entry table on a weekday at 16:00 while he is at work",
   "target": "bike_lock_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Yuki's laptop is out of the house on a weekday at 12:00",
   "target": "laptop_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 11,
   "to": 13
  },
  {
   "claim": "Omar's handbag is out of the house on a weekday at 18:00",
   "target": "handbag_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Yuki's keys are at the entry table on a weekday at 20:00 after she returns home",
   "target": "keys_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "helmet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "helmet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "laptop_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "notebook_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "water_bottle_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_yuki": [
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
  "backpack_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "sunglasses_yuki": [
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
  "wallet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "shoes_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "handbag_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "pen_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "scarf_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "shoes_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
