# p_b4e8 — Dog by the kitchen floor; Priya's midday at the sink

This document focuses on the objects that the other hypotheses get wrong or leave ambiguous: the dog's belongings and Priya's water bottle during the weekday middle of the day.

The dog bowl is a permanent fixture on the kitchen floor (floor_k_k1). It is found there on every single patrol, day and night, weekday and weekend. The dog is fed in the morning (by Priya on weekdays, by Elena on weekends) and the bowl simply stays down. The dog toy is a permanent fixture on the living room floor (floor_l_l1), found on every patrol. The leash hangs at the entry hook. The food bag is on the pantry shelf, occasionally moved to the kitchen table in the evening when someone is refilling the bowl.

Priya's water bottle is the object that trips up several documents. The sightings show it at the dish rack or pantry shelf at night, at the kitchen sink from about 10:00 through 17:00 on weekdays, and back at the dish rack or dining table in the evening. This is **not** an out-of-house pattern: Priya is home during the day and keeps her bottle at the sink while she moves between the kitchen and the bedroom. The documents that place her water bottle OUT_OF_HOUSE during afternoon errands are contradicted by the 12:00, 14:00, and 16:00 sightings at sink_k1.

The blanket is on the couch most of the time but appears on the coffee table in the evening (20:00–22:00), suggesting it is pulled over during TV time and then returned. The remote alternates between the coffee table and the TV stand, with the TV stand being the in-use position during 18:00–21:00.

What sets this hypothesis apart: Priya's water bottle is at sink_k1 (not out of the house) during 10–17h weekdays; the dog bowl and toy are permanent floor fixtures; the blanket shifts to the coffee table in the evening.

Refutation: if the dog bowl is found off the kitchen floor during 8–18h on multiple occasions; if Priya's water bottle is found out of the house or at a non-sink receptacle during 12–16h on a weekday; if the dog toy is found off the living room floor during 8–18h.

```json
{
 "claims": [
  {
   "claim": "The dog bowl is on the kitchen floor during the weekday midday",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's water bottle is at the kitchen sink during weekday midday",
   "target": "water_bottle_priya",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 11,
   "to": 16
  },
  {
   "claim": "The dog toy is on the living room floor during the weekday midday",
   "target": "dog_toy_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The blanket is on the couch during the weekday midday",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
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
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
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
    "days": "both",
    "from": 20,
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
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
