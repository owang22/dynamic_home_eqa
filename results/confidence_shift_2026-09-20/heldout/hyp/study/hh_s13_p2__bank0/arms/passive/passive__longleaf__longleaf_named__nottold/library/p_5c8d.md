# p_5c8d — Weekend Floor: Vacuum Out, Jacket Down, Blanket on the Armchair

The clock-hour data reveals three distinctive weekend patterns that no single document in the library captures together. First, the vacuum cleaner is on the living room floor (floor_l_l1) at every single weekend pass from 00:00 to 10:00 (×2 both days) and remains there or splits with storage from 12:00 to 22:00. On weekdays it is in storage_floor_s1 from 00:00 to 10:00. The weekend is cleaning day — the vacuum stays out on the floor all day. Second, Priya's jacket moves from entry_hook_e1 (weekdays, ×5 every pass) to entry_floor_e1 on weekend afternoons (14:00–22:00, ×1 or ×2). On weekend mornings it is still split hook/floor. Third, the blanket is on the armchair_l1 on every weekend pass from 00:00 to 20:00 (×1 each, shared with couch_l1 ×1), whereas on weekdays it is couch_l1 ×5 at every pass.

What sets this apart: at 10:00 on a Saturday, vacuum_cleaner_shared is at floor_l_l1 (not storage_floor_s1); at 16:00 on a Saturday, jacket_priya is at entry_floor_e1 (not entry_hook_e1); at 12:00 on a Saturday, blanket_shared is at armchair_l1 (not couch_l1). What would refute it: vacuum at storage_floor_s1 at 10:00 on a Saturday, or jacket_priya at entry_hook_e1 at 16:00 on a Saturday.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 10:00 on a Saturday",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 8,
   "to": 12
  },
  {
   "claim": "Priya's jacket is on the entry floor at 16:00 on a Saturday",
   "target": "jacket_priya",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The blanket is on the armchair at 12:00 on a Saturday",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 10,
   "to": 14
  },
  {
   "claim": "The vacuum cleaner is in storage at 08:00 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 7,
   "to": 10
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 23,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "days": "weekend",
    "from": 0,
    "to": 21,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
