# p_a3d7 — Both drive on weekdays; Omar's tablet rests at the nightstand during his shift

Yuki and Omar both drive to work on weekdays. The evidence is unambiguous: both bike locks (bike_lock_omar, bike_lock_yuki) are found at the entry table on every sighted weekday, and both helmets (helmet_omar, helmet_yuki) hang at the entry hook throughout the day. Neither resident cycles to work; cycling is a weekend-morning ritual only. Yuki leaves at roughly 8:00 and returns at 17:30, taking her keys, laptop, backpack, jacket, shoes, sunglasses, wallet, and water bottle with her. Omar leaves at roughly 13:40 and returns at 23:00, taking his keys, phone, wallet, handbag, lunchbox, notebook, pen, shoes, and scarf.

The critical correction this document makes is about Omar's tablet. Multiple competing hypotheses (p_e5f6, p_7a3f, p_4e91, p_d4e9) place it at the kitchen chair during his work hours, but the robot's weekday 9–17 h looks at the nightstand found the tablet every time (2/2), while the kitchen-chair claims accumulated against-scores. The pattern in the clock-hour sightings is: at 16:00 the tablet is at the nightstand (both passes), at 18:00 it is back at the kitchen chair. The most parsimonious reading is that Omar takes the tablet to the bedroom nightstand before heading out (or Yuki relocates it mid-afternoon), and it returns to the kitchen chair in the evening when Yuki is home and Omar comes back at 23:00.

This document is refuted if: (a) either bike lock is seen at the entry table during a weekday 9–16 h window while the corresponding helmet is simultaneously out of the house (indicating one of them actually cycles); (b) the tablet is sighted at the kitchen chair during a weekday 14–17 h look; or (c) Yuki's keys or laptop are found inside the house during a weekday 10–15 h window (contradicting her being at the office).

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand during his work hours on weekdays",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Yuki's bike lock remains at the entry table on weekday mornings because she drives to work",
   "target": "bike_lock_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Omar's helmet remains at the entry hook on weekday afternoons because he drives to his shift",
   "target": "helmet_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Yuki's keys are out of the house during her work hours on weekdays",
   "target": "keys_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 16
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 18,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "chair_k1",
    "chance": "usually"
   }
  ],
  "class:bike_lock": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "class:helmet": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "laptop_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_omar": [
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
