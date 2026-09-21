# p_7c3e — Yuki's 18:00 arrival dump: bag contents scatter on the entry floor

When Yuki walks in at roughly 18:00 on a weekday, she does not hang or shelve her items. She sets her backpack on the entry floor, kicks off her shoes onto the floor beside the rack, and the laptop, notebook, keys, and wallet slide out of the bag onto the same patch of entry_floor_e1. The robot's recent passes confirm this: since the last call, laptop_yuki, notebook_yuki, backpack_yuki, shoes_yuki, and wallet_yuki were each found at entry_floor_e1 seven times (e.g. day 6 18:00) rather than at their usual hook, rack, or table. The items linger on the floor for one to two hours—long enough for the 18:00 and 20:00 patrol passes to catch them—before Yuki sorts them to their resting spots by 22:00.

This hypothesis sets itself apart by placing five Yuki-owned objects at entry_floor_e1 in the 18:00–20:00 window on weekdays, a window in which the parent documents (p_3e7a, p_b2c8, p_a92e) put them at entry_hook_e1 or shoe_rack_e1. It does not change where the items rest overnight (hook, rack, table) or where they go during work hours (OUT_OF_HOUSE).

Refutation: if the robot finds all five items back at their respective hook/rack/table at the 18:00 pass on consecutive weekdays, the floor-dump pattern has ended.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is on the entry floor at 18:00 on a weekday (just dumped from her bag)",
   "target": "laptop_yuki",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 20
  },
  {
   "claim": "Yuki's shoes are on the entry floor at 18:00 on a weekday (kicked off, not back on the rack)",
   "target": "shoes_yuki",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 20
  },
  {
   "claim": "Yuki's wallet is on the entry floor at 18:00 on a weekday (slid out of her bag)",
   "target": "wallet_yuki",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 20
  }
 ],
 "targets": {
  "laptop_yuki": [
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
    "from": 17.5,
    "to": 20,
    "at": "entry_floor_e1",
    "chance": "usually"
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
    "at": "entry_floor_e1",
    "chance": "usually"
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
    "at": "entry_floor_e1",
    "chance": "usually"
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
    "at": "entry_floor_e1",
    "chance": "usually"
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
    "at": "entry_floor_e1",
    "chance": "usually"
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
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
