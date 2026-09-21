# p_6e3a — Shared Kitchen Table Dinner, Then Living Room

The evening follows a **two-room sequence**. From 18:00 to 19:00, both Hana and Priya are at the kitchen table for dinner: plates, mugs, and glasses are on kitchen_table_k1. The pot (or a serving dish) is on the table or counter. After dinner, they move to the living room: remote to the couch, blanket draped over the couch, snack bowl on the coffee table, guitar on the bedroom floor (or being played). The kitchen is cleared by 19:15.

What sets this apart: p_a9b4 says the laptop is at the kitchen table at 20:00 (against 4). This document says the kitchen table is for **dinner only** (18–19 h), not for evening work. After 19:00 the kitchen table is clear and the living room is the social space. p_a3f1 puts the guitar at bedroom_floor_b1 at 17–19 h; this document agrees but adds that by 19:30 the guitar may be on the coffee table or being played.

Refutation: if the robot finds laptop_hana at kitchen_table_k1 during 19–22 h, or finds the remote at tv_stand_l1 (not on the couch) at 20:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's plate is on the kitchen table at 18:30 on a weekday (dinner)",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 19.5
  },
  {
   "claim": "The remote is on the couch at 20:30 on a weekday (TV time, not at the TV stand)",
   "target": "remote_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table at 20:30 on a weekday",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The pot is on the kitchen counter at 18:00 on a weekday (dinner still simmering)",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17,
   "to": 19.5
  }
 ],
 "targets": {
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
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
    "from": 19.5,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21.5,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
