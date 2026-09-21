# p_e9c2 — Yuki's water bottle: entry dump at 18, dining table by 19

Yuki arrives home at 17:30 on weekdays. Her water bottle, carried in from the office in her bag, gets set down at the entry hook along with her laptop and notebook — a brief 30-minute stop before she moves to the kitchen and dining area. By 19:00 the bottle is at the dining table, in reach for dinner. Overnight it sleeps in the kitchen sink or dish rack (washed from the previous evening). On weekends, when Yuki is home all day, the bottle follows a simpler kitchen-to-dining-table arc without the entry stop.

This document is set apart by the specific two-stop evening arc: entry_hook (17:30–18:30) then dining_table (18:30–20:00). The p_b2c8 "permanent chaos" document predicts the bottle stays at the entry hook through the evening (19–23h); this document says it is moved to the dining table by 19:00. The three 19:00 sightings at dining_table strongly support the dinner-table placement.

What would refute it: the water bottle at the entry hook after 19:00; the bottle at the coffee table during TV time; the bottle at the dining table before 18:30 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Yuki's water bottle is at the entry hook at 18:00 on a weekday (just arrived, not yet moved)",
   "target": "water_bottle_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  },
  {
   "claim": "Yuki's water bottle is at the dining table at 19:00 on a weekday (dinner phase)",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "Yuki's water bottle is at the dining table at 19:30 on a weekday (still at dinner)",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19,
   "to": 20
  }
 ],
 "targets": {
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "almost_always"
   }
  ]
 }
}
```
