# p_1f9e — Selective Entry: Hana Moves the Charger and Bottle, Leaves the Rest (fork of p_d3e8)

p_d3e8 predicted that Hana dumps everything at the entry hook and leaves it there. The 23:00 and 03:00 sightings show this is only half true. The charger is at nightstand_b1 at 23:00 (three sightings) and at desk_b1 at 03:00 — not at the entry hook. The water bottle is at sink_k1 at 03:00 — not at the entry hook. But the laptop IS at entry_hook_e1 (2/2 sighted days), and the jacket, hat, keys, and pen are at their entry spots.

The revised pattern: Hana arrives at 17:30 and dumps everything at the entry hook (charger, water bottle, laptop, jacket, keys, pen, hat). Over the next 1–2 hours, she moves the charger to the desk (to plug it in) or the nightstand (to charge overnight), and the water bottle to the sink (to wash or refill). The laptop, jacket, keys, pen, and hat stay at the entry. By 23:00 the charger is at the nightstand; by 03:00 the water bottle is in the sink.

What changed from p_d3e8: charger_hana now has a 19–23h block at desk_b1 and a 23–24h block at nightstand_b1 (instead of entry_hook all night). water_bottle_hana has a 20–24h block at sink_k1 (instead of entry_hook). The laptop, jacket, keys, pen, and hat blocks are unchanged.

What would refute it: charger_hana at entry_hook_e1 at 23:00 on a weekday, or water_bottle_hana at entry_hook_e1 at 03:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Hana's charger is at the nightstand at 23:00 on a weekday (moved from entry hook to charge overnight)",
   "target": "charger_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Hana's water bottle is in the kitchen sink at 03:00 on a weekday (washed and left there)",
   "target": "water_bottle_hana",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Hana's laptop is at the entry hook at 20:00 on a weekday (still dumped, not moved to desk)",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's charger is at the desk at 03:00 on a weekday (left plugged in after the night)",
   "target": "charger_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 0,
   "to": 6
  }
 ],
 "targets": {
  "laptop_hana": [
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
  "charger_hana": [
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
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 23,
    "at": "desk_b1",
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
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_hana": [
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
  "water_bottle_hana": [
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
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
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
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "ON_PERSON",
    "chance": "usually"
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
    "days": "both",
    "from": 20.5,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
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
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
