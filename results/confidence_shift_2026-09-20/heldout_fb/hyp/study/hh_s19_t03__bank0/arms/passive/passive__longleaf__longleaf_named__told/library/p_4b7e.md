# p_4b7e — The two-phase laptop: coffee table before ten, desk ten to five, coffee table after

Marco commutes to his office (out roughly 8:00–17:30 on weekdays) and Omar works from home at desk_o1. The critical correction this document makes against the "laptop at the desk all workday" model is the morning and evening coffee-table phases. The sightings are unambiguous: at 09:00 on weekdays the laptop is at the coffee table (3 sightings) or the bookshelf (1), not at the desk. It reaches the desk by 10:00 and stays through 16:00 (sightings at 10, 13, 15, 16). By 18:00 it is back at the coffee table. Overnight it rests on the bookshelf or the coffee table (03:00: bookshelf x1, coffee table x2). The 17 empty looks at desk_o1 during 9–17h confirm the laptop is absent for a meaningful chunk of the workday.

Marco's laptop is at desk_b1 overnight (03:00 x3) and in the evening (18:00 x1), but the two 9–17h looks at desk_b1 found nothing: during his workday the laptop is at the office or in his backpack. A single 10:00 coffee-table sighting likely corresponds to a sick day (Friday, when Marco is home).

This document is refuted if the laptop is consistently at desk_o1 at 09:00 (before 10:00) or at the desk at 18:00 or later, or if Marco's laptop is found at desk_b1 during weekday work hours.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at the coffee table at 09:00 on a weekday before he settles at the desk",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 8.75,
   "to": 9.25
  },
  {
   "claim": "Omar's laptop is at his desk at 14:00 on a weekday during the midday work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13.75,
   "to": 14.25
  },
  {
   "claim": "Omar's laptop is at the coffee table at 18:00 on a weekday after he leaves the desk",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 17.75,
   "to": 18.25
  },
  {
   "claim": "Marco's laptop is at his desk at 03:00 overnight",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "both",
   "from": 2.75,
   "to": 3.25
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
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
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 23,
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
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ]
 }
}
```
