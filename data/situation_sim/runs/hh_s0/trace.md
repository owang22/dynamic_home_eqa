# Household hh_s0 — five days, Wednesday to Sunday

Seed-generated household. Times are clock times; ids are the receptacle and object ids used in events.jsonl. A line indented under an activity says where an object went when the activity ended and why. WHIM marks a placement that landed somewhere other than where the decision was heading. Text in [brackets] names the hidden cause the decision is attributed to.

## Household

Type: flatmates. Rooms: bathroom, bedroom_1, bedroom_2, entry, kitchen, living, office.

Residents:

- **Leo** (resident_1): works outside the home; very untidy (tidiness 0.26); average timing (jitter scale 0.94); sometimes forgets pocket items; mood moderately affects behaviour (sensitivity 0.67); sleeps in bedroom_1, works at the bedroom_1 desk
- **Nora** (resident_2): works from home; very tidy (tidiness 0.80); average timing (jitter scale 1.03); rarely forgets pocket items; mood moderately affects behaviour (sensitivity 0.51); sleeps in bedroom_2, works at the office desk

Objects and their usual place (primary slot first):

- Leo's: book_leo → nightstand_b1 / bookshelf_l1; charger_leo → desk_b1 / nightstand_b1; handbag_leo → entry_hook_e1 / bedroom_floor_b1 / desk_b1; headphones_leo → desk_b1 / nightstand_b1; jacket_leo → entry_hook_e1 / wardrobe_b1; keys_leo → entry_table_e1 / nightstand_b1; laptop_leo → desk_b1 / bookshelf_l1; lunchbox_leo → cupboard_k1 / counter_k1 / sink_k1; mug_leo → cupboard_k1 / dish_rack_k1 / sink_k1; phone_leo → nightstand_b1 / coffee_table_l1; shoes_leo → entry_floor_e1 / wardrobe_b1; towel_leo → towel_rack_ba1 / bathroom_shelf_ba1; wallet_leo → entry_table_e1 / desk_b1
- Nora's: book_nora → nightstand_b2 / bookshelf_l1; jacket_nora → entry_hook_e1 / wardrobe_b2; keys_nora → entry_table_e1 / nightstand_b2; laptop_nora → desk_o1 / bookshelf_l1; mug_nora → cupboard_k1 / dish_rack_k1 / sink_k1; notebook_nora → desk_o1 / bookshelf_l1; phone_nora → nightstand_b2 / coffee_table_l1; shoes_nora → entry_floor_e1 / wardrobe_b2; towel_nora → towel_rack_ba1 / bathroom_shelf_ba1; umbrella_nora → entry_floor_e1 / entry_hook_e1; wallet_nora → nightstand_b2 / desk_o1; water_bottle_nora → dish_rack_k1 / counter_k1 / sink_k1
- Shared: blanket_shared → couch_l1 / armchair_l1; laundry_basket_shared → bathroom_shelf_ba1 / bedroom_floor_b1; remote_shared → tv_stand_l1 / coffee_table_l1; watering_can_shared → cupboard_k1 / counter_k1

Object groups (things that travel together):

- handbag_leo carries charger_leo, laptop_leo, lunchbox_leo on trips to work and errands


## Day 0 — Wednesday

**Active causes**

- `late_work:resident_2` (Nora): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.

Internal states (0–1): Leo energy 0.61, hurriedness 0.44, distraction 0.64; Nora energy 0.48, hurriedness 0.43, distraction 0.11

**Timeline**

