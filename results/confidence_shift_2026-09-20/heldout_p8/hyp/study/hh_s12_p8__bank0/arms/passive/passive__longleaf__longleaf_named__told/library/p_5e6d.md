# p_5e6d — Priya's Saturday: late-morning walk, guitar afternoon, social evening

Priya is retired and home most of the day. On weekends she takes a late-morning walk (around 10–12), so her glasses and water bottle are out of the house in that window. After returning, she settles into the bedroom desk for reading (glasses at desk_b1) and practices guitar in the afternoon (guitar on the bedroom floor, headphones at the desk). In the evening she joins the social gathering in the living room. The yoga mat stays in the wardrobe (no morning yoga on weekends; she walks instead). This document is distinct from the weekday documents in that Priya's afternoon is not an errand window but a leisure window, and the guitar is actively in use rather than just resting.

What would refute it: if the water bottle is at the dish rack at 11:00 on Saturday (no walk), if the guitar is in the living room at 15:00 (she moved it for the guests earlier than expected), or if the glasses are on the nightstand at 14:00 (she never went to the desk).

```json
{
 "claims": [
  {
   "claim": "Priya's guitar is on the bedroom floor on Saturday afternoon during her practice session",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's glasses are at the bedroom desk on Saturday midday after her walk (reading)",
   "target": "glasses_priya",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Priya's water bottle is out of the house on Saturday late morning during her walk",
   "target": "water_bottle_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Priya's headphones are at the bedroom desk on Saturday afternoon",
   "target": "headphones_priya",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "guitar_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 13,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 18,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "headphones_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
