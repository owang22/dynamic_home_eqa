# p_4f8a — Evening Migration: Remote to TV Stand, Blanket to Coffee Table

The living room objects shift position at the start of the evening. During the day the remote sits on the floor (dropped when someone gets up, or set down while stretching), and the blanket is draped over the armchair as a decorative or comfort spot. But once evening TV begins around 17:00–18:00, the remote is picked up and placed on the tv_stand where it stays for the night, and the blanket is pulled onto the coffee table or couch where people actually sit and use it. This is not a weekend-only pattern; it holds on weekdays too. The 18:00 patrol passes confirm the remote at tv_stand_l1 and the blanket at coffee_table_l1, while the 00:00 and 08:00 passes confirm the floor and armchair positions. What sets this document apart is the explicit time-of-day transition: the objects are in two different places depending on whether it is "day mode" or "evening mode." A look at the floor at 20:00 that finds the remote, or a look at the armchair at 22:00 that finds the blanket, would refute this document.

```json
{
 "claims": [
  {
   "claim": "The remote is on the TV stand during the evening TV window",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The blanket is on the coffee table during the evening",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The remote is on the living room floor in the mid-morning",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 8,
   "to": 12
  },
  {
   "claim": "The blanket is on the armchair in the mid-morning",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "both",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 17,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
