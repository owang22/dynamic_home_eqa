# p_4b7e — Yuki's 21:00 bedroom-desk session: journal, mug, and pen together

Yuki is in her early fifties, an office worker who cycles or drives to town. Omar, in his late twenties, works afternoon-to-night shifts. On weekday evenings after dinner (which ends around 20:00), Yuki does not go straight to the couch for TV. Instead she retreats to the bedroom desk for a quiet solo session — journaling, reading, or simply drinking tea and thinking. The 21:00 patrol passes show her journal at the bedroom desk (2 sightings) alongside her mug (3 sightings) and her pen (her pen lives at desk_b1 on all four sighted days). This is distinct from the coffee-table TV phase that other documents predict for the same hour; here the mug has not yet migrated to the living room, and the blanket is still on the couch (confirmed at 18:00 and 19:00). By 22:00 the mug has moved to the coffee table (2 sightings) and the journal is back at the nightstand (2 sightings), so the desk session is brief — roughly 21:00 to 22:00.

What sets this apart: p_9c82, p_a3f7, and p_8f2a all place mug_yuki at coffee_table_l1 during the 21:00–22:30 window. This document says the mug is at desk_b1 at 21:00 (3 of 6 sightings) and only reaches the coffee table by 22:00. The journal is at the desk, not the nightstand, during that hour. The pen is at the desk, not the nightstand. If the robot finds the mug at the coffee table at 21:00 on a weekday, or the journal at the nightstand at 21:00, this document is wrong.

What would refute it: three or more weekday 21:00 passes finding mug_yuki at coffee_table_l1 while the desk is empty; or the journal consistently at the nightstand at 21:00 with no desk sightings.

```json
{
 "claims": [
  {
   "claim": "Yuki's mug is at the bedroom desk at 21:00 on a weekday during her evening desk session",
   "target": "mug_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "Yuki's journal is at the bedroom desk at 21:00 on a weekday (she is journaling)",
   "target": "journal_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "Yuki's mug is at the coffee table at 22:30 on a weekday (she has finished the desk session and moved to TV)",
   "target": "mug_yuki",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22,
   "to": 23.5
  },
  {
   "claim": "The shared blanket is still on the couch at 20:00 on a weekday (TV has not started yet)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  }
 ],
 "targets": {
  "journal_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0.5,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "pen_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
