# Revision log — hh_001 · call 2 (day 7)

Rendered from `hh_001_revision_2.json`. Prompts are reproduced verbatim inside fenced blocks; hypotheses are labelled hyp1… in prose.

## System prompt

```text
You are modelling how one household runs, for a home robot that must predict where objects are. You write competing hypotheses; a downstream statistical system converts them into probabilistic predictions and weighs them against future sightings. Be concrete and decisive; the sightings, not you, will settle who was right. This is not your only chance: you will be shown where each hypothesis was wrong and asked to revise it. Commit to sharp, different hypotheses now rather than hedging — hedged hypotheses all say the same thing and cannot be told apart by data.
```

## Prompt

```text
It is now day 7. The robot has been watching since your hypotheses were written; here is how they did. Revise them — keep what held up, fix what did not, and add at most ONE new hypothesis only if something systematic is unexplained. Do not start over: revised hypotheses keep their hypothesis_id, and a new one gets the next id.

HYPOTHESIS WEIGHTS (share of the mixture each currently earns from the sightings):
  h1: weight 0.13 — distinguishing prediction not yet tested (no sightings of the target in that window)
  h2: weight 0.55 — distinguishing prediction not yet tested (no sightings of the target in that window)
  h3: weight 0.09 — distinguishing prediction not yet tested (no sightings of the target in that window)
  h4: weight 0.07 — distinguishing prediction not yet tested (no sightings of the target in that window)
  h5: weight 0.17 — distinguishing prediction came true 0/1 times

MIXTURE'S WORST OBJECTS — where it predicted vs where the object actually was:
  remote_shared_1: predicted cupboard_k1, actually counter_k1 — 4x, e.g. day 4 06:00
  pan_shared_1: predicted sink_k1, actually counter_k1 — 4x, e.g. day 4 13:00
  makeup_kit_mara: predicted bathroom_shelf_ba1, actually kitchen_table_k1 — 4x, e.g. day 5 07:00
  water_bottle_mara: predicted kitchen_table_k1, actually counter_k1 — 3x, e.g. day 3 08:00
  mug_mara: predicted counter_k1, actually kitchen_table_k1 — 3x, e.g. day 4 07:00
  bowl_shared_2: predicted sink_k1, actually kitchen_table_k1 — 3x, e.g. day 5 07:00
  pan_shared_1: predicted sink_k1, actually kitchen_table_k1 — 3x, e.g. day 5 07:00
  plate_shared_1: predicted sink_k1, actually kitchen_table_k1 — 3x, e.g. day 6 07:00
  book_mara: predicted bookshelf_l1, actually ON_PERSON — 2x, e.g. day 3 00:00
  medication_bottle_mara: predicted counter_k1, actually bathroom_shelf_ba1 — 2x, e.g. day 3 05:00
  wallet_mara: predicted kitchen_table_k1, actually entry_hook_e1 — 2x, e.g. day 3 08:00
  pen_mara: predicted kitchen_table_k1, actually counter_k1 — 2x, e.g. day 3 18:00

RULES THAT HELD UP (object was where the rule said, during its activity):
  h2/morning_routine: mug_mara -> counter_k1 held (0.68 on 9 sightings)
  h3/morning_routine: mug_mara -> counter_k1 held (0.68 on 9 sightings)
  h4/morning_routine: mug_mara -> counter_k1 held (0.68 on 9 sightings)
  h5/morning_routine: mug_mara -> counter_k1 held (0.68 on 9 sightings)
  h1/morning_routine: mug_mara -> counter_k1 held (0.68 on 8 sightings)
  h1/morning_routine: medication_bottle_mara -> counter_k1 held (0.60 on 6 sightings)
  h2/morning_routine: water_bottle_mara -> counter_k1 held (0.69 on 4 sightings)
  h3/morning_routine: water_bottle_mara -> counter_k1 held (0.69 on 4 sightings)
  h4/morning_routine: water_bottle_mara -> counter_k1 held (0.69 on 4 sightings)
  h5/morning_routine: water_bottle_mara -> counter_k1 held (0.69 on 4 sightings)
  h1/work_day: glasses_mara -> kitchen_table_k1 held (0.71 on 3 sightings)
  h3/daytime_work: glasses_mara -> kitchen_table_k1 held (0.71 on 3 sightings)
  h5/work_day: glasses_mara -> kitchen_table_k1 held (0.71 on 3 sightings)
  h1/morning_routine: water_bottle_mara -> counter_k1 held (0.69 on 3 sightings)
  h1/lunch: bowl_shared_2 -> kitchen_table_k1 held (0.54 on 3 sightings)

RULES THAT FAILED (object was elsewhere during the rule's activity):
  (none)

OBJECTS NO HYPOTHESIS COVERS (no rule and no rest entry mentions them), with what the sightings show:
  (none)

PER-OBJECT STATISTICS over days 0-7 (modal receptacle; share of sighted days it was there; distinct receptacles seen; days with no sighting):
  backpack_mara: mostly entry_hook_e1 (4/6 sighted days); 2 receptacles; unseen 2 days
  blanket_mara: mostly couch_l1 (7/7 sighted days); 1 receptacle; unseen 1 day
  book_mara: mostly bookshelf_l1 (2/6 sighted days); 3 receptacles; unseen 2 days
  bowl_shared_1: mostly entry_table_e1 (8/8 sighted days); 1 receptacle; unseen 0 days
  bowl_shared_2: mostly sink_k1 (4/7 sighted days); 3 receptacles; unseen 1 day
  charger_mara: mostly kitchen_table_k1 (4/5 sighted days); 2 receptacles; unseen 3 days
  glasses_mara: mostly sink_k1 (2/7 sighted days); 4 receptacles; unseen 1 day
  hairbrush_mara: mostly bathroom_shelf_ba1 (5/7 sighted days); 3 receptacles; unseen 1 day
  headphones_mara: mostly kitchen_table_k1 (4/5 sighted days); 3 receptacles; unseen 3 days
  jacket_mara: mostly entry_hook_e1 (4/5 sighted days); 2 receptacles; unseen 3 days
  keys_mara: mostly entry_table_e1 (4/4 sighted days); 1 receptacle; unseen 4 days
  laptop_mara: mostly kitchen_table_k1 (5/5 sighted days); 1 receptacle; unseen 3 days
  laundry_basket_mara: mostly bedroom_floor_b1 (6/6 sighted days); 1 receptacle; unseen 2 days
  lunchbox_mara: mostly counter_k1 (4/6 sighted days); 3 receptacles; unseen 2 days
  makeup_kit_mara: mostly bathroom_shelf_ba1 (2/5 sighted days); 3 receptacles; unseen 3 days
  medication_bottle_mara: mostly bathroom_shelf_ba1 (4/7 sighted days); 3 receptacles; unseen 1 day
  mug_mara: mostly counter_k1 (4/7 sighted days); 5 receptacles; unseen 1 day
  mug_shared_1: mostly cupboard_k1 (7/7 sighted days); 1 receptacle; unseen 1 day
  notebook_mara: mostly kitchen_table_k1 (3/5 sighted days); 4 receptacles; unseen 3 days
  pan_shared_1: mostly counter_k1 (2/7 sighted days); 4 receptacles; unseen 1 day
  pen_mara: mostly kitchen_table_k1 (4/7 sighted days); 3 receptacles; unseen 1 day
  phone_mara: mostly nightstand_b1 (5/5 sighted days); 2 receptacles; unseen 3 days
  plate_shared_1: mostly sink_k1 (2/7 sighted days); 4 receptacles; unseen 1 day
  plate_shared_2: mostly counter_k1 (4/7 sighted days); 3 receptacles; unseen 1 day
  pot_shared_1: mostly dish_rack_k1 (4/7 sighted days); 2 receptacles; unseen 1 day
  remote_shared_1: mostly cupboard_k1 (3/7 sighted days); 4 receptacles; unseen 1 day
  suitcase_mara: mostly bedroom_floor_b1 (6/6 sighted days); 1 receptacle; unseen 2 days
  tablet_mara: mostly coffee_table_l1 (5/6 sighted days); 3 receptacles; unseen 2 days
  towel_mara: mostly towel_rack_ba1 (2/4 sighted days); 2 receptacles; unseen 4 days
  umbrella_mara: mostly entry_floor_e1 (4/4 sighted days); 1 receptacle; unseen 4 days
  vacuum_cleaner_shared_1: mostly bedroom_floor_b1 (6/7 sighted days); 2 receptacles; unseen 1 day
  wallet_mara: mostly entry_table_e1 (5/7 sighted days); 3 receptacles; unseen 1 day
  water_bottle_mara: mostly kitchen_table_k1 (2/6 sighted days); 4 receptacles; unseen 2 days
  watering_can_mara: mostly sink_k1 (6/7 sighted days); 2 receptacles; unseen 1 day
  yoga_mat_mara: mostly couch_l1 (5/5 sighted days); 1 receptacle; unseen 3 days

The ONLY valid identifiers are these, exactly as printed:

RECEPTACLES (valid `to` and rest locations):
  bed_b1
  nightstand_b1
  desk_b1
  bedroom_floor_b1
  couch_l1
  coffee_table_l1
  tv_stand_l1
  bookshelf_l1
  armchair_l1
  counter_k1
  sink_k1
  cupboard_k1
  dish_rack_k1
  kitchen_table_k1
  chair_k1
  chair_k2
  bathroom_shelf_ba1
  towel_rack_ba1
  entry_table_e1
  entry_hook_e1
  entry_floor_e1
  ON_PERSON
  OUT_OF_HOUSE  [never directly observable]

OBJECTS (valid `target` ids, with class):
  backpack_mara  (class: backpack)
  blanket_mara  (class: blanket)
  book_mara  (class: book)
  bowl_shared_1  (class: bowl)
  bowl_shared_2  (class: bowl)
  charger_mara  (class: charger)
  glasses_mara  (class: glasses)
  hairbrush_mara  (class: hairbrush)
  headphones_mara  (class: headphones)
  jacket_mara  (class: jacket)
  keys_mara  (class: keys)
  laptop_mara  (class: laptop)
  laundry_basket_mara  (class: laundry_basket)
  lunchbox_mara  (class: lunchbox)
  makeup_kit_mara  (class: makeup_kit)
  medication_bottle_mara  (class: medication_bottle)
  mug_mara  (class: mug)
  mug_shared_1  (class: mug)
  notebook_mara  (class: notebook)
  pan_shared_1  (class: pan)
  pen_mara  (class: pen)
  phone_mara  (class: phone)
  plate_shared_1  (class: plate)
  plate_shared_2  (class: plate)
  pot_shared_1  (class: pot)
  remote_shared_1  (class: remote)
  suitcase_mara  (class: suitcase)
  tablet_mara  (class: tablet)
  towel_mara  (class: towel)
  umbrella_mara  (class: umbrella)
  vacuum_cleaner_shared_1  (class: vacuum_cleaner)
  wallet_mara  (class: wallet)
  water_bottle_mara  (class: water_bottle)
  watering_can_mara  (class: watering_can)
  yoga_mat_mara  (class: yoga_mat)

CLASSES (valid as `class:<name>` targets): backpack, blanket, book, bowl, charger, glasses, hairbrush, headphones, jacket, keys, laptop, laundry_basket, lunchbox, makeup_kit, medication_bottle, mug, notebook, pan, pen, phone, plate, pot, remote, suitcase, tablet, towel, umbrella, vacuum_cleaner, wallet, water_bottle, watering_can, yoga_mat

YOUR PREVIOUS HYPOTHESES:

{
 "hypotheses": [
  {
   "hypothesis_id": "h1",
   "rationale": "Mara is a WFH professional who almost never leaves the house. Kitchen table is her permanent office; counter is her kitchen staging area; cupboard stores dishes and small items. Keys, jacket, backpack are rarely seen because she stays home.",
   "distinguishing_prediction": "laptop_mara remains at kitchen_table_k1 on a weekday at 14:00 because she never leaves for work",
   "distinguishing_check": {
    "target": "laptop_mara",
    "at": "kitchen_table_k1",
    "days": "weekday",
    "hour": 14.0
   },
   "activities": [
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "medication_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "work_day",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 9.0,
     "duration_h": 8.0,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "charger_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "headphones_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "phone_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "lunch",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 12.5,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "plate_shared_2",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_relax",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 19.5,
     "duration_h": 3.0,
     "moves": [
      {
       "target": "remote_shared_1",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "tablet_mara",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "blanket_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "weekend_yoga",
     "days": "weekend",
     "frequency_per_week": 2,
     "start_hour": 9.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "yoga_mat_mara",
       "to": "bedroom_floor_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "headphones_mara",
       "to": "bedroom_floor_b1",
       "chance": "sometimes",
       "after": "returned"
      },
      {
       "target": "water_bottle_mara",
       "to": "bedroom_floor_b1",
       "chance": "sometimes",
       "after": "returned"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "sink_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "water_bottle_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  },
  {
   "hypothesis_id": "h2",
   "rationale": "Mara has a hybrid schedule: WFH Mon/Wed/Fri but goes to a shared office Tue/Thu. Laptop and work kit go with her on office days; on WFH days everything stays at kitchen table. She is rarely out on non-office days.",
   "distinguishing_prediction": "laptop_mara is OUT_OF_HOUSE on a weekday at 14:00 because she is at her shared office",
   "distinguishing_check": {
    "target": "laptop_mara",
    "at": "OUT_OF_HOUSE",
    "days": "weekday",
    "hour": 14.0
   },
   "activities": [
    {
     "name": "office_out",
     "days": "weekday",
     "frequency_per_week": 2,
     "start_hour": 8.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "backpack_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "keys_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "wallet_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "phone_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "charger_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "office_home",
     "days": "weekday",
     "frequency_per_week": 2,
     "start_hour": 17.0,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "backpack_mara",
       "to": "entry_hook_e1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "keys_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "wallet_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "phone_mara",
       "to": "nightstand_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "charger_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "returned"
      }
     ]
    },
    {
     "name": "wfh_day",
     "days": "weekday",
     "frequency_per_week": 3,
     "start_hour": 9.0,
     "duration_h": 8.0,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "charger_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "headphones_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_relax",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 19.5,
     "duration_h": 3.0,
     "moves": [
      {
       "target": "remote_shared_1",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "tablet_mara",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "blanket_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "left"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "sink_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "water_bottle_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  },
  {
   "hypothesis_id": "h3",
   "rationale": "Mara works an evening shift (16:00-23:30). She is home all day using the kitchen table for personal work/study, then leaves in the late afternoon. Laptop stays home because her job doesn't require it. Keys and wallet go out with her.",
   "distinguishing_prediction": "keys_mara is OUT_OF_HOUSE on a weekday at 21:00 because she is at her evening shift",
   "distinguishing_check": {
    "target": "keys_mara",
    "at": "OUT_OF_HOUSE",
    "days": "weekday",
    "hour": 21.0
   },
   "activities": [
    {
     "name": "daytime_work",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 9.0,
     "duration_h": 6.5,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "notebook_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "shift_out",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 15.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "keys_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "wallet_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "jacket_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "phone_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "backpack_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "shift_home",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 23.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "keys_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "wallet_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "jacket_mara",
       "to": "entry_hook_e1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "phone_mara",
       "to": "nightstand_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "backpack_mara",
       "to": "entry_hook_e1",
       "chance": "sometimes",
       "after": "returned"
      }
     ]
    },
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "weekend_yoga",
     "days": "weekend",
     "frequency_per_week": 2,
     "start_hour": 10.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "yoga_mat_mara",
       "to": "bedroom_floor_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "headphones_mara",
       "to": "bedroom_floor_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "water_bottle_mara",
       "to": "bedroom_floor_b1",
       "chance": "usually",
       "after": "returned"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "sink_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "water_bottle_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  },
  {
   "hypothesis_id": "h4",
   "rationale": "Mara is a part-time student who studies at home most days but goes to campus twice a week (Mon/Wed) for in-person lectures. On campus days she takes notebook, pen, and laptop; on other days everything stays at the kitchen table. Her schedule is lighter than a full-time student.",
   "distinguishing_prediction": "notebook_mara is OUT_OF_HOUSE on a weekday at 11:00 because she is in a campus lecture",
   "distinguishing_check": {
    "target": "notebook_mara",
    "at": "OUT_OF_HOUSE",
    "days": "weekday",
    "hour": 11.0
   },
   "activities": [
    {
     "name": "campus_out",
     "days": "weekday",
     "frequency_per_week": 2,
     "start_hour": 8.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "notebook_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "pen_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "laptop_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "backpack_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "keys_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "wallet_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      }
     ]
    },
    {
     "name": "campus_return",
     "days": "weekday",
     "frequency_per_week": 2,
     "start_hour": 14.0,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "notebook_mara",
       "to": "kitchen_table_k1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "pen_mara",
       "to": "kitchen_table_k1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "backpack_mara",
       "to": "entry_hook_e1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "keys_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "wallet_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      }
     ]
    },
    {
     "name": "home_study",
     "days": "weekday",
     "frequency_per_week": 3,
     "start_hour": 10.0,
     "duration_h": 5.0,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "notebook_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_relax",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 19.5,
     "duration_h": 3.0,
     "moves": [
      {
       "target": "remote_shared_1",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "tablet_mara",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "blanket_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "weekend_yoga",
     "days": "weekend",
     "frequency_per_week": 2,
     "start_hour": 9.5,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "yoga_mat_mara",
       "to": "bedroom_floor_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "water_bottle_mara",
       "to": "bedroom_floor_b1",
       "chance": "usually",
       "after": "returned"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "sink_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "water_bottle_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  },
  {
   "hypothesis_id": "h5",
   "rationale": "Mara works from home but has a structured active routine: gym sessions 3x/week in the early evening. Laptop stays at kitchen table throughout. She briefly leaves with water bottle, phone, and keys for the gym, then returns for dinner and TV.",
   "distinguishing_prediction": "water_bottle_mara is OUT_OF_HOUSE on a weekday at 18:30 because she is at the gym during her evening session",
   "distinguishing_check": {
    "target": "water_bottle_mara",
    "at": "OUT_OF_HOUSE",
    "days": "weekday",
    "hour": 18.5
   },
   "activities": [
    {
     "name": "work_day",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 9.0,
     "duration_h": 7.0,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "charger_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "headphones_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "phone_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "gym_session",
     "days": "weekday",
     "frequency_per_week": 3,
     "start_hour": 18.0,
     "duration_h": 1.5,
     "moves": [
      {
       "target": "water_bottle_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "phone_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "keys_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "jacket_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "cooking_dinner",
     "days": "both",
     "frequency_per_week": 5,
     "start_hour": 18.5,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "pan_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "pot_shared_1",
       "to": "counter_k1",
       "chance": "sometimes",
       "after": "returned"
      },
      {
       "target": "bowl_shared_1",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_tv",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 20.0,
     "duration_h": 2.5,
     "moves": [
      {
       "target": "remote_shared_1",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "tablet_mara",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "blanket_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "weekend_yoga",
     "days": "weekend",
     "frequency_per_week": 2,
     "start_hour": 9.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "yoga_mat_mara",
       "to": "bedroom_floor_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "headphones_mara",
       "to": "bedroom_floor_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "water_bottle_mara",
       "to": "bedroom_floor_b1",
       "chance": "usually",
       "after": "returned"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "sink_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "water_bottle_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  }
 ]
}

Rules: same output format and the same seven rules as before (ids only from the tables; chances as labels; `rest` optional; every hypothesis carries a distinguishing_prediction and distinguishing_check). Keep 5 hypotheses, or 6 if you add one. Think about what the mismatches imply, then end your reply with ONE json object holding the full revised set.
```

