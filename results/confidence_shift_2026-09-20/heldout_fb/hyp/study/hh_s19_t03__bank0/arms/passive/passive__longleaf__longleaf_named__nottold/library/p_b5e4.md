# p_b5e4 — Omar's water bottle arc: dish rack, coffee table, desk, kitchen table

Omar's water bottle traces a precise path through each day. Overnight it is in the dish rack (rinsed and set to dry after the previous evening's use). In the early morning around 8–9 it is on the coffee table while he has his first coffee or water before settling at his desk. During his desk work block (roughly 10–17) it sits at his desk. After work (17–18) it goes back to the dish rack briefly. During the cooking window (18) it is on the kitchen counter. At dinner (19–21) it is at the kitchen table. Marco's bottle follows a similar arc but is out of the house with him during his workday (8–17:30), so it is only seen in the house in the early morning, evening, and overnight.

What sets this apart: this is the only document that models the water bottle's multi-receptacle daily arc as a single coherent path. The bottle is NOT at the counter during work hours (contradicting p_a1b2's claim), and it is NOT out of the house during lunch (contradicting p_c3d4's lunch-run claim for the bottle). The 17:00 pass shows it split between dish rack and desk, indicating the work block ends around 16:30–17:00.

Refutation: if Omar's water bottle is seen at the counter during 10–17 on a weekday, or out of the house at 12:00, or if Marco's bottle is seen in the house at 14:00 on a weekday, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Omar's water bottle is at his desk at 14:00 on a weekday",
   "target": "water_bottle_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13.75,
   "to": 14.25
  },
  {
   "claim": "Omar's water bottle is at the kitchen table at 19:00 on a weekday",
   "target": "water_bottle_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18.75,
   "to": 19.25
  },
  {
   "claim": "Omar's water bottle is in the dish rack at 03:00",
   "target": "water_bottle_omar",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 2.75,
   "to": 3.25
  },
  {
   "claim": "Marco's water bottle is out of the house at 14:00 on a weekday",
   "target": "water_bottle_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 13.75,
   "to": 14.25
  },
  {
   "claim": "Marco's water bottle is at the kitchen table at 20:00 on a weekend",
   "target": "water_bottle_marco",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 19.75,
   "to": 20.25
  }
 ],
 "targets": {
  "water_bottle_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 18,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 17,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ]
 }
}
```
