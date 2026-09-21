# p_a3f7 — The 21:00 TV setup: blanket and mug on coffee table, snack bowl in cupboard

Yuki and Omar settle into the living room around 20:30 on weekdays. The shared blanket comes off the couch (where it rests all day) and lands on the coffee table. Yuki's mug — her evening tea or coffee — goes to the coffee table beside her. The snack bowl, however, does NOT come out onto the table; it goes into the kitchen cupboard, suggesting either they don't snack during TV or it is stored away clean after the evening meal. The remote stays at the TV stand through most of the evening and only migrates to the coffee table around 22:00–23:00 when they shift positions.

This hypothesis is set apart by the snack bowl going INTO the cupboard during TV hours (20:30–22:30) rather than sitting on the coffee table or counter. Documents that predict the snack bowl on the coffee table during TV will be contradicted by the 21:00 and 22:00 passes showing it in the cupboard. The blanket's move from couch to coffee table at 20:30 is also a hard prediction: any sighting of the blanket still on the couch at 21:00 refutes this document.

What would refute it: the snack bowl on the coffee table or counter at 21:00–22:00; the blanket on the couch at 21:00; the mug in the cupboard at 21:00.

```json
{
 "claims": [
  {
   "claim": "The shared blanket is on the coffee table at 21:30 on a weekday during TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "Yuki's mug is at the coffee table at 21:30 on a weekday (her TV drink)",
   "target": "mug_yuki",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The snack bowl is in the kitchen cupboard at 21:30 on a weekday (stored away during TV, not on the table)",
   "target": "snack_bowl_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The remote is still at the TV stand at 21:00 on a weekday (has not migrated to the coffee table yet)",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20.5,
   "to": 22
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "mug_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 20.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22.5,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
