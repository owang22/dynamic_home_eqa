# p_e1a9 — The 21:00 wind-down: guitar to the couch, iron to Omar's bed, remote never moves

After dinner and the initial TV block, the household enters a 21:00 wind-down. Marco takes his guitar from the bedroom floor to the couch and plays until about 23:00. Simultaneously, Omar sets up the iron and ironing board in his bedroom (on his bed) and irons for about an hour, finishing by 22:30–23:00. The remote stays on the tv stand throughout — it never moves to the coffee table or anywhere else. The blanket is on the couch (it is seen there at every pass, every day). The sketchbooks are on the coffee table during this block (Marco's at 21:00–22:00, Omar's at 20:00). The pencil cases return to their respective desks by 22:00 (Marco's is seen on the coffee table at 22:00 once, Omar's at 20:00 once, but mostly they are at the desks).

What sets this apart: this document pins the guitar on the couch at 21:00–23:00 (not in the bedroom as p_789a claims, and not in the wardrobe as p_5a1c suggested). The iron and ironing board are on Omar's bed, not in storage, during 21:00–23:00 on weekdays. The remote is immovable. This is the only document that combines the guitar-couch move with the iron-bedroom move in the same time window.

Refutation: if the guitar is in the bedroom at 21:30 on a weekday, or the iron is in storage at 21:00 on a weekday, or the remote is off the tv stand at 21:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Marco's guitar is on the couch at 21:30 on a weekday",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 21.25,
   "to": 21.75
  },
  {
   "claim": "The iron is on Omar's bed at 21:30 on a weekday",
   "target": "iron_shared",
   "expect": "bed_b2",
   "days": "weekday",
   "from": 21.25,
   "to": 21.75
  },
  {
   "claim": "The ironing board is on Omar's bed at 21:30 on a weekday",
   "target": "ironing_board_shared",
   "expect": "bed_b2",
   "days": "weekday",
   "from": 21.25,
   "to": 21.75
  },
  {
   "claim": "The remote is on the tv stand at 21:00 on a weekday",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 20.75,
   "to": 21.25
  },
  {
   "claim": "The blanket is on the couch at 21:00 on a weekday",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 20.75,
   "to": 21.25
  }
 ],
 "targets": {
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "iron_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 21,
    "at": "storage_shelf_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 19,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 21,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 19,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "storage_floor_s1",
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
  "sketchbook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "sketchbook_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ]
 }
}
```
