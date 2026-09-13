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
  h1: weight 0.11 — distinguishing prediction not yet tested (no sightings of the target in that window)
  h2: weight 0.64 — distinguishing prediction not yet tested (no sightings of the target in that window)
  h3: weight 0.08 — distinguishing prediction not yet tested (no sightings of the target in that window)
  h4: weight 0.06 — distinguishing prediction not yet tested (no sightings of the target in that window)
  h5: weight 0.12 — distinguishing prediction came true 0/1 times

MIXTURE'S WORST OBJECTS — where it predicted vs where the object actually was:
  pan_shared_1: predicted sink_k1, actually counter_k1 — 4x, e.g. day 3 09:00
  bowl_shared_2: predicted sink_k1, actually kitchen_table_k1 — 4x, e.g. day 3 09:00
  makeup_kit_mara: predicted bathroom_shelf_ba1, actually kitchen_table_k1 — 4x, e.g. day 5 07:00
  remote_shared_1: predicted cupboard_k1, actually counter_k1 — 3x, e.g. day 4 06:00
  pan_shared_1: predicted sink_k1, actually kitchen_table_k1 — 3x, e.g. day 5 07:00
  plate_shared_1: predicted sink_k1, actually kitchen_table_k1 — 3x, e.g. day 6 07:00
  medication_bottle_mara: predicted counter_k1, actually bathroom_shelf_ba1 — 2x, e.g. day 3 05:00
  charger_mara: predicted ON_PERSON, actually kitchen_table_k1 — 2x, e.g. day 3 09:00
  pen_mara: predicted kitchen_table_k1, actually counter_k1 — 2x, e.g. day 3 18:00
  plate_shared_2: predicted kitchen_table_k1, actually counter_k1 — 2x, e.g. day 3 18:00
  jacket_mara: predicted entry_hook_e1, actually cupboard_k1 — 2x, e.g. day 3 18:00
  plate_shared_2: predicted counter_k1, actually kitchen_table_k1 — 2x, e.g. day 5 07:00

RULES THAT HELD UP (object was where the rule said, during its activity):
  h2/morning_routine: mug_mara -> counter_k1 held (0.74 on 8 sightings)
  h3/morning_routine: mug_mara -> counter_k1 held (0.74 on 8 sightings)
  h4/morning_routine: mug_mara -> counter_k1 held (0.74 on 8 sightings)
  h5/morning_routine: mug_mara -> counter_k1 held (0.74 on 8 sightings)
  h1/morning_routine: mug_mara -> counter_k1 held (0.73 on 8 sightings)
  h1/morning_routine: medication_bottle_mara -> counter_k1 held (0.59 on 6 sightings)
  h2/morning_routine: water_bottle_mara -> counter_k1 held (0.75 on 5 sightings)
  h3/morning_routine: water_bottle_mara -> counter_k1 held (0.75 on 5 sightings)
  h4/morning_routine: water_bottle_mara -> counter_k1 held (0.75 on 5 sightings)
  h5/morning_routine: water_bottle_mara -> counter_k1 held (0.75 on 5 sightings)
  h1/morning_routine: water_bottle_mara -> counter_k1 held (0.75 on 5 sightings)
  h1/work_day: glasses_mara -> kitchen_table_k1 held (0.74 on 4 sightings)
  h5/work_day: glasses_mara -> kitchen_table_k1 held (0.74 on 4 sightings)
  h3/daytime_work: glasses_mara -> kitchen_table_k1 held (0.74 on 4 sightings)
  h1/lunch: bowl_shared_2 -> kitchen_table_k1 held (0.54 on 3 sightings)

