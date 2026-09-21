# p_d5f1 — Evening rhythm: cook, dinner, TV; dog stays in

The evening follows a tight sequence. Cooking starts around 18: pan, knife, and cutting board move to the counter and sink. Dinner is served at the dining table from roughly 19 to 20: plates, glasses, and water bottles are there. After clearing, the residents settle into the living room for TV from 20 to 22: the remote goes to the tv_stand, the blanket stays on the couch, and the coffee table holds the remote once TV ends (back by 22). The dog's toy is never taken outside—it stays on the living-room floor all day and evening. Priya's guitar rests on the bedroom floor during the afternoon when she practises, then stays there overnight.

This document captures the in-use windows that the per-object evidence reveals from the gaps between patrol sightings. It differs from p_789a by keeping the dog toy in the house (not out on evening walks). It differs from p_a1b2 by specifying the exact dinner and TV windows. It differs from the plain statistical model by placing the remote at the tv_stand only during TV hours and at the coffee table otherwise.

Refutation: if the dog toy is sighted out of the house on multiple evenings, or if the remote is at the coffee table at 20:00 (mid-TV), or if the guitar is in the living room at 16:00 on a weekday, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Elena's plate is at the dining table during dinner",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The remote is back at the coffee table after TV ends",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "The dog toy is on the living room floor in the evening",
   "target": "dog_toy_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 18,
   "to": 20
  },
  {
   "claim": "Priya's guitar is on the bedroom floor during her afternoon practice",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 15,
   "to": 18
  }
 ],
 "targets": {
  "plate_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21.5,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
