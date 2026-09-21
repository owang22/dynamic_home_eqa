# p_5b7e — Omar's weekday morning: kitchen till eight, bathroom, gaming, out at 13:40

Omar is home from roughly 23:00 through 13:40 on weekdays. The resident-look log places him in the kitchen at 00:00, 02:00, 04:00, 06:00, and 08:00—consistent with him making coffee, taking his vitamins, and getting ready while Yuki is still asleep (she is in the bedroom at those hours). At 08:00 on day 2 both residents are in the kitchen together, the one overlap before their paths diverge. Omar then moves to the bathroom around 08:00–10:00 (shower, grooming), and from 10:00 to 13:00 he games at the TV stand (controller confirmed there). His tablet is at the kitchen chair in the very early hours (00:00–08:00) but migrates to the nightstand by 12:00, suggesting he reads or scrolls in bed before getting up, then the tablet stays at the nightstand while he games. At about 13:40 he grabs his handbag, lunchbox, notebook, pen, and wallet from the entry area and leaves for his afternoon shift.

This document is set apart from p_e5f6 (which places the tablet at the kitchen chair 07:00–13:00) by the clock evidence showing the tablet at the nightstand from 12:00 onward and at the kitchen chair only 00:00–08:00. It differs from p_c007 in that it specifies Omar's *morning* sequence in detail rather than the shared cooking window.

Refutation: finding Omar in the bedroom (not kitchen) at 02:00–06:00 on a weekday; finding his controller anywhere other than the TV stand between 10:00 and 13:00; finding his tablet at the kitchen chair at 14:00 or later on a weekday.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the kitchen chair at 06:00 on a weekday",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 4,
   "to": 8
  },
  {
   "claim": "Omar's controller is at the TV stand at 11:00 on a weekday during his gaming block",
   "target": "controller_omar",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 10,
   "to": 13
  },
  {
   "claim": "Omar's vitamins are at the kitchen table at 06:30 on a weekday",
   "target": "vitamins_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 6,
   "to": 7.5
  },
  {
   "claim": "Omar's handbag is at the entry hook at 08:00 on a weekday before he leaves for work",
   "target": "handbag_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 7,
   "to": 12
  },
  {
   "claim": "Omar's tablet is at the nightstand at 14:00 on a weekday while he is at work",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 12,
   "to": 18
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "controller_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 13,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "vitamins_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "mug_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "handbag_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "pen_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
