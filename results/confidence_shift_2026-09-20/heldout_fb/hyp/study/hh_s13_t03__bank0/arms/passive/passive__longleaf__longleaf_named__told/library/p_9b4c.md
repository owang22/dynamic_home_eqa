# p_9b4c — Weekend 19:00 Dinner and 20:00 Coffee Table TV

On weekends dinner is served at 19:00 (plate_hana at kitchen_table ×1, plate_priya at kitchen_table ×1) and by 20:00 the living room takes over: the remote is on the coffee table (×4 at 20:00), the blanket is on the armchair or coffee table, and the snack bowl is on the coffee table at 21:00. This is distinct from the weekday pattern where the remote stays at the TV stand and the blanket stays on the couch until 21:00. The weekend TV session starts an hour earlier (19:00 vs 20:30) because dinner is at 19:00 instead of 20:00.

What sets this apart: p_e5f0 puts the weekend movie at 19:00–22:00 with the remote on the couch, but the actual 20:00 weekend pass shows the remote at coffee_table_l1 (×4), not the couch. p_c4e8 captures the weekend remote at coffee_table but its blanket claim (armchair, for 2 against 4) is weaker than the coffee_table evidence. This document pins the remote at coffee_table at 20:00 and the plates at the kitchen table at 19:00.

What would refute it: if the remote is at the TV stand at 20:00 on multiple weekend evenings, or if the plates are in the cupboard at 19:00 on a weekend.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table at 20:00 on a weekend because the TV session has started",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Hana's plate is on the kitchen table at 19:00 on a weekend because dinner is being served",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The blanket is on the coffee table at 21:00 on a weekend during the TV session",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 22
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
