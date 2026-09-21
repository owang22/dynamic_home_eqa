# p_6c1a — The 21:00 wind-down: guitar on the couch, iron in Omar's room

After dinner and the first stretch of TV, the household splits for the last hour. Marco takes his guitar from the bedroom floor to the couch around 21:00 (the 21:00 pass finds it there) and plays while Omar goes to his bedroom to iron. The iron and ironing board leave storage at 20:30 and appear at Omar's bed (bed_b2) by 21:00, where they stay until about 22:30. The 21:00 passes show the iron at bed_b2 three times and the ironing board at bed_b2 twice, while the 20:00 passes still show both in storage.

The remote never leaves the tv_stand. Every document that places it on the coffee table during TV (p_789a, p_f4a7, p_b2e9) has been against five times with zero for. The blanket stays on the couch all day. Omar's headphones are at the desk during work (10:00–17:00 passes find them there five times) and drift to the couch by 18:00 for the evening. His sketchbook and pencil case are at the desk overnight and through the day, then move to the coffee table around 20:00 for a late sketching session.

This document is refuted if: the guitar is in the bedroom at 21:00; the iron is still in storage at 21:00; the remote is on the coffee table at 20:00–22:00; or the ironing board is not at bed_b2 during the 21:00 window.

```json
{
 "claims": [
  {
   "claim": "Marco's guitar is on the couch during the late evening",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The iron is in Omar's bedroom during the late-evening ironing session",
   "target": "iron_shared",
   "expect": "bed_b2",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The ironing board is in Omar's bedroom during the late-evening ironing session",
   "target": "ironing_board_shared",
   "expect": "bed_b2",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The remote stays on the tv stand during the evening",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20,
   "to": 22.5
  },
  {
   "claim": "Omar's headphones are on the couch during evening relaxation",
   "target": "headphones_omar",
   "expect": "couch_l1",
   "days": "both",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20.5,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22.5,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20.5,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22.5,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "headphones_omar": [
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "sketchbook_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "pencil_case_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
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
