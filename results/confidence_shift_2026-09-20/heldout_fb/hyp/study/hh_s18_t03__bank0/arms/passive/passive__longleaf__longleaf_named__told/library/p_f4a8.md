# p_f4a8 — The 18:00–21:00 weekday transition: laptop to floor, dinner at table, TV migration

On weekdays the 18:00 hour marks Elena's return from work. Her keys, jacket, and backpack reappear at the entry. Ines's laptop moves from the desk to the office floor (seen at floor_o_o1 at 18:00), and her mug stays at the desk. The 19:00 hour is the peak of dinner: the kitchen table is set with plates, glasses, and water bottles for both women, and pans and pots are at the counter where cooking is in progress. By 20:00 dinner is winding down—pans and knives are still at the counter, glasses being cleared. At 21:00 the TV migration begins: the remote moves from the TV stand to the coffee table, the speaker moves from the bookshelf to the couch, the blanket drapes over the coffee table, and the snack bowl appears. Ines's headphones go to the bed. By 22:00–23:00 the full TV setup is in place.

What sets this apart: this document focuses specifically on the 18:00–21:00 weekday transition, the window where the most objects change location. It predicts the specific sequence—laptop to floor (18:00), dinner at the kitchen table with pans at the counter (19:00), TV migration to the coffee table and couch (21:00)—and makes the 19:00 dinner-window claims (plates, glasses, pans, water bottles at the kitchen table and counter) that the broader "standard routine" documents do not.

What would refute it: if the robot finds the remote still on the TV stand at 21:00, or the speaker still on the bookshelf at 21:00, or the plates still in the cupboard at 19:00, or the laptop still at the desk at 18:00.

```json
{
 "claims": [
  {
   "claim": "On weekdays the pan is on the kitchen counter at 19:30",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "On weekdays Elena's plate is at the kitchen table at 19:30",
   "target": "plate_elena",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "On weekdays Ines's laptop is on the office floor at 18:30",
   "target": "laptop_ines",
   "expect": "floor_o_o1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "On weekdays the speaker is on the couch at 21:00",
   "target": "speaker_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "On weekdays Ines's water bottle is at the kitchen table at 19:30",
   "target": "water_bottle_ines",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "floor_o_o1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "speaker_shared": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "headphones_ines": [
   {
    "days": "weekday",
    "from": 21,
    "to": 22,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "keys_elena": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "mug_elena": [
   {
    "days": "weekday",
    "from": 21,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
