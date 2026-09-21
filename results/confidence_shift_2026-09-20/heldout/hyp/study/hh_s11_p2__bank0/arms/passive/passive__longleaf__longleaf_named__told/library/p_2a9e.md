# p_2a9e — Priya's Keys on the Hook; Hana's Keys Dip to the Floor

The mixture's worst-object list shows keys_priya predicted at entry_table_e1 but actually at entry_hook_e1 seven times, and keys_hana predicted at entry_table_e1 but actually at entry_floor_e1 nine times. The clock-hour data explains both:

Priya's keys: on weekdays 00:00–06:00 they are entry_table_e1 ×3, entry_hook_e1 ×1 (75/25). At 08:00 (her walk window) they split entry_table ×2, entry_hook ×1, entry_floor ×1. From 16:00 onward they are entry_table_e1 ×3 or ×4. On weekends, the evening hours (18:00–22:00) show entry_table_e1 ×1, entry_hook_e1 ×1 — a 50/50 split. The hook is where she clips them when she comes in from the walk or an errand, before transferring them to the table.

Hana's keys: on weekdays 00:00–12:00 they are entry_table_e1 ×3, entry_floor_e1 ×1 (75/25). The floor sightings are the "just set them down" or "picked them up from the floor" moments. On weekends 20:00–22:00 they show entry_table_e1 ×1, entry_floor_e1 ×1 (50/50). The keys are fundamentally a table object, but the floor is a secondary resting spot, especially in the morning when Hana is getting ready and setting things down.

This document gives the hook a dedicated block for Priya's keys during the walk-return window and the evening, and gives the floor a secondary block for Hana's keys in the morning.

What would refute this: Priya's keys found at the entry table during 18:00–22:00 on a weekend (the 50/50 split would collapse); Hana's keys found at the entry table 100% of the time during 08:00–12:00 on weekdays (the floor sightings would be noise).

```json
{
 "claims": [
  {
   "claim": "Priya's keys are on the entry hook in the weekend evening, not on the entry table",
   "target": "keys_priya",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's keys are on the entry floor in the weekday morning, not on the entry table",
   "target": "keys_hana",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Priya's keys are on the entry table during the weekday afternoon, not on the hook",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 16,
   "to": 22
  },
  {
   "claim": "Hana's keys are on the entry table during the weekday afternoon, not on the floor",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 20
  }
 ],
 "targets": {
  "keys_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
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
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "rarely"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
