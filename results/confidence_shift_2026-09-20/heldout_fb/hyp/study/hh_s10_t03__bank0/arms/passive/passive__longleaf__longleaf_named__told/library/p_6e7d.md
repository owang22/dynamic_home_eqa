# p_6e7d — Weekend evening TV: snack bowl and remote on the coffee table, controller on the couch

On weekend evenings (20:00–23:00), the household settles into the living room for TV and gaming. The snack bowl comes out of the cupboard (or the counter) and sits on the coffee table—unlike weekdays where it sometimes stays in the cupboard. The remote migrates from the TV stand to the coffee table, within arm's reach on the couch. Omar's controller is on the couch for his gaming session (21:00–23:00), and the shared blanket is pulled onto the coffee table. On Sunday evening, friends are over, so the setup is more social: the snack bowl is definitely out, and the controller is in active use.

This differs from p_f1a6 and p_a3f7, which say the snack bowl stays in the cupboard during TV and the remote stays at the TV stand. It differs from p_9f4a, which has the controller on the couch but the remote at the coffee table with a low weight. Here the full weekend TV setup is: bowl out, remote on the table, controller on the couch. It would be refuted if, on a weekend 21:00 pass, the snack bowl is in the cupboard AND the remote is at the TV stand—meaning the TV setup is the same as weekdays.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the coffee table during weekend evening TV (pulled out for the social evening)",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "The remote is on the coffee table during weekend evening TV (migrated from the TV stand)",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "Omar's controller is on the couch during weekend evening gaming",
   "target": "controller_omar",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 20,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 20,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "controller_omar": [
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
