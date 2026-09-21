# p_b9e5 — Priya's mat-out morning, counter errands, guitar at rest

Priya is home all day on weekdays. Her yoga mat is out of the wardrobe from about 9:00 through 17:00 — the robot's five empty looks at wardrobe_b1 during 9–17h on weekdays confirm the mat is not stored there. She unrolls it on the living-room floor for a morning practice (9:00–12:00), then leaves it out while she does her midday errands. The shopping bag comes back to the kitchen counter between 12:00 and 15:00 (three sightings at 12:00, three at 14:00, one at 15:00). Her mug is at the kitchen table in the early morning (7:00–9:00) while she has coffee. The guitar rests on the bedroom floor all day; she only brings it to the living room for evening practice or weekend guests. Her reading glasses go to the coffee table briefly in the mid-afternoon (15:00–17:00) and then back to the nightstand.

This document differs from p_3a7c (yoga mat on floor only 10:00–12:00) and p_7b2c (mat on floor 9:00–11:00) by extending the mat-out window to 9:00–17:00, matching the five empty wardrobe looks. It differs from p_e5f6 and p_6b4e (guitar in the office or bedroom desk area) by keeping the guitar on the bedroom floor as its resting spot. It differs from p_8c1a by adding the yoga-mat and guitar predictions alongside the shopping-bag and mug claims.

Refutation: if the yoga mat is seen in the wardrobe during 9:00–17:00 on a weekday, the mat-out window is wrong. If the guitar is seen on the living-room floor or at a desk during the workday, the bedroom-floor resting spot is wrong. If the shopping bag is not at the counter at 12:00 or 14:00, the errand window shifts.

```json
{
 "claims": [
  {
   "claim": "Priya's yoga mat is on the living-room floor during her morning practice at 10:00",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The shopping bag is at the kitchen counter during Priya's midday errand window at 13:00",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Priya's mug is at the kitchen table in the morning at 8:00",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Priya's guitar rests on the bedroom floor at midday on a weekday",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "both",
   "from": 11,
   "to": 15
  }
 ],
 "targets": {
  "yoga_mat_priya": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekday",
    "from": 12,
    "to": 15,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
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
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 15,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
