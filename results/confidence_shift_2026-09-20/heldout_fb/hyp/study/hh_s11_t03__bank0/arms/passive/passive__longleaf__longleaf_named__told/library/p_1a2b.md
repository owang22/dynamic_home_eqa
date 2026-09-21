# p_1a2b — The 18:00 Evening Sequence: Cook at the Counter, Eat at the Dining Table, TV at the Coffee Table

Hana and Priya share a structured evening that runs in three phases. Around 18:00, Priya (or sometimes Hana, who gets home at 23:00 and skips dinner) starts cooking at the kitchen counter: the pan, pot, cutting board, and knife come out to counter_k1. By 19:00 the food is on the dining table and both residents sit down — plates and glasses at dining_table_d1. The kitchen is cleared by 20:00. Then the evening shifts to the living room: the snack bowl moves from the kitchen counter to the coffee table, the remote comes into active use on the living room floor, and the blanket settles on the couch. By 22:00 Priya takes her glass to the bedroom (nightstand_b2) and the TV winds down.

This document sets itself apart by treating the 18:00–22:00 window as a single coordinated sequence rather than separate activities. It predicts that the cooking implements (pan, knife, cutting board, pot) are at the counter at 18:00 but back in their resting spots (cupboard, drawer, sink) by 20:00. It predicts the snack bowl leaves the counter and arrives at the coffee table specifically at 21:00, not earlier. It predicts Priya's glass ends the night at nightstand_b2, not the kitchen.

Refutation: if the pan or knife is still on the counter at 21:00 or later, if the snack bowl is on the coffee table before 20:00, or if Priya's glass is at the kitchen counter at 22:00 rather than the bedroom, this sequence is wrong.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter during the 18:00 cooking phase",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18,
   "to": 19.5
  },
  {
   "claim": "Priya's plate is at the dining table during the 19:00 dinner",
   "target": "plate_priya",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The snack bowl moves to the coffee table at 21:00 for the TV-and-snacking phase",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Priya's glass is at her nightstand by 22:00 as she winds down for bed",
   "target": "glass_priya",
   "expect": "nightstand_b2",
   "days": "both",
   "from": 22,
   "to": 24
  },
  {
   "claim": "The cutting board is on the counter during the 18:00 cooking phase, not at the sink",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18,
   "to": 20
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 12,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13.5,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21.5,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "tv_stand_l1",
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
    "to": 23.5,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23.5,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
