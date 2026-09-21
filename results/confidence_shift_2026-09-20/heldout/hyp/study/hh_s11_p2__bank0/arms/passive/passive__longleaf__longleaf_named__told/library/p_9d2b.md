# p_9d2b — Hana's Phone Travels; the Entry Table Holds the Rest

The mixture's worst-object list and the per-object evidence both point to a consistent pattern for Hana's mobile items that several existing documents get wrong. phone_hana is predicted at nightstand_b1 but the robot found it there **zero** times in twelve weekday 9–17h looks. The phone is with Hana: ON_PERSON while she is home in the morning, OUT_OF_HOUSE while she is at work (13:40–23:00), and back on the nightstand only after she settles in for the night. The fifteen total sightings are all at the nightstand, clustered in the overnight hours.

handbag_hana is predicted at entry_floor_e1 by p_f3a1 but the per-object evidence shows it "mostly entry_table_e1" with the weekday 9–17h looks finding it there 4 of 12 times (the other 8 being empty because the bag is out with Hana after 13:40). The handbag rests on the entry *table*, not the entry *floor*. Similarly, keys_hana is "mostly entry_table_e1" (found 8/12 in the 9–17h window), and the jacket, hat, and scarf all sit on entry_hook_e1 (found 6/12 each, the rest being the out-of-house window).

water_bottle_hana follows a small journey: entry_floor_e1 in the early morning (found 2/12 in the 9–17h window, the rest being the out-of-house window), coffee_table_l1 around midday (sightings at 12:00–16:00), and dish_rack_k1 in the evening (sightings at 18:00–22:00) after Hana rinses it. On a sick day like Friday, the bottle stays in the house and the midday/evening locations still apply.

This document covers the full weekday and weekend entry-set pattern. What would refute it: phone_hana found at the nightstand during 9:00–17:00; handbag_hana on the entry floor rather than the entry table; the water bottle at the entry floor in the evening instead of the dish rack.

```json
{
 "claims": [
  {
   "claim": "Hana's phone is not at her nightstand during her weekday morning; she carries it with her",
   "target": "phone_hana",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 8,
   "to": 12
  },
  {
   "claim": "Hana's handbag is at the entry table in the weekday morning, not on the entry floor",
   "target": "handbag_hana",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 8,
   "to": 13
  },
  {
   "claim": "Hana's water bottle is at the entry floor in the weekday early morning",
   "target": "water_bottle_hana",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 6,
   "to": 10
  },
  {
   "claim": "Hana's keys are at the entry table in the weekday morning",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 8,
   "to": 13
  },
  {
   "claim": "Hana's phone is back on her nightstand late at night",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 23,
   "to": 24
  }
 ],
 "targets": {
  "phone_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13.67,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.67,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "hat_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "scarf_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
