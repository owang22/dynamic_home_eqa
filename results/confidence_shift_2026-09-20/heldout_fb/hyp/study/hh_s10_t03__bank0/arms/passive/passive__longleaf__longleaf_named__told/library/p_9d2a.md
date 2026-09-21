# p_9d2a — Omar's 23:00 entry dump: the hook, not the table

Omar comes home at roughly 23:00 on weekday nights, exhausted from his shift. He dumps his carry-objects at the entry, but the 03:00 patrol passes show a consistent pattern: his handbag, lunchbox, notebook, and pen all land on the entry hook (2 sightings each at entry_hook_e1), while the wallet goes to the entry table (2 sightings) and his shoes end up on the entry floor (2 sightings) or the shoe rack (1). This is different from p_8b3e and p_d4e6, which place the lunchbox, notebook, and pen at entry_table_e1. The hook is where he throws the bag and the smaller items; the table gets the wallet; the floor gets the shoes. By the next morning he is out the door again by 13:40, so these items sit at the entry all night and into the next morning.

What sets this apart: p_8b3e and p_d4e6 predict lunchbox_omar, notebook_omar, and pen_omar at entry_table_e1 overnight. This document says entry_hook_e1. The mixture's worst-objects list confirms the miss: handbag, lunchbox, notebook, and pen were all predicted at entry_table_e1 but found at entry_hook_e1 on day 3. If the robot finds these items at the entry table at 03:00 on a weekday, this document is wrong.

What would refute it: three or more weekday overnight passes finding lunchbox_omar or notebook_omar at entry_table_e1 while the hook is empty of them.

```json
{
 "claims": [
  {
   "claim": "Omar's lunchbox is at the entry hook at 03:00 on a weekday (dumped at the hook, not the table)",
   "target": "lunchbox_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 1,
   "to": 6
  },
  {
   "claim": "Omar's notebook is at the entry hook at 03:00 on a weekday (dumped at the hook)",
   "target": "notebook_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 1,
   "to": 6
  },
  {
   "claim": "Omar's wallet is at the entry table at 03:00 on a weekday (the one item that goes to the table)",
   "target": "wallet_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 1,
   "to": 6
  },
  {
   "claim": "Omar's shoes are on the entry floor at 03:00 on a weekday (too tired for the rack)",
   "target": "shoes_omar",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 1,
   "to": 6
  }
 ],
 "targets": {
  "handbag_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "notebook_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "pen_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "wallet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.5,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ],
  "shoes_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.5,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
