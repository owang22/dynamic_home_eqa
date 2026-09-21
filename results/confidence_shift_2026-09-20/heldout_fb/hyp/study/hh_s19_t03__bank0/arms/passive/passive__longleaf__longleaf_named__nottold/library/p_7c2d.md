# p_7c2d — Weekend chore day: vacuum at ten, duster at eleven, ironing afternoon, grocery at five

On weekends both residents sleep in until about 9. Marco starts the vacuum around 9:30 and works through the living room until roughly 12:00–13:00. Omar takes the duster to the bookshelf around 11:00 for a dusting session that lasts about an hour. After the morning chores, Omar sets up the ironing board in his bedroom and irons from about 13:00 through 18:00 (the board is seen on his bed at 13:00, 15:00, and 18:00 on weekends). Marco goes out for errands and grocery shopping, returning around 16:30–17:00 to unload bags on the kitchen counter. Cooking starts at 18:00 on weekends, with the pan already on the counter (an hour earlier than the weekday 18:00 cupboard pass). Dinner is at the kitchen table around 19:00–20:00.

What sets this apart: this is the only document that models the full weekend chore sequence. The vacuum is on the living room floor 10:00–13:00 (not in storage), the duster is at the bookshelf at 11:00, the ironing board is in Omar's bedroom 13:00–19:00, and the shopping bag is on the counter at 17:00. The weekend cook starts an hour earlier than the weekday cook.

Refutation: if the vacuum is in storage at 10:00 on a weekend, or the duster is in storage at 11:00 on a weekend, or the ironing board is in storage at 15:00 on a weekend, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 10:00 on a weekend",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 9.75,
   "to": 10.25
  },
  {
   "claim": "The duster is at the bookshelf at 11:00 on a weekend",
   "target": "duster_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 10.75,
   "to": 11.25
  },
  {
   "claim": "The ironing board is on Omar's bed at 15:00 on a weekend",
   "target": "ironing_board_shared",
   "expect": "bed_b2",
   "days": "weekend",
   "from": 14.75,
   "to": 15.25
  },
  {
   "claim": "The shopping bag is on the kitchen counter at 17:00 on a weekend",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 16.75,
   "to": 17.25
  },
  {
   "claim": "The pan is on the counter at 18:00 on a weekend",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 17.75,
   "to": 18.25
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9.5,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 9.5,
    "to": 13,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   }
  ],
  "duster_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10.5,
    "at": "storage_shelf_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 10.5,
    "to": 12,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "almost_always"
   }
  ],
  "ironing_board_shared": [
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
   },
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
   }
  ],
  "iron_shared": [
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
   },
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
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
