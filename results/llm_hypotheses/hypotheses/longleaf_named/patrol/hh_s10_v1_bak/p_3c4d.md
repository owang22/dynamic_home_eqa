# p_3c4d — The vacuum lives at the entry; it only moves on cleaning days

The vacuum_cleaner_shared is stored at the entry floor permanently. It is only moved to the room being cleaned (floor_l_l1, floor_k_k1, floor_o_o1, bedroom_floor_b1) on specific cleaning days, roughly once a week on a Saturday afternoon. On all other days it is at the entry. What sets this hypothesis apart: the vacuum is at the entry 6 days a week, not on a room floor. What would refute it: vacuum_cleaner_shared sighted at entry_floor_e1 on a Saturday between 14:00 and 18:00 (if it is being used, it should be in a room).

```json
{
 "claims": [
  {
   "claim": "The vacuum is at the entry floor on a Tuesday",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The vacuum is at the entry floor on a Wednesday",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The vacuum may be in a room on Saturday afternoon during cleaning",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The doormat is always at the entry floor",
   "target": "doormat_shared",
   "expect": "entry_floor_e1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "doormat_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
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
  ],
  "shoes_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
