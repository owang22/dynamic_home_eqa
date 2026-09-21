# p_7b2c — Priya's mat out all morning, guitar in the living room by 3

Priya is retired and fills her day with yoga in the morning and guitar in the afternoon. The key evidence: the yoga mat is *not* in the wardrobe during 9–17h on weekdays (three empty looks), and the guitar is *not* on the bedroom floor during 9–17h (one empty look). This means both hobby objects are out in the open during the day. The mat is unrolled on the living-room floor for a yoga session roughly 8:30–11:30 (she gets up early, does her walk, then yoga before breakfast). The guitar is moved from the bedroom to the living room around 13:00 for an afternoon practice that runs until about 17:00, after which it goes back to the bedroom floor for the night. Her headphones rest at the bedroom desk (desk_b1), not the office desk—three sightings confirm desk_b1 as their home.

What sets this apart from p_3a7c: the windows are wider. The yoga mat is out 8:30–11:30 (not just 10–12), and the guitar is in the living room 13:00–17:00 (not just 15–16). The headphones are at desk_b1, not desk_o1. If the robot is asked "where is the yoga mat?" at 9:30, the answer is the living-room floor, not the wardrobe.

Refutation: if the yoga mat is found in the wardrobe at 10:00 on multiple weekdays, or the guitar is found on the bedroom floor at 15:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The yoga mat is on the living-room floor at 10:00 on a weekday",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "The guitar is on the living-room floor at 15:00 on a weekday",
   "target": "guitar_priya",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Priya's headphones are at the bedroom desk at 10:00 on a weekday",
   "target": "headphones_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The yoga mat is back in the wardrobe at 22:00",
   "target": "yoga_mat_priya",
   "expect": "wardrobe_b1",
   "days": "both",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8.5,
    "to": 11.5,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "pen_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
