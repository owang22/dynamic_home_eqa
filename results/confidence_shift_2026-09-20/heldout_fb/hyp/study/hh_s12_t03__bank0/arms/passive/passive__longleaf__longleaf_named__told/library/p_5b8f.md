# p_5b8f — Weekday morning: both residents in the bathroom 6:30–8

On weekdays, Elena and Priya both use the bathroom in the early morning window (roughly 6:30–8:00). Elena's toiletry bag moves from the dresser to the bathroom shelf, her skincare bottles go from the nightstand to the shelf, and her towel is draped at the shelf for her shower. Priya's razor is at the bathroom shelf and her reading glasses are there while she grooms. The hair dryer is a permanent fixture on the bathroom shelf. By 8:00 Elena has left for work and all her items are back at their resting places (dresser, nightstand, towel rack). On weekends Elena sleeps in; her toiletry bag stays at the dresser and her skincare at the nightstand through the morning.

What sets this apart: it captures the transient morning-bathroom state for BOTH residents' personal items simultaneously, which no single existing document does for the full set. The mixture's worst misses include skincare_elena predicted at nightstand_b1 when actually at bathroom_shelf_ba1 (2×, day 4 08:00) and towel_elena predicted at bathroom_shelf_ba1 when actually at towel_rack_ba1 (2×, day 4 12:00)—the latter showing the towel is back at the rack by midday, consistent with this document's 8:00 cutoff.

Refutation: if Elena's toiletry bag or skincare is sighted at the bathroom shelf after 8:30 on a weekday, or if Priya's razor is at the bathroom shelf on a weekend morning, the window is wrong.

```json
{
 "claims": [
  {
   "claim": "Elena's toiletry bag is on the bathroom shelf at 7:00 on a weekday",
   "target": "toiletry_bag_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 7.5
  },
  {
   "claim": "Elena's skincare is on the bathroom shelf at 7:30 on a weekday",
   "target": "skincare_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Elena's towel is on the bathroom shelf at 7:30 on a weekday",
   "target": "towel_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Priya's razor is on the bathroom shelf at 7:00 on a weekday",
   "target": "razor_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 7.5
  }
 ],
 "targets": {
  "toiletry_bag_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dresser_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "skincare_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "towel_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "razor_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
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
    "from": 6.5,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ]
 }
}
```
