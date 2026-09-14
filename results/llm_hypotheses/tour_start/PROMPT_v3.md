# Tour-start prompt, v3 — rendered for three banks

Vocabulary the model is given: only what is in these blocks. Words that appear nowhere below: not, never, seen, carry, displace, stationary, observable, person.

## hh_001 · timeline 0 · bank 0  (5462 chars)

### system

```text
You model how one household runs, so that a home robot can predict where its objects are. You write several competing hypotheses; the robot's sightings over the following days decide between them, and you will later be shown how each one did and asked to revise it.
```

### user

```text
A home robot has just been installed. Its only observation so far is one walkthrough of the home at 15:08 on day 0, a Monday. Below are the home's receptacles and objects; where the walkthrough saw an object, its row says so.

RECEPTACLES:
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
  OUT_OF_HOUSE

OBJECTS, with where the tour saw each one:
  backpack_mara  (class: backpack)
  blanket_mara  (class: blanket)  at couch_l1
  book_mara  (class: book)  at bookshelf_l1
  bowl_shared_1  (class: bowl)  at kitchen_table_k1
  bowl_shared_2  (class: bowl)  at sink_k1
  charger_mara  (class: charger)  at kitchen_table_k1
  glasses_mara  (class: glasses)  at kitchen_table_k1
  hairbrush_mara  (class: hairbrush)  at bathroom_shelf_ba1
  headphones_mara  (class: headphones)  at kitchen_table_k1
  jacket_mara  (class: jacket)
  keys_mara  (class: keys)  at entry_table_e1
  laptop_mara  (class: laptop)
  laundry_basket_mara  (class: laundry_basket)  at bedroom_floor_b1
  lunchbox_mara  (class: lunchbox)
  makeup_kit_mara  (class: makeup_kit)  at kitchen_table_k1
  medication_bottle_mara  (class: medication_bottle)  at counter_k1
  mug_mara  (class: mug)  at counter_k1
  mug_shared_1  (class: mug)  at cupboard_k1
  notebook_mara  (class: notebook)
  pan_shared_1  (class: pan)  at counter_k1
  pen_mara  (class: pen)  at kitchen_table_k1
  phone_mara  (class: phone)
  plate_shared_1  (class: plate)  at cupboard_k1
  plate_shared_2  (class: plate)  at counter_k1
  pot_shared_1  (class: pot)  at cupboard_k1
  remote_shared_1  (class: remote)  at cupboard_k1
  suitcase_mara  (class: suitcase)  at bedroom_floor_b1
  tablet_mara  (class: tablet)  at coffee_table_l1
  towel_mara  (class: towel)  at towel_rack_ba1
  umbrella_mara  (class: umbrella)  at entry_floor_e1
  vacuum_cleaner_shared_1  (class: vacuum_cleaner)  at bedroom_floor_b1
  wallet_mara  (class: wallet)
  water_bottle_mara  (class: water_bottle)
  watering_can_mara  (class: watering_can)  at sink_k1
  yoga_mat_mara  (class: yoga_mat)  at couch_l1

CLASSES (usable as `class:<name>` targets): backpack, blanket, book, bowl, charger, glasses, hairbrush, headphones, jacket, keys, laptop, laundry_basket, lunchbox, makeup_kit, medication_bottle, mug, notebook, pan, pen, phone, plate, pot, remote, suitcase, tablet, towel, umbrella, vacuum_cleaner, wallet, water_bottle, watering_can, yoga_mat

Write 5 competing hypotheses about this home's weekly routine. Each hypothesis is a set of ACTIVITIES: a name, which days (weekday, weekend, or both), roughly when it starts (start_hour, a number), how long it lasts (duration_h), how many times a week it happens (frequency_per_week), and its moves — which object (or class:<name>) goes to which receptacle, with a chance (rarely, sometimes, usually, almost_always) and whether it is `returned` afterwards or `left` there. A hypothesis may also give a `rest` map: receptacles where objects sit when nothing is happening. Each hypothesis carries a one-line `distinguishing_prediction` and a `distinguishing_check` in the form {"target": <object id>, "at": <receptacle id>, "days": weekday|weekend|both, "hour": <number>}.

Use only ids from the tables above, exactly as printed. Each hypothesis has a one-line rationale, a one-line distinguishing_prediction with its distinguishing_check, an optional rest map, and as many activities as its routine needs.

Think it through, then end your reply with one json object. The example below shows the field shapes only; it is abbreviated and is about a different, smaller home.

{
 "hypotheses": [
  {
   "hypothesis_id": "h1",
   "rationale": "one resident who is at an office on weekdays",
   "distinguishing_prediction": "keys_x are on the entry shelf on weekday evenings and gone by 9:00",
   "distinguishing_check": {
    "target": "keys_x",
    "at": "entry_shelf_1",
    "days": "weekday",
    "hour": 19.0
   },
   "rest": {
    "class:mug": "cupboard_1"
   },
   "activities": [
    {
     "name": "office_day",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 8.0,
     "duration_h": 9.0,
     "moves": [
      {
       "target": "keys_x",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "returned"
      }
     ]
    },
    {
     "name": "morning_coffee",
     "days": "both",
     "frequency_per_week": 6,
     "start_hour": 6.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "class:mug",
       "to": "counter_1",
       "chance": "usually",
       "after": "left"
      }
     ]
    }
   ]
  },
  {
   "hypothesis_id": "h2",
   "rationale": "one resident who works at the desk at home",
   "distinguishing_prediction": "keys_x on the entry shelf at weekday midday",
   "distinguishing_check": {
    "target": "keys_x",
    "at": "entry_shelf_1",
    "days": "weekday",
    "hour": 13.0
   },
   "rest": {
    "class:mug": "desk_1"
   },
   "activities": [
    {
     "name": "desk_work",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 9.0,
     "duration_h": 7.0,
     "moves": [
      {
       "target": "class:mug",
       "to": "desk_1",
       "chance": "usually",
       "after": "left"
      }
     ]
    }
   ]
  }
 ]
}
```