```
07:02  Leo — morning routine in the bathroom; brings phone_leo from nightstand_b1
07:18  Nora — morning routine in the bathroom; brings phone_nora from nightstand_b2
07:33  Leo — breakfast in the kitchen; brings mug_leo from cupboard_k1
07:58  Leo finishes breakfast
          mug_leo → sink_k1: used, so it goes in the sink
          keeps phone_leo for work
08:13  Leo leaves for work (back 17:43); takes handbag_leo (with charger_leo, laptop_leo, lunchbox_leo), keys_leo, phone_leo, wallet_leo, jacket_leo, shoes_leo
08:31  Nora — breakfast in the kitchen; brings mug_nora from cupboard_k1
09:22  Nora — work session in the office; brings mug_nora from kitchen_table_k1
12:42  Nora finishes work session
          keeps phone_nora for lunch out
12:42  Nora leaves for lunch out (back 13:42); takes keys_nora, phone_nora, wallet_nora, jacket_nora, shoes_nora, umbrella_nora
13:42  Nora is back from lunch out
          jacket_nora → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_nora → entry_table_e1: put away in its usual place after the trip
          shoes_nora → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          umbrella_nora → entry_floor_e1: wet umbrella propped by the door [rain]
          wallet_nora → nightstand_b2: put away in its usual place after the trip
          keeps phone_nora for work session
13:42  Nora — work session in the office (bout 1/2) [shifted by late_work:resident_2]
17:06  Nora — a short break in the kitchen
17:43  Leo is back from work
          handbag_leo → entry_floor_e1: wet bag left by the door [rain]
          charger_leo → entry_floor_e1: stays in the handbag
          jacket_leo → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_leo → entry_table_e1: put away in its usual place after the trip
          laptop_leo → entry_floor_e1: stays in the handbag
          lunchbox_leo → entry_floor_e1: stays in the handbag
          shoes_leo → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          wallet_leo → entry_table_e1: put away in its usual place after the trip
          keeps phone_leo for cooking dinner
18:42  Nora — work session in the office (bout 2/2) [shifted by late_work:resident_2]
18:51  Leo — cooking dinner in the kitchen
19:01  Nora finishes work session
          laptop_nora → office_chair_o1: WHIM — was heading for desk_o1 (put back in its usual place) but landed on office_chair_o1 instead
19:26  Leo — dinner in the kitchen
19:29  Nora — dinner in the kitchen; brings water_bottle_nora from dish_rack_k1
20:06  Leo — evening TV in the living (bout 1/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_leo from sink_k1
20:09  Nora finishes dinner
          water_bottle_nora → sink_k1: used, so it goes in the sink
20:09  Nora — evening TV in the living [shifted by late_work:resident_2]; brings mug_nora from desk_o1
20:39  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → sink_k1: used, so it goes in the sink
          phone_nora → nightstand_b2: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
21:00  Leo — a short break in the kitchen
21:28  Leo — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1
21:40  Leo finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
          mug_leo → sink_k1: used, so it goes in the sink
22:35  Nora — bed in the bedroom_2
22:38  Leo — reading in the bedroom_1; brings book_leo from nightstand_b1
23:08  Leo finishes reading
          phone_leo → bed_b1: left where it was used
23:08  Leo — bed in the bedroom_1
```

## Day 1 — Thursday

**Active causes**

- `guest_visit` (household): Friends come over for the evening. the living room is tidied beforehand, dinner is late, and the couch is taken by guests all evening.
- `distracted:resident_1`: Leo is distracted (0.79): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `running_late:resident_2`: Nora is running late all day (0.71): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Leo energy 0.41, hurriedness 0.60, distraction 0.79; Nora energy 0.44, hurriedness 0.71, distraction 0.26

**Timeline**

