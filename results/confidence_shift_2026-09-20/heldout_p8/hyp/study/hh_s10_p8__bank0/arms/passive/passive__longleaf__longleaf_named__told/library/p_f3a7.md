# p_f3a7 — Both drive on weekdays; Omar's tablet rests at the nightstand during his shift

Yuki and Omar both drive to work on weekdays. Yuki's helmet and bike lock stay at the entry (hook and table respectively) all day while she is at the office from 8:00 to 17:30. Omar's helmet and bike lock likewise stay at the entry during his 1:40-to-23:00 shift. Two days of helmet sightings at entry_hook_e1 during 9–17h, with zero sightings out of the house, settle the cycling question: neither resident cycles on a weekday. This directly contradicts p_7a3f (Yuki cycles) and p_a1b2 (both cycle), whose helmet-out-of-house claims have each taken two "against" votes.

This document also accounts for a new sighting: Omar's tablet was found at nightstand_b1 at 16:00 on a weekday, not at its usual chair_k1 position. The most natural explanation is that Omar leaves the tablet at the bedroom nightstand just before his 1:40 shift, and it stays there through the afternoon while both residents are at work. Yuki, home by 17:30, moves it back to the kitchen chair in the evening. The tablet is at chair_k1 at 00:00, 08:00, and 18:00, bracketing the nightstand window. This partially undermines p_d4e9, p_e5f6, p_7a3f, and p_4e91, all of which place the tablet at chair_k1 throughout the day.

What would refute this document: finding either helmet or bike lock out of the house during weekday 9–17h, or finding the tablet at chair_k1 at 16:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's helmet is at the entry hook on a weekday afternoon because she drives to work and leaves it home",
   "target": "helmet_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 16:00 on a weekday, left there before his shift",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Yuki's laptop is out of the house on a weekday morning because she took it to the office",
   "target": "laptop_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17
  },
  {
   "claim": "Omar's helmet is at the entry hook on a weekday afternoon because he drives to his shift",
   "target": "helmet_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "helmet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "helmet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 13,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 18,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "chair_k1",
    "chance": "usually"
   }
  ],
  "laptop_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_omar": [
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
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
  ],
  "class:magazine": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
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
  ]
 }
}
```