## hh_001 · timeline 1 · bank 0  (5426 chars)

### system

```text
You model how one household runs, so that a home robot can predict where its objects are. You write several competing hypotheses; the robot's sightings over the following days decide between them, and you will later be shown how each one did and asked to revise it.
```

### user

```text
A home robot has just been installed. Its only observation so far is one walkthrough of the home at 11:26 on day 1, a Tuesday. Below are the home's receptacles and objects; where the walkthrough saw an object, its row says so.

RECEPTACLES:
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
  OUT_OF_HOUSE

OBJECTS, with where the tour saw each one:
  backpack_mara  (class: backpack)
  blanket_mara  (class: blanket)  at couch_l1
  book_mara  (class: book)  at bookshelf_l1
  bowl_shared_1  (class: bowl)  at entry_table_e1
  bowl_shared_2  (class: bowl)  at sink_k1
  charger_mara  (class: charger)
  glasses_mara  (class: glasses)  at kitchen_table_k1
  hairbrush_mara  (class: hairbrush)  at bathroom_shelf_ba1
  headphones_mara  (class: headphones)
  jacket_mara  (class: jacket)
  keys_mara  (class: keys)
  laptop_mara  (class: laptop)
  laundry_basket_mara  (class: laundry_basket)  at bedroom_floor_b1
  lunchbox_mara  (class: lunchbox)
  makeup_kit_mara  (class: makeup_kit)  at bathroom_shelf_ba1
  medication_bottle_mara  (class: medication_bottle)  at bathroom_shelf_ba1
  mug_mara  (class: mug)  at kitchen_table_k1
  mug_shared_1  (class: mug)  at cupboard_k1
  notebook_mara  (class: notebook)
  pan_shared_1  (class: pan)  at sink_k1
  pen_mara  (class: pen)  at kitchen_table_k1
  phone_mara  (class: phone)
  plate_shared_1  (class: plate)  at sink_k1
  plate_shared_2  (class: plate)  at counter_k1
  pot_shared_1  (class: pot)  at cupboard_k1
  remote_shared_1  (class: remote)  at coffee_table_l1
  suitcase_mara  (class: suitcase)  at bedroom_floor_b1
  tablet_mara  (class: tablet)  at coffee_table_l1
  towel_mara  (class: towel)  at towel_rack_ba1
  umbrella_mara  (class: umbrella)  at entry_floor_e1
  vacuum_cleaner_shared_1  (class: vacuum_cleaner)  at bedroom_floor_b1
  wallet_mara  (class: wallet)
  water_bottle_mara  (class: water_bottle)  at chair_k2
  watering_can_mara  (class: watering_can)  at sink_k1
  yoga_mat_mara  (class: yoga_mat)  at couch_l1

CLASSES (usable as `class:<name>` targets): backpack, blanket, book, bowl, charger, glasses, hairbrush, headphones, jacket, keys, laptop, laundry_basket, lunchbox, makeup_kit, medication_bottle, mug, notebook, pan, pen, phone, plate, pot, remote, suitcase, tablet, towel, umbrella, vacuum_cleaner, wallet, water_bottle, watering_can, yoga_mat

Write 5 competing hypotheses about this home's weekly routine. Each hypothesis is a set of ACTIVITIES: a name, which days (weekday, weekend, or both), roughly when it starts (start_hour, a number), how long it lasts (duration_h), how many times a week it happens (frequency_per_week), and its moves — which object (or class:<name>) goes to which receptacle, with a chance (rarely, sometimes, usually, almost_always) and whether it is `returned` afterwards or `left` there. A hypothesis may also give a `rest` map: receptacles where objects sit when nothing is happening. Each hypothesis carries a one-line `distinguishing_prediction` and a `distinguishing_check` in the form {"target": <object id>, "at": <receptacle id>, "days": weekday|weekend|both, "hour": <number>}.

Use only ids from the tables above, exactly as printed. Each hypothesis has a one-line rationale, a one-line distinguishing_prediction with its distinguishing_check, an optional rest map, and as many activities as its routine needs.

Think it through, then end your reply with one json object. The example below shows the field shapes only; it is abbreviated and is about a different, smaller home.

{
 "hypotheses": [
  {
   "hypothesis_id": "h1",
   "rationale": "one resident who is at an office on weekdays",
   "distinguishing_prediction": "keys_x are on the entry shelf on weekday evenings and gone by 9:00",
   "distinguishing_check": {
    "target": "keys_x",
    "at": "entry_shelf_1",
    "days": "weekday",
    "hour": 19.0
   },
   "rest": {
    "class:mug": "cupboard_1"
   },
   "activities": [
    {
     "name": "office_day",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 8.0,
     "duration_h": 9.0,
     "moves": [
      {
       "target": "keys_x",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "returned"
      }
     ]
    },
    {
     "name": "morning_coffee",
     "days": "both",
     "frequency_per_week": 6,
     "start_hour": 6.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "class:mug",
       "to": "counter_1",
       "chance": "usually",
       "after": "left"
      }
     ]
    }
   ]
  },
  {
   "hypothesis_id": "h2",
   "rationale": "one resident who works at the desk at home",
   "distinguishing_prediction": "keys_x on the entry shelf at weekday midday",
   "distinguishing_check": {
    "target": "keys_x",
    "at": "entry_shelf_1",
    "days": "weekday",
    "hour": 13.0
   },
   "rest": {
    "class:mug": "desk_1"
   },
   "activities": [
    {
     "name": "desk_work",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 9.0,
     "duration_h": 7.0,
     "moves": [
      {
       "target": "class:mug",
       "to": "desk_1",
       "chance": "usually",
       "after": "left"
      }
     ]
    }
   ]
  }
 ]
}
```

