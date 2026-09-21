# p_7c2f — The Kitchen Waits: No Cooking Before 19:00

The evidence is overwhelming that Hana does not start cooking at 17:30. Eight empty looks for the pan on the counter during 17:30-19:00, eight for the kitchen knife, six for the cutting board. The pan is in the cupboard, the knife in the drawer, the pot in the cupboard. The kitchen is quiet in the early evening — maybe tea or coffee is made (kettle on the counter), but no full meal preparation. If cooking does happen, it starts around 19:00 and the objects come out of storage then. On a Wednesday with guests, the cooking might be even later (19:30) or they might order in entirely.

What sets this apart: the pan is in the cupboard at 18:00 (not the counter), the knife is in the drawer at 18:00 (not the counter), the pot is in the cupboard at 18:00. This directly contradicts p_b9c4 (Hana Cooks Dinner, which put all three on the counter 17:30-19:00 and accumulated 8+6+8 against) and p_c1d6 (Split Cooking, which put the pan and pot on the counter at 18:00 and accumulated 8+8 against).

What would refute it: if the pan is sighted on the counter at 18:00, or if the knife is on the counter at 18:00, or if the pot is on the counter at 18:00.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The kitchen knife is in the drawer at 18:00 on a weekday",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The pot is in the cupboard at 18:00 on a weekday",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The pan is on the counter at 20:00 on a weekday if dinner cooking has started",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kettle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
