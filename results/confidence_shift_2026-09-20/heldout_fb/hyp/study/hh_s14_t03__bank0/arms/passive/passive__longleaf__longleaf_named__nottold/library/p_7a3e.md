# p_7a3e — Marco's Book Travels: Nightstand at Night, Gone by Day

Marco's book has only ever been seen at the nightstand, yet every weekday look between 9 and 17 finds that nightstand empty of it—three empty looks in the per-object evidence. The simplest reading is that Marco takes the book with him: perhaps he reads on the commute or keeps it at his desk at work. The book rests at the nightstand overnight and reappears in the evening. No other document in the library tracks book_marco at all, so this hypothesis fills a gap. It would be refuted if the book is sighted at the nightstand during 10–16 h on a weekday, or if it is found at a different in-house receptacle during the day (suggesting it is left in the house but simply moved to a spot the robot has not yet checked).

```json
{
 "claims": [
  {
   "claim": "Marco's book is at the nightstand at 23:00 on a weekday",
   "target": "book_marco",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Marco's book is out of the house during his work shift",
   "target": "book_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 21
  },
  {
   "claim": "Marco's book is out of the house in the late morning before his shift",
   "target": "book_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 10,
   "to": 13
  }
 ],
 "targets": {
  "book_marco": [
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
