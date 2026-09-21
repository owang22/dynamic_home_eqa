# p_4e8c — Guest Evening; Blanket on the Couch, Snacks on the Coffee Table

Friends arrive at the house this Friday evening, around 18:00. The living room becomes the centre of social activity from roughly 18:00 to 22:00. The shared blanket, which the evidence places on the coffee_table_l1 at 14:00 and 18:00 on normal weekday evenings, moves to the couch_l1 where the guests sit and settle in. The remote, which rests on the tv_stand_l1 at 18:00 on normal days, enters active use and appears on the floor_l_l1 or in a resident's hand during the gathering. The snack bowl, which the evidence places on the counter_k1 at 19:00 on normal weekday evenings (sighted there 3 times), moves to the coffee_table_l1 for the guests to share. The dog is excited by the new people; its toy stays out on the living room floor. Priya moves between the kitchen (preparing drinks and light food) and the living room (hosting). Hana, being sick, is on the couch or in bed and not actively hosting.

This document differs from p_c3d4 (which keeps the blanket on the coffee table all evening, 21:00–23:00) and p_9e1f (which keeps the snack bowl on the counter, 19:00–23:00) by placing both objects in the living room for the guest gathering. It differs from the standard evening documents by having the remote in active use on the floor rather than resting on the TV stand. The glass_priya object moves to the dining table for serving drinks to guests.

This document is refuted if the snack bowl is still on the counter at 19:00–21:00, or if the blanket is on the coffee table (not the couch) during the evening window, or if the remote is on the TV stand at 19:00–21:00.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch during the guest evening, not the coffee table",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The snack bowl is on the coffee table for the guests, not the kitchen counter",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The remote is in active use on the living room floor during the guest evening",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "blanket_shared": [
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
    "to": 22,
    "at": "couch_l1",
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
    "from": 18,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "sometimes"
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
    "from": 18,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
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
    "from": 18,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ]
 }
}
```
