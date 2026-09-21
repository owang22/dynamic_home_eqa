# p_b3d8 — Hana's Evening Tablet; Dresser and Bed, Not Just the Nightstand

The worst-objects list flags tablet_hana (predicted nightstand_b1, actually dresser_b1, 2×, day 6 20:00). The hourly sightings for tablet_hana on weekdays show a clear evening pattern: from 14:00 through 22:00 the tablet is at nightstand_b1 in 1–3 of 4 passes, but also at bed_b1, dresser_b1, and occasionally coffee_table_l1. At 20:00 and 22:00 the split is nightstand x3, bed x1, dresser x1. At 14:00 and 16:00 it is bed x1, nightstand x1, coffee_table x1, dresser x1.

This is not the kitchen-table wandering of p_7d4a (which scored for 3, against 2 on the 10–12h kitchen-table claim). In the evening the tablet stays in the bedroom but bounces between the nightstand, the bed (Hana lying down reading), and the dresser (Hana sitting up, maybe getting ready for bed). The nightstand is still the modal position (3/4 of passes) but the dresser and bed are the secondary spots.

p_7d4a's evening claim (nightstand, 20–24h) scored for 6, against 8 — worse than even. The tablet is NOT reliably on the nightstand in the evening; it is spread across three bedroom surfaces.

What would refute this: tablet_hana found at the kitchen table or coffee table during the 18–24h weekday window; the tablet at the desk in the evening.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is on her bed during the weekday evening, not on the nightstand",
   "target": "tablet_hana",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Hana's tablet is on her dresser during the weekday late afternoon",
   "target": "tablet_hana",
   "expect": "dresser_b1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Hana's tablet is on her nightstand during the weekday overnight hours",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 7
  }
 ],
 "targets": {
  "tablet_hana": [
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
    "to": 10,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "dresser_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
