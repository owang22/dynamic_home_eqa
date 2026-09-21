# p_c4d9 — Priya's glasses: two coffee-table windows with a nightstand gap

Priya's reading glasses follow a strict two-window pattern. They sit on the nightstand overnight and through the morning. At 07:00 she takes them to the bathroom shelf for her routine. During the working hours (08:00–15:00) they are on her person or at the kitchen table — the robot does not see them at a fixed receptacle. In the mid-afternoon (15:00–17:00) she is in the living room and the glasses are on the coffee table. Then they go BACK to the nightstand for the early evening (17:00–20:30); the 18:00 and 20:00 patrols find them on the nightstand. When TV starts, the glasses move to the coffee table again (20:30–23:00), where they stay through the evening. By 23:00 they are back on the nightstand.

What sets this apart from p_2d9f and p_8c1a (glasses at coffee_table_l1 15–22h): the glasses are NOT at the coffee table at 18:00 or 20:00. The 15–22h window is too broad and has accumulated 7 against since the last call for both documents because the 18:00 and 20:00 patrols find the glasses on the nightstand, not the coffee table. The correct model has a gap: coffee table 15–17, nightstand 17–20:30, coffee table 20:30–23.

This is refuted if the glasses are at the coffee table at 18:00 or 20:00 on multiple days, or if they are on the nightstand at 15:00 or 21:00.

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are on the coffee table during her mid-afternoon at 15:30",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Priya's glasses are on the nightstand at 18:30 between the two coffee-table windows",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 17,
   "to": 20.5
  },
  {
   "claim": "Priya's glasses are on the coffee table during evening TV at 21:30",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 20.5,
   "to": 23
  },
  {
   "claim": "Priya's glasses are on the bathroom shelf during her morning routine at 7:00",
   "target": "glasses_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 7,
   "to": 8
  }
 ],
 "targets": {
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 15,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 15,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 20.5,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 10,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 12,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
