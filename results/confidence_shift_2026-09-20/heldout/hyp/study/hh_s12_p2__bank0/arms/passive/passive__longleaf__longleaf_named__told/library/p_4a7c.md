# p_4a7c — Transit commuter; bike is weekend recreation

Elena commutes to her office by car or public transit, not by bicycle. Her cycling gear—helmet, bike lock, and hat—stays hooked at the entry all week because she only rides on weekends or for evening recreation. What she actually takes out in the morning is her work kit: laptop, charger, notebook, pen, phone, keys, wallet, backpack, and water bottle. She leaves around 8 and is back by 17:30. Priya is retired and home most of the day: a short walk before 8, a stretch of errands from about 13 to 16, and she is back in by early evening. Wednesday evening she is home (her glasses are on the nightstand, not out with her). The dog is fed by Elena in the morning and by Priya around midday; the dog's toy stays on the living-room floor and is not taken out on walks.

This hypothesis is set apart from p_7ef3 (cyclist commuter) by placing the helmet, bike lock, and hat at the entry during work hours rather than out of the house. It differs from p_1e82 by keeping Priya home on Wednesday evenings. It differs from p_c3d4 and p_f8a6 by having Elena's laptop out of the house on all weekday work days (no WFH pattern).

Refutation: if the helmet or bike lock is sighted out of the house on a weekday morning, or if the laptop is found at a desk (desk_b1 or desk_o1) during weekday 9–17h on multiple days, this document is wrong. If Priya's glasses are out of the house on a Wednesday evening, the Priya-home-evening claim fails.

```json
{
 "claims": [
  {
   "claim": "Elena's helmet is at the entry hook during weekday work hours",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's laptop is out of the house on a weekday during work",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Priya's glasses are on the nightstand Wednesday evening",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The dog toy is on the living room floor during the evening",
   "target": "dog_toy_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 18,
   "to": 20
  }
 ],
 "targets": {
  "helmet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "hat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
