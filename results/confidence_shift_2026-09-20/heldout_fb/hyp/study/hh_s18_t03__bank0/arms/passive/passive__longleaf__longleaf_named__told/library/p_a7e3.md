# p_a7e3 — Ines at the desk in two work blocks; laptop off-desk during breaks; charger to shelf at night

Ines works from home in the office room, seated at desk_o1. The evidence shows her laptop is on the desk at 10:00, 16:00, and 17:00 but absent from the desk at most other looks during 9–17 h (24 empty looks vs 2 hits). The pattern fits two focused work sessions — late morning (10–11) and late afternoon (16–17:30) — separated by a long midday break (12–15) in which the laptop is on her lap, at the kitchen table, or on the floor beside her. After 18:00 she sets the laptop on the office floor (floor_o_o1) and leaves the room.

Her charger (charger_ines) sits on the desk during the work day but is moved to the office shelf (office_shelf_o1) after 22:00, as the 23:00 sightings confirm (2× office_shelf_o1). Her headphones (headphones_ines) are on the desk during work and go to the bed (bed_b1) at 21:00 for the evening. Her pen (pen_ines) is on the desk during both work blocks but is not always there (22 empty looks), consistent with her picking it up to write at the kitchen table during lunch. Her water bottle (water_bottle_ines) is on the desk during work, at the kitchen sink (sink_k1) at 14:00 when she refills it, and at the kitchen table (kitchen_table_k1) at 19:00 for dinner.

Elena commutes to her office in town, out roughly 8:00–17:30. Nothing in this document predicts Ines leaving the house.

What sets this apart: the two-block work schedule (10–11, 16–17:30) with the laptop explicitly off-desk during 12–15, and the charger's nightly move to office_shelf_o1. A document that pins the laptop at the desk all day (p_a3f7, p_d1e5) or on the floor all day (p_3e7a, p_c4d9) will be wrong at the 10:00 / 16:00 / 17:00 sightings or at the 18:00 floor sighting respectively.

Refutation: if the laptop is found at desk_o1 at 12:00–14:00 on multiple weekdays, the midday break is wrong. If the charger is never seen at office_shelf_o1, the nightly move is wrong. If the laptop is on the floor at 10:00 or 16:00, the two-block model collapses.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on the office desk at 10:00 on weekdays",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 11
  },
  {
   "claim": "Ines's laptop is on the office desk at 16:00 on weekdays",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 16,
   "to": 17
  },
  {
   "claim": "Ines's charger is on the office shelf at 23:00",
   "target": "charger_ines",
   "expect": "office_shelf_o1",
   "days": "both",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Ines's headphones are on the bed at 21:00",
   "target": "headphones_ines",
   "expect": "bed_b1",
   "days": "both",
   "from": 21,
   "to": 22
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 11,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 15,
    "at": "floor_o_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "floor_o_o1",
    "chance": "usually"
   }
  ],
  "charger_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "usually"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "pen_ines": [
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
    "to": 14,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 15,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
