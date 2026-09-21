# p_2f4a — Morning: bathroom by 7, dog fed by 8, laptop packed by 8

Elena wakes around 6 and is in the bathroom by 6:30. Her toiletry bag is pulled from the dresser to the bathroom shelf, her skincare bottles are set out, and her towel is on the shelf for drying off. Her hair dryer is a permanent fixture on that same shelf. By 7:30 she's done, grabs her laptop from wherever it rested (entry hook or coffee table), and is out the door by 8. Priya gets up a little later; around 7 she sets her reading glasses on the bathroom shelf while she washes up, then takes them back to the nightstand. The dog's morning feeding happens around 7:30–8:30: the food bag is dragged from the pantry shelf to the kitchen floor, the bowl is already there, and the bag goes back to the pantry by 9.

What sets this document apart: it pins the *order* of the morning. The toiletry bag is at the dresser at 3 a.m. and on the bathroom shelf by 7; the glasses are at the nightstand at 3 a.m. and on the bathroom shelf at 7; the food bag is in the pantry at 3 a.m. and on the kitchen floor at 7–8. A document that puts these items at their resting spots through the whole morning will be contradicted by the 7 a.m. looks.

Refutation: if the toiletry bag is still at the dresser at 7:15 on a weekday, or the dog food bag is in the pantry at 8 a.m. on a weekend morning, or Priya's glasses are not on the bathroom shelf at 7, this document is wrong about the timing.

```json
{
 "claims": [
  {
   "claim": "Elena's toiletry bag is on the bathroom shelf at 7:00 on a weekday",
   "target": "toiletry_bag_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 7.5
  },
  {
   "claim": "The dog food bag is on the kitchen floor at 7:30 on a weekend morning",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekend",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Priya's glasses are on the bathroom shelf at 7:00 on a weekday",
   "target": "glasses_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 6.5,
   "to": 7.5
  },
  {
   "claim": "Elena's towel is on the bathroom shelf at 7:30 on a weekday",
   "target": "towel_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8
  }
 ],
 "targets": {
  "toiletry_bag_elena": [
   {
    "days": "weekday",
    "from": 6,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 22,
    "at": "dresser_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 6.5,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 22,
    "at": "dresser_b1",
    "chance": "usually"
   }
  ],
  "skincare_elena": [
   {
    "days": "weekday",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 22,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 22,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "towel_elena": [
   {
    "days": "weekday",
    "from": 6.5,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 22,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 22,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 22,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8.5,
    "to": 19,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
