# p_9c1d — Priya's weekday: nightstand glasses, dish-rack bottle, guitar afternoon (fork of p_d6a1)

This document models Priya's full weekday arc in detail. **What changed from the parent:** two blocks and their associated claims are revised based on accumulating evidence.

First, the glasses_priya blocks: the parent asserted "desk_b1 weekday 8–17h usually." The evidence now shows the glasses are at the nightstand 4 of 9 weekday midday looks, at desk_b1 at 4 of those hours, and on the bedroom floor at 2. The glasses are a nightstand object that visits the desk in the morning (8–12h) but returns to the nightstand by early afternoon. The block is changed to "nightstand_b1 all day usually" with a "desk_b1 weekday 8–12h sometimes" override. The claim is revised to expect the nightstand.

Second, the water_bottle_priya block: the parent asserted "sink_k1 weekday 10–17h usually." The evidence shows a 1-to-1 split between sink_k1 and dish_rack_k1 during 12:00–16:00 (the "mostly" is dish_rack_k1 at 3/4 sighted days). The bottle is at the dish rack in the morning and evening, and is found at the sink only half the time during the midday window. The block is downgraded to "sometimes" to reflect the 50/50 split. The claim is revised to expect the dish rack (the more frequent location overall).

Everything else is unchanged: headphones and pen at desk_b1 all day; guitar on the bedroom floor; glass at the sink or desk; book at the nightstand; yoga mat in the wardrobe.

What sets this hypothesis apart from the parent: the glasses are a nightstand anchor (not desk_b1), and the water bottle is a dish-rack anchor with occasional sink visits (not a sink anchor).

Refutation: if the glasses are found at desk_b1 on 8+ of 10 weekday midday looks; if the water bottle is at the sink on 8+ of 10 weekday midday looks (12–16h); if the guitar is found off the bedroom floor during 9–17h.

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are at the nightstand during weekday midday",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's guitar is on the bedroom floor during weekday midday",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's water bottle is at the dish rack during weekday midday",
   "target": "water_bottle_priya",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Priya's headphones are at desk_b1 during weekday midday",
   "target": "headphones_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
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
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
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
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "shoes_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
