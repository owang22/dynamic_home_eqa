# p_9b2d — Glasses roam the house; charger on person; remote at coffee table; water bottle cycles

This is a fresh document built around the small-object patterns that no single existing document captures well. The two residents' glasses are the most mobile personal items in the house, and their paths differ sharply.

Omar's glasses (glasses_omar) follow a clear daily arc: they start on the nightstand overnight, move to the bathroom shelf at 7:00 (shaving / morning routine, 5 sightings at bathroom_shelf at 07:00), go to his desk at 9:00 for work, stay at the desk through the afternoon (sighted at 09, 11, 13, 18), return to the nightstand at 16:00 (a break), go back to the desk at 18:00, then move to the armchair at 21:00 and the TV stand / coffee table at 22:00 for evening TV. Six distinct receptacles over the day.

Marco's glasses (glasses_marco) are simpler: nightstand overnight, desk during work (sighted at 09, 11), nightstand at 18:00 and 21:00, then coffee_table at 22:00 and 23:00 (he drifts to the living room for TV).

The charger pattern is the same as in the fork documents: Marco's phone charger is ON_PERSON during 9–17 h (37 empty looks at desk_b1 vs 1 found). Omar's charger follows his laptop to the coffee table mid-day.

The remote is at the coffee table during the evening TV window (21:00 sighting), not the TV stand. The blanket is on the couch until about 21:30, then on the coffee table.

Marco's water bottle cycles: dish_rack overnight, desk 8–11, kitchen sink area 11–18 (refills), dish_rack 18–19, dining table 19–21, dish_rack after 21.

What would refute this document: Omar's glasses at the nightstand during 9–16 h on a weekday, Marco's charger at desk_b1 during 10–16 h, or the remote at tv_stand_l1 during 20–22 h.

```json
{
 "claims": [
  {
   "claim": "Omar's glasses are on the bathroom shelf in the morning on weekdays",
   "target": "glasses_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Omar's glasses are at his desk during mid-day work on weekdays",
   "target": "glasses_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's charger is on his person during weekday work hours",
   "target": "charger_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The remote is on the coffee table during evening TV",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 16,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 16,
    "to": 18,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "charger_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
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
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 11,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ]
 }
}
```