```
07:23  Leo — morning routine in the bathroom; brings phone_leo from bed_b1
07:44  Nora — morning routine in the bathroom; brings phone_nora from nightstand_b2
07:48  Leo — breakfast in the kitchen; brings mug_leo from sink_k1
08:13  Leo finishes breakfast
          mug_leo → sink_k1: used, so it goes in the sink
          keeps phone_leo for work
08:13  Leo leaves for work (back 17:43); takes handbag_leo (with charger_leo, laptop_leo, lunchbox_leo), keys_leo, phone_leo, wallet_leo, jacket_leo, shoes_leo
08:19  Nora — breakfast in the kitchen; brings mug_nora from sink_k1
08:49  Nora — work session in the office (bout 1/3); brings laptop_nora from office_chair_o1, mug_nora from kitchen_table_k1
08:59  Nora finishes work session
          laptop_nora → office_chair_o1: WHIM — was heading for desk_o1 (put back in its usual place) but landed on office_chair_o1 instead
          mug_nora → sink_k1: used, so it goes in the sink
          notebook_nora → office_chair_o1: WHIM — was heading for desk_o1 (put back in its usual place) but landed on office_chair_o1 instead
08:59  Nora — a short break in the kitchen
09:29  Nora — work session in the office (bout 2/3); brings laptop_nora from office_chair_o1, notebook_nora from office_chair_o1, mug_nora from sink_k1
09:39  Nora finishes work session
          mug_nora → kitchen_table_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on kitchen_table_k1 instead
09:39  Nora — a short break in the kitchen
10:09  Nora — work session in the office (bout 3/3); brings mug_nora from kitchen_table_k1
12:09  Nora finishes work session
          keeps phone_nora for lunch out
12:09  Nora leaves for lunch out (back 13:09); takes keys_nora, phone_nora, wallet_nora, jacket_nora, shoes_nora
13:09  Nora is back from lunch out
          jacket_nora → entry_hook_e1: put away in its usual place after the trip
          keys_nora → entry_table_e1: put away in its usual place after the trip
          shoes_nora → entry_floor_e1: put away in its usual place after the trip
          wallet_nora → nightstand_b2: put away in its usual place after the trip
          keeps phone_nora for work session
13:09  Nora — work session in the office (bout 1/4)
14:29  Nora finishes work session
          mug_nora → sink_k1: used, so it goes in the sink
14:29  Nora — a short break in the kitchen
14:52  Nora — work session in the office (bout 2/4); brings mug_nora from sink_k1
15:06  Nora — a short break in the kitchen
15:29  Nora — work session in the office (bout 3/4)
16:16  Nora finishes work session
          laptop_nora → office_shelf_o1: WHIM — was heading for desk_o1 (put back in its usual place) but landed on office_shelf_o1 instead
          mug_nora → sink_k1: used, so it goes in the sink
16:16  Nora — a short break in the kitchen
16:39  Nora — work session in the office (bout 4/4); brings laptop_nora from office_shelf_o1, mug_nora from sink_k1
16:57  Nora finishes work session
          phone_nora → nightstand_b2: put back in its usual place
17:43  Leo is back from work
          handbag_leo → entry_table_e1: dropped at the door instead of being put away
          charger_leo → entry_table_e1: stays in the handbag
          jacket_leo → entry_hook_e1: put away in its usual place after the trip
          keys_leo → entry_hook_e1: WHIM — was heading for entry_table_e1 (put away in its usual place after the trip) but landed on entry_hook_e1 instead
          laptop_leo → entry_table_e1: stays in the handbag
          lunchbox_leo → entry_table_e1: stays in the handbag
          phone_leo → nightstand_b1: put away in its usual place after the trip
          shoes_leo → entry_floor_e1: put away in its usual place after the trip
          wallet_leo → entry_table_e1: put away in its usual place after the trip
17:43  Leo — tidying up in the living [because of guest_visit]
18:08  Nora — tidying up in the living [because of guest_visit]
18:13  Leo finishes tidying up
          charger_leo (from entry_table_e1) → desk_b1: tidied away to its usual place [guest_visit]
          handbag_leo (from entry_table_e1) → entry_hook_e1: tidied away to its usual place [guest_visit]
          keys_leo (from entry_hook_e1) → entry_table_e1: tidied away to its usual place [guest_visit]
          laptop_leo (from entry_table_e1) → desk_b1: cleared away before the guests [guest_visit]
          lunchbox_leo (from entry_table_e1) → cupboard_k1: tidied away to its usual place [guest_visit]
          mug_leo (from sink_k1) → counter_k1: WHIM — was heading for cupboard_k1 (tidied away to its usual place) but landed on counter_k1 instead [guest_visit]
          remote_shared (from coffee_table_l1) → tv_stand_l1: tidied away to its usual place [guest_visit]
          water_bottle_nora (from sink_k1) → dish_rack_k1: tidied away to its usual place [guest_visit]
18:38  Nora finishes tidying up
          mug_leo (from counter_k1) → cupboard_k1: tidied away to its usual place [guest_visit]
19:08  Leo — cooking dinner in the kitchen [shifted by guest_visit]; brings phone_leo from nightstand_b1
19:40  Nora — cooking dinner in the kitchen [shifted by guest_visit]; brings phone_nora from nightstand_b2
20:15  Nora — dinner in the kitchen [shifted by guest_visit]; brings water_bottle_nora from dish_rack_k1
20:48  Leo — dinner in the kitchen [shifted by guest_visit]
20:55  Nora finishes dinner
          water_bottle_nora → sink_k1: used, so it goes in the sink
20:55  Nora — hosting the guests in the living [because of guest_visit]; brings mug_nora from desk_o1
21:28  Leo — hosting the guests in the living [because of guest_visit]; brings mug_leo from cupboard_k1
22:55  Nora finishes hosting the guests
          mug_nora → sink_k1: mugs collected into the sink after the guests [guest_visit]
          phone_nora → nightstand_b2: put back in its usual place [guest_visit]
22:55  Nora — bed in the bedroom_2
23:28  Leo finishes hosting the guests
          mug_leo → sink_k1: mugs collected into the sink after the guests [guest_visit]
          phone_leo → nightstand_b1: carried along absent-mindedly into the bedroom_1 [distracted:resident_1, guest_visit]
23:28  Leo — bed in the bedroom_1
```

