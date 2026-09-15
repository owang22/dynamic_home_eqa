# p_3a7d — Kitchen-shelf appliance in use at the counter during work hours (fork of p_e4b7)

This fork revises the core object_11 prediction of p_e4b7. The parent document placed object_11 at the bedroom shelf (receptacle_13) all day, but two recent looks at receptacle_13 during 08:00–20:00 found nothing (claim: against 2, for 0). Meanwhile, the per-object evidence shows object_11 is "mostly receptacle_18 (2/3 sighted days; 3 receptacles; 8 sightings)" yet weekday 9–17h looks at receptacle_18 found it 0 times and found nothing 3 times. The resolution: object_11 is a small kitchen-adjacent appliance (a compact blender, a coffee grinder, or a small kettle) that lives on the kitchen storage shelf (receptacle_18) when not in use—mornings before 09:00, evenings after 17:00, and all weekend—but is brought to the active counter (receptacle_4) during weekday work hours 09:00–17:00, where a resident uses it for coffee, smoothies, or a quick meal while working from home.

Everything else follows the standard home-based couple routine: object_4 parked on the kitchen shelf all day; object_15 and object_16 on the counter; desk items at receptacle_12 in the morning; object_2 and object_35 always in the house; bathroom items static at receptacle_6.

What changed from p_e4b7: object_11 moves from a fixed receptacle_13 prediction to a two-block model (receptacle_18 off-peak, receptacle_4 during weekday 09:00–17:00). What would refute this fork: object_11 found at receptacle_13 during 08:00–20:00, or object_11 found at receptacle_18 during weekday 09:00–17:00.

```json
{
 "claims": [
  {
   "claim": "object_11 (kitchen appliance) is at the kitchen shelf (receptacle_18) on weekends and weekday mornings before 9 and evenings after 17",
   "target": "object_11",
   "expect": "receptacle_18",
   "days": "weekend",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_11 (kitchen appliance) is at the active counter (receptacle_4) during weekday work hours 9-17",
   "target": "object_11",
   "expect": "receptacle_4",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_4 (kitchen item) is on the kitchen shelf (receptacle_18) all day, not the counter",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_2 (keys) is always in the house because both residents work from home",
   "target": "object_2",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "object_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_35": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_3": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_7",
    "chance": "almost_always"
   }
  ],
  "object_4": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_18",
    "chance": "almost_always"
   }
  ],
  "object_11": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_4",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_18",
    "chance": "usually"
   }
  ],
  "object_15": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_4",
    "chance": "usually"
   }
  ],
  "object_16": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_4",
    "chance": "usually"
   }
  ],
  "object_14": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
    "chance": "almost_always"
   }
  ],
  "object_26": [
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ],
  "object_17": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_8",
    "chance": "almost_always"
   }
  ],
  "object_18": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_13",
    "chance": "almost_always"
   }
  ]
 }
}
```
