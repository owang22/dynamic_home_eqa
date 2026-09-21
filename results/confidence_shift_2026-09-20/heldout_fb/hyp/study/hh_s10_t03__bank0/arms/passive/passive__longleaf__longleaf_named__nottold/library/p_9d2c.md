# p_9d2c — Weekend evening TV: snack bowl stays out, remote migrates early, controller on couch

On weekend evenings the TV and gaming session runs from about 21:00 to 23:00, and the objects behave differently than on weekdays. The snack bowl is brought to the coffee table at 21:00 (actively being used for snacks) and by 22:00 the residents have shifted to the couch, taking the bowl with them. The remote migrates to the coffee table by 21:00—earlier than on weekdays, where it stays at the TV stand until 23:00. The blanket is on the coffee table at 22:00. Omar's controller ends up on the couch at 22:00 (he has been gaming and set it down). By 23:00 the evening is winding down: Yuki's glass is at the nightstand (heading to bed), Omar's glass is on the couch (still up), his glasses are at the bedroom desk, and his tablet is at the nightstand.

What sets this apart: The weekday TV documents (p_f1a6, p_c2f9, p_a3f7, p_9d4c) all predict the snack bowl in the cupboard during TV and the remote at the TV stand. On weekends the snack bowl stays out—first on the coffee table, then on the couch. The remote is at the coffee table by 21:00. The controller is on the couch, not the TV stand. This reflects a more relaxed, longer weekend evening where people settle onto the couch rather than staying at the TV.

What would refute it: If on a weekend the snack bowl is in the cupboard at 22:00, or the remote is still at the TV stand at 21:00, or the controller is at the TV stand at 22:00, or Yuki's glass is at the coffee table at 22:00 (not yet at the nightstand).

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the couch at 22:00 on a weekend (moved from the coffee table as residents settled in)",
   "target": "snack_bowl_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The remote is at the coffee table at 21:30 on a weekend (migrated earlier than on weekdays)",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 22
  },
  {
   "claim": "Omar's controller is on the couch at 22:00 on a weekend (set down after gaming)",
   "target": "controller_omar",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 22,
   "to": 23
  },
  {
   "claim": "Yuki's glass is at the nightstand at 22:00 on a weekend (carried to the bedroom, heading to bed)",
   "target": "glass_yuki",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 22,
   "to": 23
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 21,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "controller_omar": [
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "glass_omar": [
   {
    "days": "weekend",
    "from": 23,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_omar": [
   {
    "days": "weekend",
    "from": 23,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "tablet_omar": [
   {
    "days": "weekend",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