## Day 2 — Friday

**Active causes**

- `late_work:resident_1` (Leo): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `sick_day:resident_2` (Nora): Off sick, resting on the couch all day. no work or trips out; laptop, mug, medication, book and blanket all migrate to the couch and coffee table.
- `low_energy:resident_2`: Nora has low energy (0.18): leaves things where they were used instead of putting them back.
- `running_late:resident_1`: Leo is running late all day (0.99): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Leo energy 0.31, hurriedness 0.99, distraction 0.62; Nora energy 0.18, hurriedness 0.00, distraction 0.48

**Timeline**

```
07:10  Leo — morning routine in the bathroom; brings phone_leo from nightstand_b1
07:32  Nora — morning routine in the bathroom; brings phone_nora from nightstand_b2
07:38  Leo — breakfast in the kitchen; brings mug_leo from sink_k1
07:55  Leo finishes breakfast
          keeps phone_leo for work
07:55  Leo leaves for work (back 19:25); takes handbag_leo (with charger_leo, laptop_leo, lunchbox_leo), keys_leo, phone_leo, wallet_leo, jacket_leo, shoes_leo
07:57  Nora — breakfast in the kitchen; brings mug_nora from sink_k1
11:29  Nora — resting on the couch in the living [because of sick_day:resident_2]; brings laptop_nora from desk_o1, mug_nora from kitchen_table_k1, book_nora from nightstand_b2, blanket_shared from armchair_l1, water_bottle_nora from sink_k1
19:25  Leo is back from work
          handbag_leo → entry_floor_e1: bag dumped by the door, home late [late_work:resident_1]
          charger_leo → entry_floor_e1: stays in the handbag
          jacket_leo → armchair_l1: WHIM — was heading for couch_l1 (jacket thrown over the couch, home late) but landed on armchair_l1 instead [late_work:resident_1]
          keys_leo → entry_hook_e1: WHIM — was heading for entry_table_e1 (put away in its usual place after the trip) but landed on entry_hook_e1 instead
          laptop_leo → entry_floor_e1: stays in the handbag
          lunchbox_leo → entry_floor_e1: stays in the handbag
          shoes_leo → entry_floor_e1: put away in its usual place after the trip
          wallet_leo → entry_table_e1: put away in its usual place after the trip
          keeps phone_leo for dinner
19:25  Leo — dinner in the kitchen
19:29  Nora finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_2]
          book_nora → couch_l1: book dropped on the couch [sick_day:resident_2]
          water_bottle_nora → sink_k1: used, so it goes in the sink [sick_day:resident_2]
19:29  Nora — cooking dinner in the kitchen
20:04  Nora — dinner in the kitchen; brings water_bottle_nora from sink_k1
20:14  Leo — evening TV in the living (bout 1/2) [shifted by late_work:resident_1]; brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_leo from kitchen_table_k1
20:24  Leo finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          mug_leo → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
20:24  Leo — a short break in the kitchen
20:38  Leo — evening TV in the living (bout 2/2) [shifted by late_work:resident_1]; brings remote_shared from tv_stand_l1, blanket_shared from armchair_l1, mug_leo from sink_k1
20:44  Nora finishes dinner
          water_bottle_nora → sink_k1: used, so it goes in the sink
20:44  Nora — evening TV in the living
21:02  Leo finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_leo → dish_rack_k1: left where it was used; coffee_table_l1 was full, so it went to dish_rack_k1
          phone_leo → nightstand_b1: put back in its usual place
22:14  Nora finishes evening TV
          mug_nora → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
22:14  Nora — reading in the bedroom_2; brings book_nora from couch_l1
22:23  Leo — bed in the bedroom_1
22:44  Nora finishes reading
          book_nora → nightstand_b2: put back in its usual place
          phone_nora → bed_b2: left where it was used, too tired to put it away [low_energy:resident_2]
23:13  Nora — bed in the bedroom_2
```

