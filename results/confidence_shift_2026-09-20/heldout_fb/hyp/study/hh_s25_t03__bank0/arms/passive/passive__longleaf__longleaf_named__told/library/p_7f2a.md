# p_7f2a — Omar's sick day Wednesday: bed rest, nothing leaves the house

Omar called in sick on Wednesday (today). He sleeps in past his usual 9 AM start, stays in bed through the morning and into the afternoon, and probably drifts onto the couch by late afternoon. He is not working, not going out for lunch, and not making errands. His laptop, notebook, and headphones stay at desk_o1 untouched. His mug migrates to the nightstand where he sips tea in bed. The blanket is pulled up over him in bed rather than resting on the couch. Marco continues his normal WFH day at desk_b1, 9 to about 5:30, occasionally stepping out for lunch as usual.

This document differs from p_c3d4, p_d4e9, and p_b8c2 in that Omar does NOT leave the house for lunch on this weekday—his keys, wallet, and jacket stay at their resting spots all day. It differs from p_a1b2 and p_a3f7 in that Omar is not at his desk during work hours; he is in bed. The blanket's daytime location is the bed, not the couch, and Omar's mug is on the nightstand, not at the desk.

This would be refuted if: Omar's keys or wallet are sighted out of the house during the day; the blanket is sighted on the couch during 10–16; Omar is seen at desk_o1 actively working; or Omar's mug is found at desk_o1 during the morning hours.

```json
{
 "claims": [
  {
   "claim": "Omar's keys remain at the entry table during the lunch window because he is sick and not going out",
   "target": "keys_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "The blanket is on the bed during the afternoon while Omar rests",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Omar's mug is on the nightstand in the morning while he is in bed",
   "target": "mug_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 8,
   "to": 12
  },
  {
   "claim": "Omar's jacket stays on the entry hook all day since he does not leave",
   "target": "jacket_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 12,
   "to": 14
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "bed_b1",
    "chance": "rarely"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "mug_omar": [
   {
    "days": "weekday",
    "from": 8,
    "to": 14,
    "at": "nightstand_b1",
    "chance": "rarely"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "laptop_omar": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "keys_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "class:keys": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "class:wallet": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "class:jacket": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
