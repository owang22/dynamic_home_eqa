# p_2b5f — Yuki's water bottle: dish rack overnight, entry hook at 18, dining table at dinner

A focused document on water_bottle_yuki's daily arc, which the library has been handling inconsistently. The sightings are clear: at 03:00 on weekdays the bottle is in the dish rack (x3) or the sink (x1); at 18:00 it is at the entry hook (x1, just carried in from outside); at 19:00 it is at the dining table (x4, dinner); at 20:00 it is at the dining table (x2, still at dinner). On weekends at 03:00 it is in the dish rack (x2), and at 19:00 it is back in the dish rack (x1, washed after a weekend meal).

The bottle's cycle is: out of the house with Yuki on weekday mornings (7.8–17.5), arrives at the entry hook when she comes home (~17:50), moves to the dining table for dinner (19:00–20:30), is washed and put in the dish rack (~21:00), and stays in the dish rack overnight. On weekends it stays home, is used at the dining table for meals, and ends up in the dish rack by evening.

This document is distinguished from p_c007 and p_a1b2 (which put the bottle at the entry hook as its all-day resting spot) by giving it a proper multi-receptacle arc. It is distinguished from p_f8b2 and p_6c2b (which focus on the dinner phase) by covering the full 24-hour cycle including the overnight dish-rack state. It would be refuted if the bottle is found at the entry hook at 19:00 on a weekday (should be at the dining table by then), or at the dining table at 03:00 (should be in the dish rack).

```json
{
 "claims": [
  {
   "claim": "Yuki's water bottle is in the dish rack at 03:00 on a weekday (washed after dinner, drying overnight)",
   "target": "water_bottle_yuki",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 1,
   "to": 7
  },
  {
   "claim": "Yuki's water bottle is at the dining table at 19:30 on a weekday (dinner in progress)",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  },
  {
   "claim": "Yuki's water bottle is at the entry hook at 18:00 on a weekday (just carried in from outside, not yet moved to the table)",
   "target": "water_bottle_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  }
 ],
 "targets": {
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20.5,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ]
 }
}
```
