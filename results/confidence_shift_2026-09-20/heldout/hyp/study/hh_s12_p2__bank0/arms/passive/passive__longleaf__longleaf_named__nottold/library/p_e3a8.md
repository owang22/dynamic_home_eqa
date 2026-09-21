# p_e3a8 — Resting-place splits: razor, sunglasses, toiletry bag, and dog food bag

A fresh document built around the four objects where the mixture's single-location prediction is consistently wrong. The per-hour data shows each of these objects occupies two (or three) receptacles in a stable split, not a single "usual place." The razor is 2/3 at the sink and 1/3 at the medicine cabinet, shifting toward the cabinet during the day. The sunglasses are mostly at the entry table but drop to the entry floor in the mid-afternoon. Elena's toiletry bag splits between the dresser and the bathroom shelf, with the bathroom shelf gaining ground during the day. The dog food bag is solidly in the pantry from 10:00 to 18:00 but scatters across pantry, kitchen table, and kitchen floor at night and early morning (feeding time). No existing document captures these secondary locations. What sets this apart: it predicts the secondary resting place during the hours when the object is NOT at its primary location. What would refute it: the razor found at the sink three consecutive hours during 12–16 h (meaning the cabinet is not a real resting place), or the dog food bag found in the pantry at 20:00 and 22:00 (meaning the night scatter is an artifact).

```json
{
 "claims": [
  {
   "claim": "Priya's razor is at the medicine cabinet during weekday afternoons",
   "target": "razor_priya",
   "expect": "medicine_cabinet_ba1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Priya's sunglasses are on the entry floor in the mid-afternoon",
   "target": "sunglasses_priya",
   "expect": "entry_floor_e1",
   "days": "both",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Elena's toiletry bag is on the bathroom shelf during weekday afternoons",
   "target": "toiletry_bag_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "The dog food bag is in the pantry during the midday window",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 12,
   "to": 16
  }
 ],
 "targets": {
  "razor_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 10,
    "to": 17,
    "at": "medicine_cabinet_ba1",
    "chance": "sometimes"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 17,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "toiletry_bag_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dresser_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 10,
    "to": 17,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
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
    "from": 10,
    "to": 18,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
