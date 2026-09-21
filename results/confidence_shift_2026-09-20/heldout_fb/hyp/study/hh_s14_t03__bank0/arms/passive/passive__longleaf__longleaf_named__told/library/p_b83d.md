# p_b83d — p_w8q3 — Weekend Morning: Both Residents Home, Kitchen Table Breakfast and Reading

On Saturday morning both Marco and Yuki are home from the start of the day (confirmed: both seen in bedroom_1 at 03:00 on Saturday). The morning routine centres on the kitchen table: Yuki's tablet is at the nightstand at 03:00 and at the kitchen table by 09:00 (reading or browsing). Her phone is at the nightstand at 03:00 and 08:00. Marco's phone is at the nightstand at 03:00 (unlike weekdays when it is on the coffee table). Breakfast is served at the kitchen table around 09:00–10:00: Yuki's bowl and Marco's bowl appear there in that window, along with Yuki's mug. Marco's water bottle is at the dish rack at 03:00 (washed the night before) rather than the coffee table as on weekdays.

The laundry basket sits on the bathroom shelf through the morning (03:00, 07:00, 10:00) and moves to the bedroom floor by 13:00, suggesting a midday laundry session. Marco's towel is on the towel rack at 03:00 and 10:00, at the bathroom shelf at 12:00 (post-shower), and on the bed by 15:00 (drying or in use).

This document fills a gap: no existing document captures the full weekend morning kitchen-table routine with both residents present and the specific object placements the sightings confirm.

What would refute this: Marco's phone on the coffee table before 12:00 on a weekend, or the tablet at the kitchen table before 08:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's tablet is at the kitchen table at 09:00 on a weekend during morning reading",
   "target": "tablet_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Marco's phone is at the nightstand at 03:00 on a weekend, not on the coffee table",
   "target": "phone_marco",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The laundry basket is on the bathroom shelf at 07:00 on a weekend, before the midday laundry",
   "target": "laundry_basket_shared",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 6,
   "to": 8
  },
  {
   "claim": "Marco's water bottle is at the dish rack at 03:00 on a weekend, not on the coffee table",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "tablet_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "phone_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 24,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ],
  "phone_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "laundry_basket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 18,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "towel_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 11,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
