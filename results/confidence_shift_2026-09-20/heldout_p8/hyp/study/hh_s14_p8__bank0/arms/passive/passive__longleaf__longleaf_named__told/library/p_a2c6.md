# p_a2c6 — Weekend laundry and entry: basket on the bedroom floor, shoes on the entry floor

On weekends the household runs a lighter, more casual routine that shifts several objects from their weekday spots. The laundry basket is on the bedroom floor (not the bathroom shelf) for most of the weekend day: the 16:00 weekend pass shows bedroom_floor_b1 twice, and the morning passes show a split between bathroom_shelf_ba1 and bedroom_floor_b1, suggesting the basket is pulled into the bedroom for a weekend laundry session. Marco's towel is on the bed (not the towel rack) in the weekend afternoon, possibly after a weekend shower or nap.

In the entry area, Yuki's shoes are on the entry floor (not the shoe rack) in the weekend morning, as she puts them on for the late-morning walk. Her jacket is at the entry hook, sometimes on the entry floor. Marco's shoes are at the shoe rack, sometimes on the entry floor in the afternoon. This is a more casual pattern than the weekday entry area where items are neatly hung or racked.

This document is a small, focused correction to the weekend entry and bedroom patterns. It does not compete with p_a9d2 or p_e1b3 on kitchen, guitar, or baking predictions; it covers only the laundry basket, Marco's towel, and the entry-area shoes and jacket.

What would refute it: If on a weekend the laundry basket is at the bathroom shelf all day, Marco's towel is on the towel rack in the afternoon, and Yuki's shoes are on the shoe rack in the morning, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The laundry basket is on the bedroom floor during the weekend afternoon",
   "target": "laundry_basket_shared",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 12,
   "to": 22
  },
  {
   "claim": "Marco's towel is on the bed during the weekend afternoon",
   "target": "towel_marco",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 12,
   "to": 22
  },
  {
   "claim": "Yuki's shoes are on the entry floor during the weekend morning walk prep",
   "target": "shoes_yuki",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 7,
   "to": 12
  }
 ],
 "targets": {
  "laundry_basket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "towel_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "shoes_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "rarely"
   }
  ],
  "shoes_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "entry_floor_e1",
    "chance": "rarely"
   }
  ]
 }
}
```
