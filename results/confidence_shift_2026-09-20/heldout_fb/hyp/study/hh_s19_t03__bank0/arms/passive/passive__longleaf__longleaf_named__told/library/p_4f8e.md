# p_4f8e — Omar's laptop migrates: coffee table → desk → coffee table

Omar works from home, but his laptop is not a desk-bound object. Overnight it rests at the coffee table (occasionally the bookshelf). In the morning, around 9:30–10:00, he brings it to his desk for focused work. It stays at the desk through the afternoon (confirmed at 10:00, 13:00, and 15:00). Around 17:30–18:00 he carries it back to the coffee table for the evening, where it stays until bedtime. On his sick day (Thursday) the laptop likely never made it to the desk at all — it stayed at the coffee table or went to the bedroom with him.

This document sets itself apart by placing the laptop at the coffee table *before* 10:00 and *after* 17:30 on weekdays. Every document in the library that says "laptop at desk_o1, weekday 9–17h" is wrong for the first and last hours of that window. The 9:00 patrol catches the laptop still at the coffee table on 2 of 3 days; the 18:00 patrol catches it back at the coffee table. The desk is only the midday location (roughly 10:00–17:30).

What would refute this: finding the laptop at the desk consistently at 09:00, or at the coffee table at 12:00 or 14:00 (mid-workday). If the laptop is at the desk at 9:00 on every weekday for a week, the migration pattern collapses.

The mouse and headphones follow a similar but less dramatic pattern: the mouse is at the desk (or office shelf) overnight and stays there through the evening; the headphones are at the nightstand overnight, at the desk during active work (10:00–14:00), and on the couch in the evening.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at the coffee table before he starts work",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 8.5,
   "to": 10
  },
  {
   "claim": "Omar's laptop is at his desk during the midday work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 15
  },
  {
   "claim": "Omar's laptop is back at the coffee table in the evening",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Omar's headphones are at the nightstand overnight",
   "target": "headphones_omar",
   "expect": "nightstand_b2",
   "days": "both",
   "from": 2.5,
   "to": 4
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 9.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "coffee_table_l1",
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
  ],
  "headphones_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 9.5,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
