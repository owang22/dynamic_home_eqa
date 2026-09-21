# p_4e7a — The Tablet Migration; Nightstand, Kitchen Table, Coffee Table, Nightstand

Hana's tablet follows a tight weekday arc that the 09:00, 10:00, and 12:00 patrol passes confirm repeatedly. Overnight it sleeps on her nightstand (six weekday 03:00 sightings at nightstand_b1 or bed_b1). Around 08:30–09:00 she picks it up and carries it to the kitchen table, where she does a short work or reading session while the house is still quiet. By 10:00 the tablet has migrated again, this time to the coffee table in the living room, where it sits while she lingers over a second cup of coffee or scrolls through music. By 12:00 it is back on the nightstand, where it stays for the rest of the day because Hana leaves for her afternoon shift at 13:40 and does not need it. On weekends the pattern collapses: the tablet stays on the nightstand almost all day, with only a brief appearance at the kitchen table around 10:00 (two weekend sightings) before returning.

This document differs from p_7e2a, which places the tablet at the kitchen table from 08:00 to 10:00 and accumulates "against" votes because the tablet is still on the nightstand at the 08:00 pass. Here the kitchen-table window starts at 08:50, after the 08:00 pass, and the coffee-table window is 10:00–12:00. It also differs from p_2f7c, which predicts a 09:00 kitchen-table sighting that the 08:50 start makes less vulnerable to an 08:00 empty look. On weekends, p_5b9c predicts the tablet at the nightstand all weekend; this document agrees but adds the brief 10:00 kitchen-table interlude that two sightings support.

The document would be refuted if the tablet is consistently seen at the desk (desk_b1) during the 09:00–12:00 window, or if it is found at the kitchen table at the 08:00 pass on multiple weekday mornings (which would push the migration earlier than 08:50).

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is on the kitchen table at the 09:00 weekday pass",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8.83,
   "to": 9.5
  },
  {
   "claim": "Hana's tablet is on the coffee table at the 10:00 weekday pass",
   "target": "tablet_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 10.5
  },
  {
   "claim": "Hana's tablet is back on the nightstand by the 12:00 weekday pass",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 12,
   "to": 12.5
  },
  {
   "claim": "Hana's tablet stays on the nightstand through the weekend 03:00 pass",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 0,
   "to": 3
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8.83,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.83,
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
    "days": "weekday",
    "from": 12,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
