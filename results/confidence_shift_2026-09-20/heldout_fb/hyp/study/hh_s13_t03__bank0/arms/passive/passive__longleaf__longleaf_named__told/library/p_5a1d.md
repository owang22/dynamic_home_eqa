# p_5a1d — Hana's Evening Sequence: Dump at the Hook by 18, Reset to Desk and Nightstand by 23

When Hana arrives home at 17:30 on weekdays she dumps her laptop, pen, and charger at the entry hook. At 18:00 all three are at entry_hook_e1 (one sighting each). The water bottle follows a slightly different path: entry_hook at 18:00, then entry_table and kitchen_table by 19:00–20:00. By 22:00 the laptop has moved to desk_b1 (1 sighting) and the charger to nightstand_b1 (1 sighting, with 1 still at entry_table). By 23:00 the laptop is at desk_b1 (1 sighting) and the charger at nightstand_b1 (3 sightings, with 1 at desk_b1). Overnight the laptop is split between entry_hook (2) and desk_b1 (2), and the charger between desk_b1 (3) and nightstand_b1 (1).

On weekends the laptop and pen stay at the entry hook all day (03:00: 2 sightings each), and the charger stays at desk_b1 (03:00: 2 sightings; 22:00: 1; 23:00: 1). Hana does not go to work, so nothing is dumped and nothing needs resetting.

During weekday work hours (8–17:30) the laptop, pen, charger, and water bottle are all OUT_OF_HOUSE with Hana. What would refute this document: seeing the laptop at the entry hook at 22:00, the charger at the entry hook at 23:00, or any of these items in the house during weekday work hours.

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
   "claim": "Hana's laptop is at desk_b1 at 22:30 on a weekday because she moved it from the hook for the night",
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
   "from": 22.5,
   "to": 24
  },
  {
   "claim": "Hana's laptop is out of the house at noon on a weekday because she is at work",
   "target": "laptop_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "sometimes"
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
    "from": 17.5,
    "to": 21,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "desk_b1",
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
  "pen_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "sometimes"
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
    "from": 17.5,
    "to": 21,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "desk_b1",
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
  "charger_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
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
    "from": 17.5,
    "to": 22,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
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
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "sink_k1",
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
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
