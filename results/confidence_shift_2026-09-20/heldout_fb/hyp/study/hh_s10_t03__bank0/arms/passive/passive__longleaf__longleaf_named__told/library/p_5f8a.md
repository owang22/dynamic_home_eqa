# p_5f8a — Weekend evening: full cooking at 19, dinner at the dining table, TV and gaming from 21

On weekends both residents are home. Dinner cooking is a real, multi-item affair: the pan goes on the counter at 18:30, the kitchen knife comes out of the drawer, the spatula is used for flipping, and the pot simmers alongside. This is richer than the weekday solo meal. Both eat at the dining table from roughly 19:00 to 20:15. After dinner, the evening settles into the living room: the blanket migrates from the couch to the coffee table, the remote joins it, the snack bowl is pulled out, and Omar's controller goes to the couch for gaming. On Sunday, friends arrive around 20:00, making the evening more social.

What sets this apart: p_8a4b covers only the cooking items; p_9f4a and p_6e7d cover only the TV/gaming subset. This document unifies the full weekend evening arc from cooking through dinner through the living-room setup. The weekend sightings (knife at counter 19:00 ×3, spatula at counter 19:00, pot at counter 19:00–20:00, controller at couch 22:00, blanket at coffee_table 22:00) are the core support.

What would refute it: if the cooking items are not on the counter at 19:00 on weekends (i.e., no real cooking), or if Omar's controller stays at the TV stand rather than migrating to the couch, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The kitchen knife is on the counter at 19:30 on a weekend (active cooking)",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "The pan is on the counter at 19:30 on a weekend (dinner cooking in progress)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 18.5,
   "to": 20.5
  },
  {
   "claim": "Omar's controller is on the couch at 22:00 on a weekend (gaming after dinner)",
   "target": "controller_omar",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 21,
   "to": 23.5
  },
  {
   "claim": "The blanket is on the coffee table at 22:00 on a weekend (TV time)",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 23.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "controller_omar": [
   {
    "days": "weekend",
    "from": 21,
    "to": 23.5,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 21,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
