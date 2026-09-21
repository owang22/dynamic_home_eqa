# p_9f4a — Weekend evening: Omar games on the couch, 21:00–23:00

On weekend evenings the living room takes on a different configuration than on weekdays. The controller_omar is sighted at couch_l1 at 22:00 on the weekend (it is at tv_stand_l1 at 03:00). The snack_bowl_shared is at coffee_table_l1 at 21:00 (×2) and at couch_l1 at 22:00 (×2) on the weekend, whereas on weekdays it is at the cupboard during the 21:00–22:00 TV window. The remote_shared is at coffee_table_l1 at 21:00 on the weekend (vs. tv_stand_l1 until 23:00 on weekdays). The blanket is at the coffee table at 22:00 on the weekend.

This document predicts that on weekend evenings Omar sits on the couch with his controller, the snack bowl is out on the coffee table (not stored in the cupboard as on weekdays), and the remote has already migrated to the coffee table by 21:00. The friends-coming-over message on Sunday suggests the living room is more active and cluttered on weekend evenings.

What sets this apart: the snack bowl is ON the coffee table or couch during weekend TV (not in the cupboard), the controller is on the couch (not the TV stand), and the remote is at the coffee table by 21:00 (not the TV stand). What would refute it: the controller at the TV stand at 22:00 on a weekend; the snack bowl in the cupboard at 21:00 on a weekend; the remote at the TV stand at 21:00 on a weekend.

```json
{
 "claims": [
  {
   "claim": "Omar's controller is on the couch during weekend evening gaming",
   "target": "controller_omar",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the coffee table during weekend evening TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "The remote is at the coffee table during weekend evening TV",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20.5,
   "to": 22.5
  }
 ],
 "targets": {
  "controller_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23.5,
    "at": "couch_l1",
    "chance": "usually"
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
    "days": "weekend",
    "from": 20.5,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22.5,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
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
    "days": "weekend",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "days": "weekend",
    "from": 21.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
