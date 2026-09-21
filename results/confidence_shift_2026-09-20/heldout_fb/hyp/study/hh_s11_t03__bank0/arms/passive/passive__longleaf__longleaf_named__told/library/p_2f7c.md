# p_2f7c — The Tablet Migration; Kitchen Table at 09:00, Coffee Table at 10:00, Nightstand by 12:00

This document captures the full daily migration of Hana's tablet, the most contested object in the library. The sighting log shows a clear three-stage pattern on weekdays: the tablet is at the kitchen table at the 09:00 pass (four sightings), migrates to the coffee table by 10:00 (two sightings, with one still at the kitchen table), and is back at the nightstand by 12:00 (one sighting). Overnight and in the evening it rests at the nightstand or on the bed. On weekends, the tablet skips the coffee-table stage and goes directly from the nightstand to the kitchen table around 10:00 (two sightings), then back to the nightstand.

What sets this apart from p_3e7a (kitchen table only) and p_7e2a (kitchen table 8-10, coffee table 10-12, nightstand 14-22): this document places the kitchen-table window at 8-10 (matching the 09:00 pass) and the coffee-table window at 10-12 (matching the 10:00 pass), with the nightstand as the default for all other hours. It also explicitly handles the weekend pattern where the tablet goes to the kitchen table rather than the coffee table. The 18:00 pass shows the tablet at the nightstand (one sighting) or kitchen table (one sighting), suggesting an occasional evening return to the kitchen table that this document allows via the default nightstand block being overridden only during the morning windows.

A look at the coffee table at 09:00 on a weekday that finds the tablet there (rather than the kitchen table) would refute the morning block. A look at the kitchen table at 11:00 on a weekday that finds the tablet there (rather than the coffee table) would weaken the migration claim. A look at the desk at any hour that finds the tablet there would strongly refute this document, since the tablet has never been seen at desk_b1 in the log.

No objects leave the house in this document. The tablet stays home; Hana takes her phone to work, not the tablet.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table at the 09:00 weekday pass, not at the desk or nightstand",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8.5,
   "to": 9.5
  },
  {
   "claim": "Hana's tablet is at the coffee table at the 10:00 weekday pass, having migrated from the kitchen table",
   "target": "tablet_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 11
  },
  {
   "claim": "Hana's tablet is back at the nightstand by the 12:00 weekday pass",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 12,
   "to": 13
  },
  {
   "claim": "Hana's notebook stays at her desk all day and does not migrate to the kitchen table or coffee table",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "both",
   "from": 0,
   "to": 24
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
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