## hh_002 · timeline 0 · bank 0  (7100 chars)

### system

```text
You model how one household runs, so that a home robot can predict where its objects are. You write several competing hypotheses; the robot's sightings over the following days decide between them, and you will later be shown how each one did and asked to revise it.
```

### user

```text
A home robot has just been installed. Its only observation so far is one walkthrough of the home at 20:59 on day 1, a Tuesday. Below are the home's receptacles and objects; where the walkthrough saw an object, its row says so.

RECEPTACLES:
  bed_b1
  nightstand_b1
  desk_b1
  bedroom_floor_b1
  bed_b2
  nightstand_b2
  desk_b2
  bedroom_floor_b2
  bed_b3
  nightstand_b3
  desk_b3
  bedroom_floor_b3
  bed_b4
  nightstand_b4
  desk_b4
  bedroom_floor_b4
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
  toy_chest_l1
  game_shelf_l1
  reading_table_l1
  medicine_cabinet_ba1
  OUT_OF_HOUSE

OBJECTS, with where the tour saw each one:
  backpack_leo  (class: backpack)  at sink_k1
  backpack_marco  (class: backpack)  at chair_k1
  backpack_priya  (class: backpack)  at entry_floor_e1
  backpack_sofia  (class: backpack)  at desk_b3
  blanket_elena  (class: blanket)  at armchair_l1
  blanket_leo  (class: blanket)  at couch_l1
  book_elena  (class: book)  at armchair_l1
  bowl_shared_1  (class: bowl)  at coffee_table_l1
  charger_shared_1  (class: charger)  at coffee_table_l1
  gaming_controller_shared_1  (class: gaming_controller)  at tv_stand_l1
  gaming_controller_sofia  (class: gaming_controller)  at couch_l1
  glasses_elena  (class: glasses)  at reading_table_l1
  hairbrush_priya  (class: hairbrush)  at bathroom_shelf_ba1
  headphones_sofia  (class: headphones)  at chair_k1
  jacket_leo  (class: jacket)  at entry_floor_e1
  jacket_marco  (class: jacket)  at entry_hook_e1
  jacket_priya  (class: jacket)  at entry_hook_e1
  jacket_sofia  (class: jacket)  at chair_k2
  keys_elena  (class: keys)  at chair_k1
  keys_leo  (class: keys)  at entry_table_e1
  keys_marco  (class: keys)  at counter_k1
  keys_priya  (class: keys)  at counter_k1
  keys_sofia  (class: keys)  at entry_table_e1
  laptop_marco  (class: laptop)  at desk_b2
  laptop_sofia  (class: laptop)  at bed_b3
  laundry_basket_shared_1  (class: laundry_basket)  at bedroom_floor_b2
  lunchbox_leo  (class: lunchbox)  at sink_k1
  lunchbox_marco  (class: lunchbox)  at counter_k1
  lunchbox_priya  (class: lunchbox)  at counter_k1
  makeup_kit_priya  (class: makeup_kit)  at bathroom_shelf_ba1
  medication_bottle_elena_1  (class: medication_bottle)  at medicine_cabinet_ba1
  mug_elena  (class: mug)  at dish_rack_k1
  notebook_elena  (class: notebook)  at counter_k1
  notebook_leo  (class: notebook)  at kitchen_table_k1
  notebook_priya  (class: notebook)  at counter_k1
  notebook_sofia  (class: notebook)  at desk_b3
  pan_shared_1  (class: pan)  at counter_k1
  pen_leo  (class: pen)  at kitchen_table_k1
  pen_sofia  (class: pen)  at dish_rack_k1
  phone_elena  (class: phone)  at reading_table_l1
  phone_leo  (class: phone)  at ON_PERSON
  phone_marco  (class: phone)  at coffee_table_l1
  phone_priya  (class: phone)  at counter_k1
  phone_sofia  (class: phone)  at kitchen_table_k1
  plate_shared_1  (class: plate)  at sink_k1
  pot_shared_1  (class: pot)  at cupboard_k1
  remote_shared_1  (class: remote)  at chair_k1
  suitcase_shared_1  (class: suitcase)  at bedroom_floor_b2
  tablet_leo  (class: tablet)  at coffee_table_l1
  toy_leo_1  (class: toy)  at couch_l1
  umbrella_shared_1  (class: umbrella)  at entry_hook_e1
  vacuum_cleaner_shared_1  (class: vacuum_cleaner)  at entry_floor_e1
  wallet_elena  (class: wallet)  at desk_b1
  wallet_marco  (class: wallet)  at desk_b2
  wallet_priya  (class: wallet)  at desk_b2
  water_bottle_leo  (class: water_bottle)  at sink_k1
  water_bottle_marco  (class: water_bottle)  at counter_k1
  water_bottle_priya  (class: water_bottle)  at sink_k1
  water_bottle_sofia  (class: water_bottle)  at chair_k2
  watering_can_elena  (class: watering_can)  at entry_floor_e1

CLASSES (usable as `class:<name>` targets): backpack, blanket, book, bowl, charger, gaming_controller, glasses, hairbrush, headphones, jacket, keys, laptop, laundry_basket, lunchbox, makeup_kit, medication_bottle, mug, notebook, pan, pen, phone, plate, pot, remote, suitcase, tablet, toy, umbrella, vacuum_cleaner, wallet, water_bottle, watering_can

Write 5 competing hypotheses about this home's weekly routine. Each hypothesis is a set of ACTIVITIES: a name, which days (weekday, weekend, or both), roughly when it starts (start_hour, a number), how long it lasts (duration_h), how many times a week it happens (frequency_per_week), and its moves — which object (or class:<name>) goes to which receptacle, with a chance (rarely, sometimes, usually, almost_always) and whether it is `returned` afterwards or `left` there. A hypothesis may also give a `rest` map: receptacles where objects sit when nothing is happening. Each hypothesis carries a one-line `distinguishing_prediction` and a `distinguishing_check` in the form {"target": <object id>, "at": <receptacle id>, "days": weekday|weekend|both, "hour": <number>}.

Use only ids from the tables above, exactly as printed. Each hypothesis has a one-line rationale, a one-line distinguishing_prediction with its distinguishing_check, an optional rest map, and as many activities as its routine needs.

Think it through, then end your reply with one json object. The example below shows the field shapes only; it is abbreviated and is about a different, smaller home.

{
 "hypotheses": [
  {
   "hypothesis_id": "h1",
   "rationale": "one resident who is at an office on weekdays",
   "distinguishing_prediction": "keys_x are on the entry shelf on weekday evenings and gone by 9:00",
   "distinguishing_check": {
    "target": "keys_x",
    "at": "entry_shelf_1",
    "days": "weekday",
    "hour": 19.0
   },
   "rest": {
    "class:mug": "cupboard_1"
   },
   "activities": [
    {
     "name": "office_day",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 8.0,
     "duration_h": 9.0,
     "moves": [
      {
       "target": "keys_x",
       "to": "OUT_OF_HOUSE",
       "chance": "almost_always",
       "after": "returned"
      }
     ]
    },
    {
     "name": "morning_coffee",
     "days": "both",
     "frequency_per_week": 6,
     "start_hour": 6.5,
     "duration_h": 0.5,
     "moves": [
      {
       "target": "class:mug",
       "to": "counter_1",
       "chance": "usually",
       "after": "left"
      }
     ]
    }
   ]
  },
  {
   "hypothesis_id": "h2",
   "rationale": "one resident who works at the desk at home",
   "distinguishing_prediction": "keys_x on the entry shelf at weekday midday",
   "distinguishing_check": {
    "target": "keys_x",
    "at": "entry_shelf_1",
    "days": "weekday",
    "hour": 13.0
   },
   "rest": {
    "class:mug": "desk_1"
   },
   "activities": [
    {
     "name": "desk_work",
     "days": "weekday",
     "frequency_per_week": 5,
     "start_hour": 9.0,
     "duration_h": 7.0,
     "moves": [
      {
       "target": "class:mug",
       "to": "desk_1",
       "chance": "usually",
       "after": "left"
      }
     ]
    }
   ]
  }
 ]
}
```
