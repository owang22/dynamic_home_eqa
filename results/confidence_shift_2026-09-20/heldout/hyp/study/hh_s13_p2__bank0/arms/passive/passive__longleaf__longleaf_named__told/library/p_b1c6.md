# p_b1c6 — Guitar is the Evening Anchor: Hana plays 19-to-21 every single day

The guitar is the most important part of Hana's evening, every day of the week, including weekdays. She plays from 19:00 to 21:00 daily. During this window the guitar is ON_PERSON or on the coffee table (she moves it from the bedroom). The TV does not start until 21:00 (after guitar). The blanket and remote go to the couch at 21:00. Priya listens to the guitar or reads nearby. On weekends the guitar session is longer: 15:00–18:00.

What sets this apart: at 20:00 on a weekday, guitar_hana is ON_PERSON or at coffee_table_l1 (not bedroom_floor_b1). The remote is still at tv_stand_l1 at 20:00 (TV hasn't started). At 22:00 the guitar is back on the bedroom floor. In the standard hypothesis the guitar session is 19:00–20:30 and TV starts at 20:30. What would refute it: guitar_hana at bedroom_floor_b1 at 20:00 on a weekday, or remote_shared at couch_l1 at 20:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The guitar is being played at 20:00 on a weekday",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The remote is still at the TV stand at 20:00 on a weekday",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The guitar is being played at 16:00 on a Saturday",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 15,
   "to": 18
  },
  {
   "claim": "The guitar is back on the bedroom floor at 22:00 on a weekday",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "ON_PERSON",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 18,
    "at": "ON_PERSON",
    "chance": "almost_always"
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
    "days": "weekday",
    "from": 21,
    "to": 22.5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "couch_l1",
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
    "days": "weekday",
    "from": 21,
    "to": 22.5,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
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
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
