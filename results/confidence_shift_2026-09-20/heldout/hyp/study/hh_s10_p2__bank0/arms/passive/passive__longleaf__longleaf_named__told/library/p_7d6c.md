# p_7d6c — Omar's weekday morning: home 6:00–13:30, kitchen activities, out at 13:30

Omar is home from roughly 6:00 (or earlier, just after his night shift ends at 23:00 the previous night) until 13:30 on weekdays. His morning is kitchen-centric: he is in the kitchen at 08:00, 10:00, and 12:00. Around 10:00 he sits at the kitchen table for coffee, takes his vitamins, and scrolls his tablet. His personal items (keys, wallet, jacket, shoes, handbag, lunchbox, notebook, pen) are at the entry from 06:00 until he grabs them at 13:30 to head to work.

The 9–17 h window for his entry items shows a clean split: roughly 4–6 sightings at the entry (9:00–13:30, he is home) and 6–8 empty looks (13:30–17:00, he is at work). His helmet and bike lock are the exception: they are at the entry *all day* (12/12) because he drives to work.

This differs from p_e5f6 (which puts his tablet at the kitchen chair 7–13 h and his controller at the TV stand 10–13 h for gaming) in that the tablet is at the *nightstand* or *kitchen table*, not the kitchen chair, and the 10:00 pass shows him in the kitchen, not gaming. It agrees with p_3e7a that his cycling gear stays home.

Refuted if the robot finds Omar's keys at the entry table at 15:00 on a weekday (he has not left yet) or finds his jacket at the entry at 20:00 (he has not come home yet, but it should be out with him).

```json
{
 "claims": [
  {
   "claim": "Omar's keys are at the entry table at 10:00 on a weekday (he is home, not yet at work)",
   "target": "keys_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Omar's vitamins are at the kitchen table at 10:00 on a weekday (morning routine)",
   "target": "vitamins_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9.5,
   "to": 10.5
  },
  {
   "claim": "Omar's mug is at the kitchen table during his morning on weekdays",
   "target": "mug_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 10,
   "to": 13
  },
  {
   "claim": "Omar's jacket is at the entry hook at 10:00 on a weekday (he is home, not yet at work)",
   "target": "jacket_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 13
  }
 ],
 "targets": {
  "keys_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "handbag_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "vitamins_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
