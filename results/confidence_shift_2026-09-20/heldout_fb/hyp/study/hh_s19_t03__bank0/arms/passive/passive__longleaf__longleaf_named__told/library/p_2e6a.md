# p_2e6a — Marco's evening sketch: desk items migrate to the coffee table

Marco's sketching is an evening hobby that happens at the coffee table, not his desk. Around 20:30–21:00, his sketchbook moves from desk_b1 to coffee_table_l1 (confirmed at 21:00 and 22:00). His pencil case follows a similar migration, arriving at the coffee table by 22:00. He sketches for about 1–2 hours, then puts them back at the desk before bed. His guitar stays on the bedroom floor — the 18:00 sighting confirms it there, and the 03:00 split (floor vs. wardrobe) suggests the floor is the default resting spot. His charger is at the desk during the day but sometimes on the bedroom floor overnight (charging the phone beside the bed).

This document sets itself apart by placing sketchbook_marco and pencil_case_marco at coffee_table_l1 during 21:00–23:00, and guitar_marco at bedroom_floor_b1 (not wardrobe_b1) as the default. The "worst objects" section confirms the library is currently predicting the sketchbook at desk_b1 when it is actually at the coffee table at 21:00.

What would refute this: finding the sketchbook at desk_b1 at 21:00 or 22:00 on multiple evenings, or the guitar in the wardrobe at 18:00.

```json
{
 "claims": [
  {
   "claim": "Marco's sketchbook is at the coffee table during his evening sketching",
   "target": "sketchbook_marco",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "Marco's pencil case is at the coffee table late evening",
   "target": "pencil_case_marco",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "Marco's guitar is on the bedroom floor in the evening",
   "target": "guitar_marco",
   "expect": "bedroom_floor_b1",
   "days": "both",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Marco's charger is at his desk in the late evening",
   "target": "charger_marco",
   "expect": "desk_b1",
   "days": "both",
   "from": 22,
   "to": 23
  }
 ],
 "targets": {
  "sketchbook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 20.5,
    "at": "desk_b1",
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
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "pencil_case_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 21.5,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "charger_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 2,
    "to": 6,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
