# p_2f7b — Phone at the Coffee Table Overnight and Morning, Bed at Noon, Entry at Night (fork of p_4b6a)

This fork of p_4b6a corrects the phone's morning resting spot. The parent placed phone_marco at nightstand_b1 from 7:00 to 9:00, but the patrol passes show it at coffee_table_l1 at 03:00 (× 2), 07:00 (× 1), and 10:00 (× 1), with only a single nightstand sighting at 03:00 and 08:00. The 9–17 h looks at coffee_table_l1 found it once (at 10:00) and found nothing 8 times, meaning the phone leaves the coffee table by midday. At 13:00 it is at bed_b1 (Marco is in the bedroom getting ready for his shift). At 22:00 it is at entry_table_e1 (he has just walked in from work). The revised pattern: coffee table from 0:00 through about 11:00, bed from 12:00 to 14:00, entry table from 22:00 to 23:30.

What changed from the parent: the 7–9 h block shifts from nightstand_b1 to coffee_table_l1; the base block is coffee_table_l1 (not nightstand_b1).

What would refute this: the phone at the nightstand at 07:00 or 10:00 on a weekday, or at the coffee table at 13:00.

```json
{
 "claims": [
  {
   "claim": "Marco's phone is at the coffee table at 03:00 on a weekday",
   "target": "phone_marco",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Marco's phone is at the bed during his pre-work preparation at 13:00",
   "target": "phone_marco",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Marco's phone is at the entry table at 22:00 after his shift",
   "target": "phone_marco",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  }
 ],
 "targets": {
  "phone_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 23.5,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
