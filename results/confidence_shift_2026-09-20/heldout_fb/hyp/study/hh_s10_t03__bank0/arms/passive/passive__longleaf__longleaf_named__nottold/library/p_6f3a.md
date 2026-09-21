# p_6f3a — Weekday 19:00 quick cook: pan emerges from cupboard, knife briefly out

On weekday evenings Yuki does a brief cooking session centred on 19:00. The pan is confirmed in the cupboard at 18:00 and on the counter at 19:00 (two sightings), meaning it is taken out between 18:00 and 19:00 and used for roughly 30 minutes. The cutting board is already on the counter at 18:00 (it has been out since earlier prep) and remains there through 19:00. The kitchen knife is in the drawer at 18:00 and briefly appears on the counter at 19:00 (one sighting)—a quick chop, not a full cooking session. The pot stays in the cupboard throughout. This is a quick meal assembly, not a full dinner cook: the pan is out for under an hour, and by 19:30 everything is back in storage.

What sets this apart: The wider-window documents (p_c007 with 18–19.5h for the pan on the counter) are penalised because at 18:00 the pan is still in the cupboard. The "no cooking" documents (p_8d2c, p_7b3e, p_b4e6) predict the pan stays in the cupboard, but the 19:00 sightings contradict this. This document uses a tight 19–19.5h window for the pan being out and a separate 18–19h window for it being in the cupboard. The knife is only briefly out (sometimes, not usually).

What would refute it: If the pan is found in the cupboard at 19:00 on a weekday (not on the counter), or on the counter at 18:00 (too early), or if the knife is on the counter at 18:00 (before the cook begins).

```json
{
 "claims": [
  {
   "claim": "The shared pan is on the kitchen counter at 19:00 on a weekday (just emerged from the cupboard for the quick cook)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 19.5
  },
  {
   "claim": "The shared pan is in the kitchen cupboard at 18:00 on a weekday (not yet taken out for cooking)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 18,
   "to": 18.5
  },
  {
   "claim": "The shared cutting board is on the kitchen counter at 18:30 on a weekday (out since earlier prep)",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The shared kitchen knife is in the drawer at 18:00 on a weekday (not yet needed for the cook)",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 18,
   "to": 18.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
