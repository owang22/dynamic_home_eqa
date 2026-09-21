# p_f5b2 — Marco's water bottle traces a five-stop daily path

Marco's water bottle is the most frequently sighted object in the house (11 sightings across 4 receptacles) and follows a clear daily arc. Overnight it rests at the dish rack (03:00) or the kitchen sink. In the early morning (08:00–10:00) it is at his desk, where he fills it and drinks while settling into work. During the core work block (10:00–17:00) it is not at the desk — 19 empty looks confirm this — so it is either in his hand (ON_PERSON) or beside him off-camera. At 18:00 it returns to the dish rack, at 19:00 it is at the sink (being refilled before dinner), and at 20:00 it is at the dining table for the meal. This five-stop path (dish_rack → desk → ON_PERSON → dish_rack/sink → dining_table) is the core prediction.

What sets this apart from p_9b4d (which puts the bottle at the desk all day and got 19 against-hits) and from p_3e9a (which covers the same path but as part of a larger document): this document isolates the water bottle and makes its migration the central, testable claim. What would refute it: the bottle at desk_b1 during 12:00–16:00, or at the dining table at 14:00.

```json
{
 "claims": [
  {
   "claim": "Marco's water bottle is at his desk in the early morning before core work",
   "target": "water_bottle_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Marco's water bottle is NOT at his desk during the core afternoon work block",
   "target": "water_bottle_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 12,
   "to": 16
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
   "claim": "Marco's water bottle is at the dish rack in the early evening after work",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
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
    "from": 8,
    "to": 10,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "ON_PERSON",
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
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