## Round 1: revision  (completion_tokens=18471, generation_seconds=718.56, finish_reason=stop, think_closed=True, cached=False)

### Model reasoning

```text
Let me analyze the performance of each hypothesis and the mismatches to decide what to keep, fix, and potentially add.

**Key observations from the data:**

1. **MIXTURE'S WORST OBJECTS** - The biggest systematic errors:
   - `remote_shared_1`: predicted cupboard_k1, actually counter_k1 — 4x (day 4 06:00)
   - `pan_shared_1`: predicted sink_k1, actually counter_k1 — 4x (day 4 13:00)
   - `makeup_kit_mara`: predicted bathroom_shelf_ba1, actually kitchen_table_k1 — 4x (day 5 07:00)
   - `water_bottle_mara`: predicted kitchen_table_k1, actually counter_k1 — 3x (day 3 08:00)
   - `mug_mara`: predicted counter_k1, actually kitchen_table_k1 — 3x (day 4 07:00)
   - `bowl_shared_2`: predicted sink_k1, actually kitchen_table_k1 — 3x (day 5 07:00)
   - `pan_shared_1`: predicted sink_k1, actually kitchen_table_k1 — 3x (day 5 07:00)
   - `plate_shared_1`: predicted sink_k1, actually kitchen_table_k1 — 3x (day 6 07:00)
   - `book_mara`: predicted bookshelf_l1, actually ON_PERSON — 2x (day 3 00:00)
   - `medication_bottle_mara`: predicted counter_k1, actually bathroom_shelf_ba1 — 2x (day 3 05:00)
   - `wallet_mara`: predicted kitchen_table_k1, actually entry_hook_e1 — 2x (day 3 08:00)
   - `pen_mara`: predicted kitchen_table_k1, actually counter_k1 — 2x (day 3 18:00)

2. **RULES THAT HELD UP** - All hypotheses correctly predicted:
   - mug_mara -> counter_k1 during morning_routine (all 5 hypotheses)
   - water_bottle_mara -> counter_k1 during morning_routine (all 5)
   - glasses_mara -> kitchen_table_k1 during work (h1, h3, h5)
   - medication_bottle_mara -> counter_k1 during morning_routine (h1)
   - bowl_shared_2 -> kitchen_table_k1 during lunch (h1)

3. **RULES THAT FAILED** - None! This is good.

4. **Hypothesis weights:**
   - h2: 0.55 (highest) - hybrid WFH/office
   - h5: 0.17 - WFH + gym
   - h1: 0.13 - pure WFH
   - h3: 0.09 - evening shift
   - h4: 0.07 - part-time student

5. **Distinguishing predictions:**
   - h1: laptop at kitchen_table_k1 on weekday 14:00 - NOT YET TESTED
   - h2: laptop OUT_OF_HOUSE on weekday 14:00 - NOT YET TESTED
   - h3: keys OUT_OF_HOUSE on weekday 21:00 - NOT YET TESTED
   - h4: notebook OUT_OF_HOUSE on weekday 11:00 - NOT YET TESTED
   - h5: water_bottle OUT_OF_HOUSE on weekday 18:30 - CAME TRUE 0/1 times (FAILED)

So h5's distinguishing prediction FAILED. Water bottle was NOT out of house at 18:30 on a weekday. This weakens h5's gym hypothesis.

**Systematic errors to address:**

1. **remote_shared_1 at counter_k1 (not cupboard_k1)**: All hypotheses have remote at cupboard_k1 as rest. But it's being seen at counter_k1 4 times. This suggests the remote is used in the kitchen area, not just the living room. Maybe it's a kitchen radio remote or it gets moved to the counter.

2. **pan_shared_1 at counter_k1 (not sink_k1)**: All hypotheses have pan at sink_k1 as rest. But it's at counter_k1 4 times and kitchen_table_k1 3 times. The pan is more mobile - used for cooking and then set on counter or table.

3. **makeup_kit_mara at kitchen_table_k1 (not bathroom_shelf_ba1)**: All hypotheses have makeup at bathroom_shelf_ba1. But it's at kitchen_table_k1 4 times. This suggests Mara does her makeup at the kitchen table, not in the bathroom.

4. **water_bottle_mara at counter_k1 (not kitchen_table_k1)**: The rest location is kitchen_table_k1 in all hypotheses, but it's seen at counter_k1 3 times. However, the morning routine correctly puts it at counter_k1. The issue is the REST location - when not in morning routine, it should be at counter_k1, not kitchen_table_k1.

5. **mug_mara at kitchen_table_k1 (not counter_k1)**: Rest is counter_k1, but seen at kitchen_table_k1 3 times. This makes sense - during work, the mug moves to the kitchen table. The morning routine correctly puts it at counter_k1, but the rest location should perhaps be kitchen_table_k1 since that's where it is most of the day.

Wait, looking at per-object stats:
- mug_mara: mostly counter_k1 (4/7 sighted days); 5 receptacles
- water_bottle_mara: mostly kitchen_table_k1 (2/6 sighted days); 4 receptacles

Actually mug_mara is MOSTLY at counter_k1 (4/7 days). So the rest location of counter_k1 is correct. The 3 times at kitchen_table_k1 are during work hours when it's moved there. The issue is that the prediction is saying counter_k1 when it should be kitchen_table_k1 during work hours. But the work_day activity already moves it to kitchen_table_k1... Let me re-read.

The worst objects say: "mug_mara: predicted counter_k1, actually kitchen_table_k1 — 3x, e.g. day 4 07:00"

Day 4 07:00 is during morning_routine (7:00-8:00). The morning routine moves mug to counter_k1. But it was actually at kitchen_table_k1 at 07:00. Hmm, that's interesting. Maybe the morning routine starts a bit later, or the mug is at the table before being moved to the counter.

Actually wait - the morning routine starts at 7:00. At 07:00, the mug might still be at the kitchen_table_k1 from the night before (or from work the previous day), and hasn't been moved to counter yet. The "after: left" means the move happens when the activity starts. So at exactly 07:00, the mug might still be at its previous location.

But this is only 3 times out of 7 days, and the rule "held" at 0.68 on 9 sightings. So it's mostly working.

6. **bowl_shared_2, plate_shared_1, pan_shared_1 at kitchen_table_k1 (not sink_k1)**: These are dinner items. The rest location is sink_k1, but they're being seen at kitchen_table_k1. This suggests they're set out for meals and left on the table. The cooking_dinner activity in h5 moves them to kitchen_table_k1, but other hypotheses don't have this.

7. **book_mara ON_PERSON**: Seen 2 times at ON_PERSON. This suggests Mara carries the book with her (reading in bed, on the couch, etc.)

8. **medication_bottle_mara at bathroom_shelf_ba1 (not counter_k1)**: 2 times. The rest is counter_k1, but sometimes it's in the bathroom. Maybe she takes medication in the bathroom.

9. **wallet_mara at entry_hook_e1 (not kitchen_table_k1)**: Wait, the prediction says kitchen_table_k1? Let me re-read. "wallet_mara: predicted kitchen_table_k1, actually entry_hook_e1 — 2x". But in all hypotheses, wallet rest is entry_table_e1. Why would it predict kitchen_table_k1? 

Oh wait - maybe during the work_day activity, the wallet isn't moved, so it stays at its rest location (entry_table_e1). But the prediction says kitchen_table_k1... That's odd. Unless there's some other mechanism. Actually, looking more carefully, none of the hypotheses move the wallet to kitchen_table_k1. So why is the mixture predicting kitchen_table_k1?

Hmm, maybe I'm misreading. Let me look again: "wallet_mara: predicted kitchen_table_k1, actually entry_hook_e1 — 2x, e.g. day 3 08:00"

This is strange. The rest location for wallet in all hypotheses is entry_table_e1. No activity moves it to kitchen_table_k1. Unless the statistical system is doing something with the mixture that I'm not seeing. Or maybe I'm wrong about which hypothesis is making the prediction.

Actually, I think the "predicted" location is what the MIXTURE predicted, which is a weighted combination. If most hypotheses say entry_table_e1 but one says something else... No, all say entry_table_e1 for rest.

Wait, maybe the issue is timing. At 08:00, the morning routine is happening. The wallet isn't moved during morning routine in any hypothesis. So it should be at entry_table_e1. But the mixture predicted kitchen_table_k1? That doesn't make sense unless there's a bug or I'm misunderstanding the system.

Let me not overthink this and focus on the systematic fixes.

**Key systematic issues to fix:**

1. **Dinner/cooking items (pan, plate, bowl) should be at kitchen_table_k1 during evening, not sink_k1**: The rest location of sink_k1 is wrong for when they're in use. They should be at kitchen_table_k1 during dinner.

2. **makeup_kit_mara should be at kitchen_table_k1, not bathroom_shelf_ba1**: Mara does makeup at the kitchen table.

3. **remote_shared_1 should be at counter_k1, not cupboard_k1**: Or at least sometimes at counter_k1.

4. **water_bottle_mara rest should be counter_k1, not kitchen_table_k1**: It's mostly at counter_k1 (well, actually the stats say mostly kitchen_table_k1 at 2/6... but the morning routine puts it at counter_k1). Actually the stats say "mostly kitchen_table_k1 (2/6 sighted days)" - that's only 2 out of 6. It has 4 distinct receptacles. The morning routine correctly puts it at counter_k1. The issue is the REST location when not in any activity.

Wait, let me re-read the stats: "water_bottle_mara: mostly kitchen_table_k1 (2/6 sighted days); 4 receptacles; unseen 2 days". So on 2 of 6 sighted days it was at kitchen_table_k1. On other days it was elsewhere. The morning routine puts it at counter_k1. The worst object says it was predicted at kitchen_table_k1 but actually at counter_k1 3 times. So the rest location of kitchen_table_k1 is wrong - it should be counter_k1.

5. **h5's gym prediction FAILED**: Water bottle was NOT out of house at 18:30. This significantly weakens h5. I should modify h5 to remove or weaken the gym component, or change the distinguishing prediction.

**What to do with each hypothesis:**

- **h1 (pure WFH, weight 0.13)**: Keep. Fix rest locations for the systematic errors. The distinguishing prediction (laptop at kitchen_table_k1) is untested.

- **h2 (hybrid WFH/office, weight 0.55)**: Keep as top hypothesis. Fix rest locations. The distinguishing prediction (laptop OUT_OF_HOUSE) is untested.

- **h3 (evening shift, weight 0.09)**: Keep. Fix rest locations. The distinguishing prediction (keys OUT_OF_HOUSE at 21:00) is untested.

- **h4 (part-time student, weight 0.07)**: Keep. Fix rest locations. The distinguishing prediction (notebook OUT_OF_HOUSE at 11:00) is untested.

- **h5 (WFH + gym, weight 0.17)**: The gym prediction FAILED. I need to revise this. The distinguishing prediction came true 0/1 times. I should either:
  - Remove the gym and make it something else
  - Change the distinguishing prediction
  - Keep the gym but acknowledge it's weaker

Since h5's distinguishing prediction failed, I should change it. What could h5 be instead? Maybe the gym is real but the timing is wrong, or maybe it's not a gym at all. Let me think about what's unexplained.

Actually, looking at the data more carefully:
- yoga_mat_mara: mostly couch_l1 (5/5 sighted days) - always at couch
- The weekend_yoga activities in h1, h3, h4, h5 all move yoga_mat to bedroom_floor_b1, but it's ALWAYS at couch_l1. This is a systematic error!

Wait, the yoga mat is at couch_l1 5/5 days. None of the hypotheses have it at couch_l1 as rest - they all have it at couch_l1 actually. Let me re-check... Yes, all hypotheses have yoga_mat_mara rest at couch_l1. Good. But the weekend_yoga activities move it to bedroom_floor_b1. If it's always at couch_l1, then the yoga mat doesn't get moved to the bedroom floor. Maybe she does yoga on the couch? Or maybe the yoga activity is wrong.

Actually, the per-object stats say "yoga_mat_mara: mostly couch_l1 (5/5 sighted days); 1 receptacle; unseen 3 days". It's ALWAYS at couch_l1 when sighted. So the weekend_yoga activity that moves it to bedroom_floor_b1 is wrong. She either doesn't do yoga, or she does it on the couch, or the mat stays on the couch.

This is a systematic error across all hypotheses! But it's a minor one (the mat is only sighted 5 days and always at couch).

Let me focus on the bigger issues.

**Revised plan:**

For ALL hypotheses, fix these rest locations:
- `remote_shared_1`: change from cupboard_k1 to counter_k1 (seen at counter 4x vs cupboard 3x)
- `pan_shared_1`: change from sink_k1 to counter_k1 (seen at counter 2/7, kitchen_table 3x in worst objects... actually stats say "mostly counter_k1 (2/7 sighted days); 4 receptacles")
- `makeup_kit_mara`: change from bathroom_shelf_ba1 to kitchen_table_k1 (seen at kitchen_table 4x in worst objects)
- `water_bottle_mara`: change from kitchen_table_k1 to counter_k1 (seen at counter 3x in worst objects, and morning routine puts it there)
- `bowl_shared_2`: change from sink_k1 to kitchen_table_k1 (seen at kitchen_table 3x in worst objects)
- `plate_shared_1`: change from sink_k1 to kitchen_table_k1 (seen at kitchen_table 3x in worst objects)
- `book_mara`: add ON_PERSON as a possibility, or change rest to... hmm, it's mostly bookshelf_l1 (2/6) with 3 receptacles. The ON_PERSON sightings are only 2. Maybe keep bookshelf but note it can be ON_PERSON.
- `medication_bottle_mara`: keep counter_k1 as rest (it held up in morning routine), but the 2 times at bathroom_shelf_ba1 suggest she sometimes takes it in the bathroom.
- `wallet_mara`: The worst object says predicted kitchen_table_k1, actually entry_hook_e1. But rest is entry_table_e1. The entry_hook_e1 is where jacket and backpack are. Maybe wallet goes on the hook too? Or maybe this is a timing issue. I'll keep entry_table_e1 as rest.
- `pen_mara`: predicted kitchen_table_k1, actually counter_k1 2x. Rest is kitchen_table_k1. Maybe change to counter_k1? Stats say "mostly kitchen_table_k1 (4/7 sighted days)". So kitchen_table is still the mode. The 2 times at counter might be during specific activities. I'll keep kitchen_table_k1.

For h5 specifically:
- The gym prediction FAILED. I need to change the distinguishing prediction.
- What if h5 is actually about a different evening activity? Maybe she goes for a walk, or has a social evening?
- Or maybe the gym is real but at a different time?
- Since the prediction failed, I should change h5's distinguishing prediction to something else that's testable.
- Actually, let me reconsider h5. The weight is 0.17, second highest. The gym component is what distinguishes it. If the gym prediction failed, maybe I should change h5 to be about something else entirely.

What's unexplained by the other 4 hypotheses?
- h1: pure WFH
- h2: hybrid WFH/office (2 days office)
- h3: evening shift
- h4: part-time student (2 days campus)

What if h5 is: Mara has a regular evening social/friend activity (dinner out, etc.) 2-3x per week? This would explain why sometimes items go out in the evening but not for work.

Or: What if h5 is about a cooking/baking hobby? She spends evenings cooking elaborate meals, which would explain why pans, plates, bowls are out on the counter/table during evening hours.

Actually, looking at the data again:
- pan_shared_1: 4 distinct receptacles, mostly counter_k1 (2/7)
- plate_shared_1: 4 distinct receptacles, mostly sink_k1 (2/7)
- bowl_shared_2: 3 distinct receptacles, mostly sink_k1 (4/7)

The cooking items are very mobile. This suggests active cooking happens regularly.

Let me make h5 about a "cooking enthusiast" who spends significant time cooking in the evening, which explains the mobile kitchen items. The distinguishing prediction could be about a cooking item being at the counter during evening hours.

Actually, I think the simplest fix for h5 is:
- Remove the gym (it failed)
- Replace with a "cooking_dinner" focus that's more prominent
- New distinguishing prediction: pan_shared_1 is at counter_k1 on a weekday at 19:00 (during cooking)

Wait, but h5 already has cooking_dinner. Let me restructure h5 to be primarily about cooking/food preparation as the main evening activity, with the distinguishing prediction being about a cooking item.

Let me also reconsider: the "distinguishing_prediction came true 0/1 times" for h5 means the water bottle was NOT out of house at 18:30. This could mean:
1. No gym at all
2. Gym at a different time
3. Gym but water bottle stays home

I'll go with option 1: remove the gym, make h5 about cooking/food prep as the main distinguishing feature.

**New distinguishing prediction for h5**: pan_shared_1 is at counter_k1 on a weekday at 19:00 because she is cooking dinner.

This is testable and different from the other hypotheses (which don't specifically predict pan at counter during evening).

Actually wait - h5 already has cooking_dinner that moves pan to counter_k1. So the distinguishing prediction would be testing that existing rule. That's fine - it makes h5's cooking component the key differentiator.

Let me also think about whether to add a 6th hypothesis. The systematic unexplained things:
- makeup_kit at kitchen_table (all hypotheses had it at bathroom) - this is a fix, not a new hypothesis
- remote at counter (all had it at cupboard) - fix
- book ON_PERSON - minor, 2 sightings
- The yoga mat always at couch - minor fix

I don't think there's a systematic pattern that requires a new hypothesis. The fixes to rest locations and h5's gym removal should address the main issues. I'll stick with 5 hypotheses.

Let me now write the revised hypotheses:

**Common rest location fixes (applied to all):**
- remote_shared_1: cupboard_k1 → counter_k1
- pan_shared_1: sink_k1 → counter_k1
- makeup_kit_mara: bathroom_shelf_ba1 → kitchen_table_k1
- water_bottle_mara: kitchen_table_k1 → counter_k1
- bowl_shared_2: sink_k1 → kitchen_table_k1 (hmm, but stats say mostly sink_k1 4/7... let me reconsider)

Wait, bowl_shared_2: "mostly sink_k1 (4/7 sighted days); 3 receptacles". So it IS mostly at sink_k1. But the worst objects say it was predicted at sink_k1 but actually at kitchen_table_k1 3 times. So on 3 of 7 days it was at kitchen_table_k1. The mode is still sink_k1. Maybe I should keep sink_k1 as rest but add a dinner activity that moves it to kitchen_table_k1.

Actually, looking at h1's lunch activity: "bowl_shared_2 -> kitchen_table_k1, sometimes, after left" with 0.54 on 3 sightings. This held up. So the lunch activity correctly predicts it at the table during lunch. The issue is that OUTSIDE of lunch, the rest location should account for it being at the table sometimes.

Hmm, but the rest location is where it is when NO activity is active. If it's at kitchen_table_k1 3 times and those times are during dinner (not lunch), then I need a dinner activity. Let me add a dinner/cooking activity to hypotheses that don't have one.

Actually, let me reconsider. The worst objects show:
- bowl_shared_2: predicted sink_k1, actually kitchen_table_k1 — 3x, e.g. day 5 07:00

Day 5 07:00 is MORNING! Not dinner. So the bowl is at the kitchen table in the morning. This is strange. Maybe it's a breakfast bowl that's left on the table overnight? Or maybe she eats breakfast at the kitchen table.

Similarly:
- pan_shared_1: predicted sink_k1, actually kitchen_table_k1 — 3x, e.g. day 5 07:00

Pan at kitchen table at 7 AM? That's weird. Unless it's being used for breakfast cooking and set on the table.

- plate_shared_1: predicted sink_k1, actually kitchen_table_k1 — 3x, e.g. day 6 07:00

Plate at kitchen table at 7 AM. Same pattern.

So there's a MORNING pattern where cooking/dining items are at the kitchen_table_k1. This suggests breakfast is prepared and eaten at the kitchen table, and the items are left there.

This is a systematic pattern! All hypotheses have morning_routine at 7:00-8:00, but none of them move cooking items to the kitchen table. I should add breakfast items to the morning routine or add a breakfast activity.

Let me add to morning_routine (or create a breakfast activity):
- bowl_shared_2 → kitchen_table_k1 (sometimes)
- plate_shared_1 → kitchen_table_k1 (sometimes)  
- pan_shared_1 → counter_k1 (sometimes, for cooking)

Actually, the pan at kitchen_table_k1 is weird. Maybe it's at counter_k1 for cooking and then set on the table? Or maybe the "kitchen_table_k1" sightings for the pan are actually during a different time.

Let me just fix the rest locations to match the modal location and add activities where needed:

For the morning breakfast pattern, I'll extend morning_routine or add a breakfast activity that moves:
- bowl_shared_2 → kitchen_table_k1
- plate_shared_1 → kitchen_table_k1
- pan_shared_1 → counter_k1 (for cooking, then maybe table)

And for the evening:
- pan_shared_1 → counter_k1 (cooking)
- plate_shared_1 → kitchen_table_k1 (dinner)
- bowl_shared_2 → kitchen_table_k1 (dinner)

Let me restructure. I'll add a "breakfast" activity to all hypotheses (or extend morning_routine) and a "dinner" activity where missing.

Actually, to keep things manageable, let me:
1. Extend morning_routine to include breakfast items at kitchen_table_k1
2. Add/keep a dinner activity with cooking items
3. Fix rest locations to match modal locations

Let me finalize my changes:

**Rest location changes (all hypotheses):**
- remote_shared_1: cupboard_k1 → counter_k1
- pan_shared_1: sink_k1 → counter_k1  
- makeup_kit_mara: bathroom_shelf_ba1 → kitchen_table_k1
- water_bottle_mara: kitchen_table_k1 → counter_k1
- bowl_shared_2: keep sink_k1 (modal is 4/7)
- plate_shared_1: keep sink_k1 (modal is 2/7... actually "mostly sink_k1 (2/7 sighted days)" - that's only 2 out of 7. Hmm, but it has 4 distinct receptacles. Let me keep sink_k1 since it's listed as "mostly")

Actually wait: "plate_shared_1: mostly sink_k1 (2/7 sighted days); 4 receptacles; unseen 1 days". 2/7 is not really "mostly" but it's what the system reports. The worst objects show it at kitchen_table_k1 3 times. So maybe I should change rest to kitchen_table_k1? But 3/7 vs 2/7... it's close. Let me keep sink_k1 for now since the system says "mostly sink_k1".

Hmm, but the predictions are wrong 3 times for plate at kitchen_table. If I change rest to kitchen_table_k1, that would fix those 3 predictions but might break the 2 where it's at sink. Net gain of 1. I'll change it.

Similarly for bowl_shared_2: "mostly sink_k1 (4/7)" - 4/7 is solidly modal. Keep sink_k1. The 3 times at kitchen_table are during meals (activities should handle this).

For pan_shared_1: "mostly counter_k1 (2/7 sighted days); 4 receptacles". 2/7 is weak. Worst objects show counter_k1 4x and kitchen_table_k1 3x. So counter_k1 appears 4 times in worst objects. Let me change rest to counter_k1.

OK let me finalize:

**Rest changes:**
- remote_shared_1: → counter_k1
- pan_shared_1: → counter_k1
- makeup_kit_mara: → kitchen_table_k1
- water_bottle_mara: → counter_k1
- plate_shared_1: → kitchen_table_k1 (3x at table vs 2x at sink in the data)
- bowl_shared_2: keep sink_k1 (4/7 modal)
- mug_mara: keep counter_k1 (4/7 modal, and morning routine confirms)

**Activity changes:**
- Add breakfast to morning_routine or as separate activity: bowl_shared_2 → kitchen_table_k1, plate_shared_1 → kitchen_table_k1
- Keep/ensure dinner activity has cooking items
- Fix h5: remove gym, make cooking the main evening activity

**h5 revision:**
- Remove gym_session
- Make cooking_dinner more prominent (increase frequency, add more items)
- New distinguishing prediction: pan_shared_1 at counter_k1 on weekday at 19:00
- Rationale: Mara is a home cook who spends significant time preparing meals, especially in the evening. Kitchen items are frequently in use on the counter and table.

Let me write this out now. I'll be careful to keep the format exactly right.

Actually, let me reconsider the morning routine. The current morning_routine (7:00-8:00) moves mug and water_bottle to counter_k1. The breakfast items (bowl, plate) being at kitchen_table_k1 at 7:00 suggests they were left there from the previous night's dinner, OR breakfast is being prepared at 7:00.

If it's leftover from dinner, then the rest location should be kitchen_table_k1 (they're left on the table overnight). If it's breakfast being prepared, then I need a breakfast activity.

Given that plate_shared_1 is at kitchen_table_k1 at 7 AM on day 6, and bowl_shared_2 at kitchen_table_k1 at 7 AM on day 5, I think these are dinner items left on the table overnight. So the rest location for plate_shared_1 should be kitchen_table_k1 (left from dinner), and bowl_shared_2... well, bowl is mostly at sink (4/7), so maybe it gets washed but the plate doesn't?

This is getting complicated. Let me simplify:
- plate_shared_1 rest: kitchen_table_k1 (left from dinner)
- bowl_shared_2 rest: sink_k1 (washed and put away, but sometimes left on table)
- pan_shared_1 rest: counter_k1 (set on counter after cooking)

And I'll add a "dinner" activity to hypotheses that don't have one, which moves these items to the table/counter.

For the morning, I'll add to morning_routine:
- plate_shared_1 → kitchen_table_k1 (chance: sometimes, after: left) - this represents it being at the table from the night before
- Actually no, if rest is kitchen_table_k1, then it's already there. The morning routine doesn't need to move it.

OK I think the cleanest solution is:
- Set rest locations to where items are when NOT in an activity
- Add activities that move items during specific times
- The rest location is the "default" when no activity is active

So:
- plate_shared_1 rest: kitchen_table_k1 (it's left on the table after dinner, and is there in the morning)
- bowl_shared_2 rest: sink_k1 (it gets washed and put in sink, but during meals it's at table)
- pan_shared_1 rest: counter_k1 (set on counter after use)

And activities:
- morning_routine: add plate_shared_1 → kitchen_table_k1 (sometimes) to represent breakfast
- dinner/cooking: move pan to counter, plate/bowl to table

Let me write the final version now. I'll keep it focused and make the changes clear.

One more thing: the book_mara ON_PERSON issue. 2 sightings at ON_PERSON. The rest is bookshelf_l1 (2/6 sighted days). I could add a "reading" activity where the book is ON_PERSON, or just note it. Since it's only 2 sightings, I'll add a small activity or just leave it. Actually, let me add a "reading" activity to one or two hypotheses where the book is ON_PERSON in the evening.

Actually, to keep things simple and not over-engineer, I'll just note in the rationale that the book is sometimes carried. The 2 sightings aren't enough to warrant a whole new activity.

Let me write the final JSON now.
```

