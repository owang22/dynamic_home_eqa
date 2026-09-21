# p_0d1e — The bathroom shelf is a shared zone; personal items rotate

The bathroom shelf holds shared items (detergent, laundry basket) permanently, but personal items (hair dryer, skincare, toiletry bags, towel_yuki) rotate between the shelf and the sink or towel rack. Omar's hair dryer is at the shelf on weekdays but may be at the sink on weekends (he uses it more). Yuki's towel is at the shelf on weekdays (stored) but at the towel rack on weekends (in use). What sets this hypothesis apart: towel_yuki is at the towel rack on weekends but at the bathroom shelf on weekdays. What would refute it: towel_yuki sighted at bathroom_shelf_ba1 on a Saturday at 14:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's towel is at the bathroom shelf on a Wednesday",
   "target": "towel_yuki",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Yuki's towel is at the towel rack on a Saturday",
   "target": "towel_yuki",
   "expect": "towel_rack_ba1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Omar's hair dryer is at the bathroom shelf on a Tuesday",
   "target": "hair_dryer_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Omar's towel is at the towel rack at all times",
   "target": "towel_omar",
   "expect": "towel_rack_ba1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "towel_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "towel_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "hair_dryer_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 10,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   }
  ],
  "skincare_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
