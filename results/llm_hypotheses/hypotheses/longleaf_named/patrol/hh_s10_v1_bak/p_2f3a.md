# p_2f3a — The magazines and remote are living-room constants; the blanket moves with the viewer

The magazines (Omar's and Yuki's) are on the coffee table permanently. The remote is at the TV stand permanently. The blanket on the couch is pulled over to the armchair when Omar is gaming (he sits in the armchair) or stays on the couch when Yuki is watching TV. The cushions stay where they are. What sets this hypothesis apart: blanket_shared is at the armchair when Omar is home in the evening (after 23:00) and at the couch when he is at work. What would refute it: blanket_shared sighted at the armchair at 14:00 on a weekday (Omar is at work).

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch at 2pm on a weekday (Omar at work)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "The blanket may be on the armchair at 11:30pm on a weekday (Omar home, gaming)",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "The remote is at the TV stand at all times",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Yuki's magazine is on the coffee table at all times",
   "target": "magazine_yuki",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 2,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "armchair_l1",
    "chance": "sometimes"
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
  "magazine_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "magazine_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "cushion_1_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "cushion_2_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "almost_always"
   }
  ],
  "controller_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