## Day 3 — Saturday

**Active causes**

- `laundry_day` (household): Laundry day. the laundry basket travels, towels and the blanket get washed and end up airing in the bedroom rather than where they live.
- `distracted:resident_1`: Leo is distracted (0.72): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `running_late:resident_1`: Leo is running late all day (0.82): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Leo energy 0.36, hurriedness 0.82, distraction 0.72; Nora energy 0.42, hurriedness 0.18, distraction 0.22

**Timeline**

```
08:15  Leo — morning routine in the bathroom; brings phone_leo from nightstand_b1
08:39  Nora — morning routine in the bathroom; brings phone_nora from bed_b2
09:39  Leo — breakfast in the kitchen; brings mug_leo from dish_rack_k1
09:45  Nora — breakfast in the kitchen; brings mug_nora from sink_k1
10:14  Leo finishes breakfast
          mug_leo → sink_k1: used, so it goes in the sink
10:14  Leo — chores in the kitchen (bout 1/2); brings watering_can_shared from cupboard_k1
10:20  Nora finishes breakfast
          mug_nora → sink_k1: used, so it goes in the sink
10:20  Nora — chores in the kitchen
10:24  Leo finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_leo (from sink_k1) → cupboard_k1: tidied away to its usual place
          mug_nora (from sink_k1) → kitchen_table_k1: WHIM — was heading for cupboard_k1 (tidied away to its usual place) but landed on kitchen_table_k1 instead
          water_bottle_nora (from sink_k1) → kitchen_table_k1: WHIM — was heading for dish_rack_k1 (tidied away to its usual place) but landed on kitchen_table_k1 instead
10:24  Leo — a short break in the kitchen
10:36  Leo — chores in the kitchen (bout 2/2); brings watering_can_shared from cupboard_k1
11:14  Leo finishes chores
          mug_nora (from kitchen_table_k1) → cupboard_k1: tidied away to its usual place
          water_bottle_nora (from kitchen_table_k1) → cupboard_k1: WHIM — was heading for dish_rack_k1 (tidied away to its usual place) but landed on cupboard_k1 instead
11:34  Leo — laundry in the bathroom [because of laundry_day]; brings towel_leo from towel_rack_ba1, blanket_shared from couch_l1
11:40  Nora finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          water_bottle_nora (from cupboard_k1) → dish_rack_k1: tidied away to its usual place
          keeps phone_nora for errands
13:04  Leo finishes laundry
          blanket_shared → bed_b1: washed blanket airing on the bed [laundry_day]
          laundry_basket_shared → wardrobe_b1: WHIM — was heading for bedroom_floor_b1 (basket left in the bedroom while things dry) but landed on wardrobe_b1 instead [laundry_day]
          towel_leo → bed_b1: clean towel folded on the bed [laundry_day]
          keeps phone_leo for errands
13:04  Leo leaves for errands (back 15:04); takes handbag_leo, phone_leo, jacket_leo, shoes_leo; never takes wallet_leo on errands
          forgets keys_leo (still at entry_hook_e1, distracted today)
13:20  Nora leaves for errands (back 15:10); takes keys_nora, phone_nora, wallet_nora, jacket_nora, shoes_nora
15:04  Leo is back from errands
          handbag_leo → entry_table_e1: WHIM — was heading for entry_hook_e1 (put away in its usual place after the trip) but landed on entry_table_e1 instead
          jacket_leo → entry_hook_e1: put away in its usual place after the trip
          shoes_leo → entry_floor_e1: put away in its usual place after the trip
          keeps phone_leo for lunch
15:04  Leo — lunch in the kitchen
15:10  Nora is back from errands
          jacket_nora → entry_hook_e1: put away in its usual place after the trip
          keys_nora → entry_table_e1: put away in its usual place after the trip
          shoes_nora → entry_floor_e1: put away in its usual place after the trip
          wallet_nora → desk_b2: WHIM — was heading for nightstand_b2 (put away in its usual place after the trip) but landed on desk_b2 instead
          keeps phone_nora for lunch
15:10  Nora — lunch in the kitchen
15:44  Leo finishes lunch
          keeps phone_leo for the gym
15:50  Nora finishes lunch
          keeps phone_nora for a walk
16:27  Leo leaves for the gym (back 17:47); takes keys_leo, phone_leo, wallet_leo, jacket_leo, shoes_leo
16:49  Nora leaves for a walk (back 17:34); takes keys_nora, phone_nora, wallet_nora, jacket_nora, shoes_nora
17:34  Nora is back from a walk
          jacket_nora → entry_hook_e1: put away in its usual place after the trip
          keys_nora → entry_table_e1: put away in its usual place after the trip
          shoes_nora → entry_floor_e1: put away in its usual place after the trip
          wallet_nora → nightstand_b2: put away in its usual place after the trip
          keeps phone_nora for cooking dinner
17:47  Leo is back from the gym
          jacket_leo → entry_hook_e1: put away in its usual place after the trip
          keys_leo → entry_table_e1: put away in its usual place after the trip
          shoes_leo → entry_floor_e1: put away in its usual place after the trip
          wallet_leo → entry_table_e1: put away in its usual place after the trip
          keeps phone_leo for cooking dinner
18:54  Nora — cooking dinner in the kitchen
19:16  Leo — cooking dinner in the kitchen
19:34  Nora — dinner in the kitchen; brings water_bottle_nora from dish_rack_k1
19:56  Leo — dinner in the kitchen
20:19  Nora finishes dinner
          water_bottle_nora → sink_k1: used, so it goes in the sink
20:35  Nora — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from bed_b1, mug_nora from cupboard_k1
20:41  Leo — evening TV in the living; brings mug_leo from cupboard_k1
22:25  Nora finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
          mug_nora → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
22:31  Leo finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_leo → desk_b1: WHIM — was heading for nightstand_b1 (carried along absent-mindedly into the bedroom_1) but landed on desk_b1 instead [distracted:resident_1]
          phone_leo → nightstand_b1: carried along absent-mindedly into the bedroom_1 [distracted:resident_1]
          remote_shared → armchair_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on armchair_l1 instead
22:56  Nora — reading in the bedroom_2; brings book_nora from nightstand_b2
23:08  Leo — bed in the bedroom_1
23:26  Nora finishes reading
          book_nora → nightstand_b2: put back in its usual place
          phone_nora → nightstand_b2: put back in its usual place
23:41  Nora — bed in the bedroom_2
```

