# p_4b6f — Weekend Evening; Guitar on the Couch, Yoga on the Floor, Blanket on the Bed

On weekends both Hana and Priya are home all day. The evening routine is leisurely and distinct from weekdays. Around 19:00–20:00 Priya unrolls her yoga mat on the living room floor for a short session (about 30 minutes), then rolls it back up. Around 20:00–21:00 Hana brings her guitar from the bedroom to the couch and plays for an hour or two, sometimes with Priya listening. The blanket, which rests on the couch during the day, is moved to Hana's bed (bed_b1) in the early morning hours (00:00–09:00) because both residents sleep under it or it is draped over the bed.

What sets this document apart: it specifically predicts the guitar at couch_l1 on weekend evenings (20:00–23:00), the yoga mat at floor_l_l1 on weekend evenings (19:00–21:00), and the blanket at bed_b1 on weekend early mornings (00:00–09:00). These three objects are in different places on weekends than on weekdays. On weekdays the guitar stays in the bedroom, the yoga mat stays in wardrobe_b2, and the blanket is on the couch or coffee table.

Refutation: if the guitar is sighted in the bedroom at 21:00 on a weekend, or the yoga mat is in wardrobe_b2 at 20:00 on a weekend, or the blanket is on the couch at 07:00 on a weekend, the document is weakened. If the guitar is on the couch on a weekday evening, this document is wrong (it only predicts weekend couch guitar).

```json
{
 "claims": [
  {
   "claim": "Hana's guitar is on the couch during the weekend evening",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Priya's yoga mat is on the living room floor during the weekend evening yoga session",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The blanket is on Hana's bed during the weekend early morning",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 0,
   "to": 9
  },
  {
   "claim": "Hana's guitar stays in her bedroom on weekdays",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "class:dog_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ]
 }
}
```
