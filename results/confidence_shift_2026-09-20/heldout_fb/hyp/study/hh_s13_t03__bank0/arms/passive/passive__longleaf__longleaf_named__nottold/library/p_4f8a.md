# p_4f8a — Priya's Midday Grocery: Shopping Bag at the Counter

Hana is at work from 8 to 5:30 on weekdays, so the midday kitchen activity belongs to Priya. The strongest unexplained signal in the evidence is the shopping bag: five sightings at the kitchen counter at 12:00 on weekdays, with the bag in the pantry shelf at 03:00 and 18:00. This is a grocery run. Priya leaves the house in the late morning (around 10:30), goes to the shop, and returns around 11:30–12:00 carrying a bag. She unpacks at the counter, which is where the robot catches it. By the evening the bag is folded and stored back on the pantry shelf.

What sets this document apart: p_f7a2 says Priya travels only on Tuesdays and Thursdays, but the five noon sightings of the bag suggest a more regular (possibly daily or near-daily) midday errand. This document predicts the bag at the counter every weekday around noon, and Priya's keys, jacket, and phone out of the house in the 10:30–12:00 window. If the bag is never seen at the counter on a Wednesday or Friday, or if Priya's keys are found at the entry table at 11:00, this hypothesis is wrong.

```json
{
 "claims": [
  {
   "claim": "The shopping bag is on the kitchen counter at noon on a weekday",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 12.5
  },
  {
   "claim": "Priya's keys are out of the house at 11:00 on a weekday",
   "target": "keys_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 10.5,
   "to": 12
  },
  {
   "claim": "Priya's jacket is out of the house at 11:00 on a weekday",
   "target": "jacket_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 10.5,
   "to": 12
  },
  {
   "claim": "The shopping bag is in the pantry shelf at 18:00 on a weekday",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
