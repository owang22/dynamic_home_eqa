# p_a7f3 — Both drive on weekdays; Omar's tablet rests at the nightstand all day (fork of p_f3a7)

This fork corrects the tablet timing inherited from p_f3a7. The parent placed tablet_omar at chair_k1 from 0:00 to 13:00, but the sightings contradict this: at 00:00 the tablet was at nightstand_b1 on 2 of 3 passes, at 08:00 again 2 of 3 at nightstand_b1, and at 16:00 it was at nightstand_b1 on all 3 passes. The only chair_k1 sighting in the day is at 18:00 (1/1). The tablet is a bedroom object overnight and through the working day; it moves to the kitchen chair only in the evening, after Yuki arrives home at 17:30 and the household shifts to living-room/kitchen activity.

Everything else in the parent is retained: both residents drive on weekdays (helmets and bike locks at entry 3/3 in the 9–17h window, zero out-of-house sightings), Yuki's laptop and keys are OUT_OF_HOUSE 8:00–17:30, and Omar's keys are OUT_OF_HOUSE 13:40–23:00.

What changed: the three tablet blocks are replaced by two (nightstand 0–17, chair 17–24). The claim about the tablet at nightstand 14–18 is retained; a new claim is added for the tablet at nightstand at 08:00, which the parent's chair_k1 block would have predicted wrong.

What would refute this document: finding tablet_omar at chair_k1 at 10:00 or 14:00 on a weekday, or finding either helmet out of the house during weekday 9–17h.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 08:00 on a weekday, still in its overnight position",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 7,
   "to": 9
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
   "claim": "Yuki's helmet is at the entry hook on a weekday afternoon because she drives to work and leaves it home",
   "target": "helmet_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
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
    "to": 17,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "chair_k1",
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
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_omar": [
   {
    "days": "weekday",
    "from": 13.5,
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
