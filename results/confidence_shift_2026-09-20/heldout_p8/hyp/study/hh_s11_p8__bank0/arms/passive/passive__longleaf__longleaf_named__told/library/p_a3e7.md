# p_a3e7 — Tuesday Friends Evening; Hana Home by 17:00, Priya Hosts

Hana and Priya have friends coming over this Tuesday evening. Unlike the Friday sick-day gathering, Hana is well and working her normal afternoon-to-night shift, but the "we" in the message implies she will come home early—around 17:00—to help Priya host. In the morning the routine is standard: Hana works at her desk with notebook and pen while Priya walks the dog. By early afternoon Priya tidies the living room (duster, vacuum) in preparation for guests. Hana arrives home around 5 pm; her handbag, keys, and phone come back in with her. Dinner is served with the shared serving dish on the dining table. In the evening the puzzle box comes out for board games. Crucially, Hana's guitar stays in her bedroom all day—she does not play for guests, and the evidence (19 sightings at bedroom_floor_b1, zero elsewhere) is unambiguous. Hana's tablet remains at the nightstand; she does not work from home on a social evening. The blanket shifts to the coffee table for the gathering. The remote stays on the TV stand because the group is talking, not watching.

What sets this document apart: it predicts Hana is home by 17:00 (unlike her normal 23:00 return), the duster and vacuum are at the coffee table in the afternoon (pre-guest cleaning), the serving dish and puzzle box are out on the dining table, and the guitar does NOT come to the living room. A sighting of the guitar at the armchair or coffee table, or of the handbag still at the entry hook past 18:00, would refute the early-return premise.

```json
{
 "claims": [
  {
   "claim": "The duster is at the coffee table on Tuesday afternoon while Priya tidies for guests",
   "target": "duster_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The vacuum cleaner is at the coffee table on Tuesday afternoon",
   "target": "vacuum_cleaner_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The serving dish is on the dining table while dinner is served to the guests",
   "target": "serving_dish_shared",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 17,
   "to": 22
  },
  {
   "claim": "The puzzle box is on the dining table for evening board games with guests",
   "target": "puzzle_box_shared",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's guitar stays in her bedroom all day even with guests over",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 8,
   "to": 22
  },
  {
   "claim": "Hana's handbag is out of the house during her shortened work shift",
   "target": "handbag_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 13,
   "to": 17
  }
 ],
 "targets": {
  "duster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
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
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "pen_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
