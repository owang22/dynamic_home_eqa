# p_7c2d — Weekend: Yuki at the bedroom desk, Omar's gear on the dresser, cooking at eight

On weekends the household inverts its weekday logic. Yuki sleeps in until roughly eight, then spends a lazy morning in the kitchen and bathroom. Around midday she settles at the bedroom desk (desk_b1) with her laptop and notebook for a work or study session that runs through the evening; on weekdays those same items hang on the entry hook while she is at the office, but on weekends they migrate to the desk and stay there from noon onward. Her journal, which rests on the nightstand on weekdays, stays on the bed (bed_b1) all weekend — she reads and writes in bed rather than at the desk.

Omar is off work. His glasses, which sit on the nightstand during the week, move to the bedroom desk (desk_b1) for the entire weekend; he is at that desk gaming, with music, or reading. His tablet shifts from the nightstand to the dresser (dresser_b1) from midday through the evening, suggesting he is in the bedroom but not at the desk — perhaps in the chair or on the bed. His handbag and jacket stay on the entry hook; his shoes stay on the entry floor. Nothing in the evidence supports a weekend cycling trip: both helmets and both bike locks remain at the entry all weekend, contradicting the joint-cycling claims in p_4e91 and p_7a3f.

Dinner cooking on weekends happens around 19:00–20:00. The knife, spatula, pan, and pot all appear at the counter (counter_k1) in that window, then return to drawers and cupboards by 22:00. Yuki's mug, which rests at the sink on weekdays, is in the cupboard (cupboard_k1) from midday through the evening on weekends. Omar's plate is at the dining table (dining_table_d1) for much of the weekend day rather than tucked in the cupboard as on weekdays.

This document is distinguished from the others by its weekend-specific predictions for the objects where the mixture currently fails most: laptop_yuki, notebook_yuki, journal_yuki, glasses_omar, tablet_omar, mug_yuki, plate_omar, and the cooking tools. It also explicitly denies weekend cycling (a claim made by p_4e91 and p_7a3f that has been refuted).

What would refute this document: a weekend sighting of the laptop at entry_hook_e1 after 12:00; the journal at nightstand_b1 on a weekend; the glasses at the nightstand on a weekend; the tablet at the nightstand after 12:00 on a weekend; or a helmet or bike lock out of the house on a weekend morning.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is at the bedroom desk on a Saturday afternoon",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "Yuki's journal is on the bed on a Sunday morning",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 6,
   "to": 12
  },
  {
   "claim": "Omar's glasses are at the bedroom desk on a Saturday afternoon",
   "target": "glasses_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "Omar's tablet is at the dresser on a Sunday afternoon",
   "target": "tablet_omar",
   "expect": "dresser_b1",
   "days": "weekend",
   "from": 14,
   "to": 20
  },
  {
   "claim": "The kitchen knife is on the counter during weekend dinner cooking",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "laptop_yuki": [
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "journal_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "almost_always"
   }
  ],
  "glasses_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "tablet_omar": [
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "dresser_b1",
    "chance": "usually"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekend",
    "from": 12,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "plate_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "class:helmet": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "class:bike_lock": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