RULES THAT FAILED (object was elsewhere during the rule's activity):
  (none)

OBJECTS NO HYPOTHESIS COVERS (no rule and no rest entry mentions them), with what the sightings show:
  (none)

PER-OBJECT STATISTICS over days 0-7 (modal receptacle; share of sighted days it was there; distinct receptacles seen; days with no sighting):
  backpack_mara: mostly entry_hook_e1 (4/6 sighted days); 2 receptacles; unseen 2 days
  blanket_mara: mostly couch_l1 (7/7 sighted days); 1 receptacle; unseen 1 day
  book_mara: mostly bookshelf_l1 (2/5 sighted days); 3 receptacles; unseen 3 days
  bowl_shared_1: mostly entry_table_e1 (8/8 sighted days); 2 receptacles; unseen 0 days
  bowl_shared_2: mostly kitchen_table_k1 (2/7 sighted days); 3 receptacles; unseen 1 day
  charger_mara: mostly kitchen_table_k1 (5/5 sighted days); 2 receptacles; unseen 3 days
  glasses_mara: mostly kitchen_table_k1 (4/7 sighted days); 4 receptacles; unseen 1 day
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
  phone_mara: mostly nightstand_b1 (5/5 sighted days); 1 receptacle; unseen 3 days
  plate_shared_1: mostly kitchen_table_k1 (3/7 sighted days); 4 receptacles; unseen 1 day
  plate_shared_2: mostly counter_k1 (4/7 sighted days); 3 receptacles; unseen 1 day
  pot_shared_1: mostly dish_rack_k1 (4/7 sighted days); 2 receptacles; unseen 1 day
  remote_shared_1: mostly cupboard_k1 (3/7 sighted days); 4 receptacles; unseen 1 day
  suitcase_mara: mostly bedroom_floor_b1 (6/6 sighted days); 1 receptacle; unseen 2 days
  tablet_mara: mostly coffee_table_l1 (5/6 sighted days); 3 receptacles; unseen 2 days
  towel_mara: mostly towel_rack_ba1 (3/4 sighted days); 2 receptacles; unseen 4 days
  umbrella_mara: mostly entry_floor_e1 (4/5 sighted days); 2 receptacles; unseen 3 days
  vacuum_cleaner_shared_1: mostly bedroom_floor_b1 (6/7 sighted days); 2 receptacles; unseen 1 day
  wallet_mara: mostly entry_table_e1 (5/7 sighted days); 3 receptacles; unseen 1 day
  water_bottle_mara: mostly kitchen_table_k1 (1/6 sighted days); 4 receptacles; unseen 2 days
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
   "distinguishing_prediction": "laptop_mara is OUT_OF_HOUSE on a weekday at 14:00 because she is at her shared office on office days",
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
       "after": "returned"
      },
      {
       "target": "phone_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "keys_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "returned"
      },
      {
       "target": "jacket_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
       "after": "returned"
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

## Round 1: revision  (completion_tokens=19432, generation_seconds=756.85, finish_reason=stop, think_closed=True, cached=False)

### Model reasoning

```text
Let me analyze the performance of each hypothesis and the mismatches to decide what to keep, fix, and potentially add.

**Key observations from the data:**

1. **Mixture's worst objects:**
   - pan_shared_1: predicted sink_k1, actually counter_k1 (4x) and kitchen_table_k1 (3x) — The rest location of sink_k1 is wrong. Pan is mostly at counter_k1 (2/7) but seen in 4 receptacles.
   - bowl_shared_2: predicted sink_k1, actually kitchen_table_k1 (4x) — Rest at sink_k1 is wrong. Bowl_shared_2 is mostly at kitchen_table_k1 (2/7) but seen in 3 receptacles.
   - makeup_kit_mara: predicted bathroom_shelf_ba1, actually kitchen_table_k1 (4x) — Rest at bathroom_shelf_ba1 is wrong. Makeup kit is mostly at bathroom_shelf_ba1 (2/5) but seen in 3 receptacles.
   - remote_shared_1: predicted cupboard_k1, actually counter_k1 (3x) — Rest at cupboard_k1 is wrong. Remote is mostly at cupboard_k1 (3/7) but seen in 4 receptacles.
   - plate_shared_1: predicted sink_k1, actually kitchen_table_k1 (3x) — Wait, plate_shared_1 rest is at cupboard_k1 in all hypotheses. But the prediction says sink_k1. Let me re-read... Actually the "predicted" location comes from the mixture, not a single hypothesis. The mixture predicted sink_k1 for plate_shared_1. But in the hypotheses, plate_shared_1 rest is cupboard_k1. Hmm, but the worst objects say "predicted sink_k1" — this must be the mixture's overall prediction. Let me look more carefully.

   Actually wait - looking at the rest entries across all hypotheses:
   - pan_shared_1: rest at sink_k1 (all hypotheses)
   - bowl_shared_2: rest at sink_k1 (all hypotheses)
   - plate_shared_1: rest at cupboard_k1 (all hypotheses)
   - remote_shared_1: rest at cupboard_k1 (all hypotheses)
   - makeup_kit_mara: rest at bathroom_shelf_ba1 (all hypotheses)

   But the worst objects show:
   - pan_shared_1: predicted sink_k1, actually counter_k1 (4x) — matches the rest prediction being wrong
   - bowl_shared_2: predicted sink_k1, actually kitchen_table_k1 (4x) — matches
   - makeup_kit_mara: predicted bathroom_shelf_ba1, actually kitchen_table_k1 (4x) — matches
   - remote_shared_1: predicted cupboard_k1, actually counter_k1 (3x) — matches
   - plate_shared_1: predicted sink_k1, actually kitchen_table_k1 (3x) — Wait, plate_shared_1 rest is cupboard_k1, not sink_k1. But the prediction says sink_k1. This is confusing. Maybe the mixture weighted differently. Actually, looking at h5's cooking_dinner activity, it moves plate_shared_1 to kitchen_table_k1. And the rest is cupboard_k1. But the "predicted sink_k1" is strange. Unless there's some other factor. Let me not overthink this - the point is plate_shared_1 is actually at kitchen_table_k1 more often than predicted.

   Actually, re-reading: "plate_shared_1: predicted sink_k1, actually kitchen_table_k1 — 3x, e.g. day 6 07:00". The day 6 07:00 timing is during morning_routine. None of the hypotheses move plate_shared_1 during morning_routine. The rest location is cupboard_k1. So why is the prediction sink_k1? Maybe it's a mixture artifact. Regardless, the actual location is kitchen_table_k1, which contradicts all rest predictions.

   Wait - looking at per-object stats: plate_shared_1 is mostly kitchen_table_k1 (3/7 sighted days), 4 receptacles. So it's actually at kitchen_table_k1 more than anywhere else! The rest prediction of cupboard_k1 is wrong.

2. **What held up:**
   - mug_mara -> counter_k1 during morning_routine: held for ALL hypotheses (0.73-0.74)
   - water_bottle_mara -> counter_k1 during morning_routine: held for ALL (0.75)
   - medication_bottle_mara -> counter_k1 during morning_routine: held for h1 (0.59)
   - glasses_mara -> kitchen_table_k1 during work_day/daytime: held for h1, h3, h5 (0.74)
   - bowl_shared_2 -> kitchen_table_k1 during lunch: held for h1 (0.54)

3. **What failed (distinguishing predictions):**
   - h5: "distinguishing prediction came true 0/1 times" — water_bottle_mara was NOT at OUT_OF_HOUSE on a weekday at 18:30. This means the gym hypothesis is wrong or at least the water bottle doesn't go out.

4. **Per-object statistics that contradict rest locations:**
   - pan_shared_1: mostly counter_k1 (2/7), 4 receptacles — rest at sink_k1 is wrong
   - bowl_shared_2: mostly kitchen_table_k1 (2/7), 3 receptacles — rest at sink_k1 is wrong
   - plate_shared_1: mostly kitchen_table_k1 (3/7), 4 receptacles — rest at cupboard_k1 is wrong
   - remote_shared_1: mostly cupboard_k1 (3/7), 4 receptacles — rest at cupboard_k1 is partially right but it's also at counter_k1
   - makeup_kit_mara: mostly bathroom_shelf_ba1 (2/5), 3 receptacles — rest at bathroom_shelf_ba1 is partially right but it's also at kitchen_table_k1
   - water_bottle_mara: mostly kitchen_table_k1 (1/6), 4 receptacles — rest at kitchen_table_k1 is weakly supported
   - medication_bottle_mara: mostly bathroom_shelf_ba1 (4/7), 3 receptacles — rest at counter_k1 is wrong! It's mostly at bathroom_shelf_ba1.
   
   Wait, but the morning_routine rule says medication_bottle_mara -> counter_k1 held (0.59 on 6 sightings). So during morning routine it IS at counter_k1, but its REST location (when not in an activity) is bathroom_shelf_ba1. The rest should be bathroom_shelf_ba1, not counter_k1.

   - charger_mara: mostly kitchen_table_k1 (5/5), 2 receptacles — rest at kitchen_table_k1 is correct
   - laptop_mara: mostly kitchen_table_k1 (5/5), 1 receptacle — rest at kitchen_table_k1 is correct, and it's NEVER seen elsewhere. This strongly supports h1 (WFH, never leaves).
   - keys_mara: mostly entry_table_e1 (4/4), 1 receptacle — never seen out of house! This contradicts h2, h3, h4 which predict keys going OUT_OF_HOUSE.
   - jacket_mara: mostly entry_hook_e1 (4/5), 2 receptacles — the worst objects show it was predicted at entry_hook_e1 but actually at cupboard_k1 (2x). So it sometimes goes to cupboard_k1.
   - phone_mara: mostly nightstand_b1 (5/5), 1 receptacle — never seen at kitchen_table_k1 or OUT_OF_HOUSE. This contradicts h1's work_day move of phone to kitchen_table_k1, and h2/h3/h4/h5 predictions of phone going OUT_OF_HOUSE.
   - water_bottle_mara: mostly kitchen_table_k1 (1/6), 4 receptacles — very mobile, seen in 4 places. Rest at kitchen_table_k1 is weakly supported.
   - makeup_kit_mara: mostly bathroom_shelf_ba1 (2/5), 3 receptacles — but worst objects show it at kitchen_table_k1 4 times when predicted at bathroom_shelf_ba1.

5. **Critical findings:**
   - **laptop_mara**: 5/5 at kitchen_table_k1, 1 receptacle, unseen 3 days. NEVER out of house. This strongly supports h1 and contradicts h2 (office days), h4 (campus days).
   - **keys_mara**: 4/4 at entry_table_e1, 1 receptacle, unseen 4 days. NEVER out of house. This contradicts h2, h3, h4, h5 which all predict keys going OUT_OF_HOUSE.
   - **phone_mara**: 5/5 at nightstand_b1, 1 receptacle, unseen 3 days. NEVER at kitchen_table_k1 or OUT_OF_HOUSE. Contradicts h1 (phone to kitchen_table during work), h2/h3/h4/h5 (phone OUT_OF_HOUSE).
   - **jacket_mara**: 4/5 at entry_hook_e1, 2 receptacles. The second receptacle appears to be cupboard_k1 (from worst objects). Never OUT_OF_HOUSE. Contradicts h2, h3, h4, h5.
   - **backpack_mara**: 4/6 at entry_hook_e1, 2 receptacles, unseen 2 days. Never OUT_OF_HOUSE. Contradicts h2, h3, h4.
   - **wallet_mara**: 5/7 at entry_table_e1, 3 receptacles, unseen 1 day. Never OUT_OF_HOUSE. Contradicts h2, h3, h4, h5.

   This is a MASSIVE finding. The data shows Mara NEVER leaves the house during the observation period. No object is ever seen at OUT_OF_HOUSE. This kills h2 (office days), h3 (evening shift), h4 (campus), and h5 (gym).

   Wait, but h2 has weight 0.64! How can it have the highest weight if its core prediction (laptop OUT_OF_HOUSE) is never tested? The system says "distinguishing prediction not yet tested (no sightings of the target in that window)" for h1-h4. For h5, "distinguishing prediction came true 0/1 times."

   So the distinguishing checks haven't been triggered for h1-h4 because the specific day/hour combinations haven't been observed. But the per-object stats tell us a lot:
   - laptop_mara: 1 receptacle (kitchen_table_k1), never seen elsewhere → supports h1, contradicts h2/h4
   - keys_mara: 1 receptacle (entry_table_e1), never seen elsewhere → contradicts h2/h3/h4/h5
   - phone_mara: 1 receptacle (nightstand_b1), never seen elsewhere → contradicts h1 (phone to kitchen_table), h2/h3/h4/h5 (phone out)
   - jacket_mara: 2 receptacles (entry_hook_e1 + cupboard_k1), never OUT_OF_HOUSE → contradicts h2/h3/h4/h5
   - backpack_mara: 2 receptacles (entry_hook_e1 + ?), never OUT_OF_HOUSE → contradicts h2/h3/h4
   - wallet_mara: 3 receptacles (entry_table_e1 + 2 others), never OUT_OF_HOUSE → contradicts h2/h3/h4/h5

   The "unseen" days are important:
   - keys_mara: unseen 4 days (out of 7) — only seen 4 days, always at entry_table_e1
   - phone_mara: unseen 3 days — only seen 5 days, always at nightstand_b1
   - laptop_mara: unseen 3 days — only seen 5 days, always at kitchen_table_k1
   - jacket_mara: unseen 3 days — only seen 5 days
   - backpack_mara: unseen 2 days — only seen 6 days
   - wallet_mara: unseen 1 day — seen 7 days (wait, 5/7 sighted days, 3 receptacles, unseen 1 day)

   So the pattern is clear: Mara is home ALL the time. No object ever goes OUT_OF_HOUSE. The "unseen" days are probably when the robot's camera doesn't cover those areas, or the objects are in places not being monitored.

   Actually wait - "unseen" means no sighting that day. If keys are at entry_table_e1 and the camera sees them, they'd be sighted. If unseen, maybe the camera angle doesn't cover that spot on those days, or the robot wasn't active. This is a data collection issue, not evidence of absence.

   But the key point is: when these objects ARE sighted, they're ALWAYS at their "home" location. Never at OUT_OF_HOUSE, never at a second location (except jacket at cupboard_k1, and wallet at 3 locations).

   Let me reconsider. The "unseen" days might mean the robot simply didn't observe them (camera coverage, timing). The fact that when seen, they're always in one place, strongly suggests they don't move.

   **Revised understanding:**
   - Mara is a WFH worker who stays home essentially all day
   - Her work setup is at kitchen_table_k1 (laptop, charger, headphones, glasses, notebook, pen)
   - Phone stays at nightstand_b1 (NOT at kitchen table during work!)
   - Keys stay at entry_table_e1
   - Jacket stays at entry_hook_e1 (sometimes cupboard_k1)
   - Backpack stays at entry_hook_e1
   - Wallet stays at entry_table_e1
   - She never (or very rarely) leaves the house
   - Morning routine: mug, water bottle, medication at counter
   - Dishes: the rest locations need fixing
     - pan_shared_1: NOT at sink_k1, more at counter_k1
     - bowl_shared_2: NOT at sink_k1, more at kitchen_table_k1
     - plate_shared_1: NOT at cupboard_k1, more at kitchen_table_k1
     - remote_shared_1: at cupboard_k1 (3/7) but also counter_k1
     - makeup_kit_mara: at bathroom_shelf_ba1 (2/5) but also kitchen_table_k1
     - medication_bottle_mara: REST at bathroom_shelf_ba1 (4/7), not counter_k1

   **Now let me decide on the 5 hypotheses:**

   Given the data, the main axis of uncertainty is:
   1. Does Mara ever leave? (h1 says no, h2/h3/h4/h5 say yes)
   2. Where do dishes rest? (sink vs counter vs kitchen table)
   3. What's her daily structure?

   The data strongly supports "she stays home." But I need to keep 5 hypotheses that are genuinely different. Let me think about what's still uncertain:

   - h1 (pure WFH, never leaves): Strongly supported. Keep but fix rest locations.
   - h2 (hybrid office): Strongly contradicted (laptop never leaves, keys never leave). But it has weight 0.64 because its distinguishing prediction hasn't been tested. I should revise it significantly or change its core claim.
   - h3 (evening shift): Contradicted (keys never leave, jacket never leaves). 
   - h4 (part-time student/campus): Contradicted (laptop, notebook, pen never leave).
   - h5 (gym 3x/week): Distinguishing prediction FAILED (water_bottle not OUT_OF_HOUSE at 18:30).

   The problem is: if I just make all 5 say "she stays home," they become indistinguishable. I need to find genuine axes of variation that the data hasn't yet resolved.

   Let me think about what IS still uncertain:
   1. **Dish storage**: Where do plates, bowls, pans rest when not in use? The data shows:
      - pan_shared_1: counter_k1 (2/7), 4 receptacles
      - bowl_shared_2: kitchen_table_k1 (2/7), 3 receptacles
      - plate_shared_1: kitchen_table_k1 (3/7), 4 receptacles
      - plate_shared_2: counter_k1 (4/7), 3 receptacles
      - pot_shared_1: dish_rack_k1 (4/7), 2 receptacles
      - mug_shared_1: cupboard_k1 (7/7), 1 receptacle
      - bowl_shared_1: entry_table_e1 (8/8), 2 receptacles
      
      So dishes are scattered: some at counter, some at kitchen table, some at dish_rack, one at entry_table. This is unusual. Maybe she doesn't put dishes away neatly, or uses them as storage.

   2. **Phone location**: Always at nightstand_b1 (5/5). Never at kitchen table. This is a clear correction needed.

   3. **Medication bottle**: Rest at bathroom_shelf_ba1 (4/7), but during morning routine at counter_k1 (0.59). So it goes to counter in the morning and back to bathroom shelf.

   4. **Makeup kit**: bathroom_shelf_ba1 (2/5) but also kitchen_table_k1 (from worst objects, 4x). Maybe she does makeup at kitchen table?

   5. **Remote**: cupboard_k1 (3/7) but also counter_k1 (from worst objects). Maybe she uses it in the kitchen?

   6. **Does she EVER leave?** The data shows no object at OUT_OF_HOUSE. But "unseen" days could hide brief outings. However, the consistency of single-receptacle objects (laptop, keys, phone) strongly suggests she doesn't leave.

   7. **Water bottle**: Very mobile (4 receptacles, 1/6 at kitchen_table_k1). Where does it rest? It's at counter_k1 during morning routine. But its "mostly" location is kitchen_table_k1 with only 1/6. This is odd. Maybe it's on the counter most of the time but the "mostly" stat is misleading because of the 4 receptacles.

   Let me design 5 genuinely different hypotheses:

   **h1 (revised): Pure WFH, never leaves, organized kitchen**
   - Core: Mara works from home, never leaves. Dishes go to cupboard/dish_rack after use.
   - Distinguishing: laptop_mara at kitchen_table_k1 on weekday at 14:00 (same as before, still valid)
   - Fix: phone rest at nightstand_b1 (remove from work_day moves), medication rest at bathroom_shelf_ba1, pan rest at counter_k1 (not sink), bowl_shared_2 rest at kitchen_table_k1 (not sink), plate_shared_1 rest at kitchen_table_k1 (not cupboard)

   **h2 (revised): WFH with brief errands (grocery, pharmacy) 1-2x/week**
   - Core: She stays home most days but occasionally goes out for 1-2 hours (grocery store, pharmacy). Takes keys, wallet, phone, jacket.
   - Distinguishing: keys_mara OUT_OF_HOUSE on a weekday at 10:00 (brief errand)
   - This is different from h1 because she DOES leave sometimes, but rarely and briefly.
   - Actually, the data shows keys at entry_table_e1 4/4 sighted days, 1 receptacle, unseen 4 days. If she went out, we'd expect to see keys missing or at a different location. The "unseen 4 days" could be when she's out. But we can't confirm.
   - Hmm, but this is very similar to h1. The distinguishing test would be: on the 4 days keys are unseen, is she out? We can't tell from the data.
   - Let me think of a better axis...

   Actually, let me reconsider. The main uncertainties that remain:
   
   A) **Dish placement**: Where do used/clean dishes rest?
      - Option A: Cupboard (traditional)
      - Option B: Counter (staging area)
      - Option C: Kitchen table (used as surface)
      - Data suggests: mixed. Plate_shared_1 at kitchen_table, pan at counter, pot at dish_rack, mug at cupboard.
   
   B) **Phone location during work**: 
      - Option A: Nightstand (doesn't come to kitchen)
      - Option B: Kitchen table (works at kitchen table)
      - Data: Always nightstand_b1. Strongly supports A.
   
   C) **Does she leave at all?**
      - Option A: Never (pure WFH)
      - Option B: Rarely, briefly (errands)
      - Option C: Regularly (office/campus/shift)
      - Data: No evidence of leaving. Supports A, weakly B, contradicts C.
   
   D) **Makeup kit location**:
      - Option A: Bathroom shelf (rest)
      - Option B: Kitchen table (she does makeup there)
      - Data: 2/5 bathroom, 4x kitchen_table in worst objects. Supports B or mixed.
   
   E) **Water bottle rest location**:
      - Option A: Kitchen table
      - Option B: Counter
      - Option C: Very mobile, no fixed rest
      - Data: 1/6 kitchen_table, 4 receptacles. Very mobile.

   Let me design 5 hypotheses around these axes:

   **h1: Pure WFH, dishes in cupboard, phone at nightstand**
   - She never leaves. Dishes go to cupboard after washing. Phone stays at nightstand.
   - Distinguishing: laptop_mara at kitchen_table_k1, weekday, 14:00
   
   **h2: WFH with brief daily errand (30 min, 3x/week)**
   - She leaves briefly 3x/week for a quick errand (mail, pharmacy). Takes keys, wallet, phone, jacket. Everything else stays.
   - Distinguishing: keys_mara OUT_OF_HOUSE, weekday, 10:00
   - This is different from h1 because keys/phone/jacket are briefly absent.
   
   **h3: WFH, dishes on counter (staging), phone at nightstand**
   - She never leaves but doesn't put dishes away. Used dishes rest on counter. Phone at nightstand.
   - Distinguishing: plate_shared_1 at counter_k1, both days, 15:00 (afternoon, dishes from lunch still out)
   
   **h4: WFH, dishes on kitchen table, phone at nightstand, makeup at kitchen table**
   - She never leaves. Kitchen table is her "everything" surface - work, dishes, makeup. Phone at nightstand.
   - Distinguishing: makeup_kit_mara at kitchen_table_k1, both days, 08:00 (morning, before work)
   
   **h5: WFH with evening walk (30 min, 5x/week)**
   - She takes a daily evening walk. Takes phone, keys, water bottle. Everything else stays.
   - Distinguishing: water_bottle_mara OUT_OF_HOUSE, weekday, 18:30
   - Wait, this was the OLD h5 and it FAILED. The water bottle was NOT out at 18:30.
   - I should NOT keep this. Let me think of something else.

   Actually, let me reconsider h5. The old h5 (gym) failed. What else could explain the mobile water bottle and the 4 receptacles for several objects?

   **h5 (new): WFH, she has a "kitchen work" pattern where she moves between counter and kitchen table throughout the day, and objects follow her**
   - Objects are more mobile than a fixed-rest model predicts. The water bottle, plates, and bowls move between counter and kitchen table depending on what she's doing (cooking, eating, working).
   - Distinguishing: water_bottle_mara at counter_k1, weekday, 14:00 (during work, she's at counter not kitchen table)
   
   Hmm, but this is hard to distinguish from the others. Let me think differently.

   Actually, the key insight is: the data shows NO object ever at OUT_OF_HOUSE. All the "leaving" hypotheses (old h2, h3, h4, h5) are contradicted. But I need 5 DIFFERENT hypotheses. The remaining uncertainty is about WHERE things rest and the internal kitchen dynamics.

   Let me look at the per-object stats more carefully for the "mobile" objects:
   - pan_shared_1: counter_k1 (2/7), 4 receptacles, unseen 1 day
   - bowl_shared_2: kitchen_table_k1 (2/7), 3 receptacles, unseen 1 day
   - plate_shared_1: kitchen_table_k1 (3/7), 4 receptacles, unseen 1 day
   - plate_shared_2: counter_k1 (4/7), 3 receptacles, unseen 1 day
   - remote_shared_1: cupboard_k1 (3/7), 4 receptacles, unseen 1 day
   - water_bottle_mara: kitchen_table_k1 (1/6), 4 receptacles, unseen 2 days
   - mug_mara: counter_k1 (4/7), 5 receptacles, unseen 1 day
   - medication_bottle_mara: bathroom_shelf_ba1 (4/7), 3 receptacles, unseen 1 day
   - makeup_kit_mara: bathroom_shelf_ba1 (2/5), 3 receptacles, unseen 3 days
   - notebook_mara: kitchen_table_k1 (3/5), 4 receptacles, unseen 3 days
   - pen_mara: kitchen_table_k1 (4/7), 3 receptacles, unseen 1 day
   - glasses_mara: kitchen_table_k1 (4/7), 4 receptacles, unseen 1 day

   Objects with 4+ receptacles are genuinely mobile. The "mostly" location is just the mode.

   OK here's my revised plan:

   **h1: WFH, organized (dishes to cupboard/dish_rack, phone at nightstand)**
   - Dishes rest in cupboard or dish_rack
   - Phone at nightstand always
   - Medication at bathroom_shelf
   - Distinguishing: plate_shared_1 at cupboard_k1, both days, 16:00 (afternoon, dishes put away)

   **h2: WFH, dishes stay on counter (she doesn't put them away)**
   - Used dishes rest on counter_k1
   - Phone at nightstand
   - Distinguishing: plate_shared_1 at counter_k1, both days, 16:00

   **h3: WFH, kitchen table is the "dump" surface (dishes, makeup, random stuff)**
   - Dishes, makeup kit, and misc items rest at kitchen_table_k1
   - Phone at nightstand
   - Distinguishing: makeup_kit_mara at kitchen_table_k1, both days, 08:00

   **h4: WFH with a brief daily walk (keys+phone+water bottle out for 30 min, 5x/week)**
   - She goes for a short walk every day. Takes minimal items.
   - Distinguishing: keys_mara OUT_OF_HOUSE, weekday, 17:00
   - This is different from h1-h3 because objects are briefly absent.
   - But wait, the data shows keys at entry_table_e1 4/4 sighted days, 1 receptacle. If she walked at 17:00 and the robot saw keys at 16:50, they'd be at entry_table. If seen at 17:10, they'd be... not there? Or the robot doesn't see the entry area at that time?
   - Actually "unseen 4 days" for keys means on 4 of 7 days, keys were never sighted. If she's out on those days, that explains it. But it could also be camera coverage.
   - This hypothesis is testable: if keys are ever seen OUT_OF_HOUSE or if there's a pattern of keys being absent at specific times, it's supported.

   **h5: WFH, she works at the counter (not kitchen table) in the afternoon, moving her work setup**
   - In the morning she's at kitchen table, but in the afternoon she moves to the counter area. Laptop, charger, headphones move to counter.
   - Distinguishing: laptop_mara at counter_k1, weekday, 15:00
   
   Wait, but laptop_mara is 5/5 at kitchen_table_k1, 1 receptacle. It's NEVER seen at counter_k1. So this would be contradicted. Let me not do this.

   Let me reconsider h5. What's genuinely uncertain?

   Looking at the data again:
   - bowl_shared_1: entry_table_e1 (8/8), 2 receptacles — this is at the ENTRY table! Very unusual for a bowl.
   - remote_shared_1: cupboard_k1 (3/7), 4 receptacles — very mobile
   - water_bottle_mara: kitchen_table_k1 (1/6), 4 receptacles — very mobile, no clear home

   The bowl at entry_table is interesting. Maybe it's a decorative bowl or a pet bowl? Or maybe she uses the entry table as a staging area for things going in/out.

   For h5, let me focus on the "mobile objects" hypothesis:
   **h5: WFH, objects are highly mobile with no fixed rest (she moves things around the kitchen throughout the day)**
   - Water bottle, plates, bowls, and remote don't have a fixed home; they're wherever she last used them.
   - Distinguishing: water_bottle_mara at counter_k1, weekday, 14:00 (she's at counter during work, not kitchen table)

   Actually, I realize I should be more careful. Let me look at what the "distinguishing" predictions need to be:
   - They should be testable in the near future
   - They should differentiate the hypotheses
   - They should be specific (day, hour, location)

   Let me finalize:

   **h1: WFH, dishes to cupboard, organized**
   - Rest: plates/bowls/pans → cupboard_k1 or dish_rack_k1
   - Phone → nightstand_b1
   - Medication → bathroom_shelf_ba1
   - Distinguishing: plate_shared_1 at cupboard_k1, both days, 16:00

   **h2: WFH, dishes on counter (staging, doesn't put away)**
   - Rest: plates/pans → counter_k1
   - Phone → nightstand_b1
   - Medication → bathroom_shelf_ba1
   - Distinguishing: pan_shared_1 at counter_k1, both days, 16:00

   **h3: WFH, kitchen table is the catch-all surface**
   - Rest: plates, bowls, makeup → kitchen_table_k1
   - Phone → nightstand_b1
   - Medication → bathroom_shelf_ba1
   - Distinguishing: makeup_kit_mara at kitchen_table_k1, both days, 08:00

   **h4: WFH with brief daily outing (walk/errand, 30 min, 5x/week)**
   - Keys, wallet, phone, jacket briefly OUT_OF_HOUSE
   - Distinguishing: keys_mara OUT_OF_HOUSE, weekday, 17:00

   **h5: WFH, highly mobile objects (no fixed rest for water bottle, remote, plates)**
   - Water bottle, remote, and plates are "last-used" location, no fixed rest
   - Distinguishing: remote_shared_1 at counter_k1, weekday, 14:00

   Wait, I need to check: are these hypotheses genuinely different in their predictions?
   - h1 says plate at cupboard at 16:00
   - h2 says pan at counter at 16:00
   - h3 says makeup at kitchen_table at 08:00
   - h4 says keys OUT_OF_HOUSE at 17:00
   - h5 says remote at counter at 14:00

   These are testable and different. Good.

   Now let me think about the activities for each:

   Common to all (since she's WFH and stays home):
   - morning_routine: mug → counter, water_bottle → counter, medication → counter (then back to bathroom)
   - work_day: laptop, charger, headphones, glasses at kitchen_table
   - evening_relax: remote → coffee_table, tablet → coffee_table, blanket → couch

   Differences:
   - h1: cooking_dinner moves dishes to cupboard/dish_rack after
   - h2: cooking_dinner leaves dishes on counter
   - h3: cooking_dinner leaves dishes on kitchen_table; makeup at kitchen_table in morning
   - h4: brief_out activity (keys, wallet, phone, jacket → OUT_OF_HOUSE for 30 min)
   - h5: no fixed rest for mobile objects; they stay where last used

   Let me also fix the specific errors:
   - Remove phone from work_day moves (it stays at nightstand)
   - Fix medication rest to bathroom_shelf_ba1 (not counter_k1)
   - Fix pan rest (not sink_k1)
   - Fix bowl_shared_2 rest (not sink_k1)
   - Fix plate_shared_1 rest (not cupboard_k1 for h1... wait, h1 IS the "organized" one, so cupboard makes sense for h1)
   - Fix jacket: sometimes at cupboard_k1 (from worst objects)

   Actually, I realize I need to be more careful about what "rest" means. Rest is where the object is when NOT in an activity. So:
   - If h1 says "dishes go to cupboard after cooking," then rest for plates = cupboard_k1
   - If h2 says "dishes stay on counter," then rest for plates = counter_k1
   - If h3 says "dishes on kitchen table," then rest for plates = kitchen_table_k1

   This makes the hypotheses genuinely different in their rest predictions.

   Let me also consider: the data shows pot_shared_1 at dish_rack_k1 (4/7). So pots go to dish_rack. This is consistent across all hypotheses (it's a specific object behavior).

   And mug_shared_1 at cupboard_k1 (7/7) — always in cupboard. Consistent.

   bowl_shared_1 at entry_table_e1 (8/8) — always at entry table. Very consistent. This is a fixed object.

   OK, let me write the final hypotheses. I'll keep the structure similar but fix the errors.

   Key fixes across all:
   1. phone_mara rest: nightstand_b1 (remove from any work_day moves)
   2. medication_bottle_mara rest: bathroom_shelf_ba1 (not counter_k1)
   3. Remove phone from work_day activity moves
   4. jacket_mara: add cupboard_k1 as secondary (from worst objects)
   5. Fix dish rest locations per hypothesis

   Let me write this out now.

   For h1 (organized, dishes to cupboard):
   - pan_shared_1 rest: cupboard_k1
   - bowl_shared_2 rest: cupboard_k1
   - plate_shared_1 rest: cupboard_k1
   - plate_shared_2 rest: cupboard_k1
   - pot_shared_1 rest: dish_rack_k1
   - mug_shared_1 rest: cupboard_k1
   - bowl_shared_1 rest: entry_table_e1

   For h2 (dishes on counter):
   - pan_shared_1 rest: counter_k1
   - bowl_shared_2 rest: counter_k1
   - plate_shared_1 rest: counter_k1
   - plate_shared_2 rest: counter_k1
   - pot_shared_1 rest: dish_rack_k1
   - mug_shared_1 rest: cupboard_k1
   - bowl_shared_1 rest: entry_table_e1

   For h3 (kitchen table catch-all):
   - pan_shared_1 rest: kitchen_table_k1
   - bowl_shared_2 rest: kitchen_table_k1
   - plate_shared_1 rest: kitchen_table_k1
   - plate_shared_2 rest: kitchen_table_k1
   - makeup_kit_mara rest: kitchen_table_k1
   - pot_shared_1 rest: dish_rack_k1
   - mug_shared_1 rest: cupboard_k1
   - bowl_shared_1 rest: entry_table_e1

   For h4 (brief daily outing):
   - Same dish rest as h1 (organized)
   - But has a "brief_out" activity
   - phone, keys, wallet, jacket go OUT_OF_HOUSE briefly

   For h5 (mobile objects, no fixed rest):
   - water_bottle_mara: no rest entry (or rest at counter_k1 as "last used")
   - remote_shared_1: no fixed rest (or counter_k1)
   - plates: counter_k1 (last used during cooking)
   - Actually, I can't have "no rest" - I need to assign something. Let me say they rest at counter_k1 (the kitchen work surface) since that's where cooking happens.
   - Distinguishing: remote at counter_k1 at 14:00 (she used it in kitchen, not living room)

   Hmm wait, for h5 the distinguishing prediction should be something that's DIFFERENT from the other hypotheses. If h5 says remote is at counter at 14:00, and h1 says remote is at cupboard (rest) or coffee_table (evening), then at 14:00 (afternoon, not evening), h1 would predict cupboard and h5 would predict counter. That's a good distinction.

   Actually, let me reconsider. At 14:00 on a weekday:
   - h1: remote at cupboard_k1 (rest, not in evening activity)
   - h2: remote at cupboard_k1 (rest)
   - h3: remote at cupboard_k1 (rest)
   - h4: remote at cupboard_k1 (rest)
   - h5: remote at counter_k1 (mobile, last used in kitchen)

   So h5's distinguishing prediction of remote at counter_k1 at 14:00 differentiates it from h1-h4. Good.

   For h4's distinguishing prediction (keys OUT_OF_HOUSE at 17:00):
   - h1: keys at entry_table_e1 (rest)
   - h2: keys at entry_table_e1 (rest)
   - h3: keys at entry_table_e1 (rest)
   - h4: keys OUT_OF_HOUSE (brief outing)
   - h5: keys at entry_table_e1 (rest)

   Good, this differentiates h4.

   For h1's distinguishing (plate_shared_1 at cupboard_k1 at 16:00):
   - h1: cupboard_k1
   - h2: counter_k1
   - h3: kitchen_table_k1
   - h4: cupboard_k1 (same as h1 for dishes)
   - h5: counter_k1

   Hmm, h1 and h4 would both predict cupboard. That's a problem. Let me change h4's dish rest to be different. Actually, h4's core differentiator is the outing, not the dishes. Let me make h4's dish rest = counter_k1 (like h2) to differentiate from h1.

   Actually, the distinguishing predictions are the KEY differentiator. The rest locations are secondary. Let me make sure the distinguishing predictions are all different:
   - h1: plate_shared_1 at cupboard_k1, both days, 16:00
   - h2: pan_shared_1 at counter_k1, both days, 16:00
   - h3: makeup_kit_mara at kitchen_table_k1, both days, 08:00
   - h4: keys_mara OUT_OF_HOUSE, weekday, 17:00
   - h5: remote_shared_1 at counter_k1, weekday, 14:00

   These are all different objects, locations, and times. Good.

   Now let me write the full JSON. I'll keep the activities similar across hypotheses (since the core WFH structure is the same) but vary the dish-related moves and rest locations.

   Let me also make sure I'm not adding a 6th hypothesis. The instructions say "add at most ONE new hypothesis only if something systematic is unexplained." I don't think there's a systematic unexplained pattern that requires a 6th hypothesis. The 5 I have cover the main axes of uncertainty.

   Let me finalize and write the JSON.
```

### Model output — hypotheses

### hyp1 — Mara is a pure WFH professional who never leaves the house. She is organized: after cooking, dishes go back to the cupboard. Phone stays at nightstand (she doesn't bring it to the kitchen table). Medication rests in the bathroom. Laptop, charger, headphones, glasses are her fixed work kit at the kitchen table.

*Distinguishing prediction:* plate_shared_1 is at cupboard_k1 on a weekday at 16:00 because she puts dishes away after lunch
  (checkable form: plate_shared_1 at cupboard_k1, weekday, 16.0h)

*Rest entries:* 35 — medication_bottle_mara→bathroom_shelf_ba1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→dish_rack_k1, plate_shared_1→cupboard_k1 …

- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - medication_bottle_mara → counter_k1 (usually, left)
- **work_day** (weekday, 5×/week, 9.0h for 8.0h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - charger_mara → kitchen_table_k1 (usually, left)
  - headphones_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
- **lunch** (both, 7×/week, 12.5h for 1.0h)
  - plate_shared_2 → kitchen_table_k1 (usually, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
  - water_bottle_mara → kitchen_table_k1 (usually, left)
- **dishes_away** (both, 7×/week, 14.0h for 0.5h)
  - plate_shared_1 → cupboard_k1 (usually, returned)
  - plate_shared_2 → cupboard_k1 (usually, returned)
  - pan_shared_1 → cupboard_k1 (usually, returned)
  - bowl_shared_2 → cupboard_k1 (usually, returned)
- **evening_relax** (both, 7×/week, 19.5h for 3.0h)
  - remote_shared_1 → coffee_table_l1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
- **weekend_yoga** (weekend, 2×/week, 9.0h for 1.0h)
  - yoga_mat_mara → bedroom_floor_b1 (usually, returned)
  - headphones_mara → bedroom_floor_b1 (sometimes, returned)
  - water_bottle_mara → bedroom_floor_b1 (sometimes, returned)

### hyp2 — Mara is WFH and never leaves, but she does NOT put dishes away. Used plates, pans, and bowls stay on the counter as a staging area until the next meal. The counter is her 'dirty dish' zone. Phone stays at nightstand. She is disorganized about kitchenware but organized about work items.

*Distinguishing prediction:* pan_shared_1 is at counter_k1 on a weekday at 16:00 because she left it out after cooking and hasn't put it away
  (checkable form: pan_shared_1 at counter_k1, weekday, 16.0h)

*Rest entries:* 35 — medication_bottle_mara→bathroom_shelf_ba1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→dish_rack_k1, plate_shared_1→counter_k1 …

- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - medication_bottle_mara → counter_k1 (usually, left)
- **work_day** (weekday, 5×/week, 9.0h for 8.0h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - charger_mara → kitchen_table_k1 (usually, left)
  - headphones_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
- **cooking_dinner** (both, 7×/week, 18.0h for 1.5h)
  - pan_shared_1 → counter_k1 (usually, left)
  - pot_shared_1 → counter_k1 (sometimes, left)
  - plate_shared_1 → counter_k1 (usually, left)
  - plate_shared_2 → counter_k1 (usually, left)
  - bowl_shared_2 → counter_k1 (sometimes, left)
- **evening_relax** (both, 7×/week, 20.0h for 2.5h)
  - remote_shared_1 → coffee_table_l1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
- **weekend_yoga** (weekend, 2×/week, 9.0h for 1.0h)
  - yoga_mat_mara → bedroom_floor_b1 (usually, returned)
  - headphones_mara → bedroom_floor_b1 (sometimes, returned)
  - water_bottle_mara → bedroom_floor_b1 (sometimes, returned)

### hyp3 — Mara is WFH and the kitchen table is her universal surface: work, meals, AND personal items like makeup all land there. She doesn't separate 'work zone' from 'living zone' in the kitchen. Dishes rest on the kitchen table after meals. Phone stays at nightstand. The bathroom shelf only holds toiletries (hairbrush, towel), not the makeup kit.

*Distinguishing prediction:* makeup_kit_mara is at kitchen_table_k1 on a weekday at 08:00 because she does her morning makeup at the kitchen table before work
  (checkable form: makeup_kit_mara at kitchen_table_k1, weekday, 8.0h)

*Rest entries:* 35 — medication_bottle_mara→bathroom_shelf_ba1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→dish_rack_k1, plate_shared_1→kitchen_table_k1 …

- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - medication_bottle_mara → counter_k1 (usually, left)
  - makeup_kit_mara → kitchen_table_k1 (usually, left)
- **work_day** (weekday, 5×/week, 9.0h for 8.0h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - charger_mara → kitchen_table_k1 (usually, left)
  - headphones_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
- **lunch** (both, 7×/week, 12.5h for 1.0h)
  - plate_shared_1 → kitchen_table_k1 (usually, left)
  - plate_shared_2 → kitchen_table_k1 (usually, left)
  - bowl_shared_2 → kitchen_table_k1 (usually, left)
  - water_bottle_mara → kitchen_table_k1 (usually, left)
- **evening_relax** (both, 7×/week, 19.5h for 3.0h)
  - remote_shared_1 → coffee_table_l1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
- **weekend_yoga** (weekend, 2×/week, 9.0h for 1.0h)
  - yoga_mat_mara → bedroom_floor_b1 (usually, returned)
  - headphones_mara → bedroom_floor_b1 (sometimes, returned)
  - water_bottle_mara → bedroom_floor_b1 (sometimes, returned)

### hyp4 — Mara is WFH but takes a brief daily walk or errand (20-30 min) in the mid-afternoon, 5x/week. She grabs keys, wallet, phone, and jacket. Everything else (laptop, charger, dishes) stays put. This is the ONLY hypothesis where objects are briefly OUT_OF_HOUSE. Dishes rest on the counter (she doesn't organize them).

*Distinguishing prediction:* keys_mara is OUT_OF_HOUSE on a weekday at 17:00 because she is on her daily walk/errand
  (checkable form: keys_mara at OUT_OF_HOUSE, weekday, 17.0h)

*Rest entries:* 35 — medication_bottle_mara→bathroom_shelf_ba1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→dish_rack_k1, plate_shared_1→counter_k1 …

- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - medication_bottle_mara → counter_k1 (usually, left)
- **work_day** (weekday, 5×/week, 9.0h for 7.0h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - charger_mara → kitchen_table_k1 (usually, left)
  - headphones_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
- **daily_walk** (weekday, 5×/week, 16.5h for 0.5h)
  - keys_mara → OUT_OF_HOUSE (almost_always, left)
  - wallet_mara → OUT_OF_HOUSE (almost_always, left)
  - phone_mara → OUT_OF_HOUSE (usually, left)
  - jacket_mara → OUT_OF_HOUSE (usually, left)
- **walk_return** (weekday, 5×/week, 17.0h for 0.5h)
  - keys_mara → entry_table_e1 (almost_always, returned)
  - wallet_mara → entry_table_e1 (almost_always, returned)
  - phone_mara → nightstand_b1 (usually, returned)
  - jacket_mara → entry_hook_e1 (usually, returned)
- **evening_relax** (both, 7×/week, 19.5h for 3.0h)
  - remote_shared_1 → coffee_table_l1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
- **weekend_yoga** (weekend, 2×/week, 9.0h for 1.0h)
  - yoga_mat_mara → bedroom_floor_b1 (usually, returned)
  - headphones_mara → bedroom_floor_b1 (sometimes, returned)
  - water_bottle_mara → bedroom_floor_b1 (sometimes, returned)

### hyp5 — Mara is WFH and never leaves, but her kitchen objects are HIGHLY MOBILE with no fixed rest location. The water bottle, remote, and plates are wherever she last used them — they migrate between counter, kitchen table, and sink throughout the day. The remote is often in the kitchen (she watches cooking videos or takes calls there), not just in the living room. This explains the 4-receptacle pattern for these objects.

*Distinguishing prediction:* remote_shared_1 is at counter_k1 on a weekday at 14:00 because she used it in the kitchen during her work break and left it there
  (checkable form: remote_shared_1 at counter_k1, weekday, 14.0h)

*Rest entries:* 35 — medication_bottle_mara→bathroom_shelf_ba1, lunchbox_mara→counter_k1, glasses_mara→kitchen_table_k1, hairbrush_mara→bathroom_shelf_ba1, watering_can_mara→sink_k1, mug_shared_1→cupboard_k1, pot_shared_1→dish_rack_k1, plate_shared_1→counter_k1 …

- **morning_routine** (both, 7×/week, 7.0h for 1.0h)
  - mug_mara → counter_k1 (usually, left)
  - water_bottle_mara → counter_k1 (usually, left)
  - medication_bottle_mara → counter_k1 (usually, left)
- **work_day** (weekday, 5×/week, 9.0h for 8.0h)
  - laptop_mara → kitchen_table_k1 (usually, left)
  - charger_mara → kitchen_table_k1 (usually, left)
  - headphones_mara → kitchen_table_k1 (usually, left)
  - glasses_mara → kitchen_table_k1 (usually, left)
  - mug_mara → kitchen_table_k1 (usually, left)
  - remote_shared_1 → counter_k1 (sometimes, left)
  - water_bottle_mara → kitchen_table_k1 (sometimes, left)
- **lunch** (both, 7×/week, 12.5h for 1.0h)
  - plate_shared_2 → kitchen_table_k1 (usually, left)
  - bowl_shared_2 → kitchen_table_k1 (sometimes, left)
  - water_bottle_mara → kitchen_table_k1 (usually, left)
- **evening_relax** (both, 7×/week, 19.5h for 3.0h)
  - remote_shared_1 → coffee_table_l1 (usually, left)
  - tablet_mara → coffee_table_l1 (usually, left)
  - blanket_mara → couch_l1 (usually, left)
- **weekend_yoga** (weekend, 2×/week, 9.0h for 1.0h)
  - yoga_mat_mara → bedroom_floor_b1 (usually, returned)
  - headphones_mara → bedroom_floor_b1 (sometimes, returned)
  - water_bottle_mara → bedroom_floor_b1 (sometimes, returned)

<details><summary>raw JSON</summary>

```json
{
 "hypotheses": [
  {
   "hypothesis_id": "h1",
   "rationale": "Mara is a pure WFH professional who never leaves the house. She is organized: after cooking, dishes go back to the cupboard. Phone stays at nightstand (she doesn't bring it to the kitchen table). Medication rests in the bathroom. Laptop, charger, headphones, glasses are her fixed work kit at the kitchen table.",
   "distinguishing_prediction": "plate_shared_1 is at cupboard_k1 on a weekday at 16:00 because she puts dishes away after lunch",
   "distinguishing_check": {
    "target": "plate_shared_1",
    "at": "cupboard_k1",
    "days": "weekday",
    "hour": 16.0
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
     "name": "dishes_away",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 14.0,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "plate_shared_1",
       "to": "cupboard_k1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "plate_shared_2",
       "to": "cupboard_k1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "pan_shared_1",
       "to": "cupboard_k1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "bowl_shared_2",
       "to": "cupboard_k1",
       "chance": "usually",
       "after": "returned"
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
     "at": "bathroom_shelf_ba1"
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
     "at": "dish_rack_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "cupboard_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "cupboard_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "cupboard_k1"
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
     "target": "makeup_kit_mara",
     "at": "bathroom_shelf_ba1"
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
   "rationale": "Mara is WFH and never leaves, but she does NOT put dishes away. Used plates, pans, and bowls stay on the counter as a staging area until the next meal. The counter is her 'dirty dish' zone. Phone stays at nightstand. She is disorganized about kitchenware but organized about work items.",
   "distinguishing_prediction": "pan_shared_1 is at counter_k1 on a weekday at 16:00 because she left it out after cooking and hasn't put it away",
   "distinguishing_check": {
    "target": "pan_shared_1",
    "at": "counter_k1",
    "days": "weekday",
    "hour": 16.0
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
      }
     ]
    },
    {
     "name": "cooking_dinner",
     "days": "both",
     "frequency_per_week": 7,
     "start_hour": 18.0,
     "duration_h": 1.5,
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
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "plate_shared_1",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_2",
       "to": "counter_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "bowl_shared_2",
       "to": "counter_k1",
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
     "at": "bathroom_shelf_ba1"
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
     "at": "dish_rack_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "counter_k1"
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
     "target": "makeup_kit_mara",
     "at": "bathroom_shelf_ba1"
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
   "rationale": "Mara is WFH and the kitchen table is her universal surface: work, meals, AND personal items like makeup all land there. She doesn't separate 'work zone' from 'living zone' in the kitchen. Dishes rest on the kitchen table after meals. Phone stays at nightstand. The bathroom shelf only holds toiletries (hairbrush, towel), not the makeup kit.",
   "distinguishing_prediction": "makeup_kit_mara is at kitchen_table_k1 on a weekday at 08:00 because she does her morning makeup at the kitchen table before work",
   "distinguishing_check": {
    "target": "makeup_kit_mara",
    "at": "kitchen_table_k1",
    "days": "weekday",
    "hour": 8.0
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
       "target": "makeup_kit_mara",
       "to": "kitchen_table_k1",
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
       "target": "plate_shared_1",
       "to": "kitchen_table_k1",
       "chance": "usually",
       "after": "left"
      },
      {
       "target": "plate_shared_2",
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
     "at": "bathroom_shelf_ba1"
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
     "at": "dish_rack_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "kitchen_table_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "kitchen_table_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "kitchen_table_k1"
    },
    {
     "target": "pan_shared_1",
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
     "target": "makeup_kit_mara",
     "at": "kitchen_table_k1"
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
   "rationale": "Mara is WFH but takes a brief daily walk or errand (20-30 min) in the mid-afternoon, 5x/week. She grabs keys, wallet, phone, and jacket. Everything else (laptop, charger, dishes) stays put. This is the ONLY hypothesis where objects are briefly OUT_OF_HOUSE. Dishes rest on the counter (she doesn't organize them).",
   "distinguishing_prediction": "keys_mara is OUT_OF_HOUSE on a weekday at 17:00 because she is on her daily walk/errand",
   "distinguishing_check": {
    "target": "keys_mara",
    "at": "OUT_OF_HOUSE",
    "days": "weekday",
    "hour": 17.0
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
      }
     ]
    },
    {
     "name": "daily_walk",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 16.5,
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
       "target": "phone_mara",
       "to": "OUT_OF_HOUSE",
       "chance": "usually",
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
     "name": "walk_return",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 17.0,
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
       "target": "phone_mara",
       "to": "nightstand_b1",
       "chance": "usually",
       "after": "returned"
      },
      {
       "target": "jacket_mara",
       "to": "entry_hook_e1",
       "chance": "usually",
       "after": "returned"
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
     "at": "bathroom_shelf_ba1"
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
     "at": "dish_rack_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "cupboard_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "counter_k1"
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
     "target": "makeup_kit_mara",
     "at": "bathroom_shelf_ba1"
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
   "rationale": "Mara is WFH and never leaves, but her kitchen objects are HIGHLY MOBILE with no fixed rest location. The water bottle, remote, and plates are wherever she last used them \u2014 they migrate between counter, kitchen table, and sink throughout the day. The remote is often in the kitchen (she watches cooking videos or takes calls there), not just in the living room. This explains the 4-receptacle pattern for these objects.",
   "distinguishing_prediction": "remote_shared_1 is at counter_k1 on a weekday at 14:00 because she used it in the kitchen during her work break and left it there",
   "distinguishing_check": {
    "target": "remote_shared_1",
    "at": "counter_k1",
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
       "target": "remote_shared_1",
       "to": "counter_k1",
       "chance": "sometimes",
       "after": "left"
      },
      {
       "target": "water_bottle_mara",
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
     "at": "bathroom_shelf_ba1"
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
     "at": "dish_rack_k1"
    },
    {
     "target": "plate_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "plate_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "remote_shared_1",
     "at": "counter_k1"
    },
    {
     "target": "bowl_shared_2",
     "at": "counter_k1"
    },
    {
     "target": "pan_shared_1",
     "at": "counter_k1"
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
     "target": "makeup_kit_mara",
     "at": "bathroom_shelf_ba1"
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

- **hyp1:** rationale rewritten; rest moved for medication_bottle_mara, pot_shared_1, bowl_shared_2, pan_shared_1, plate_shared_2; activities added: dishes_away; moves added: bowl_shared_2→cupboard_k1, pan_shared_1→cupboard_k1, plate_shared_1→cupboard_k1, plate_shared_2→cupboard_k1; moves removed: phone_mara→kitchen_table_k1
- **hyp2:** rationale rewritten; rest moved for medication_bottle_mara, pot_shared_1, plate_shared_1, bowl_shared_2, pan_shared_1; activities added: cooking_dinner, weekend_yoga, work_day; activities removed: office_home, office_out, wfh_day; evening_relax.start_hour 19.5 → 20.0; evening_relax.duration_h 3.0 → 2.5; moves added: bowl_shared_2→counter_k1, headphones_mara→bedroom_floor_b1, medication_bottle_mara→counter_k1, pan_shared_1→counter_k1, plate_shared_1→counter_k1, plate_shared_2→counter_k1 …; moves removed: backpack_mara→OUT_OF_HOUSE, backpack_mara→entry_hook_e1, charger_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, keys_mara→entry_table_e1, laptop_mara→OUT_OF_HOUSE …
- **hyp3:** rationale rewritten; rest moved for medication_bottle_mara, pot_shared_1, plate_shared_1, bowl_shared_2, pan_shared_1; activities added: evening_relax, lunch, work_day; activities removed: daytime_work, shift_home, shift_out; weekend_yoga.start_hour 10.0 → 9.0; moves added: blanket_mara→couch_l1, bowl_shared_2→kitchen_table_k1, charger_mara→kitchen_table_k1, headphones_mara→kitchen_table_k1, makeup_kit_mara→kitchen_table_k1, medication_bottle_mara→counter_k1 …; moves removed: backpack_mara→OUT_OF_HOUSE, backpack_mara→entry_hook_e1, jacket_mara→OUT_OF_HOUSE, jacket_mara→entry_hook_e1, keys_mara→OUT_OF_HOUSE, keys_mara→entry_table_e1 …
- **hyp4:** rationale rewritten; rest moved for medication_bottle_mara, pot_shared_1, plate_shared_1, bowl_shared_2, pan_shared_1; activities added: daily_walk, walk_return, work_day; activities removed: campus_out, campus_return, home_study; weekend_yoga.start_hour 9.5 → 9.0; moves added: charger_mara→kitchen_table_k1, headphones_mara→bedroom_floor_b1, headphones_mara→kitchen_table_k1, jacket_mara→OUT_OF_HOUSE, jacket_mara→entry_hook_e1, medication_bottle_mara→counter_k1 …; moves removed: backpack_mara→OUT_OF_HOUSE, backpack_mara→entry_hook_e1, laptop_mara→OUT_OF_HOUSE, notebook_mara→OUT_OF_HOUSE, notebook_mara→kitchen_table_k1, pen_mara→OUT_OF_HOUSE …
- **hyp5:** rationale rewritten; rest moved for medication_bottle_mara, pot_shared_1, plate_shared_1, remote_shared_1, bowl_shared_2; activities added: evening_relax, lunch; activities removed: cooking_dinner, evening_tv, gym_session; work_day.duration_h 7.0 → 8.0; moves added: bowl_shared_2→kitchen_table_k1, medication_bottle_mara→counter_k1, plate_shared_2→kitchen_table_k1, remote_shared_1→counter_k1, water_bottle_mara→kitchen_table_k1; moves removed: bowl_shared_1→kitchen_table_k1, jacket_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, pan_shared_1→counter_k1, phone_mara→OUT_OF_HOUSE, phone_mara→kitchen_table_k1 …

## Result

- valid hypotheses: 5
- outcome: revised
- generation seconds: 756.85
