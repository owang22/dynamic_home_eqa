# p_3a7f — Evening arc: dining-table dinner at 19, coffee-table TV from 21

Yuki arrives home around 17:30 on weekdays. For the next half-hour she transitions from the entry (jacket on hook, water bottle still in hand, keys on the entry floor) to the dining room. By 19:00 she is eating at the dining table—plate, glass, and water bottle all converge there. Omar is at work until 23:00, so this is a solo dinner, but it is eaten at the proper dining table, not the kitchen table. After dinner (around 20:00–20:30) the plates go to the sink or cupboard, and the living room becomes the focus: the blanket moves from the couch to the coffee table, the remote shifts to the coffee table, and Yuki's mug (pulled from the cupboard) appears beside the TV. This TV block runs from roughly 21:00 to 23:00. The blanket is on the couch for the entire daytime (03:00 through 18:00 sightings confirm this).

What sets this document apart: it pins the dinner at the *dining* table (not the kitchen table, not the counter) and the TV block at the *coffee* table (not the side table, not the TV stand). It also places the blanket on the couch all day and only at the coffee table during the TV window. The mug is in the cupboard between dinner and TV (the 18:00 sighting confirms cupboard), not at the dining table.

Refutation: if the robot finds Yuki's plate at the kitchen table or counter during 19:00–20:00, or the blanket on the couch at 21:30, or the mug at the dining table during dinner, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Yuki's plate is at the dining table during her solo weekday dinner at 19:30",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Yuki's mug is at the coffee table during the TV block at 21:30 on a weekday",
   "target": "mug_yuki",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The shared blanket is on the coffee table at 21:30 on a weekday during TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The shared blanket is on the couch at 14:00 on a weekday (all-day resting spot)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 13,
   "to": 18
  }
 ],
 "targets": {
  "plate_yuki": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "weekday",
    "from": 18,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
