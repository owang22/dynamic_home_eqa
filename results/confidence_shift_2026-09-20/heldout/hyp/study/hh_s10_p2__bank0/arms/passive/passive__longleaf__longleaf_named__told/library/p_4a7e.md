# p_4a7e — Weekend bedroom desk: both residents work and study at desk_b1 in the afternoon

Yuki and Omar are home all day on weekends, and the evidence is unambiguous: from midday onward, both of them gravitate to the bedroom desk (desk_b1). On Saturday, Yuki's laptop, notebook, and pen all appear at desk_b1 from 12:00 through 22:00, and Omar's notebook and pen do the same. Omar's reading glasses also sit at desk_b1 all day on weekends rather than at the nightstand where they rest on weekdays. This is the single largest source of prediction error in the current library: the mixture keeps predicting entry_hook_e1 for Yuki's laptop and notebook (the weekday "she took it to work" pattern) and entry_hook_e1 for Omar's notebook and pen, when on weekends those items are at the bedroom desk. The weekend is when they actually *use* the desk for journaling, reading, and light work; on weekdays the items are in transit (out the door) or dumped at the entry.

What this document predicts that sets it apart: on any weekend hour from 12:00 to 22:00, Yuki's laptop and notebook are at desk_b1, not entry_hook_e1; Omar's notebook and pen are at desk_b1, not entry_hook_e1; and Omar's glasses are at desk_b1 for the entire weekend, not at the nightstand. Before 12:00 on weekends, Yuki's laptop and notebook are still at entry_hook_e1 (overnight resting spot, same as weekday evenings), and Omar's notebook and pen are at entry_hook_e1 as well.

This document is refuted if, on a weekend afternoon, the laptop or notebook is sighted at entry_hook_e1 (meaning she did not move it to the desk), or if Omar's glasses are at the nightstand during weekend hours.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is at the bedroom desk during weekend afternoons",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 12,
   "to": 22
  },
  {
   "claim": "Omar's notebook is at the bedroom desk during weekend afternoons",
   "target": "notebook_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 12,
   "to": 22
  },
  {
   "claim": "Omar's glasses are at the bedroom desk all day on weekends, not the nightstand",
   "target": "glasses_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Yuki's notebook is at the bedroom desk during weekend afternoons",
   "target": "notebook_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 12,
   "to": 22
  }
 ],
 "targets": {
  "laptop_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "notebook_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "pen_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "glasses_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "pen_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
