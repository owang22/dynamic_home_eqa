# p_c4f1 — Guitar Weekday Anchor, Weekend Couch Rest (fork of p_b1c6)

The parent (p_b1c6) predicted the guitar ON_PERSON at 15:00–18:00 on weekends. The Saturday evidence refutes this: at 16:00 the guitar was on the couch (2×) or the bedroom floor (1×), never held. The claim "guitar ON_PERSON at 16:00 Saturday" went against 3 times with zero for. The weekday 19:00–21:00 playing window has no evidence against it yet (the 18:00 pass shows the guitar still on the bedroom floor, consistent with playing starting at 19:00).

What changed: (1) The weekend 15:00–18:00 ON_PERSON block is replaced with a couch_l1 block (the guitar is propped on or draped over the couch in the afternoon). (2) The claim about Saturday guitar playing is replaced with a claim that the guitar is on the couch at 16:00. (3) The weekday 19:00–21:00 playing and the 21:00–23:00 return to the bedroom floor are retained. (4) The remote and blanket blocks are unchanged from the parent.

What would refute this: the guitar ON_PERSON at 16:00 Saturday, the guitar at the bedroom floor at 20:00 on a weekday (playing not happening), or the guitar on the coffee table at 16:00 Saturday (it's on the couch, not the coffee table).

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
   "claim": "The guitar is on the couch at 16:00 on a Saturday (not being played)",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 15,
   "to": 17.5
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
    "from": 14,
    "to": 18,
    "at": "couch_l1",
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
    "days": "weekday",
    "from": 21,
    "to": 22.5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "armchair_l1",
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
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
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
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
