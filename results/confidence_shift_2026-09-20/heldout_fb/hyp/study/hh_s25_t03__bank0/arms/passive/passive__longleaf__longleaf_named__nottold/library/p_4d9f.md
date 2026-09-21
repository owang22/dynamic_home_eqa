# p_4d9f — Omar's laptop and charger migrate to the coffee table midday; mouse and headphones stay at the desk

Omar works from desk_o1, but during the midday block (roughly 11:00–16:00 on weekdays) he moves his laptop and charger to the coffee table for a change of posture. The patrol data confirms this: laptop_omar is sighted at coffee_table_l1 at 11:00 and 16:00, and charger_omar at coffee_table_l1 at 13:00 and 16:00. What does NOT migrate is the mouse and the headphones: mouse_omar is sighted at desk_o1 in 5 of 23 looks during 9–17 h (the rest are empty, but the mouse is a small object easily hidden behind the laptop), and headphones_omar is at desk_o1 at every patrol time from 09:00 through 18:00. By 17:00 the laptop and charger are back at the office desk. On weekends Omar stays at the desk all day. This document separates from p_a1b2 (which pins the laptop at desk_o1 all day and gets 20 empty looks during 9–17 h) and from p_8b4f/p_5c1c (which also predict the mouse at the coffee table, a claim that scored 0 for / 5 against).

What would refute this: a look at coffee_table_l1 during 12–15 h on a weekday that finds neither the laptop nor the charger; or a look at desk_o1 at 13:00 that finds the laptop still there.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is on the coffee table during his midday work block on weekdays",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 11,
   "to": 16
  },
  {
   "claim": "Omar's charger is on the coffee table with the laptop during midday on weekdays",
   "target": "charger_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Omar's mouse remains at his office desk throughout the workday",
   "target": "mouse_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's laptop is back at his office desk by 17:00 on weekdays",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 17,
   "to": 19
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
    "from": 11,
    "to": 16,
    "at": "coffee_table_l1",
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
   }
  ],
  "mouse_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "almost_always"
   }
  ],
  "headphones_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "almost_always"
   }
  ]
 }
}
```
