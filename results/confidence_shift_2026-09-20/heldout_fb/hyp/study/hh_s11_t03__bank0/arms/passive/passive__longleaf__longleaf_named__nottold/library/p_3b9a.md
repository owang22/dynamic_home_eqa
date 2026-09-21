# p_3b9a — Hana's Tablet Walks the Kitchen; Table at Nine, Coffee Table at Ten, Nightstand by Twelve

Hana's weekday morning work session begins at the kitchen table, not at her desk. The tablet is at kitchen_table_k1 at 09:00 (four sightings across multiple weekday mornings), then moves to coffee_table_l1 by 10:00 (two sightings), and is back at nightstand_b1 by 12:00 (one sighting, confirmed at 18:00). The notebook, by contrast, stays at desk_b1 all day (six sightings, one receptacle, zero distinct alternatives). The mug follows the tablet to the coffee table: seen at coffee_table_l1 at 10:00, 13:00, and 17:00 on weekdays. The bowl is at the kitchen table during the 09:00 meal (three sightings at 09:00, one at 10:00).

This document differs from p_b8c2 and p_a1b2, which place the tablet at desk_b1 in the morning (contradicted 7–8 times), and from p_7e2a and p_4f8c, which use an 8–10 h window that catches the tablet before it has arrived at the table (13 "against" sightings). The tighter 9–10 h window matches the evidence: the tablet is reliably at the kitchen table at 09:00 but not at 08:00. The 10–12 h coffee-table window captures the mid-morning break where the tablet is set down while Hana moves around the kitchen.

On weekends the tablet is at the kitchen table around 10:00 (two sightings) before returning to the nightstand.

What would refute this document: if the tablet is found at desk_b1 during the 9–10 h weekday window, or if it never appears at coffee_table_l1 between 10 and 12 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table during her weekday morning work",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 10
  },
  {
   "claim": "Hana's tablet is at the coffee table during her weekday mid-morning break",
   "target": "tablet_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Hana's notebook stays at her desk all day",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Hana's mug is at the coffee table during the weekday afternoon",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 17
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
    "from": 9,
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
    "from": 9,
    "to": 11,
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
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "bowl_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
