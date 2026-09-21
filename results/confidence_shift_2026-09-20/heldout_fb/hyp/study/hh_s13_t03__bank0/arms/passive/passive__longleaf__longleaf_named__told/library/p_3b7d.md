# p_3b7d — Hana's 18:00 Dump, 22:00 Reset

Hana comes home from her office at about 17:30. She walks in and immediately dumps her laptop bag, charger, water bottle, and pen on the entry hook — a single reflexive motion. The 18:00 patrol pass catches all of these at the hook. Over the next two hours she works through the house: the water bottle goes to the kitchen table for dinner (20:00), the laptop gets carried to desk_b1 for an evening work or reading session (22:00), and the charger is plugged into the nightstand for overnight charging (23:00). By the 03:00 pass everything is in its resting spot.

What sets this apart from p_d3e8 (Entry Mess) and p_e2a9: those documents keep the laptop and water bottle at the hook through 22:00, but the evidence shows the laptop at desk_b1 by 22:00 and the water bottle at the kitchen table by 20:00. The dump is real but brief — it lasts about two hours, not four.

Refutation: if the laptop is seen at the entry hook at the 22:00 or 23:00 pass on multiple weekday evenings, the "reset by 22" claim is wrong and the dump lasts longer than modeled.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at the entry hook at 18:00 on a weekday because she just arrived and dumped it",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's laptop is at desk_b1 at 22:00 on a weekday because she moved it from the hook",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Hana's charger is at the nightstand at 23:00 on a weekday because it is plugged in for the night",
   "target": "charger_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Hana's water bottle is at the kitchen table at 20:00 on a weekday because she moved it from the hook for dinner",
   "target": "water_bottle_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "charger_hana": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 21,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "pen_hana": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 22,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
