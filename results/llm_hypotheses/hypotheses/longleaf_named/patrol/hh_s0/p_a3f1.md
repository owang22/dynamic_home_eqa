# p_a3f1 — The Standard Tuesday: Nora commutes, Yuki stays put, both home by six

Two residents share this home with a dog. Nora leaves for her office around 8:00 on weekdays and returns around 17:30. Yuki works from home at desk_b1 from roughly 9:00 to 17:30, eating lunch at the kitchen table without leaving the house. In the evening they cook together around 18:30, walk the dog around 19:30 (Nora handles the leash), and wind down with TV or reading by 21:00. On weekends both sleep in until about 9:00, run errands together from 11:00 to 14:00, and are home the rest of the day.

What sets this hypothesis apart: Yuki's keys, wallet, jacket, hat, scarf, and shoes remain in the house at all times on weekdays. The entry hook and entry table are never bare of Yuki's belongings during the workday. The dog leash stays at the entry hook until Nora picks it up in the evening.

What would refute it: keys_yuki or wallet_yuki sighted OUT_OF_HOUSE at any weekday hour, or the entry hook empty of jacket_yuki between 9:00 and 17:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Yuki's keys stay at the entry table all day on weekdays",
   "target": "keys_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 8,
   "to": 18
  },
  {
   "claim": "Yuki's jacket hangs on the entry hook during the workday",
   "target": "jacket_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 8,
   "to": 18
  },
  {
   "claim": "The dog leash is at the entry hook in the morning before the evening walk",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 7,
   "to": 18
  },
  {
   "claim": "Yuki's laptop is at the desk during work hours",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "hat_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "scarf_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "laptop_yuki": [
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
    "to": 18,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "sketchbook_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   }
  ],
  "pencil_case_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   }
  ]
 }
}
```
