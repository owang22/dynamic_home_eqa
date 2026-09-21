# p_f4b2 — Hana's Tablet Belongs at the Kitchen Table; The Desk Is Only for the Notebook

The four 09:00 sightings of tablet_hana at kitchen_table_k1 (and the 4/8 hit rate on 9–17 h looks at that receptacle) settle the matter: Hana does not work at desk_b1 in the morning. Her tablet lives at the kitchen table from roughly 08:00 until she leaves at 13:40, after which it returns to nightstand_b1 for the evening. The notebook_hana, by contrast, is confirmed at desk_b1 on both sighted days and is not displaced by the breakfast routine. This means the "morning work session" that p_b8c2 and p_a1b2 place at desk_b1 is actually a kitchen-table activity—perhaps reading, scrolling, or light study over a cup of coffee.

This document is distinguished by its single strong claim: tablet_hana at kitchen_table_k1 (not desk_b1) during 08:00–13:00 on weekdays. If the robot finds the tablet at desk_b1 during that window, this document is refuted. If it finds the tablet at kitchen_table_k1, this document gains weight. The notebook at desk_b1 is a secondary confirmation.

Hana's water bottle and phone follow her out at 13:40; they are OUT_OF_HOUSE from 13:40 to 23:00 on weekdays.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table during her weekday morning, not at desk_b1",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Hana's notebook remains at her desk all day",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 7,
   "to": 13
  },
  {
   "claim": "Hana's phone is out of the house during her weekday shift",
   "target": "phone_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13,
    "at": "kitchen_table_k1",
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
  ],
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
