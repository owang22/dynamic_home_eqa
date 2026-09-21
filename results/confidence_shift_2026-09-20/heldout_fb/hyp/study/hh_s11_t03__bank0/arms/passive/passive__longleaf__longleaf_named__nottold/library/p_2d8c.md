# p_2d8c — Priya's Afternoon Armchair; Magazine and Book Migrate to the Chair at 14:00

Priya's afternoon is a reading block. After her morning walk (back by 09:30) and a midday errand, she settles into armchair_l1 around 14:00 with her magazine and a book. The sightings confirm this: magazine_priya at armchair_l1 three times at 15:00, book_priya at armchair_l1 at 15:00. By 18:00 both items have moved back to coffee_table_l1 (the evening resting spot), and by 22:00 the book is back on bookshelf_l1.

This document is distinguished by predicting magazine_priya and book_priya at armchair_l1 (not coffee_table_l1 or bookshelf_l1) during the 14:00–17:00 window. If the robot finds the magazine on the coffee table at 15:00, this document is weakened. If it finds the magazine in the armchair, this document gains.

The camera_priya, whose bookshelf claim has been failing, is predicted here to be ON_PERSON with Priya during her afternoon (she may be taking photos in the garden or balcony) and back on bookshelf_l1 by 18:00.

```json
{
 "claims": [
  {
   "claim": "Priya's magazine is in the armchair during her afternoon reading block",
   "target": "magazine_priya",
   "expect": "armchair_l1",
   "days": "both",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's book is in the armchair during her afternoon reading block",
   "target": "book_priya",
   "expect": "armchair_l1",
   "days": "both",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's camera is on the bookshelf in the evening, not out or on person",
   "target": "camera_priya",
   "expect": "bookshelf_l1",
   "days": "both",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "magazine_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 17.5,
    "at": "armchair_l1",
    "chance": "almost_always"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 17.5,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ]
 }
}
```
