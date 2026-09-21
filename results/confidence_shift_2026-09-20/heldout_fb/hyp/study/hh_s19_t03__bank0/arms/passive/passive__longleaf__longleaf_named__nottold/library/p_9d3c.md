# p_9d3c — Omar's laptop arc: coffee table overnight, desk at work, coffee table after

The 03:00 passes show Omar's laptop on the coffee table (×2) or the bookshelf (×1); the 09:00 passes show it in transition (coffee table ×3, desk ×2, bookshelf ×1); the 10:00–16:00 passes show it solidly at the desk (×2, ×1, ×3, ×1); the 17:00 pass shows it splitting between bookshelf and desk; and the 18:00 pass shows it back on the coffee table. The weekday 9–17h looks at desk_o1 found it 9 times and found nothing 17 times — the "nothing" looks cluster in the 9–10h and 17–17.5h gaps, consistent with the laptop being on the coffee table or bookshelf at those edges.

This differs from p_4f8e and p_7e3a (which split the day into two desk blocks with a lunch gap) by treating the work block as one continuous 10–17h stretch at the desk, with the coffee table as the overnight and post-work resting spot. It differs from p_9b4f (home lunch, laptop stays put) by acknowledging the laptop is NOT at the desk at 09:00 or 18:00. The bookshelf is a secondary resting spot, seen at 03:00 and 17:00, perhaps where Omar sets it down when he's sketching at the desk.

Refutation: if the laptop is at the desk at 03:00 or 09:00, if it is out of the house at any point during the day, or if it is on the kitchen table rather than the coffee table in the evening.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is on the coffee table at 03:00 overnight",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 3,
   "to": 3.5
  },
  {
   "claim": "Omar's laptop is at his desk during the core work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Omar's laptop is on the coffee table after work at 18:30",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Omar's laptop is NOT at his desk at 09:00 before the work block starts",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 9,
   "to": 9.5
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 18,
    "at": "bookshelf_l1",
    "chance": "rarely"
   }
  ],
  "mouse_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "sometimes"
   }
  ],
  "notebook_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ]
 }
}
```
