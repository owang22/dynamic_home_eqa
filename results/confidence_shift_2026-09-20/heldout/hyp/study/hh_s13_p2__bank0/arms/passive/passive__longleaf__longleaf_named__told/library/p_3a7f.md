# p_3a7f — Weekend Entry Floor Drop: Jacket, Shoes, and Sunglasses Hit the Floor

Hana and Priya run a tidy weekday entry: Hana's jacket hangs on the hook, her shoes sit on the rack, Priya's sunglasses rest on the entry table. But weekends are different. Both residents are "around the house more" (their own words), and the entry becomes a drop-zone. Priya's jacket, which hangs neatly on the hook every weekday, ends up on the entry floor from Saturday afternoon through Sunday evening. Hana's shoes, normally on the rack, appear on the entry floor from mid-afternoon on weekends. Priya's sunglasses, usually on the table, shift to the floor in the weekend afternoon.

This hypothesis predicts that on weekends, specifically from about 14:00 onward, three entry objects migrate from their weekday resting spots (hook, rack, table) to the entry floor. The mechanism is simple: on weekends the residents are in and out of the house for errands and walks, and rather than hanging or shelving their things, they set them down on the floor by the door. The pattern is weekend-specific; on weekdays the same objects stay at their proper spots.

What would refute this: if on a weekend afternoon the robot finds jacket_priya still on the hook, shoes_hana still on the rack, and sunglasses_priya still on the table, the drop-zone hypothesis loses support. If the objects are found on the floor on a weekday, the weekend-specificity is wrong.

```json
{
 "claims": [
  {
   "claim": "Priya's jacket is on the entry floor at 16:00 on a Saturday because it was dropped after a walk",
   "target": "jacket_priya",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Hana's shoes are on the entry floor at 18:00 on a Saturday, not on the shoe rack",
   "target": "shoes_hana",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 16,
   "to": 20
  },
  {
   "claim": "Priya's sunglasses are on the entry floor at 15:00 on a Saturday, not on the entry table",
   "target": "sunglasses_priya",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
  "jacket_priya": [
   {
    "days": "weekend",
    "from": 14,
    "to": 23,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekend",
    "from": 16,
    "to": 23,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
