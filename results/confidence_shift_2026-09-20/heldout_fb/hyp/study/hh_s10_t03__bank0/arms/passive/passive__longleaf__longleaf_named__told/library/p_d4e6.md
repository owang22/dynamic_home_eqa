# p_d4e6 — Omar's 23:00 entry dump: bag, lunchbox, notebook, pen, wallet, shoes

Omar comes home at 23:00 on weekdays after his night shift, too tired to sort his belongings. His handbag (which he uses as a work bag) goes on the entry hook or the entry table. His lunchbox from work hits the entry table. His notebook and pen go on the entry hook. His wallet lands on the entry table or the entry floor. His shoes either make it to the shoe rack or just get kicked off on the entry floor. By the 03:00 robot pass, everything is still at the entry, untouched.

This is a "too tired to sort" dump, not a deliberate sorting. The items do not reach their proper homes (wardrobe for the scarf, kitchen for the lunchbox, desk for the notebook) until the next morning at the earliest. This document is set apart by predicting ALL of Omar's carry items at the entry zone simultaneously from 23:00 through 07:00, rather than scattered across their resting spots.

What would refute it: the lunchbox in the kitchen at 03:00; the notebook at the desk at 03:00; the shoes on the shoe rack at 03:00 (though this is a soft refutation since the dump is inconsistent).

```json
{
 "claims": [
  {
   "claim": "Omar's handbag is at the entry hook at 03:00 on a weekday (dumped when he came home at 23:00)",
   "target": "handbag_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Omar's lunchbox is at the entry table at 03:00 on a weekday (dumped at the entry, not yet in the kitchen)",
   "target": "lunchbox_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Omar's wallet is at the entry table at 03:00 on a weekday (dumped at the entry)",
   "target": "wallet_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Omar's shoes are at the entry floor at 03:00 on a weekday (too tired to put them on the rack)",
   "target": "shoes_omar",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 0,
   "to": 7
  }
 ],
 "targets": {
  "handbag_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 1,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "notebook_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "pen_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "wallet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ],
  "shoes_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
