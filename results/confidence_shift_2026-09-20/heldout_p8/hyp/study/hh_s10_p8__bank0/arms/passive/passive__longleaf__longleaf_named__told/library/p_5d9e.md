# p_5d9e — Dinner prep in two stages: cutting board out at 18:00, pan and pot still in storage

Yuki gets home at 17:30 and begins dinner in two distinct stages. The 18:00 weekday pass shows the cutting board already on the counter while the pan, pot, knife, and spatula are still in their storage spots: cupboard_k1 (pan, pot), drawer_k_k1 (knife, spatula). She starts by prepping vegetables — cutting board out, knife still in the drawer — before moving to actual cooking. The pan and pot come out around 19:00, when the stove is lit.

This reconciles p_c007 (which places the cutting board at the counter at 18:00, confirmed by the 18:00 sighting) with p_a3f7 (which places the pan at the cupboard at 18:30, also consistent with the 18:00 cupboard_k1 sighting). The two documents are not in conflict; they describe different stages of the same process. The cutting-board claim in p_c007 has accumulated 7 "against" votes, but those likely come from time windows where the board is at the sink; the 18:00 counter_k1 sighting is genuine.

What sets this apart: the explicit two-stage model (prep 18–19, cook 19–20) and the prediction that the pan is still in the cupboard at 18:00 while the cutting board is already on the counter. Refutation: finding the pan on the counter at 18:00, or the cutting board at the sink at 18:00.

```json
{
 "claims": [
  {
   "claim": "The cutting board is on the kitchen counter at 18:00 on a weekday while Yuki preps vegetables",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The pan is at the kitchen sink at 10:00 on a weekday because no one is home to cook",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "The pot is on the pantry shelf at 10:00 on a weekday because it has not been taken out for cooking",
   "target": "pot_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "The pan is on the kitchen counter at 19:30 on a weekday while Yuki cooks dinner",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  }
 ],
 "targets": {
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
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "class:kitchen_knife": [
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
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "sometimes"
   }
  ],
  "class:spatula": [
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
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "sometimes"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "class:book": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
