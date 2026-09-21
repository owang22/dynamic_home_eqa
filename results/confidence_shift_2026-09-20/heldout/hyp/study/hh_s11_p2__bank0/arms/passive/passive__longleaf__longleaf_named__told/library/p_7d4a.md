# p_7d4a — Hana's Tablet Wanders the Bedroom; Dresser and Bed, Not Just the Nightstand

The mixture's worst-object list shows tablet_hana predicted at nightstand_b1 but actually at dresser_b1 four times (e.g., day 6 12:00). The clock-hour data reveals the tablet is not a single-spot object: on weekdays 00:00–08:00 it is nightstand_b1 ×3, bed_b1 ×1. At 10:00 it jumps to kitchen_table_k1 ×3, nightstand_b1 ×1 (Hana is at the kitchen table, maybe having breakfast or working). From 12:00–16:00 it splits across nightstand_b1, bed_b1, coffee_table_l1, and dresser_b1 (one each per hour). By 18:00 it is back to nightstand_b1 ×3, bed_b1 ×1, dresser_b1 ×1. On weekends it is nightstand_b1 ×2 for nearly all hours, with a brief kitchen_table_k1 appearance at 12:00.

The tablet follows Hana's movement through the house: nightstand at rest, kitchen table during a morning break, coffee table or dresser during an afternoon activity (maybe she is on the couch or at the dresser doing something), then back to the nightstand. The dresser_b1 sightings (4× in the worst list) are the afternoon "at the dresser" window.

This document gives the tablet a multi-block pattern that tracks Hana's rooms rather than pinning it to the nightstand.

What would refute this: the tablet found at the nightstand 100% of the time during 12:00–16:00 on weekdays (the wandering would be noise); the tablet found at the kitchen table during 20:00–24:00 (outside any activity window).

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table during the weekday mid-morning, not on the nightstand",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Hana's tablet is at the dresser during the weekday early afternoon, not on the nightstand",
   "target": "tablet_hana",
   "expect": "dresser_b1",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Hana's tablet is on the nightstand during the weekday evening, not at the dresser or bed",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 20,
   "to": 24
  },
  {
   "claim": "Hana's tablet is on the nightstand all day on the weekend, not at the kitchen table",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
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
