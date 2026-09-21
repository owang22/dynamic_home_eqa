# p_d2f8 — Cyclist's kit out 8–17:30; hat, jacket, shoes stay at the entry

Elena cycles to her office. Each weekday morning she grabs her helmet, bike lock, keys, wallet, laptop, backpack, notebook, and pen, and they are out of the house from about 8:00 until 5:30. The laptop's absence is well-supported (eight weak-for empty looks at its usual spots during 9–17h). The helmet and bike lock would be at the office (helmet on a hook, lock on the bike). Her keys and wallet are in her bag.

What stays home: her hat, jacket, shoes, and umbrella remain at the entry area all day. She does not wear the hat or jacket for a short bike commute, and her shoes are at the shoe rack (she wears cycling shoes). The umbrella is at the entry floor for when it rains and she is home.

This document differs from p_1e82 ("Walker commuter") which claims the helmet and bike lock stay at the entry during work hours. It differs from p_7ef3 ("Cyclist commuter") by adding the wallet, keys, and the explicit claim that hat/jacket/shoes stay home. It differs from p_a1b2 (standard split, no specific commute mode) by naming the bike and its accessories.

Refutation: if the helmet is seen at entry_hook_e1 during 9:00–17:00 on a weekday, she is not cycling (or leaves the helmet at home). If the bike lock is at the entry table during work hours, same. If the hat or jacket is seen OUT_OF_HOUSE, the "stays home" claim is wrong. If the wallet is at the entry table at noon on a weekday, she does not take it to work.

```json
{
 "claims": [
  {
   "claim": "Elena's helmet is out of the house on weekday mornings while she cycles to work",
   "target": "helmet_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17
  },
  {
   "claim": "The bike lock is out of the house on weekdays while Elena's bike is locked at the office",
   "target": "bike_lock_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17
  },
  {
   "claim": "Elena's hat stays at the entry hook on weekdays since she does not wear it while cycling",
   "target": "hat_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Elena's wallet is out of the house on weekdays during work hours",
   "target": "wallet_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "helmet_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "hat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "umbrella_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ]
 }
}
```
