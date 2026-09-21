# p_d5a8 — Priya's glasses: the full daily cycle through nightstand, bathroom, and coffee table

Priya's reading glasses follow a clear daily arc. They sleep on the nightstand (sighted at nightstand_b1 at 03:00 on five of seven days). In the morning routine (07:00–08:00) they move to the bathroom shelf, where she uses them for her skincare and shaving. By mid-afternoon (15:00–17:00) they are on the coffee table for reading or watching TV. There is a brief return to the nightstand around 18:00–20:00 (one weekday sighting at 18:00, one at 20:00 alongside a coffee-table sighting). For evening TV (21:00–23:00) they are back on the coffee table (five weekday sightings at 21:00–22:00). They return to the nightstand by 23:00 for the night.

This document differs from p_c4d9 (weight 0.005, "two coffee-table windows with a nightstand gap") by adding the morning bathroom window and the 23:00 nightstand return, and by placing the first coffee-table window at 15:00–17:00 rather than 15:00–17:00 (same, but with explicit morning block). It differs from p_2d9f (glasses at coffee table 15–22) by splitting the afternoon and evening into two separate windows with a nightstand gap at 18–20. It differs from p_a1b2 (glasses ON_PERSON 7–22, which failed with 0.11) by placing them at specific receptacles rather than on her person.

What would refute this document: glasses at the nightstand during 15:00–17:00 on a weekday; glasses at the coffee table during 07:00–08:00; glasses at the bathroom shelf during 15:00–17:00.

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are on the bathroom shelf during her morning routine at 7:00 on a weekday",
   "target": "glasses_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Priya's glasses are on the coffee table at 15:30 on a weekday",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 15,
   "to": 16.5
  },
  {
   "claim": "Priya's glasses are on the coffee table during evening TV at 21:30 on a weekday",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "Priya's glasses are on the nightstand at 23:00 on a weekday",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22.5,
   "to": 23.5
  }
 ],
 "targets": {
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 20.5,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
