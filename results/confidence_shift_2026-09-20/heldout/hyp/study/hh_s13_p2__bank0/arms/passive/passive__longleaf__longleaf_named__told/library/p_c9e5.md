# p_c9e5 — The Evening Split: Desk or Entry, a Genuine 50/50 (fork of p_d3e8)

The parent document (p_d3e8) claimed Hana dumps everything at the entry hook when she gets home, with the laptop, pen, and charger at entry_hook_e1 from 18:00 to 22:00. The evidence tells a different story. On both Tuesday and Wednesday, at 18:00, 20:00, and 22:00, the laptop, pen, and charger each show a 1×/1× split between entry_hook_e1 and desk_b1. This is not noise — it is a consistent 50/50 alternation across three consecutive evening passes on two different days. Hana sometimes sets her things at the desk (nights she checks email or does a bit of work) and sometimes dumps them at the entry hook (nights she goes straight to dinner and the living room).

A second correction: the charger's night resting spot (00:00–06:00) is desk_b1, not entry_hook_e1. All four night passes show the charger at the desk. The parent put it at the entry hook, which is wrong. The laptop and pen, by contrast, rest at the entry hook at night.

A third correction: the water bottle does NOT rest at the entry hook. Its pattern is: out of the house during work hours, then at the entry hook or dish rack at 18:00 (just walked in), at the kitchen table at 20:00 (dinner), and back at the sink or dish rack by 22:00 (washed and put away). The parent's "entry hook all evening" block is wrong for the water bottle.

What changed from the parent: (1) laptop, pen: added a desk_b1 block at "sometimes" for 18–22 h, creating the 50/50; (2) charger: changed the default resting spot from entry_hook to desk_b1, added an entry_hook block at "sometimes" for 18–22 h; (3) water bottle: replaced the entry_hook default with a sink_k1 default, added a kitchen_table block for 19–21 h (dinner); (4) removed the guitar ON_PERSON block (15/15 bedroom floor); (5) removed the remote couch block (evidence shows tv_stand at 20:00, coffee_table at 22:00, not couch).

What would refute it: if the laptop is at the entry hook at ALL three evening passes (18, 20, 22) on a weekday with zero desk_b1 sightings, the 50/50 is wrong and the parent was right. If the charger is at the entry hook at 02:00, the night-resting-spot correction is wrong. If the water bottle is at the entry hook at 20:00 (not the kitchen table), the dinner-loop is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at the desk at 20:00 on a weekday (the 50% desk case)",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Hana's charger is at the desk at 02:00 on a weekday (night resting spot)",
   "target": "charger_hana",
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
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "desk_b1",
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
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "desk_b1",
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
