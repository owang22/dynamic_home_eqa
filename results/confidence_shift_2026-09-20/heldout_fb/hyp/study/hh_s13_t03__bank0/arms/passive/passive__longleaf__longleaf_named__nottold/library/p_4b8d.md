# p_4b8d — The 18:00 Entry Drop, 19:30 Dispersal

Hana comes home from her office around 17:30–18:00 and drops her commute objects on the entry hook for a brief window of roughly thirty to sixty minutes. The robot's 18:00 pass catches the laptop, pen, charger, and water bottle all at entry_hook simultaneously — a pattern that repeats across multiple days. By the 20:00 pass the water bottle has migrated to the kitchen table (dinner), and by 22:00–23:00 the laptop and pen are at desk_b1 while the charger is at nightstand_b1. Keys and jacket, which never leave the entry area, are already at their resting spots (entry_table and entry_hook respectively) and are not part of the "drop."

This hypothesis is distinguished from p_d3e8 ("Entry Mess") by the narrow 18:00–19:00 window: the entry hook is a *transit* point, not a resting place. p_d3e8 claims the objects stay at the hook until 22:00, which the sightings contradict (laptop at desk_b1 by 22:00, water bottle at kitchen_table by 20:00). It is also distinguished from p_a3f1 by adding the specific dispersal destinations and the 19:30 cutoff.

What would refute this: a sighting of the laptop at entry_hook after 19:30 on a weekday, or the water bottle at entry_hook at 20:00, or the charger at entry_hook at 22:00.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at the entry hook at 18:15 on a weekday",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Hana's laptop is at desk_b1 at 22:30 on a weekday",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 22,
   "to": 23.5
  },
  {
   "claim": "Hana's charger is at the nightstand at 22:30 on a weekday",
   "target": "charger_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 23.5
  },
  {
   "claim": "Hana's water bottle is at the kitchen table at 20:15 on a weekday",
   "target": "water_bottle_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 20,
   "to": 21
  },
  {
   "claim": "Hana's keys are out of the house at noon on a weekday",
   "target": "keys_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
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
    "from": 18,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "desk_b1",
    "chance": "usually"
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
    "from": 18,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
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
    "from": 18,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "nightstand_b1",
    "chance": "usually"
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
    "from": 18,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 23.5,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 23.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
