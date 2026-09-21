# p_7e4d — Evening Wind-Down: Washing Up, Evening Shower, and the Shopping Bag

This house's evening (21:00–01:00) is a distinct phase that no other document in the library addresses. Yuki is home alone (Marco is at work until 23:00), and the kitchen transitions from dinner to cleanup. The key pattern visible in the sightings: Marco's glass, which rests in the cupboard all day, ends up at the kitchen counter by 23:00 (seen there three times at that hour) — either Yuki has washed it and set it aside, or Marco arrives and places it there. His glasses move to the bathroom shelf for his evening shower around 22:00–24:00. The shopping bag, if Yuki has been out for errands, is left on the entry floor in the evening (seen there twice at 23:00) before being put away in the pantry the next morning. Marco's phone appears at the entry table around 22:00, possibly left there before his work shift or moved by Yuki. The snack bowl comes out to the counter for an evening snack.

What sets this apart from the other documents: it is the only one that makes specific predictions for the 21:00–01:00 window. The glass at the counter (not the cupboard, not the kitchen table) at 23:00 is the sharpest distinguishing prediction. The shopping bag at the entry floor (not the pantry) is another. The glasses at the bathroom shelf (not the nightstand) at 23:00 is a third.

What would refute it: if the glass is found at the cupboard or kitchen table at 23:00 on multiple occasions; if the shopping bag is at the pantry at 23:00; if the glasses are at the nightstand at 23:00; if the phone is at the coffee table at 22:00.

```json
{
 "claims": [
  {
   "claim": "Marco's glass is at the kitchen counter during the evening wind-down",
   "target": "glass_marco",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Marco's glasses are on the bathroom shelf during his evening shower",
   "target": "glasses_marco",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "The shopping bag is on the entry floor in the evening after Yuki's errands",
   "target": "shopping_bag_shared",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Marco's phone is at the entry table in the evening before his work shift ends",
   "target": "phone_marco",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 21,
   "to": 22.5
  }
 ],
 "targets": {
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "phone_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 22.5,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "plate_yuki": [
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
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
