# p_6d1f — Saturday social: friends fill the living room, the kitchen preps early, guitar on the couch

Saturday is the social day: friends arrive in the evening (per the residents' message). The living room becomes the gathering space, so the laptop (which would be at the desk on a weekday) stays at the coffee table all day — Omar does no desk work. The guitar moves to the couch in the evening (21:00 pass confirms couch_l1 on weekdays; on Saturday it is likely there earlier as the social hub). The blanket is on the couch from the afternoon (17:00 and 18:00 passes confirm couch_l1). Marco does not commute, so his keys, backpack, and notebook stay at the entry. The kitchen is prepped for guests: the pan is on the counter at 19:00 (4 weekend passes confirm counter_k1), the snack bowl is on the counter (not the coffee table, which is occupied by the laptop and social items). The vacuum cleaner is pulled out to floor_l_l1 at 12:00 (weekend pass confirms), suggesting a midday clean before guests arrive.

This document is distinct from p_5a1c (which also covers Saturday but is low-weight) by specifying the vacuum cleaner outing and the guitar-on-couch timing. It is refuted if the laptop is found at desk_o1 on Saturday afternoon, or if the guitar is in the bedroom at 21:00 on Saturday.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at the coffee table all day on Saturday (no desk work)",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 10,
   "to": 18
  },
  {
   "claim": "Marco's guitar is on the couch during Saturday evening social time",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Marco's keys stay at the entry table on Saturday (no commute)",
   "target": "keys_marco",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 10,
   "to": 18
  },
  {
   "claim": "The vacuum cleaner is out on the living room floor during Saturday midday cleaning",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 11,
   "to": 13
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "keys_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "backpack_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
