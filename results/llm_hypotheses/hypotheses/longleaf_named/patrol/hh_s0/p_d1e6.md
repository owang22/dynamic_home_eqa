# p_d1e6 — Nora's Hybrid Week: Work-from-home on Mondays and Wednesdays

Nora does not go to the office every weekday. On Mondays and Wednesdays she works from home, so her personal items (book_nora, sketchbook_nora, pencil_case_nora) remain in the house and she is present in the rooms. On Tuesdays, Thursdays, and Fridays she commutes as usual (out 8:00–17:30). Yuki's schedule is unchanged: WFH all weekdays, lunch at home.

What sets this hypothesis apart: on Monday and Wednesday midday, Nora is in the house (visible in a room look) and her desk_b2 items are present. On Tue/Thu/Fri midday, Nora is absent from all rooms and her items stay put but she is not listed in any room.

What would refute it: Nora sighted in any room on a Tuesday between 10:00 and 16:00.

```json
{
 "claims": [
  {
   "claim": "Nora's sketchbook is at desk_b2 on Monday midday",
   "target": "sketchbook_nora",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Nora's pencil case is at desk_b2 on Wednesday midday",
   "target": "pencil_case_nora",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Nora's book is at the nightstand on Tuesday midday (she is out but items stay)",
   "target": "book_nora",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Nora's toiletry bag is at the bathroom shelf on Friday midday",
   "target": "toiletry_bag_nora",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "sketchbook_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   }
  ],
  "pencil_case_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   }
  ],
  "book_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "toiletry_bag_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "laptop_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
