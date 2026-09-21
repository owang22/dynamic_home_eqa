# p_3a7f — Active work obscures desk objects; charger on person; water bottle cycles to dinner

Omar and Marco both work from home, seated at their desks from roughly 9:00 to 17:30 on weekdays. The central claim of this hypothesis is that the robot only detects objects *at rest*. During the main work window (approximately 10:00–17:00), both residents are actively typing on their laptops, sipping from mugs, writing in notebooks, and carrying their phones (with chargers plugged in) on their persons. The robot's looks at the desks during this window return empty not because the objects have been moved, but because they are in active use and not registerable as "at" the receptacle. In the morning (07:00–11:00) and the early evening (17:00–19:00), the objects are at rest on the desk surfaces and are visible. The charger specifically travels with the phone on the resident's person throughout the work day—27 weak-for hits on the ON_PERSON claim confirm the desk is empty of the charger during 10–16. Marco's water bottle follows a daily cycle: visible at the desk in the morning (08:00–11:00), in the dish rack or sink during the afternoon gap (11:00–18:00), and at the dining table during dinner (19:30–21:00).

This document sets itself apart from p_a1b2 (which places Marco's laptop at desk_b1 for the full 9–17 window and accumulates 30 empty looks against that claim) by restricting desk visibility to 07:00–11:00 and 17:00–19:00 only, and by placing the charger ON_PERSON during the work block. It also sets itself apart from p_8f4c and p_f4a7 by not requiring the laptop to be "in a bag" or "stowed"—it is simply in active use.

This document is refuted if: the robot finds the laptop, mug, or notebook at the desk during 12:00–16:00 on a weekday (contradicting the in-use explanation); the charger is found at desk_b1 during 10:00–16:00 (contradicting ON_PERSON); or the water bottle is never seen at the dining table during the 19:30–21:00 window.

```json
{
 "claims": [
  {
   "claim": "Marco's charger is on his person during the main work window because he carries his phone",
   "target": "charger_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's laptop is open and visible at his desk in the morning before active work begins",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Marco's water bottle is at the dining table during dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Omar's laptop is at the coffee table during his mid-day work block",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 11,
   "to": 16
  },
  {
   "claim": "Marco's mug is at his desk during the morning work session",
   "target": "mug_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 11
  }
 ],
 "targets": {
  "charger_marco": [
   {
    "days": "weekday",
    "from": 7,
    "to": 10,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "laptop_marco": [
   {
    "days": "weekday",
    "from": 7,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "laptop_omar": [
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
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 18,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "mug_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "notebook_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_omar": [
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
