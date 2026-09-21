# p_d1c3 — Marco's water bottle: desk in the morning, in his hand through the afternoon, kitchen in the evening

Marco's water bottle follows a clear daily arc. It is at desk_b1 from 08:00 through 11:00 (confirmed by sightings at 08:00, 09:00, 10:00, 11:00). During the core afternoon work block (12:00–17:00) it is absent from the desk 32 of 38 times; the most likely explanation is that it is in his hand (ON_PERSON) as he drinks while working. After work it goes to the dish rack (18:00 sighting), briefly to the sink (19:00, for a rinse), then to the dining table for dinner (20:00). Overnight it rests in the dish rack. This is distinct from p_f5b2 which claims the bottle is OUT_OF_HOUSE during the afternoon (no evidence for that) and from p_9b4d which places it at the desk all day (contradicted by the 32 empty looks). What would refute it: the water bottle sighted at a third receptacle (not desk_b1, not ON_PERSON, not dish_rack, not dining_table) during 12–17 h, or at the desk at 14:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Marco's water bottle is at his desk in the early morning before core work",
   "target": "water_bottle_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 11
  },
  {
   "claim": "Marco's water bottle is in his hand during the afternoon work block",
   "target": "water_bottle_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "Marco's water bottle is at the dish rack in the early evening after work",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Marco's water bottle is at the dining table during dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19.5,
   "to": 21
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
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "usually"
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
