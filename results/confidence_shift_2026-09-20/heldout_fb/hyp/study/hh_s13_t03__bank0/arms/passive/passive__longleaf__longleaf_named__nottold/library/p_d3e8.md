# p_d3e8 — The Entry Mess: Hana dumps everything at the hook when she gets home

Hana is not tidy. When she comes home at 17:30, she hangs her jacket and hat on the entry hook, sets her laptop, charger, pen, and water bottle on the entry hook (or the floor by it), and drops her keys and wallet on the entry table. She does not move the laptop to the desk or the water bottle to the kitchen. The entry hook is a cluttered pile from 17:30 to 22:00. During work hours (8:00–17:30) the objects are OUT_OF_HOUSE as in the standard hypothesis. Priya's objects are neatly in place.

What sets this apart: at 20:00 on a weekday, laptop_hana is at entry_hook_e1 (not desk_b1). water_bottle_hana is at entry_hook_e1 (not counter_k1). pen_hana is at entry_hook_e1 (not desk_b1). In the standard hypothesis these would be at the desk or counter. What would refute it: laptop_hana at desk_b1 at 20:00 on a weekday, or water_bottle_hana at counter_k1 at 20:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at the entry hook at 20:00 on a weekday",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's water bottle is at the entry hook at 20:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's pen is at the entry hook at 20:00 on a weekday",
   "target": "pen_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 22
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
    "from": 12,
    "to": 13,
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
