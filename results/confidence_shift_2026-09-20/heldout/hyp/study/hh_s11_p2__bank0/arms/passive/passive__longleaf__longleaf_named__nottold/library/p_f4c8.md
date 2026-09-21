# p_f4c8 — The 22:00 Couch; Remote and Blanket at the Coffee Table

The evening TV is a shared activity that happens around 22:00. At that hour the remote is at the coffee table, the blanket is at the coffee table, and the snack bowl is at the coffee table; Priya is in the living room (confirmed by the 22:00 look on day 0). The remote's full weekday cycle is: floor_l_l1 from 00:00 to 08:00 (dropped after TV), tv_stand_l1 from 18:00 to 21:00 (stored during the day), coffee_table_l1 from 21:00 to 24:00 (in use for TV). The blanket follows a similar arc: armchair_l1 overnight, coffee_table_l1 at 18:00, couch_l1 at 20:00, coffee_table_l1 at 22:00. This directly contradicts p_c3d4, which claims no shared TV and the remote stays on the TV stand 21–23 h. If the remote is found at tv_stand_l1 during 22–23 h on a weekday, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "The remote is at the coffee table during the 22:00 TV",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The blanket is at the coffee table during the 22:00 TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The snack bowl is at the coffee table during the 22:00 TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
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
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
