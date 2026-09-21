# p_9b6e — Saturday Brunch: Kitchen Table 10-to-13, Then Living-Room Afternoon

On Saturday the meal rhythm shifts: breakfast becomes brunch, served at the kitchen table from about 10:00 to 13:00. Both residents are in the kitchen for this window. Plates, glasses, and mugs are at the kitchen table during brunch. After 13:00, dishes go to the sink, and by 14:00 both residents have drifted to the living room—blanket on the couch, remote at the TV stand, snack bowl still in the sink (not yet brought out). The afternoon is low-key: no guitar playing, no puzzle, just lounging.

What sets this document apart: it is the only one that makes the **brunch window 10–13 h** the central prediction, with plates, glasses, AND mugs all at the kitchen table simultaneously. It also predicts the blanket stays on the couch (not the coffee table) through the afternoon, and the remote stays at the TV stand until 20:00. The guitar and puzzle box both stay in their resting spots all day.

Refutation: if plates are still in the cupboard at 11:00, the brunch claim fails. If the blanket is on the coffee table at 16:00, the couch claim fails. If the remote is on the coffee table at 16:00, the TV-stand claim fails. If the guitar is ON_PERSON at 12:00, the "no playing" claim fails.

```json
{
 "claims": [
  {
   "claim": "Hana's plate is at the kitchen table at 11:00 on a Saturday because brunch is in progress",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 10,
   "to": 13
  },
  {
   "claim": "Hana's glass is at the kitchen table at 11:00 on a Saturday because brunch is in progress",
   "target": "glass_hana",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 10,
   "to": 13
  },
  {
   "claim": "Priya's mug is at the kitchen table at 11:00 on a Saturday because brunch is in progress",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 10,
   "to": 13
  },
  {
   "claim": "The blanket is on the couch at 16:00 on a Saturday (afternoon lounging, not yet TV time)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The remote is at the TV stand at 16:00 on a Saturday (not yet the evening TV session)",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "class:plate": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "kettle_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "keys_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "phone_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ]
 }
}
```
