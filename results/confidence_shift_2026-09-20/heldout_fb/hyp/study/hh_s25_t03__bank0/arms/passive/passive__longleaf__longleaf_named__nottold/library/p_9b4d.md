# p_9b4d — Marco's water bottle traces a daily path through kitchen and dining

The water bottle's sightings reveal a clear daily circuit: dish_rack_k1 at 03:00 (washed overnight), desk_b1 at 09:00 (twice, at Marco's workstation), dish_rack_k1 at 18:00 (back in the kitchen after work), sink_k1 at 19:00 (rinsing), and dining_table_d1 at 20:00 (drinking at dinner). This refutes p_e1a5's claim that the bottle is OUT_OF_HOUSE during an evening run (2 "against" since the last call: the bottle was at the sink and dining table, both in the house). It also corrects the mixture's default prediction of dish_rack_k1 during work hours, when the bottle is actually at the desk. Nothing travels with Marco in the evening; the bottle stays in the house.

What would refute this: the bottle sighted OUT_OF_HOUSE at any hour; or the bottle at the desk after 17:00 (it should be back in the kitchen by then).

```json
{
 "claims": [
  {
   "claim": "Marco's water bottle is at his desk during weekday work hours",
   "target": "water_bottle_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's water bottle is at the dining table during dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Marco's water bottle is at the dish rack overnight",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Marco's water bottle is NOT out of the house in the evening",
   "target": "water_bottle_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  }
 ],
 "targets": {
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 19.5,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ]
 }
}
```
