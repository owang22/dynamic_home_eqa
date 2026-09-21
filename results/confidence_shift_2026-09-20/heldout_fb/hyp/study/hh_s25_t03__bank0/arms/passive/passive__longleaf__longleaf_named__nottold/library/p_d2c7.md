# p_d2c7 — Omar's glasses trace a full-day path through five rooms

Omar's glasses are the most mobile object in the household, sighted at five different receptacles in a single weekday. The path is: nightstand_b1 overnight (03:00), bathroom_shelf_ba1 during his morning routine (07:00), desk_o1 when he starts work (11:00), back to nightstand_b1 during a mid-afternoon break (16:00), desk_o1 again when he resumes (18:00), armchair_l1 during evening relaxation (21:00), and tv_stand_l1 during late TV (22:00). This is not a simple "on the desk all day" object; it follows Omar's body through the house. The 16:00 nightstand sighting is the key differentiator: it means Omar leaves the office, goes to the bedroom (perhaps a nap or a stretch), and the glasses go with him.

What sets this apart from p_5e1c (which puts the glasses at desk_o1 9–17 h and got 12 against-hits) and from the generic "nightstand all day" in p_a1b2: the glasses are actively moving through the day, and the 16:00 nightstand stop and the 21:00 armchair stop are the distinctive predictions. What would refute it: a sighting of glasses_omar at a sixth receptacle not in this path, or at the nightstand at 10:00 (before the 16:00 break).

```json
{
 "claims": [
  {
   "claim": "Omar's glasses are on the bathroom shelf during his weekday morning routine",
   "target": "glasses_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8.5
  },
  {
   "claim": "Omar's glasses are at the nightstand during his mid-afternoon break",
   "target": "glasses_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Omar's glasses are on the armchair during evening relaxation",
   "target": "glasses_omar",
   "expect": "armchair_l1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Omar's glasses are at his desk when he resumes work in the late afternoon",
   "target": "glasses_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 11,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
