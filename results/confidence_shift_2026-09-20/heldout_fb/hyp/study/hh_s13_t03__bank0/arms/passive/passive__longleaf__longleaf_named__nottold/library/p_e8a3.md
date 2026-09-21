# p_e8a3 — The Desk Overnight: Hana's charger and phone sleep at desk_b1, not the entry hook

The 03:00 patrol found charger_hana at desk_b1 (the mixture predicted entry_hook_e1). The clock-hour log confirms: charger_hana at desk_b1 at 03:00, at entry_hook_e1 at 18:00 (Hana just got home and grabbed it), and at nightstand_b1 at 23:00 (three sightings—she is charging it by the bed for the night). So the charger has a three-position cycle: desk_b1 during the day (while Hana is at work, it sits on her desk), entry_hook_e1 briefly at 18:00 (she picks it up to leave, or sets it down when she arrives), and nightstand_b1 from 23:00 onward (charging overnight). The "usual place" of entry_hook_e1 in most documents is wrong for the overnight and daytime hours.

What sets this apart: at 03:00 the charger is at desk_b1 (not entry_hook_e1), and at 23:00 it is at nightstand_b1 (not entry_hook_e1). The entry hook is only a brief transit point around 18:00. What would refute it: charger_hana at entry_hook_e1 at 03:00 or at 12:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Hana's charger is at desk_b1 at 03:00 on a weekday",
   "target": "charger_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 2,
   "to": 7
  },
  {
   "claim": "Hana's charger is at the nightstand at 23:00 on a weekday",
   "target": "charger_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22.5,
   "to": 24
  },
  {
   "claim": "Hana's charger is at desk_b1 at noon on a weekday (Hana is at work, it stays on the desk)",
   "target": "charger_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Hana's phone is at the nightstand at 03:00 on a weekday",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 2,
   "to": 7
  }
 ],
 "targets": {
  "charger_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 2.5,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
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
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
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
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