## Day 4 — Sunday

**Active causes**

- `guest_visit` (household): Friends come over for the evening. the living room is tidied beforehand, dinner is late, and the couch is taken by guests all evening.
- `laundry_day` (household): Laundry day. the laundry basket travels, towels and the blanket get washed and end up airing in the bedroom rather than where they live.
- `distracted:resident_1`: Leo is distracted (0.78): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `running_late:resident_1`: Leo is running late all day (0.97): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Leo energy 0.42, hurriedness 0.97, distraction 0.78; Nora energy 0.86, hurriedness 0.33, distraction 0.13

**Timeline**

```
08:38  Leo — morning routine in the bathroom; brings phone_leo from nightstand_b1
09:03  Leo — breakfast in the kitchen; brings mug_leo from desk_b1
09:14  Nora — morning routine in the bathroom; brings phone_nora from nightstand_b2
09:38  Leo finishes breakfast
          mug_leo → cupboard_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on cupboard_k1 instead
09:39  Nora — breakfast in the kitchen; brings mug_nora from sink_k1
10:14  Nora finishes breakfast
          mug_nora → sink_k1: used, so it goes in the sink
12:43  Leo — chores in the kitchen (bout 1/3); brings watering_can_shared from cupboard_k1
12:48  Nora — chores in the kitchen
12:54  Leo finishes chores
          watering_can_shared → kitchen_table_k1: WHIM — was heading for cupboard_k1 (tidied away to its usual place) but landed on kitchen_table_k1 instead
          mug_nora (from sink_k1) → cupboard_k1: tidied away to its usual place
          water_bottle_nora (from sink_k1) → dish_rack_k1: tidied away to its usual place
12:54  Leo — a short break in the kitchen
13:04  Leo — chores in the kitchen (bout 2/3); brings watering_can_shared from kitchen_table_k1
13:30  Leo finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
13:30  Leo — a short break in the kitchen
13:40  Leo — chores in the kitchen (bout 3/3); brings watering_can_shared from cupboard_k1
13:54  Leo finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
14:03  Leo — laundry in the bathroom (bout 1/2) [because of laundry_day]; brings laundry_basket_shared from wardrobe_b1, towel_leo from bed_b1, blanket_shared from couch_l1
14:08  Nora — lunch in the kitchen
14:13  Leo finishes laundry
          blanket_shared → bed_b1: washed blanket airing on the bed [laundry_day]
          laundry_basket_shared → bedroom_floor_b1: basket left in the bedroom while things dry [laundry_day]
          towel_leo → bed_b1: clean towel folded on the bed [laundry_day]
14:13  Leo — a short break in the kitchen [because of laundry_day]
14:40  Leo — laundry in the bathroom (bout 2/2) [because of laundry_day]; brings laundry_basket_shared from bedroom_floor_b1, towel_leo from bed_b1, blanket_shared from bed_b1
14:48  Nora finishes lunch
          keeps phone_nora for a walk
15:33  Leo finishes laundry
          blanket_shared → bed_b1: washed blanket airing on the bed [laundry_day]
          laundry_basket_shared → wardrobe_b1: WHIM — was heading for bedroom_floor_b1 (basket left in the bedroom while things dry) but landed on wardrobe_b1 instead [laundry_day]
          towel_leo → bedroom_floor_b1: WHIM — was heading for bed_b1 (clean towel folded on the bed) but landed on bedroom_floor_b1 instead [laundry_day]
          keeps phone_leo for errands
15:33  Leo leaves for errands (back 17:33); takes handbag_leo, keys_leo, phone_leo, jacket_leo, shoes_leo; never takes wallet_leo on errands
16:12  Nora leaves for a walk (back 16:57); takes keys_nora, phone_nora, wallet_nora, jacket_nora, shoes_nora
16:57  Nora is back from a walk
          jacket_nora → entry_hook_e1: put away in its usual place after the trip
          keys_nora → entry_table_e1: put away in its usual place after the trip
          phone_nora → entry_table_e1: dropped at the door instead of being put away
          shoes_nora → entry_floor_e1: put away in its usual place after the trip
          wallet_nora → nightstand_b2: put away in its usual place after the trip
17:33  Leo is back from errands
          handbag_leo → entry_table_e1: dropped at the door instead of being put away
          jacket_leo → entry_hook_e1: put away in its usual place after the trip
          keys_leo → entry_hook_e1: WHIM — was heading for entry_table_e1 (put away in its usual place after the trip) but landed on entry_hook_e1 instead
          shoes_leo → entry_floor_e1: put away in its usual place after the trip
          keeps phone_leo for lunch
17:33  Leo — lunch in the kitchen
17:43  Nora — tidying up in the living [because of guest_visit]
18:13  Leo finishes lunch
          phone_leo → coffee_table_l1: carried along absent-mindedly into the living [distracted:resident_1]
18:13  Nora finishes tidying up
          charger_leo (from entry_floor_e1) → desk_b1: tidied away to its usual place [guest_visit]
          handbag_leo (from entry_table_e1) → entry_hook_e1: tidied away to its usual place [guest_visit]
          keys_leo (from entry_hook_e1) → entry_table_e1: tidied away to its usual place [guest_visit]
          laptop_leo (from entry_floor_e1) → desk_b1: cleared away before the guests [guest_visit]
          laptop_nora (from coffee_table_l1) → desk_o1: cleared away before the guests [guest_visit]
          lunchbox_leo (from entry_floor_e1) → cupboard_k1: tidied away to its usual place [guest_visit]
          phone_leo (from coffee_table_l1) → nightstand_b1: tidied away to its usual place [guest_visit]
          phone_nora (from entry_table_e1) → nightstand_b2: tidied away to its usual place [guest_visit]
          remote_shared (from armchair_l1) → tv_stand_l1: tidied away to its usual place [guest_visit]
18:45  Leo — tidying up in the living [because of guest_visit]
19:03  Nora — cooking dinner in the kitchen [shifted by guest_visit]; brings phone_nora from nightstand_b2
19:15  Leo — cooking dinner in the kitchen [shifted by guest_visit]; brings phone_leo from nightstand_b1
19:49  Nora — dinner in the kitchen [shifted by guest_visit]; brings water_bottle_nora from dish_rack_k1
20:06  Leo — dinner in the kitchen [shifted by guest_visit]
20:34  Nora finishes dinner
          water_bottle_nora → sink_k1: used, so it goes in the sink
20:47  Nora — hosting the guests in the living [because of guest_visit]; brings mug_nora from cupboard_k1
20:51  Leo — hosting the guests in the living [because of guest_visit]; brings mug_leo from cupboard_k1
22:47  Nora finishes hosting the guests
          mug_nora → sink_k1: mugs collected into the sink after the guests [guest_visit]
          phone_nora → nightstand_b2: put back in its usual place [guest_visit]
22:51  Leo finishes hosting the guests
          mug_leo → sink_k1: mugs collected into the sink after the guests [guest_visit]
          phone_leo → desk_b1: WHIM — was heading for nightstand_b1 (carried along absent-mindedly into the bedroom_1) but landed on desk_b1 instead [distracted:resident_1, guest_visit]
23:19  Leo — bed in the bedroom_1
23:34  Nora — bed in the bedroom_2
```
