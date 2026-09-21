# p_7b3e — Meal-Time Table: Dishes Come Out, Go Back

Marco and Yuki share the kitchen table for all three meals. Marco is home for breakfast (7:30–9:00) and lunch (12:00–13:30, just before his 13:40 departure); Yuki is home for all three. Dinner (18:00–19:30) is Yuki alone on weekdays since Marco is at his afternoon-to-night shift, but both sit down together on weekends. During each meal window the plates, bowls, glasses, mugs, and water bottles that rest in the cupboard or dish rack are pulled out and set on the kitchen table. Between meals they return: washed dishes go to the sink or dish rack, dry dishes go back to the cupboard.

This hypothesis sets itself apart by placing the full set of tableware at the kitchen table during the three meal windows rather than leaving it in the cupboard all day. The per-object evidence confirms this: glass_marco was sighted at kitchen_table_k1 at 13:00 (twice), bowl_marco at kitchen_table_k1 at 09:00, plate_marco at kitchen_table_k1 at 13:00, plate_yuki at kitchen_table_k1 at 13:00, and glass_yuki at kitchen_table_k1 at 18:00. A document that keeps these objects in the cupboard through the meal hours will be wrong at every meal.

Refutation: if the robot repeatedly finds plates, glasses, or bowls still in the cupboard at 12:30 or 18:30 on a weekday, or finds them on the table at 10:00 (outside any meal window), this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Marco's glass is at the kitchen table during his pre-work lunch",
   "target": "glass_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12.5,
   "to": 13.5
  },
  {
   "claim": "Marco's bowl is at the kitchen table during breakfast",
   "target": "bowl_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9
  },
  {
   "claim": "Yuki's plate is at the kitchen table during lunch",
   "target": "plate_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12.5,
   "to": 13.5
  },
  {
   "claim": "Yuki's glass is at the kitchen table during dinner",
   "target": "glass_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  }
 ],
 "targets": {
  "class:plate": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:water_bottle": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
