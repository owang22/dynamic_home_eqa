# p_2f8a — Sunday evening gathering: friends over, dining and living room in use

The residents' Sunday message says friends are coming over in the evening. This changes the object landscape from roughly 17:00 onward: plates, glasses, and mugs that would stay in the cupboard or sink are brought out to the dining table for a shared meal. The snack bowl moves from its resting spot to the coffee table or dining table for sharing. The blanket is pulled from the couch to the lap or kept ready on the couch for the group. The remote is at the TV stand, ready for group TV or a movie. Omar's controller may be set aside if the group watches something together, or it stays at the TV stand if they play a group game. Yuki's water bottle is at the dining table rather than the dish rack, as she drinks during the meal.

This hypothesis is set apart by its narrow time window (Sunday evening only, 17:00 to 23:00) and its social-dining focus. It does not change weekday patterns or weekend daytime patterns. What would refute it: if Sunday-evening sightings show plates still in the cupboard, the snack bowl still at the sink, or the blanket still folded on the couch with no one in the living room. It is also weakened if the residents are seen in the bedroom at 19:00 on a Sunday (suggesting the gathering did not happen or was much smaller).

```json
{
 "claims": [
  {
   "claim": "Plates are set at the dining table on Sunday evening for the friend gathering",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Glasses are at the dining table on Sunday evening for the shared meal",
   "target": "glass_omar",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table on Sunday evening for the group",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The blanket is on the couch on Sunday evening, ready for the group to use",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The remote is at the TV stand on Sunday evening for group viewing",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "class:plate": [
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "controller_omar": [
   {
    "days": "weekend",
    "from": 17,
    "to": 23,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ]
 }
}
```
