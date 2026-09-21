# p_8f4c — The 15:00 Vacuum: mid-afternoon cleaning in the living room

The vacuum cleaner is stored at storage_floor_s1 for most of the day, but at 15:00 on weekdays it appears on floor_l_l1 (the living room floor) — someone is vacuuming. The evidence shows vacuum_cleaner_shared at storage_floor_s1 at 03:00 (2x), 09:00 (1x), 14:00 (1x), 18:00 (2x), and at floor_l_l1 at 15:00 (1x). This is a brief mid-afternoon cleaning session, likely by Priya (who is home most of the day) or by Hana if she gets home early. The vacuum goes back to storage by 18:00.

What sets this apart: at 15:00 on a weekday, vacuum_cleaner_shared is at floor_l_l1 (not storage_floor_s1). In the standard hypothesis the vacuum never leaves storage during the day. What would refute it: vacuum_cleaner_shared at storage_floor_s1 at 15:00 on a weekday, or vacuum_cleaner_shared at floor_l_l1 at 10:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 15:00 on a weekday (mid-afternoon cleaning)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 14.5,
   "to": 15.5
  },
  {
   "claim": "The vacuum cleaner is in storage at 09:00 on a weekday (not yet in use)",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 8,
   "to": 14
  },
  {
   "claim": "The vacuum cleaner is back in storage at 18:00 on a weekday (cleaning done)",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 16,
   "to": 19
  },
  {
   "claim": "The duster is on the storage shelf at 15:00 on a weekday (cleaning supplies are out)",
   "target": "duster_shared",
   "expect": "storage_shelf_s1",
   "days": "weekday",
   "from": 14,
   "to": 16
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 15.5,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "duster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "almost_always"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   }
  ],
  "laundry_basket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
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
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
