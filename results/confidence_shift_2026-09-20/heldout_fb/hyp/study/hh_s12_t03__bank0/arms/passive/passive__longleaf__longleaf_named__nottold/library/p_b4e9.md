# p_b4e9 — Priya's glasses: set on the coffee table from mid-afternoon, not worn

Priya puts on her glasses in the morning bathroom (sighted at bathroom_shelf_ba1 at 07:00) and wears them for her morning walk and early tasks. By the time she settles into the living room for her mid-afternoon reading or music (around 14:00–15:00), she takes them off and sets them on the coffee table. They stay there through the evening TV window and are only picked up again when she goes to bed, returning to the nightstand around 23:00. The ON_PERSON block in p_a1b2 and p_4c7d (7–22 h) failed at 0.14 on 3 sightings; the actual pattern is a long stretch on the coffee table, not on her face.

What sets this apart: p_a1b2, p_4c7d, and p_1e82 all place the glasses ON_PERSON or at the nightstand for most of the waking day. This document replaces that with a coffee-table residency from 14:00 to 23:00, matching the sightings at 15:00, 16:00, 20:00, 21:00, and 22:00.

Refutation: if the glasses are sighted ON_PERSON (on Priya) at the coffee table or living room during 15:00–22:00 on two or more days, or if they are found on the nightstand during that window, the coffee-table claim is wrong.

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are on the coffee table at 15:30 on a weekday afternoon",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 15,
   "to": 16
  },
  {
   "claim": "Priya's glasses are on the coffee table at 21:00 during evening TV",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 20.5,
   "to": 21.5
  },
  {
   "claim": "Priya's glasses are back on the nightstand at 23:30 after she goes to bed",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 23,
   "to": 24
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
    "days": "weekday",
    "from": 6,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
