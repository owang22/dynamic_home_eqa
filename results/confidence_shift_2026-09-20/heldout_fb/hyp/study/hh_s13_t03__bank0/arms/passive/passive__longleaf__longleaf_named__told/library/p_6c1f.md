# p_6c1f — Priya's Midday Table: Lunch, Errands, and the 12:00 Counter

Priya is home all morning, takes her walk, and heads out for afternoon errands around 11:00. She returns at roughly 12:00 carrying the shopping bag, which she sets on the kitchen counter to unpack. At the same time she has a midday drink (glass of water or tea at the kitchen table) and a light lunch (plate at the kitchen table). The 12:00 and 13:00 patrol passes catch the shopping bag on the counter (5 and 3 sightings respectively), her glass at the kitchen table (4 sightings at 12:00), and her plate at the kitchen table (2 sightings at 12:00). By 13:00 the plate is back in the cupboard and the glass is heading to the nightstand or sink. The shopping bag goes back to the pantry shelf by 18:00.

What sets this apart: p_a9b4 (Kitchen Social Hub) puts mugs and glasses at the kitchen table at 10:00 and 14:00, but the evidence shows the midday cluster at 12:00-13:00, not 10:00 or 14:00. p_4e1b captures the shopping bag but also puts glass_priya at the nightstand at 13:00, which conflicts with the 12:00 kitchen table sightings.

Refutation: if the shopping bag is seen at the counter at 10:00 or 15:00 on multiple weekdays, the 12-13h window is wrong. If Priya's glass is at the kitchen table at 14:00 rather than 12:00, the midday cluster shifts.

```json
{
 "claims": [
  {
   "claim": "The shopping bag is on the kitchen counter at 12:00 on a weekday because Priya just returned from errands",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 12,
   "to": 13
  },
  {
   "claim": "Priya's glass is at the kitchen table at 12:00 on a weekday for her midday drink",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13
  },
  {
   "claim": "Priya's plate is at the kitchen table at 12:00 on a weekday for her light lunch",
   "target": "plate_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13
  },
  {
   "claim": "Priya's mug is at the kitchen table at 08:00 on a weekday for morning tea",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
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
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
