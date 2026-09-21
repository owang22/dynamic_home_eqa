# p_e7f3 — Weekend at home: slow start, midday errands, long dinner, evening chores

Ines and Elena both sleep in on weekends, skipping the weekday 7:00 bathroom-and-breakfast routine. The first kitchen activity is around 8:00–10:00: bowls come out of the cupboard, and Elena's tablet joins the kitchen table for a lazy brunch. Around 12:00–15:00 both women head out for errands—keys, wallets, phones, and sunglasses leave the house, and the entry area empties. They are back by 15:00–16:00, the shopping bag landing on the kitchen counter. The afternoon stretches into a long, unhurried dinner: plates, glasses, and serving dishes move to the kitchen table from 15:00 to 20:00. In the evening the laundry basket appears on the bedroom floor (19:00–21:00) as they fold and sort. TV time comes late (21:00+): the speaker settles on the couch, the remote and blanket migrate to the coffee table. Elena's water bottle ends up at the kitchen table or armchair. Elena's yoga mat rests on the living-room floor all day; she may roll it out in the evening. Ines's laptop stays at the office desk all weekend—she does not work on it. Her headphones rest at the desk or move to the bed for music in the evening.

What sets this apart: this is the only document in the library focused entirely on the weekend. It predicts that both women are OUT OF THE HOUSE during the 12:00–15:00 errand window, the key weekend difference from weekdays (where Elena is at her office and Ines is at her desk). It also predicts the long dinner window (15:00–20:00) with plates and glasses at the kitchen table, the late-evening TV migration, and the laundry basket on the bedroom floor.

What would refute it: if the robot finds Elena's keys or Ines's keys at the entry table during 12:00–15:00 on a weekend (meaning they did not go out), or if the shopping bag never appears on the counter after 15:00, or if the laundry basket is never on the bedroom floor in the evening.

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
   "claim": "On weekends the shopping bag is on the kitchen counter after the midday errand",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 15,
   "to": 18
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
   "claim": "On weekends Elena's keys are out of the house during the midday errand",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 15
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "keys_ines": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "phone_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "phone_ines": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "wallet_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "wallet_ines": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
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
  "laundry_basket_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ],
  "speaker_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "class:plate": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "tablet_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "headphones_ines": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "class:bowl": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
