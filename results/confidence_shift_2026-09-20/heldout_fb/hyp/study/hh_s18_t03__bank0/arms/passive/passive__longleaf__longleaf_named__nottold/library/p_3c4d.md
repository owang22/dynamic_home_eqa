# p_3c4d — Ines's balcony midday: laptop at the balcony table 11–15h

Ines breaks her workday into three sessions, but the midday one takes place outside. Around 11 she carries the laptop to the balcony table, works in the fresh air until about 15, then brings it back to the office desk for the late-afternoon session. The charger, headphones, and pen remain at the office desk throughout—she does not plug in the laptop on the balcony. Elena commutes to her office in town (8 to 5:30) with keys, laptop, backpack, jacket, and sunglasses. The evening migration to the coffee table follows the usual pattern at 21.

What sets this apart: the laptop is at balcony_table_y1 during 11–15, a location the robot rarely inspects during work hours, which accounts for the absence of sightings in that window. Unlike the ON_PERSON hypothesis, the laptop is set down on a fixed surface, so a look at the balcony table during 11–15 would find it.

What would refute it: a sighting of laptop_ines at desk_o1 or floor_o_o1 during 11–15 on a weekday; a look at balcony_table_y1 in that window that finds nothing; Ines being seen in the office without the laptop.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is at the balcony table during the midday session",
   "target": "laptop_ines",
   "expect": "balcony_table_y1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Ines's laptop is at the office desk during the morning session",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Ines's charger stays at the office desk during the midday balcony session",
   "target": "charger_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Elena's laptop is out of the house during her weekday work day",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "laptop_ines": [
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
    "to": 15,
    "at": "balcony_table_y1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "floor_o_o1",
    "chance": "sometimes"
   }
  ],
  "charger_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
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
    "from": 20,
    "to": 23,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "keys_elena": [
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
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
