# p_4e7f — Priya's desk_b1: the bedroom is her studio

Priya's creative life is anchored at desk_b1 in the bedroom, not the office. Her headphones and pen are sighted at desk_b1 on all six days the robot has looked, and her guitar rests on bedroom_floor_b1. The office (desk_o1) holds only a plant pot and is otherwise an empty room. On weekdays Priya is home most of the day: a morning walk around 7–8, then the desk from 10 onward for guitar practice, reading, and writing, with an errand window 12–15 (shopping bag at the kitchen counter). On weekends she stays home, takes a late-morning walk, and returns to the desk in the afternoon. Elena is out on weekdays (commuting) and home on weekends.

This document sets itself apart from p_e5f6, which places Priya's creative work at desk_o1, and from p_6b4e, which also says desk_b1 but is sparse on the full weekly rhythm. The 6/6-day consistency of headphones and pen at desk_b1 is the core evidence: the office is not her studio.

What would refute it: headphones or pen found at desk_o1 during a weekday afternoon; the guitar found in the office; the yoga mat found on the living-room floor during a weekday morning (it stays in the wardrobe).

```json
{
 "claims": [
  {
   "claim": "Priya's headphones are at the bedroom desk on weekday afternoons",
   "target": "headphones_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Priya's pen is at the bedroom desk on weekday afternoons",
   "target": "pen_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 14
  },
  {
   "claim": "The guitar rests on the bedroom floor at midday on a weekday",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "The shopping bag is at the kitchen counter during Priya's midday errand window",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 12,
   "to": 15
  }
 ],
 "targets": {
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 9,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
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
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "almost_always"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 15,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
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
    "from": 14,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
