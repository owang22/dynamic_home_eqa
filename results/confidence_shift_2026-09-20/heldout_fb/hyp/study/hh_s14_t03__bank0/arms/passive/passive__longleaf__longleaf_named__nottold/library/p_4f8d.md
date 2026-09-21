# p_4f8d — Journal at the Desk Overnight and Through the Morning, Nightstand Only While Marco Is at Work

Marco journals as a hobby and does his writing in the early morning before his afternoon shift. The journal lives at the bedroom desk from the time he wakes (or even overnight, since he sometimes writes late) through his morning session, which ends when he leaves for work at about 13:40. Before leaving, he sets the journal on the nightstand where it stays for the entire work shift (14:00–23:00). When he gets home at 23:00, he picks it up for an evening journaling session at the desk, so it returns to the desk from 23:00 onward. On weekends, when Marco is home all day, the journal stays at the desk essentially the whole time; the 03:00 weekend pass confirms desk_b1.

This differs from p_9c4e, which places the journal at the nightstand from 17:00–24:00 (a window that has been failing with 6 againsts, because Marco is home after 23:00 and the journal is back at the desk). It also differs from p_d4e7, which has the journal at the desk only 7:00–13:00 and at the nightstand 14:00–22:00, leaving the overnight hours and the post-23:00 hours uncovered. This document would be refuted if the journal were sighted at the nightstand at 23:30 on a weekday (meaning Marco does not pick it up when he gets home) or at the desk at 16:00 on a weekday (meaning he takes it to work, as p_b7c2 claims).

```json
{
 "claims": [
  {
   "claim": "Marco's journal is at the bedroom desk at 03:00 on a weekday",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Marco's journal is at the nightstand at 16:00 on a weekday while he is at work",
   "target": "journal_marco",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 15,
   "to": 19
  },
  {
   "claim": "Marco's journal is at the bedroom desk at 03:00 on a weekend",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Marco's journal is at the bedroom desk at noon on a weekday during his writing session",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 13
  }
 ],
 "targets": {
  "journal_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
