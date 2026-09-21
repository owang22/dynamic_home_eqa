# p_f1b8 — Weekend laundry: the basket moves to the bedroom floor in the evening

On weekdays the laundry basket sits on the bathroom shelf (where it is seen at 03:00, 09:00, 18:00, 19:00). On weekends, after the midday errands, one of the residents does the laundry in the late afternoon or early evening: the basket is carried from the bathroom to the bedroom floor around 18:00–19:00 and stays there while clothes are sorted and put away, until about 21:00 when it is returned to the bathroom shelf. The day-4 (Saturday) 19:00 and 20:00 sightings at bedroom_floor_b1 confirm this. Elena's yoga mat is in the living room area (floor, coffee table, or bed) in the early morning for her yoga practice, then stored in the wardrobe by the evening. Ines's laptop rests at the office desk on weekends since she is not working.

What sets this apart from every other document: the laundry basket is NOT at the bathroom shelf on weekend evenings; it is at the bedroom floor. No existing document predicts this weekend-specific relocation.

Refutation: if the laundry basket is sighted at the bathroom shelf on a weekend between 18:00 and 21:00, or if it is at the bedroom floor on a weekday, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The laundry basket is on the bedroom floor during the weekend evening laundry session",
   "target": "laundry_basket_shared",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The laundry basket is on the bathroom shelf during weekday work hours",
   "target": "laundry_basket_shared",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's yoga mat is in the living room during her early-morning yoga",
   "target": "yoga_mat_elena",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 6,
   "to": 8
  },
  {
   "claim": "Ines's laptop is at the office desk on weekend mornings",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekend",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "laundry_basket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "yoga_mat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "sometimes"
   }
  ],
  "laptop_ines": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
