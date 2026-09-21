# p_c6b4 — Elena's 7:00 bathroom ritual and 8:00 departure

Elena's weekday morning follows a tight sequence. By 07:00 she is in the bathroom: her towel is pulled from the rack to the shelf (seen there ×3 at 07:00), her razor is on the shelf or in the medicine cabinet (×1 at 07:00), and her water bottle is at the armchair in the living room (×2 at 07:00). By 08:00 the towel is back on the rack and she is out the door. From 08:00 to 17:30 her keys, backpack, laptop, jacket, hat, headphones, wallet, and sunglasses are all out of the house. She returns around 17:30–18:00: keys at the entry table, water bottle at the entry floor, backpack at the entry floor.

This document differs from p_d1e5 (departure at 07:15) by placing the departure at 08:00, consistent with the WHO LIVES HERE description ("out at work from about 8") and the 07:00 bathroom sightings showing her still home. It differs from p_b8c2 (nothing leaves) by tracking Elena's objects out of the house for the full work day. It differs from p_2e9f (morning transition 6–9 h) by extending the pattern through the full day and into the evening return.

Refutation: finding Elena's keys or water bottle inside the house at 09:00 on a weekday, or finding her towel still on the bathroom shelf at 09:00.

```json
{
 "claims": [
  {
   "claim": "Elena's water bottle is at the armchair at 07:00",
   "target": "water_bottle_elena",
   "expect": "armchair_l1",
   "days": "both",
   "from": 6.5,
   "to": 7.5
  },
  {
   "claim": "Elena's towel is on the bathroom shelf at 07:00",
   "target": "towel_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 6.5,
   "to": 8
  },
  {
   "claim": "Elena's keys are out of the house at 09:00 on weekdays",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Elena's backpack is out of the house at 09:00 on weekdays",
   "target": "backpack_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 6.5,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "armchair_l1",
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
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "towel_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 6.5,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 23.5,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "razor_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 6.5,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 23.5,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7.5,
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
    "days": "both",
    "from": 18,
    "to": 23.5,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7.5,
    "at": "entry_floor_e1",
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
    "days": "both",
    "from": 18,
    "to": 23.5,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 23.5,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
