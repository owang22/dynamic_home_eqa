# p_4b7e — Weekend at home: brunch, errands, afternoon chores, evening kitchen

Ines and Elena are both home all weekend. They sleep in until roughly 10, then share a late breakfast or brunch at the kitchen table. Around midday one or both go out for errands (groceries, post, a walk), so keys, wallets, and phones leave the house for a couple of hours. The afternoon is for chores and casual living: the laundry basket moves from the bathroom shelf to the bedroom floor where they fold, the vacuum is dragged out to the living-room floor, and a shopping bag lands on the kitchen counter. Dinner is at the kitchen table again in the early evening, and the speaker goes to the couch for any music or TV. The blanket drifts between the couch and the bed as they nap or lounge.

What sets this apart: no document in the library tracks the weekend object movements in detail. The weekday documents assume the 9-to-5 work structure, but on weekends the kitchen table is the centre of gravity for meals, the bedroom floor hosts the laundry, and the entry area stays quiet because nobody is commuting.

Refutation: if the laundry basket is still on the bathroom shelf at 19:00–20:00 on a weekend, or if the tablet and bowl are in the cupboard (not the kitchen table) at 10:00 on a Saturday, the brunch-and-chores pattern is wrong.

```json
{
 "claims": [
  {
   "claim": "On weekends the laundry basket is on the bedroom floor in the evening",
   "target": "laundry_basket_shared",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "On weekends Elena's tablet is at the kitchen table during the late-morning brunch",
   "target": "tablet_elena",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 9,
   "to": 11
  },
  {
   "claim": "On weekends Ines's plate is at the kitchen table during the afternoon meal",
   "target": "plate_ines",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 14,
   "to": 16
  },
  {
   "claim": "On weekends the speaker is on the couch during evening entertainment",
   "target": "speaker_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 21,
   "to": 23
  },
  {
   "claim": "On weekends the shopping bag is on the kitchen counter after the midday errand",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 15,
   "to": 18
  }
 ],
 "targets": {
  "laundry_basket_shared": [
   {
    "days": "weekend",
    "from": 14,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ],
  "tablet_elena": [
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "bowl_elena": [
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_elena": [
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "plate_ines": [
   {
    "days": "weekend",
    "from": 14,
    "to": 16,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "glass_ines": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "glass_elena": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_elena": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekend",
    "from": 15,
    "to": 18,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 15,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "rarely"
   }
  ],
  "speaker_shared": [
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 17,
    "at": "bed_b1",
    "chance": "rarely"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "keys_elena": [
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_ines": [
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "yoga_mat_elena": [
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "towel_ines": [
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ]
 }
}
```
