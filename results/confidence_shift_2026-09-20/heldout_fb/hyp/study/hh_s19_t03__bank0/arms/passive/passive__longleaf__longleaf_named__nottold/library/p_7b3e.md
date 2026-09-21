# p_7b3e — Omar's burst work: two desk blocks with a kitchen-table lunch

Marco commutes to the office 8:00–17:30 on weekdays; his keys, backpack, water bottle, and jacket leave the house in the morning and return in the evening. Omar works from home but not in one continuous block: the sightings put his laptop at desk_o1 at 09:00 and 10:00, then at desk_o1 again at 13:00 and 15:00, with the coffee table as its resting spot at 03:00 and 18:00. The twelve empty looks at desk_o1 during 9–17h (against only four hits) mean the laptop is *not* at the desk for a large fraction of the afternoon. Crucially, Omar's glass and plate are both at the kitchen table at 12:00, and his mug was at the kitchen table at 08:00. He eats lunch at home, at the kitchen table, roughly 11:30–13:00, and his laptop stays on the coffee table (or he is briefly at the kitchen table) during that gap. This sets the document apart from p_c3d4 (laptop out of the house for lunch) and from p_a1b2 / p_3a7f (laptop at the desk the whole 9–17 block).

What would refute this document: a sighting of laptop_omar at OUT_OF_HOUSE during 11–14 on a weekday, or a sighting of glass_omar / plate_omar at the kitchen table outside the 11–14 window on a weekday (suggesting the lunch is at a different hour).

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at his desk during the first work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Omar's glass is at the kitchen table during his lunch",
   "target": "glass_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  },
  {
   "claim": "Omar's laptop is back at his desk during the second work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Omar's plate is at the kitchen table during his lunch",
   "target": "plate_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  },
  {
   "claim": "Marco's keys are out of the house on weekday mornings",
   "target": "keys_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 11,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 16,
    "at": "desk_o1",
    "chance": "almost_always"
   }
  ],
  "glass_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 22,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
