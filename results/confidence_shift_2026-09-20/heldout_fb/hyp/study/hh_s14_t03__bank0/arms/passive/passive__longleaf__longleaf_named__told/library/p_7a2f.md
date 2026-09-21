# p_7a2f — Marco Home Sick Friday: Nothing Leaves the House, Resting Routine

Marco called in sick on Friday. He is home the entire day — no 1:40 departure, no 11 PM return. He will likely sleep in past his usual 6 AM yoga, rest in bed or on the couch through the morning and afternoon, and perhaps do a light journaling session mid-morning. Yuki adjusts her routine to look after him: she still takes the dog for the morning walk (the dog's feeding is unchanged) but skips or shortens her afternoon errands, staying home to make soup and keep him company.

This hypothesis sets itself apart from the standard-split documents (p_a3f1, p_4a7c, p_7d2a) and the work-kit documents (p_b7c2, p_8e2f) in a fundamental way: **nothing leaves the house.** On a normal weekday, Marco's lunchbox, vitamins, keys, jacket, shoes, backpack, and water bottle are all OUT_OF_HOUSE from roughly 14:00 to 23:00. On this sick Friday, every one of those objects remains in the house. There are no OUT_OF_HOUSE blocks in this document; the absence is the claim. His phone stays at the bed as he rests, rather than cycling through the coffee table, entry table, and out the door as it does on work days. His glasses are at the bed or nightstand all day — no morning shower routine when he is sleeping in.

Yuki's keys, jacket, and sunglasses remain at the entry table and entry floor all day because she is not making her afternoon errand trip. This directly contradicts p_c9d4, which has her out 13:00–17:30 on weekdays. Her water bottle stays at the dish rack as usual.

What would refute this document: if Marco's jacket is seen at the entry floor being put on, or his keys are picked up from the entry table and carried out, or his lunchbox is missing from the cupboard during 14–22h (suggesting he went out despite being "sick"), or Yuki's keys are absent from the entry table during 14–17h (suggesting she went out on errands anyway). A single sighting of Marco's shoes off the shoe rack during the day would be a strong refutation.

```json
{
 "claims": [
  {
   "claim": "Marco's lunchbox stays in the cupboard all day because he is not going to work",
   "target": "lunchbox_marco",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's jacket remains on the entry hook all day because he is not going out",
   "target": "jacket_marco",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's keys stay at the entry table all day because he is not going out",
   "target": "keys_marco",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Yuki's keys remain at the entry table in the afternoon because she skips errands to care for Marco",
   "target": "keys_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Marco's phone is at the bed during the afternoon while he rests",
   "target": "phone_marco",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "lunchbox_marco": [
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "vitamins_marco": [
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_marco": [
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_marco": [
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "backpack_marco": [
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "phone_marco": [
   {
    "days": "weekday",
    "from": 10,
    "to": 22,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "glasses_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 22,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 22,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "journal_marco": [
   {
    "days": "weekday",
    "from": 10,
    "to": 14,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_yuki": [
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_yuki": [
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ]
 }
}
```
