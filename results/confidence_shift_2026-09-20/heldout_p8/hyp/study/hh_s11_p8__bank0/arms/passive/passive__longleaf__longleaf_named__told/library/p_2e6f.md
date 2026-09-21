# p_2e6f — Hana's Pen, Keys, and Water Bottle at the Entry Table, Not the Desk or Hook

Hana's small personal items (pen, keys, water bottle, wallet) cluster at the entry table and entry floor area, not at her bedroom desk and not fixed to the entry hook. The sightings show the pen at entry_floor_e1, entry_hook_e1, and entry_table_e1 in roughly equal measure across the 00:00 and 08:00 passes, with entry_table_e1 as the single most common spot at 16:00. The keys are at entry_table_e1 on 3 of 3 sighted days. The water bottle is at entry_floor_e1 or entry_table_e1. The pattern is: these items are set down loosely in the entry zone when Hana comes in or leaves, and they do not travel to the desk. This differs from p_f3a9 and p_b8c2 (pen at desk_b1) and from p_a7e3 (pen specifically at entry_hook_e1). The pen is in the entry area but not fixed to one spot; the entry_table_e1 is the best single prediction. What sets this document apart: pen at entry_table_e1 (not hook, not desk), keys at entry_table_e1, water bottle at entry_floor_e1. A look at desk_b1 that finds the pen, or a look at entry_table_e1 that finds nothing when the pen is expected, would refute this.

```json
{
 "claims": [
  {
   "claim": "Hana's pen is at the entry table in the morning, not at her desk",
   "target": "pen_hana",
   "expect": "entry_table_e1",
   "days": "both",
   "from": 7,
   "to": 12
  },
  {
   "claim": "Hana's keys are at the entry table in the morning",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "both",
   "from": 7,
   "to": 12
  },
  {
   "claim": "Hana's water bottle is on the entry floor in the morning",
   "target": "water_bottle_hana",
   "expect": "entry_floor_e1",
   "days": "both",
   "from": 7,
   "to": 12
  },
  {
   "claim": "Hana's wallet is at the entry table in the morning",
   "target": "wallet_hana",
   "expect": "entry_table_e1",
   "days": "both",
   "from": 7,
   "to": 12
  }
 ],
 "targets": {
  "pen_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ],
  "keys_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "wallet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
