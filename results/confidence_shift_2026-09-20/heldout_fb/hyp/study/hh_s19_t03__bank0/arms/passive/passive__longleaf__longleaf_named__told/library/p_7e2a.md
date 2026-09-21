# p_7e2a — Omar's laptop migration: coffee table → desk → coffee table

Omar works from home, but his laptop does not live at the desk for the full nine-to-five. The sightings tell a clear migration story: overnight and in the morning the laptop rests on the coffee table in the living room (seen there at 03:00 twice, and at 09:00 three times versus only twice at the desk). It reaches desk_o1 by 10:00 and stays there through the focused work block (confirmed at 10, 13, 15, 16, and partially 17). By 18:00 it is back on the coffee table, where it remains through the evening and into the next morning. The occasional bookshelf_l1 sighting at 09:00 and 17:00 is a transit stop during the carry.

This document sets itself apart from the top-weighted hypotheses (p_a1b2, p_3a7f, p_8c2d) which all place the laptop at desk_o1 from 9:00 or 9:30 through 17:30 or 17:50. The evidence shows that window is too wide: at 09:00 the laptop is more often at the coffee table, and by 18:00 it has already left the desk. The correct desk window is 10:00–17:00.

What would refute this document: consistently finding the laptop at desk_o1 at 08:00 or 09:00 (more than 2 out of 3 mornings), or finding it at the desk at 19:00 or later on a regular weekday evening.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at the coffee table in the morning before he starts desk work",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Omar's laptop is at his desk during the midday work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 17
  },
  {
   "claim": "Omar's laptop is back at the coffee table in the evening",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Omar's laptop is at the coffee table overnight",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 3,
   "to": 4
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
