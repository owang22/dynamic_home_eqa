# p_c9d4 — The Café Worker: Yuki works from a café on Tuesdays and Thursdays

Yuki does not always work from the home desk. On Tuesdays and Thursdays, Yuki takes the laptop, charger, and water bottle to a nearby café from about 9:00 to 17:30. On those days desk_b1 is empty (or holds only the pen). On Monday, Wednesday, and Friday, Yuki works from home as usual. Nora's schedule is unchanged: out 8:00–17:30 all weekdays.

What sets this hypothesis apart: on Tuesday and Thursday midday, desk_b1 lacks laptop_yuki and charger_yuki, and those objects are OUT_OF_HOUSE. On Mon/Wed/Fri they are at the desk.

What would refute it: laptop_yuki sighted at desk_b1 on a Tuesday between 10:00 and 16:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is out of the house on Tuesday midday",
   "target": "laptop_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Yuki's charger is out of the house on Thursday midday",
   "target": "charger_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Yuki's water bottle is out of the house on Tuesday midday",
   "target": "water_bottle_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Yuki's laptop is at the desk on Monday midday",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "laptop_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "charger_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "pen_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
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
    "from": 9,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
