# p_7a8b — Sick Day Friday; Hana at the Kitchen Table in the Morning, Couch in the Afternoon, Guests at 19:00

On Friday (the sick day), Hana does not go to work. Her day is unstructured: she sleeps in, gets up around 08:00, and drifts to the kitchen table with her tablet for a light morning session (09:00–10:00). By 10:00 she has moved to the living room, settling on the couch with her mug, book, and water bottle at the coffee table. She stays in the living room through the afternoon. In the evening (19:00+), friends arrive and the living room becomes a social space: the blanket is on the couch, the snack bowl is on the coffee table, and the remote is in active use. Hana's tablet, which would normally be at the kitchen table in the morning, is still at the kitchen table at 09:00 on the sick day — she is too unwell to work but still scrolls or reads.

This document differs from p_7f2a (which places the tablet at the nightstand all day) by acknowledging that Hana does bring the tablet to the kitchen table in the morning even while sick. It differs from the normal-weekday documents by keeping Hana home all day (no 13:40 departure) and by adding the guest evening. The guitar stays in her bedroom; she is too sick to play.

Refutation: if the tablet is at the nightstand at 09:00 on the sick day (never at the kitchen table), or if Hana's items are at the desk rather than the kitchen table, the sick-day pattern is wrong. If the guitar appears in the living room, the "too sick to play" claim fails.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table at 09:00 on the sick day, not at the nightstand",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 10.5
  },
  {
   "claim": "Hana's mug is at the coffee table in the sick-day afternoon, not the cupboard",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 11,
   "to": 17
  },
  {
   "claim": "Hana's guitar stays in her bedroom all day on the sick day and does not come to the living room",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "both",
   "from": 8,
   "to": 22
  },
  {
   "claim": "Hana's phone stays at her nightstand all day on the sick day because she is not going to work",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "book_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "entry_table_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_table_e1",
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
  "phone_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
