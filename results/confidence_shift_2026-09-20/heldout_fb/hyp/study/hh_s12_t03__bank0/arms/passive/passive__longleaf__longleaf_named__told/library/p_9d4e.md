# p_9d4e — The evening: dinner at 19, TV at 20

Both residents are home by 18:00 (Elena arrives at 17:30). The evening follows a tight sequence that the clock-hour sightings make visible: at 18:00 the remote is on the tv_stand (TV just switched on) and the glasses are still in the kitchen (sink or cupboard); by 19:00 Priya's glass is at the dining table (dinner is underway); by 20:00 Elena's glass and her water bottle are at the dining table, the remote has returned to the coffee table, and Priya's reading glasses have migrated from the nightstand to the coffee table (she is settling in for TV). At 22:00 the blanket has moved from the couch to the coffee table (three sightings), the remote is back on the coffee table (four sightings), and Priya's glass is put away in the cupboard. The mugs follow a parallel arc: in the cupboard at 18:00, on the coffee table by 20–21:00 (evening tea/coffee while watching TV).

This document is about the *sequence*, not about who goes where during the day. It overlaps with p_a1b2 and p_c3d4 on the daytime picture but adds the evening choreography that none of them spell out. It is refuted if, say, the remote is found on the coffee table at 18:00 (TV not on) or the blanket is still on the couch at 22:00 (no late TV).

```json
{
 "claims": [
  {
   "claim": "Priya's glass is at the dining table during dinner",
   "target": "glass_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The remote is on the tv stand when TV first starts in the evening",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The blanket is on the coffee table during late-evening TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22,
   "to": 23
  },
  {
   "claim": "Elena's water bottle is at the dining table during dinner",
   "target": "water_bottle_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
