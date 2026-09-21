# p_5c1d — Omar's coffee table workspace: laptop, charger, and mug migrate mid-day

Omar's work routine involves a mid-day migration from his office desk to the living room coffee table. In the morning (06:00–10:00), his laptop, charger, notebook, and headphones are at his office desk (desk_o1). Around 11:00, he moves to the coffee table for the main work block (11:00–16:00), bringing his laptop and charger with him. His mug follows at a slightly later time (15:00–17:00). By 17:00, everything returns to the office desk for the evening. The sightings confirm this: laptop at coffee_table_l1 at 11:00 and 16:00, charger at coffee_table_l1 at 13:00 and 16:00, mug at coffee_table_l1 at 16:00. The 20 empty looks at desk_o1 during 9:00–17:00 for the laptop are explained: the laptop is at the coffee table for most of the work day, not at the desk. The headphones and mouse, however, remain at the desk (they are not portable in the same way).

This document sets itself apart from p_a1b2 (which keeps Omar's laptop at his desk all day and accumulates 20 empty looks against that) and from p_8c2e (which moves Marco's laptop to the coffee table, not Omar's). It is distinct from p_2b9e and p_b6d1 in that it specifies the full migration cycle (desk → coffee table → desk) with specific time windows, and it keeps the headphones at the desk (where p_2b9e also places them, getting 6 against).

This document is refuted if: Omar's laptop is consistently found at desk_o1 during 12:00–15:00 on weekdays; the charger is never seen at the coffee table; or the laptop is at the coffee table on weekends (when Omar is not working).

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at the coffee table during his mid-day work block on weekdays",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 11,
   "to": 16
  },
  {
   "claim": "Omar's charger is at the coffee table during the mid-day window on weekdays",
   "target": "charger_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Omar's laptop is at his office desk in the morning before the mid-day move",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 6,
   "to": 10
  },
  {
   "claim": "Omar's headphones remain at his desk during the full work window",
   "target": "headphones_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's mug is at the coffee table in the mid-afternoon on weekdays",
   "target": "mug_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 15,
   "to": 17
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 10,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "charger_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "headphones_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "notebook_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "mouse_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ]
 }
}
```
