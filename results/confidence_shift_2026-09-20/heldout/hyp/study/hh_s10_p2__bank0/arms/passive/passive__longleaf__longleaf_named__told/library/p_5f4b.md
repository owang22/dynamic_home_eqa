# p_5f4b — Omar's tablet lives at the bedroom nightstand; kitchen table only at 10:00 breakfast

Omar's tablet is a bedside device. It sits on the nightstand from the time he gets up until he goes to bed, with a single exception: around 10:00 on weekdays he takes it to the kitchen table for his morning coffee and a quick scroll before heading out. It is *not* a kitchen-chair device. The kitchen chair (chair_k1) is where it was seen a handful of times in the early data, but the overwhelming pattern (9/12 weekday 9–17 h looks at the nightstand find it; the 10:00 pass shows it at the kitchen table 2×) says nightstand is home.

This directly contradicts p_e5f6 (tablet at kitchen chair 7–13 h), p_7a3f (tablet at kitchen chair 14–22 h), and p_4e91 (tablet at kitchen chair 15–22 h). It also refines p_a3d7, which correctly puts it at the nightstand 12–16 h but then moves it back to the kitchen chair for evening gaming (19–22 h); the 20:00 and 22:00 passes show it at the nightstand 3× and the kitchen chair only 1×, so the nightstand wins.

Refuted if the robot finds the tablet at the kitchen chair at 14:00 or 20:00 on a weekday, or if it is absent from the nightstand at 12:00.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand during his midday window on weekdays (he is home, not at the kitchen chair)",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Omar's tablet is at the bedroom nightstand during his evening gaming on weekdays (not the kitchen chair)",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Omar's tablet is at the kitchen table during his 10:00 morning coffee on weekdays",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9.5,
   "to": 10.5
  },
  {
   "claim": "Omar's tablet is NOT at the kitchen chair during his 14:00 window on weekdays",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 16
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