### Model output — hypotheses

### hyp1 — Mara is a WFH professional who almost never leaves the house. Kitchen table is her permanent office and dining surface; counter is her kitchen staging area. She does her makeup at the kitchen table (not bathroom). Dinner items are left on the table overnight. Keys, jacket, backpack rarely seen because she stays home.

*Distinguishing prediction:* laptop_mara remains at kitchen_table_k1 on a weekday at 14:00 because she never leaves for work
  (checkable form: laptop_mara at kitchen_table_k1, weekday, 14.0h)

*Rest entries:* 35 — medication_bottle_mara→counter_k1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→cupboard_k1, remote_shared_1→counter_k1 …

- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - medication_bottle_mara → counter_k1 (usually, left)
  - plate_shared_1 → kitchen_table_k1 (sometimes, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
- **work_day** (weekday, 5×/week, 9.0h for 8.0h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - charger_mara → kitchen_table_k1 (usually, left)
  - headphones_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
  - phone_mara → kitchen_table_k1 (sometimes, left)
  - makeup_kit_mara → kitchen_table_k1 (sometimes, left)
- **lunch** (both, 7×/week, 12.5h for 1.0h)
  - plate_shared_2 → kitchen_table_k1 (usually, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
  - water_bottle_mara → kitchen_table_k1 (usually, left)
- **evening_dinner** (both, 7×/week, 18.5h for 1.5h)
  - pan_shared_1 → counter_k1 (usually, left)
  - plate_shared_1 → kitchen_table_k1 (usually, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
- **evening_relax** (both, 7×/week, 20.0h for 3.0h)
  - remote_shared_1 → counter_k1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
  - book_mara → ON_PERSON (sometimes, left)
- **weekend_yoga** (weekend, 2×/week, 9.0h for 1.0h)
  - yoga_mat_mara → couch_l1 (usually, returned)
  - headphones_mara → couch_l1 (sometimes, returned)
  - water_bottle_mara → couch_l1 (sometimes, returned)

### hyp2 — Mara has a hybrid schedule: WFH Mon/Wed/Fri but goes to a shared office Tue/Thu. Laptop and work kit go with her on office days; on WFH days everything stays at kitchen table. She does makeup at the kitchen table. Dinner items are left on the table overnight. Remote is kept at the counter, not the cupboard.

*Distinguishing prediction:* laptop_mara is OUT_OF_HOUSE on a weekday at 14:00 because she is at her shared office
  (checkable form: laptop_mara at OUT_OF_HOUSE, weekday, 14.0h)

*Rest entries:* 35 — medication_bottle_mara→counter_k1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→cupboard_k1, remote_shared_1→counter_k1 …

- **office_out** (weekday, 2×/week, 8.5h for 0.5h)
  - laptop_mara → OUT_OF_HOUSE (usually, left)
  - backpack_mara → OUT_OF_HOUSE (usually, left)
  - keys_mara → OUT_OF_HOUSE (almost_always, left)
  - wallet_mara → OUT_OF_HOUSE (almost_always, left)
  - phone_mara → OUT_OF_HOUSE (usually, left)
  - charger_mara → OUT_OF_HOUSE (usually, left)
- **office_home** (weekday, 2×/week, 17.0h for 0.5h)
  - laptop_mara → kitchen_table_k1 (usually, returned)
  - backpack_mara → entry_hook_e1 (usually, returned)
  - keys_mara → entry_table_e1 (almost_always, returned)
  - wallet_mara → entry_table_e1 (almost_always, returned)
  - phone_mara → nightstand_b1 (usually, returned)
  - charger_mara → kitchen_table_k1 (usually, returned)
- **wfh_day** (weekday, 3×/week, 9.0h for 8.0h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - charger_mara → kitchen_table_k1 (usually, left)
  - headphones_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
  - makeup_kit_mara → kitchen_table_k1 (sometimes, left)
- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - plate_shared_1 → kitchen_table_k1 (sometimes, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
- **evening_dinner** (both, 7×/week, 18.5h for 1.5h)
  - pan_shared_1 → counter_k1 (usually, left)
  - plate_shared_1 → kitchen_table_k1 (usually, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
- **evening_relax** (both, 7×/week, 20.0h for 3.0h)
  - remote_shared_1 → counter_k1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
  - book_mara → ON_PERSON (sometimes, left)

### hyp3 — Mara works an evening shift (16:00-23:30). She is home all day using the kitchen table for personal work/study and doing makeup there, then leaves in the late afternoon. Laptop stays home because her job doesn't require it. Dinner items are left on the table; remote is at the counter. Keys and wallet go out with her.

*Distinguishing prediction:* keys_mara is OUT_OF_HOUSE on a weekday at 21:00 because she is at her evening shift
  (checkable form: keys_mara at OUT_OF_HOUSE, weekday, 21.0h)

*Rest entries:* 35 — medication_bottle_mara→counter_k1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→cupboard_k1, remote_shared_1→counter_k1 …

- **daytime_work** (weekday, 5×/week, 9.0h for 6.5h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - notebook_mara → kitchen_table_k1 (sometimes, left)
  - makeup_kit_mara → kitchen_table_k1 (sometimes, left)
- **shift_out** (weekday, 5×/week, 15.5h for 0.5h)
  - keys_mara → OUT_OF_HOUSE (almost_always, left)
  - wallet_mara → OUT_OF_HOUSE (almost_always, left)
  - jacket_mara → OUT_OF_HOUSE (usually, left)
  - phone_mara → OUT_OF_HOUSE (usually, left)
  - backpack_mara → OUT_OF_HOUSE (sometimes, left)
- **shift_home** (weekday, 5×/week, 23.5h for 0.5h)
  - keys_mara → entry_table_e1 (almost_always, returned)
  - wallet_mara → entry_table_e1 (almost_always, returned)
  - jacket_mara → entry_hook_e1 (usually, returned)
  - phone_mara → nightstand_b1 (usually, returned)
  - backpack_mara → entry_hook_e1 (sometimes, returned)
- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - plate_shared_1 → kitchen_table_k1 (sometimes, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
- **evening_relax** (both, 7×/week, 20.0h for 3.0h)
  - remote_shared_1 → counter_k1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
  - book_mara → ON_PERSON (sometimes, left)
- **weekend_yoga** (weekend, 2×/week, 10.0h for 1.0h)
  - yoga_mat_mara → couch_l1 (usually, returned)
  - headphones_mara → couch_l1 (usually, returned)
  - water_bottle_mara → couch_l1 (usually, returned)

### hyp4 — Mara is a part-time student who studies at home most days but goes to campus twice a week (Mon/Wed) for in-person lectures. On campus days she takes notebook, pen, and laptop; on other days everything stays at the kitchen table. She does makeup at the kitchen table. Dinner items left on table overnight; remote at counter.

*Distinguishing prediction:* notebook_mara is OUT_OF_HOUSE on a weekday at 11:00 because she is in a campus lecture
  (checkable form: notebook_mara at OUT_OF_HOUSE, weekday, 11.0h)

*Rest entries:* 35 — medication_bottle_mara→counter_k1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→cupboard_k1, remote_shared_1→counter_k1 …

- **campus_out** (weekday, 2×/week, 8.5h for 0.5h)
  - notebook_mara → OUT_OF_HOUSE (almost_always, left)
  - pen_mara → OUT_OF_HOUSE (almost_always, left)
  - laptop_mara → OUT_OF_HOUSE (usually, left)
  - backpack_mara → OUT_OF_HOUSE (usually, left)
  - keys_mara → OUT_OF_HOUSE (almost_always, left)
  - wallet_mara → OUT_OF_HOUSE (almost_always, left)
- **campus_return** (weekday, 2×/week, 14.0h for 0.5h)
  - notebook_mara → kitchen_table_k1 (almost_always, returned)
  - pen_mara → kitchen_table_k1 (almost_always, returned)
  - laptop_mara → kitchen_table_k1 (usually, returned)
  - backpack_mara → entry_hook_e1 (usually, returned)
  - keys_mara → entry_table_e1 (almost_always, returned)
  - wallet_mara → entry_table_e1 (almost_always, returned)
- **home_study** (weekday, 3×/week, 10.0h for 5.0h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - notebook_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - makeup_kit_mara → kitchen_table_k1 (sometimes, left)
- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - plate_shared_1 → kitchen_table_k1 (sometimes, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
- **evening_dinner** (both, 7×/week, 18.5h for 1.5h)
  - pan_shared_1 → counter_k1 (usually, left)
  - plate_shared_1 → kitchen_table_k1 (usually, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
- **evening_relax** (both, 7×/week, 20.0h for 3.0h)
  - remote_shared_1 → counter_k1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
  - book_mara → ON_PERSON (sometimes, left)
- **weekend_yoga** (weekend, 2×/week, 9.5h for 1.0h)
  - yoga_mat_mara → couch_l1 (usually, returned)
  - water_bottle_mara → couch_l1 (usually, returned)

### hyp5 — Mara works from home and is an avid home cook. She spends significant time preparing meals in the evening (18:00-20:00), which is why pans, plates, and bowls are frequently on the counter and kitchen table. Her laptop stays at the kitchen table throughout the day. The gym hypothesis was falsified (water bottle never seen out of house at 18:30); the distinguishing feature is her cooking routine, not exercise.

*Distinguishing prediction:* pan_shared_1 is at counter_k1 on a weekday at 19:00 because she is actively cooking dinner
  (checkable form: pan_shared_1 at counter_k1, weekday, 19.0h)

*Rest entries:* 35 — medication_bottle_mara→counter_k1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→cupboard_k1, remote_shared_1→counter_k1 …

- **work_day** (weekday, 5×/week, 9.0h for 7.0h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - charger_mara → kitchen_table_k1 (usually, left)
  - headphones_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
  - phone_mara → kitchen_table_k1 (sometimes, left)
  - makeup_kit_mara → kitchen_table_k1 (sometimes, left)
- **cooking_dinner** (both, 7×/week, 18.0h for 2.0h)
  - pan_shared_1 → counter_k1 (usually, left)
  - pot_shared_1 → counter_k1 (usually, left)
  - plate_shared_1 → kitchen_table_k1 (usually, left)
  - bowl_shared_2 → kitchen_table_k1 (usually, left)
  - bowl_shared_1 → kitchen_table_k1 (sometimes, left)
- **evening_tv** (both, 7×/week, 20.0h for 2.5h)
  - remote_shared_1 → counter_k1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
  - book_mara → ON_PERSON (sometimes, left)
- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - plate_shared_1 → kitchen_table_k1 (sometimes, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
- **weekend_yoga** (weekend, 2×/week, 9.0h for 1.0h)
  - yoga_mat_mara → couch_l1 (usually, returned)
  - headphones_mara → couch_l1 (usually, returned)
  - water_bottle_mara → couch_l1 (usually, returned)

<details><summary>raw JSON</summary>

```json
{
 "hypotheses": [
  {
   "hypothesis_id": "h1",
   "rationale": "Mara is a WFH professional who almost never leaves the house. Kitchen table is her permanent office and dining surface; counter is her kitchen staging area. She does her makeup at the kitchen table (not bathroom). Dinner items are left on the table overnight. Keys, jacket, backpack rarely seen because she stays home.",
   "distinguishing_prediction": "laptop_mara remains at kitchen_table_k1 on a weekday at 14:00 because she never leaves for work",
   "distinguishing_check": {
    "target": "laptop_mara",
    "at": "kitchen_table_k1",
    "days": "weekday",
    "hour": 14.0
   },
   "activities": [
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "medication_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "work_day",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 9.0,
     "duration_h": 8.0,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "charger_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "headphones_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "phone_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "makeup_kit_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "lunch",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 12.5,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "plate_shared_2",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_dinner",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 18.5,
     "duration_h": 1.5,
     "moves": [
      {
       "target": "pan_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_relax",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 20.0,
     "duration_h": 3.0,
     "moves": [
      {
       "target": "remote_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "tablet_mara",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "blanket_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "book_mara",
       "to": "ON_PERSON",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "weekend_yoga",
     "days": "weekend",
     "frequency_per_week": 2,
     "start_hour": 9.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "yoga_mat_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "headphones_mara",
       "to": "couch_l1",
       "chance": "sometimes",
       "after": "returned"
      },
      {
       "target": "water_bottle_mara",
       "to": "couch_l1",
       "chance": "sometimes",
       "after": "returned"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "kitchen_table_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "water_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  },
  {
   "hypothesis_id": "h2",
   "rationale": "Mara has a hybrid schedule: WFH Mon/Wed/Fri but goes to a shared office Tue/Thu. Laptop and work kit go with her on office days; on WFH days everything stays at kitchen table. She does makeup at the kitchen table. Dinner items are left on the table overnight. Remote is kept at the counter, not the cupboard.",
   "distinguishing_prediction": "laptop_mara is OUT_OF_HOUSE on a weekday at 14:00 because she is at her shared office",
   "distinguishing_check": {
    "target": "laptop_mara",
    "at": "OUT_OF_HOUSE",
    "days": "weekday",
    "hour": 14.0
   },
   "activities": [
    {
     "name": "office_out",
     "days": "weekday",
     "frequency_per_week": 2,
     "start_hour": 8.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "backpack_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "keys_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "wallet_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "phone_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "charger_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      }
     ]
    },
    {
     "name": "office_home",
     "days": "weekday",
     "frequency_per_week": 2,
     "start_hour": 17.0,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "backpack_mara",
       "to": "entry_hook_e1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "keys_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "wallet_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "phone_mara",
       "to": "nightstand_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "charger_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "returned"
      }
     ]
    },
    {
     "name": "wfh_day",
     "days": "weekday",
     "frequency_per_week": 3,
     "start_hour": 9.0,
     "duration_h": 8.0,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "charger_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "headphones_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "makeup_kit_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_dinner",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 18.5,
     "duration_h": 1.5,
     "moves": [
      {
       "target": "pan_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_relax",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 20.0,
     "duration_h": 3.0,
     "moves": [
      {
       "target": "remote_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "tablet_mara",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "blanket_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "book_mara",
       "to": "ON_PERSON",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "kitchen_table_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "water_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  },
  {
   "hypothesis_id": "h3",
   "rationale": "Mara works an evening shift (16:00-23:30). She is home all day using the kitchen table for personal work/study and doing makeup there, then leaves in the late afternoon. Laptop stays home because her job doesn't require it. Dinner items are left on the table; remote is at the counter. Keys and wallet go out with her.",
   "distinguishing_prediction": "keys_mara is OUT_OF_HOUSE on a weekday at 21:00 because she is at her evening shift",
   "distinguishing_check": {
    "target": "keys_mara",
    "at": "OUT_OF_HOUSE",
    "days": "weekday",
    "hour": 21.0
   },
   "activities": [
    {
     "name": "daytime_work",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 9.0,
     "duration_h": 6.5,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "notebook_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "makeup_kit_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "shift_out",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 15.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "keys_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "wallet_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "jacket_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "phone_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "backpack_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "shift_home",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 23.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "keys_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "wallet_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "jacket_mara",
       "to": "entry_hook_e1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "phone_mara",
       "to": "nightstand_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "backpack_mara",
       "to": "entry_hook_e1",
       "chance": "sometimes",
       "after": "returned"
      }
     ]
    },
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_relax",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 20.0,
     "duration_h": 3.0,
     "moves": [
      {
       "target": "remote_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "tablet_mara",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "blanket_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "book_mara",
       "to": "ON_PERSON",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "weekend_yoga",
     "days": "weekend",
     "frequency_per_week": 2,
     "start_hour": 10.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "yoga_mat_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "headphones_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "water_bottle_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "returned"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "kitchen_table_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "water_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  },
  {
   "hypothesis_id": "h4",
   "rationale": "Mara is a part-time student who studies at home most days but goes to campus twice a week (Mon/Wed) for in-person lectures. On campus days she takes notebook, pen, and laptop; on other days everything stays at the kitchen table. She does makeup at the kitchen table. Dinner items left on table overnight; remote at counter.",
   "distinguishing_prediction": "notebook_mara is OUT_OF_HOUSE on a weekday at 11:00 because she is in a campus lecture",
   "distinguishing_check": {
    "target": "notebook_mara",
    "at": "OUT_OF_HOUSE",
    "days": "weekday",
    "hour": 11.0
   },
   "activities": [
    {
     "name": "campus_out",
     "days": "weekday",
     "frequency_per_week": 2,
     "start_hour": 8.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "notebook_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "pen_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "laptop_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "backpack_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "keys_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      },
      {
       "target": "wallet_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "left"
      }
     ]
    },
    {
     "name": "campus_return",
     "days": "weekday",
     "frequency_per_week": 2,
     "start_hour": 14.0,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "notebook_mara",
       "to": "kitchen_table_k1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "pen_mara",
       "to": "kitchen_table_k1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "backpack_mara",
       "to": "entry_hook_e1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "keys_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "wallet_mara",
       "to": "entry_table_e1",
       "chance": "almost_always",
       "after": "returned"
      }
     ]
    },
    {
     "name": "home_study",
     "days": "weekday",
     "frequency_per_week": 3,
     "start_hour": 10.0,
     "duration_h": 5.0,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "notebook_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "makeup_kit_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_dinner",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 18.5,
     "duration_h": 1.5,
     "moves": [
      {
       "target": "pan_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_relax",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 20.0,
     "duration_h": 3.0,
     "moves": [
      {
       "target": "remote_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "tablet_mara",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "blanket_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "book_mara",
       "to": "ON_PERSON",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "weekend_yoga",
     "days": "weekend",
     "frequency_per_week": 2,
     "start_hour": 9.5,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "yoga_mat_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "water_bottle_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "returned"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "kitchen_table_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "water_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  },
  {
   "hypothesis_id": "h5",
   "rationale": "Mara works from home and is an avid home cook. She spends significant time preparing meals in the evening (18:00-20:00), which is why pans, plates, and bowls are frequently on the counter and kitchen table. Her laptop stays at the kitchen table throughout the day. The gym hypothesis was falsified (water bottle never seen out of house at 18:30); the distinguishing feature is her cooking routine, not exercise.",
   "distinguishing_prediction": "pan_shared_1 is at counter_k1 on a weekday at 19:00 because she is actively cooking dinner",
   "distinguishing_check": {
    "target": "pan_shared_1",
    "at": "counter_k1",
    "days": "weekday",
    "hour": 19.0
   },
   "activities": [
    {
     "name": "work_day",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 9.0,
     "duration_h": 7.0,
     "moves": [
      {
       "target": "laptop_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "charger_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "headphones_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "glasses_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "mug_mara",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "phone_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "makeup_kit_mara",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "cooking_dinner",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 18.0,
     "duration_h": 2.0,
     "moves": [
      {
       "target": "pan_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "pot_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "bowl_shared_1",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "evening_tv",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 20.0,
     "duration_h": 2.5,
     "moves": [
      {
       "target": "remote_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "tablet_mara",
       "to": "coffee_table_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "blanket_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "book_mara",
       "to": "ON_PERSON",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "morning_routine",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 7.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "mug_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "kitchen_table_k1",
       "chance": "sometimes",
       "after": "left"
      }
     ]
    },
    {
     "name": "weekend_yoga",
     "days": "weekend",
     "frequency_per_week": 2,
     "start_hour": 9.0,
     "duration_h": 1.0,
     "moves": [
      {
       "target": "yoga_mat_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "headphones_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "water_bottle_mara",
       "to": "couch_l1",
       "chance": "usually",
       "after": "returned"
      }
     ]
    }
   ],
   "rest": [
    {
     "target": "medication_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "lunchbox_mara",
     "at": "counter_k1"
    },
    {
     "target": "glasses_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "hairbrush_mara",
     "at": "bathroom_shelf_ba1"
    },
    {
     "target": "watering_can_mara",
     "at": "sink_k1"
    },
    {
     "target": "mug_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "pot_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "sink_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "kitchen_table_k1"
    },
    {
     "target": "tablet_mara",
     "at": "coffee_table_l1"
    },
    {
     "target": "suitcase_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "laundry_basket_mara",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "vacuum_cleaner_shared_1",
     "at": "bedroom_floor_b1"
    },
    {
     "target": "towel_mara",
     "at": "towel_rack_ba1"
    },
    {
     "target": "umbrella_mara",
     "at": "entry_floor_e1"
    },
    {
     "target": "book_mara",
     "at": "bookshelf_l1"
    },
    {
     "target": "phone_mara",
     "at": "nightstand_b1"
    },
    {
     "target": "keys_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "jacket_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "backpack_mara",
     "at": "entry_hook_e1"
    },
    {
     "target": "wallet_mara",
     "at": "entry_table_e1"
    },
    {
     "target": "blanket_mara",
     "at": "couch_l1"
    },
    {
     "target": "yoga_mat_mara",
     "at": "couch_l1"
    },
    {
     "target": "notebook_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pen_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "bowl_shared_1",
     "at": "entry_table_e1"
    },
    {
     "target": "mug_mara",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "makeup_kit_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "water_bottle_mara",
     "at": "counter_k1"
    },
    {
     "target": "laptop_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "charger_mara",
     "at": "kitchen_table_k1"
    },
    {
     "target": "headphones_mara",
     "at": "kitchen_table_k1"
    }
   ]
  }
 ]
}
```

</details>

## What the revision changed

- **hyp1:** rationale rewritten; rest moved for plate_shared_1, remote_shared_1, pan_shared_1, makeup_kit_mara, water_bottle_mara; activities added: evening_dinner; evening_relax.start_hour 19.5 → 20.0; moves added: book_mara→ON_PERSON, headphones_mara→couch_l1, makeup_kit_mara→kitchen_table_k1, pan_shared_1→counter_k1, plate_shared_1→kitchen_table_k1, remote_shared_1→counter_k1 …; moves removed: headphones_mara→bedroom_floor_b1, remote_shared_1→coffee_table_l1, water_bottle_mara→bedroom_floor_b1, yoga_mat_mara→bedroom_floor_b1
- **hyp2:** rationale rewritten; rest moved for plate_shared_1, remote_shared_1, pan_shared_1, makeup_kit_mara, water_bottle_mara; activities added: evening_dinner; evening_relax.start_hour 19.5 → 20.0; moves added: book_mara→ON_PERSON, bowl_shared_2→kitchen_table_k1, makeup_kit_mara→kitchen_table_k1, pan_shared_1→counter_k1, plate_shared_1→kitchen_table_k1, remote_shared_1→counter_k1; moves removed: remote_shared_1→coffee_table_l1
- **hyp3:** rationale rewritten; rest moved for plate_shared_1, remote_shared_1, pan_shared_1, makeup_kit_mara, water_bottle_mara; activities added: evening_relax; moves added: blanket_mara→couch_l1, book_mara→ON_PERSON, bowl_shared_2→kitchen_table_k1, headphones_mara→couch_l1, makeup_kit_mara→kitchen_table_k1, plate_shared_1→kitchen_table_k1 …; moves removed: headphones_mara→bedroom_floor_b1, water_bottle_mara→bedroom_floor_b1, yoga_mat_mara→bedroom_floor_b1
- **hyp4:** rationale rewritten; rest moved for plate_shared_1, remote_shared_1, pan_shared_1, makeup_kit_mara, water_bottle_mara; activities added: evening_dinner; evening_relax.start_hour 19.5 → 20.0; moves added: book_mara→ON_PERSON, bowl_shared_2→kitchen_table_k1, makeup_kit_mara→kitchen_table_k1, pan_shared_1→counter_k1, plate_shared_1→kitchen_table_k1, remote_shared_1→counter_k1 …; moves removed: remote_shared_1→coffee_table_l1, water_bottle_mara→bedroom_floor_b1, yoga_mat_mara→bedroom_floor_b1
- **hyp5:** rationale rewritten; rest moved for plate_shared_1, remote_shared_1, pan_shared_1, makeup_kit_mara, water_bottle_mara; activities removed: gym_session; cooking_dinner.start_hour 18.5 → 18.0; cooking_dinner.duration_h 1.0 → 2.0; cooking_dinner.frequency_per_week 5 → 7; moves added: book_mara→ON_PERSON, bowl_shared_2→kitchen_table_k1, headphones_mara→couch_l1, makeup_kit_mara→kitchen_table_k1, remote_shared_1→counter_k1, water_bottle_mara→couch_l1 …; moves removed: headphones_mara→bedroom_floor_b1, jacket_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, remote_shared_1→coffee_table_l1, water_bottle_mara→OUT_OF_HOUSE …

## Result

- valid hypotheses: 5
- outcome: revised
- generation seconds: 718.56
