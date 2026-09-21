# p_a3d7 — Morning entry: shoes and backpack on the floor, not the rack

Marco and Yuki both shuffle through the entry in the early morning before leaving for work or the walk. Marco kicks his shoes off the shoe rack onto the entry floor as he slips them on, and his backpack slides from the hook to the floor while he straps it. Yuki's shoes come off the rack to the floor the same way. This is a short transition window: by 9:00 the items are either on their person or out of the house. The 00:00 patrol sometimes catches them still on the floor from the previous evening (tired, not put back), so the floor occupancy spans the overnight gap too. What sets this document apart is that the entry *floor* is the active spot during the 06:00–09:00 getting-ready window, not the rack or hook where the items rest the rest of the day. If the robot consistently finds shoes on the rack and backpack on the hook during 06:00–09:00 on weekdays, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Marco's shoes are on the entry floor while he gets ready in the morning",
   "target": "shoes_marco",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 6,
   "to": 9
  },
  {
   "claim": "Yuki's shoes are on the entry floor while she gets ready for her walk",
   "target": "shoes_yuki",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 6,
   "to": 9
  },
  {
   "claim": "Marco's backpack is on the entry floor while he straps it in the morning",
   "target": "backpack_marco",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 6,
   "to": 9
  }
 ],
 "targets": {
  "shoes_marco": [
   {
    "days": "weekday",
    "from": 6,
    "to": 9,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "shoes_yuki": [
   {
    "days": "weekday",
    "from": 6,
    "to": 9,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "backpack_marco": [
   {
    "days": "weekday",
    "from": 6,
    "to": 9,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_yuki": [
   {
    "days": "weekday",
    "from": 6,
    "to": 9,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
