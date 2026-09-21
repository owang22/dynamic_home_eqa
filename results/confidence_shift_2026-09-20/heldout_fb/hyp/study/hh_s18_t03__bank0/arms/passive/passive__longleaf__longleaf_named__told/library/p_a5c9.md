# p_a5c9 — The 22:00 wind-down: charger to shelf, glasses to cupboard, TV still on

On weekdays the 22:00–24:00 window is the final stretch of the evening. The TV is still on: the remote, blanket, and snack bowl sit at the coffee table. Ines's mug is at the coffee table for a late drink. The wind-down begins: Ines's charger is moved from the desk to the office shelf (or the nightstand) for the night. Glasses are put away to the kitchen cupboard. By 23:00 the kitchen is clear and the living room is the centre of activity. Both women are in the bedroom by 23:30, phones and tablets on the nightstand.

What sets this apart: this document focuses on the 22:00–24:00 wind-down, a window not well covered by existing documents. It predicts the charger at the office shelf (22:00–24:00), glasses in the cupboard (22:00–24:00), and the TV objects still at the coffee table. It differs from the 21:00-migration documents by focusing on what happens after the migration—where objects go once the evening is winding down.

What would refute it: if the robot finds the charger still at the desk at 23:00, or the glasses still at the kitchen table at 23:00, or the remote back on the TV stand at 23:00.

```json
{
 "claims": [
  {
   "claim": "On weekdays Ines's charger is on the office shelf at 23:00",
   "target": "charger_ines",
   "expect": "office_shelf_o1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "On weekdays the remote is on the coffee table at 23:00",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "On weekdays the blanket is on the coffee table at 23:00",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "On weekdays Ines's glass is in the kitchen cupboard at 23:00",
   "target": "glass_ines",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "On weekdays Elena's glass is in the kitchen cupboard at 23:00",
   "target": "glass_elena",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 22,
   "to": 24
  }
 ],
 "targets": {
  "charger_ines": [
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_ines": [
   {
    "days": "weekday",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "phone_elena": [
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "phone_ines": [
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "tablet_elena": [
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
