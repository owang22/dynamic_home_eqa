# p_e5a8 — Omar's lunchbox hangs at the entry hook overnight and in the morning

The robot's recent passes find lunchbox_omar at entry_hook_e1 five times since the last call (e.g. day 7 00:00), where the mixture predicted cupboard_k1. The cumulative sightings confirm: on weekdays from 00:00 through 12:00 the lunchbox is at entry_hook_e1 (3×) with only 1× at cupboard_k1. It is only in the afternoon and evening of weekends that it shifts to cupboard_k1 (2× at 12:00–22:00). The pattern is: Omar packs his lunch the night before or early morning, hooks the lunchbox on the entry hook beside his keys and wallet, and takes it with him at 13:30. On weekends, with no work shift, the lunchbox is put away in the cupboard at midday.

This document differs from p_9c1b (which puts the lunchbox at cupboard_k1 on weekends 12–22 h but does not specify the weekday morning location) and from the mixture's default (cupboard_k1). It specifically claims entry_hook_e1 for the weekday 0–13 h window.

Refutation: if the robot finds lunchbox_omar at cupboard_k1 at the 00:00 or 06:00 pass on three consecutive weekdays, the hook pattern has ended.

```json
{
 "claims": [
  {
   "claim": "Omar's lunchbox is at the entry hook at 06:00 on a weekday (packed and waiting for his shift)",
   "target": "lunchbox_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 5,
   "to": 13
  },
  {
   "claim": "Omar's lunchbox is at the entry hook at 10:00 on a weekday (he is home but has not yet left for work)",
   "target": "lunchbox_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Omar's lunchbox is in the kitchen cupboard on weekend afternoons (no work shift, put away at midday)",
   "target": "lunchbox_omar",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 12,
   "to": 22
  }
 ],
 "targets": {
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
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
