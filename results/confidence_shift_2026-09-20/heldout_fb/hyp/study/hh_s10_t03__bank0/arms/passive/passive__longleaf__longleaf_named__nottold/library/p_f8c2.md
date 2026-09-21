# p_f8c2 — The 19:00 cook: pan and knife come out, cutting board stays on the counter

The 18:00 pass shows the pan still in the cupboard, the cutting board already on the counter, and the kitchen knife in the drawer. By 19:00 the picture has changed: the pan is on the counter (2×), the cutting board is still on the counter (2×), and the knife has come out to the counter (1×) while a second pass still finds it in the drawer (1×). This is a brief, light cooking window centred on 19:00. It is not the 18:00 start that p_c007 predicts (its pan-at-counter claim collected 12 "against" tallies), and it is not the "no cooking at all" that p_8d2c and p_7b3e assert (their pan-at-cupboard claims each collected 7–10 "against" tallies). Yuki is home by 17:30 and Omar is at work, so this is her solo dinner prep: she takes the pan out around 18:30, works with the cutting board that was already out, and briefly needs the knife for a quick chop. By 20:00 the pan goes to the sink and the knife returns to the drawer.

This document differs from p_c007 (cooking starts at 18, not 18:30–19), p_8d2c (no pan on counter at all), and p_7b3e (no active cooking). It agrees with p_b4e6 that the knife-based work is minimal, but adds that the pan does come out.

What would refute it: two or more 19:00 passes that find the pan still in the cupboard, or a 19:00 pass that finds the knife in the sink (implying a heavier, wetter cook than a quick chop).

```json
{
 "claims": [
  {
   "claim": "The shared pan is on the kitchen counter at 19:00 on a weekday during Yuki's dinner prep",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The shared cutting board is on the kitchen counter at 19:00 on a weekday",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The shared kitchen knife is on the kitchen counter at 19:00 on a weekday (briefly out for a chop)",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 19.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 6,
    "to": 18,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ]
 }
}
```
