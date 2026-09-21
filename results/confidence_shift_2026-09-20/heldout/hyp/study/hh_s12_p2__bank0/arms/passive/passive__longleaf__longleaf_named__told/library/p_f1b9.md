# p_f1b9 — Weekend domestic shift: Elena's personal items move to the bathroom and entry floor

On weekends Elena is home all day and her personal-care routine shifts the location of her items. Her toiletry bag moves from the dresser (its weekday resting spot) to the bathroom shelf, where she does her full morning routine. Her skincare follows the same shift: from the nightstand on weekdays to the bathroom shelf on weekends. Her hair dryer moves from the bathroom shelf to the bedroom desk in the afternoon, where she styles her hair at the desk. Her keys and shoes shift from the entry table and shoe rack to the entry floor, where she sets them down more casually when she's home all day. The vacuum cleaner is out in the living room during the afternoon chore block (12:00–18:00), which is when Elena does the weekend cleaning.

This differs from the weekday documents where the toiletry bag is at the dresser, the skincare is at the nightstand, and the hair dryer is at the bathroom shelf. The weekend data confirms: toiletry bag at bathroom_shelf_ba1 (2/2 sightings every hour 08:00–22:00), skincare at bathroom_shelf_ba1 (2/2), hair dryer at desk_b1 (2/2 from 14:00 onward), and keys split between entry_floor and entry_table.

What would refute this: if the toiletry bag is found at the dresser on a weekend morning, if the hair dryer is at the bathroom shelf during a weekend afternoon, or if the vacuum is at the entry floor during the weekend afternoon chore window.

```json
{
 "claims": [
  {
   "claim": "Elena's toiletry bag is on the bathroom shelf during a weekend morning",
   "target": "toiletry_bag_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 8,
   "to": 14
  },
  {
   "claim": "Elena's skincare is on the bathroom shelf during a weekend morning",
   "target": "skincare_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 8,
   "to": 14
  },
  {
   "claim": "Elena's hair dryer is at the bedroom desk during a weekend afternoon",
   "target": "hair_dryer_elena",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Elena's keys are on the entry floor during a weekend morning",
   "target": "keys_elena",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 8,
   "to": 14
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
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
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
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 22,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 18,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
