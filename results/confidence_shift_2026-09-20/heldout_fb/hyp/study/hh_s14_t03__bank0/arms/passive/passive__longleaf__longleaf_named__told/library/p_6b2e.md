# p_6b2e — Weekend Home: Marco's Errands, Yuki's Late Walk, Both Around the House

Marco is off work on weekends and home from early morning. He heads out for errands around midday (roughly 12:00–14:00) and is back by early afternoon. Yuki takes her walk in the late morning (10:00–11:00) rather than the early morning she does on weekdays. The Saturday message confirms both are "around the house more," so the house is populated all day. Crucially, Marco's work kit—lunchbox, vitamins, journal—stays in the house all day on weekends; nothing is packed for a shift. His journal rests at the bedroom desk, where the evidence places it 3 of 4 sighted days. His yoga mat is pulled from the wardrobe for a short morning session, then stored again.

What sets this apart from the weekday documents (p_a3f1, p_b7c2, p_7d2a): on weekdays Marco is OUT_OF_HOUSE from roughly 13:40 to 23:00, carrying his lunchbox and vitamins. Here, those objects remain at their resting spots all day. The only time Marco's personal items leave is the midday errand window, and only keys, wallet, and phone go with him.

This document is refuted if Marco's lunchbox or vitamins are sighted OUT_OF_HOUSE on a weekend, or if his journal is found at the nightstand rather than the desk during the day, or if Yuki's leash is on her person before 09:00 (indicating an early-morning walk rather than a late-morning one).

```json
{
 "claims": [
  {
   "claim": "Marco's lunchbox stays in the kitchen cupboard all day on the weekend because he is not going to work",
   "target": "lunchbox_marco",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's keys are out of the house during his midday errand",
   "target": "keys_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Marco's yoga mat is on the living room floor during his weekend morning yoga",
   "target": "yoga_mat_marco",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 6,
   "to": 7
  },
  {
   "claim": "The dog leash is on Yuki's person during her weekend late-morning walk",
   "target": "dog_leash_shared",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 10,
   "to": 11
  }
 ],
 "targets": {
  "lunchbox_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "vitamins_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "journal_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "phone_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_marco": [
   {
    "days": "weekend",
    "from": 6,
    "to": 7,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 6,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
