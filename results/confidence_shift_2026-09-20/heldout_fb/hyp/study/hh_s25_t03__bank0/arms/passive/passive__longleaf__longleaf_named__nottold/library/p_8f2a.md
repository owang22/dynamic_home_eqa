# p_8f2a — Marco's core work: laptop and charger ON_PERSON, notebook and mug on desk

Marco works from home at his desk (desk_b1) from 9 to about 5:30. Seven days of sightings make the picture clear: his laptop is found on the desk surface only 8 out of 38 weekday work-hour looks, and his charger only 1 out of 38. Meanwhile his notebook (6/38), pen (8/30), and mug (6/32) are found on the desk regularly. The interpretation is that Marco works with the laptop open on his lap, the charger plugged in and dangling, while his writing materials and drink sit on the desk surface. His glasses are on the desk during work (sighted at 09:00 and 11:00) and move to the nightstand in the evening (18:00, 21:00), then to the coffee table late at night (22:00, 23:00). Nothing leaves the house: his keys, jacket, hat, scarf, sunglasses, and running shoes are all at the entry on every sighted day.

This document is distinguished from p_a1b2 (which places the laptop on the desk surface all day) and from p_3e9a and p_7a3e (which also place the notebook ON_PERSON, but the notebook's ON_PERSON claim failed with 0.14 on 3 sightings — the notebook stays on the desk).

Refutation: if the laptop is found on desk_b1 during 10–16 h on multiple weekday mornings, or if the charger is found on desk_b1 during that window, the ON_PERSON core is wrong.

```json
{
 "claims": [
  {
   "claim": "Marco's laptop is in his hands during weekday core work hours, not on the desk surface",
   "target": "laptop_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's charger is in his hands plugged into the laptop during weekday core work hours",
   "target": "charger_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's notebook is on the desk surface during weekday work hours",
   "target": "notebook_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's glasses are on the desk during weekday work hours",
   "target": "glasses_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's keys are at the entry table at all times",
   "target": "keys_marco",
   "expect": "entry_table_e1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "laptop_marco": [
   {
    "days": "weekday",
    "from": 9.5,
    "to": 16.5,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "charger_marco": [
   {
    "days": "weekday",
    "from": 9.5,
    "to": 16.5,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "mug_marco": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "pen_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "glasses_marco": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21.5,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "running_shoes_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
