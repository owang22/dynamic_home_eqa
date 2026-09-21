# p_9f4a — Marco's laptop never leaves: desk_b1 all day, charger at desk or nightstand

This document makes the explicit claim that Marco's laptop and charger do NOT go to the office. The evidence supports this: laptop_marco is at desk_b1 at 03:00 (4× weekday, 2× weekend), at 18:00 (1×), and the only off-desk sighting is one 10:00 coffee_table_l1 pass. The charger is at desk_b1 at 03:00 (3× weekday, 1× weekend), at 18:00 (1×), and at 22:00 splits between desk_b1 (2×) and nightstand_b1 (1×). No OUT_OF_HOUSE sightings for either object in seven days.

This contrasts with p_8c2d (which claims the laptop is out of the house during work) and p_3a7f (which gets one "against" for the 10:00 coffee_table sighting). The 10:00 coffee_table pass is treated here as a brief break — Marco opens his laptop on the coffee table for a quick check while waiting for coffee, then puts it back.

The rest of the household follows the standard pattern: Omar's laptop at desk 10–16, remote on tv_stand, pan on counter 18:25–20, guitar to couch at 21:00, iron to bed at 21:00.

What would refute this: finding laptop_marco out of the house on a weekday morning; finding it at the office or on Marco's person; finding the charger out of the house.

```json
{
 "claims": [
  {
   "claim": "Marco's laptop is at his desk at 03:00 overnight",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "both",
   "from": 2.75,
   "to": 3.25
  },
  {
   "claim": "Marco's laptop is at his desk when he returns home at 18:00",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 17.75,
   "to": 18.25
  },
  {
   "claim": "Marco's charger is at his desk at 03:00 overnight",
   "target": "charger_marco",
   "expect": "desk_b1",
   "days": "both",
   "from": 2.75,
   "to": 3.25
  },
  {
   "claim": "Omar's laptop is at his desk at 14:00 during his work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13.75,
   "to": 14.25
  },
  {
   "claim": "The remote is on the tv stand at 21:00",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20.75,
   "to": 21.25
  }
 ],
 "targets": {
  "laptop_marco": [
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
    "days": "both",
    "from": 0,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 16,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
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
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.25,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.25,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
