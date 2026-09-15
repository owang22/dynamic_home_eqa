# p_7c3e — Retired couple; slow pace, objects barely move (fork of p_f2a8)

Two retired adults live here. They wake around 07:30, are at home all day, and go to bed around 21:30. The walkthrough at 15:08 caught them in their usual afternoon routine: reading in the living room (receptacle_10, receptacle_20), perhaps tending to the kitchen (receptacle_18, receptacle_19, receptacle_4). Almost nothing leaves the house: they take short walks but leave keys and bags inside. The objects are extremely stable: the bathroom items (class_12, class_24, class_28) never move. The bedroom (receptacle_8, receptacle_13) items are undisturbed.

**What changed from the parent:** The parent placed object_4 on the counter (receptacle_4) for 08:00–20:00, but seven consecutive looks at receptacle_4 in that window found nothing; the object was instead consistently sighted at receptacle_18 (a kitchen shelf or cabinet). I have moved object_4's primary block to receptacle_18 for the full day, and added object_15 and object_16 at receptacle_4 (the active counter, where they are actually found 3 out of 4 weekday afternoon looks). The claim about object_4 is updated accordingly. Everything else—the keys at receptacle_11, the bathroom item at receptacle_6, the living-room item at receptacle_10—remains as in the parent.

What sets this apart: on ALL days, object_2, object_35, and object_3 are IN the house at all times. object_4 is at receptacle_18 (stored on the shelf) for the full waking day, while object_15 and object_16 occupy the counter (receptacle_4). The living room (receptacle_10) is occupied from 09:00 to 21:00. What would refute it: object_2 or object_35 found receptacle_2 at any time, or object_4 found at receptacle_4 during 10:00–18:00.

```json
{
 "claims": [
  {
   "claim": "object_2 (keys) is always in the house because the retired couple rarely goes far",
   "target": "object_2",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "object_4 (kitchen item) is stored on the kitchen shelf all day, not on the counter",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_26 (living room item) is in the living room during afternoon reading",
   "target": "object_26",
   "expect": "receptacle_10",
   "days": "both",
   "from": 9,
   "to": 21
  },
  {
   "claim": "object_13 (bathroom item) is at the bathroom sink at all hours",
   "target": "object_13",
   "expect": "receptacle_6",
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
  "object_4": [
   {
    "days": "both",
    "from": 8,
    "to": 20,
    "at": "receptacle_18",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_18",
    "chance": "usually"
   }
  ],
  "object_26": [
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
    "chance": "almost_always"
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
  ]
 }
}
```
