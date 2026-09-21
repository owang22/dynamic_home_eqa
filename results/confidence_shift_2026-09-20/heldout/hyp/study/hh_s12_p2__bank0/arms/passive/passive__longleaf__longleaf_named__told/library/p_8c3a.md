# p_8c3a — Priya's midday rest: headphones at the bed, glasses at the nightstand, guitar to the couch

Priya's weekday midday (roughly 11:00–16:00) is a rest-and-reset period. After her morning walk and a light lunch, she settles in the bedroom for a short nap or quiet time: her headphones move from the desk to the bed, her glasses stay on the nightstand (she removes them for the rest), and her water bottle is at the kitchen sink (she filled it before sitting down and it's within reach of the kitchen where she had lunch). Around 14:00–15:00 she gets up, moves to the living room, and takes the guitar from the bedroom floor to the couch for her afternoon practice. By 17:00 the guitar is back in the bedroom.

This differs from p_d6a1 (which puts her glasses at desk_b1 midday and water bottle at the sink) and p_9c1d (which puts headphones at desk_b1 midday). The evidence shows headphones at bed_b1 and glasses at nightstand_b1 during the 12–16 h window, not at the desk. The "MIXTURE'S WORST OBJECTS" report confirms headphones_priya was found at bed_b1 three times on day 6 when the mixture predicted desk_b1.

What would refute this: if the headphones are consistently at desk_b1 during 12–15 h on multiple weekday afternoons, if the glasses are found at desk_b1 or on the bedroom floor during the midday window, or if the guitar never appears at the couch on a weekday afternoon.

```json
{
 "claims": [
  {
   "claim": "Priya's headphones are at the bed during her weekday midday rest",
   "target": "headphones_priya",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Priya's glasses are at the nightstand during the weekday midday",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Priya's guitar is on the couch during her weekday afternoon practice",
   "target": "guitar_priya",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Priya's water bottle is at the kitchen sink during weekday midday",
   "target": "water_bottle_priya",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 12,
   "to": 15
  }
 ],
 "targets": {
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 16,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
