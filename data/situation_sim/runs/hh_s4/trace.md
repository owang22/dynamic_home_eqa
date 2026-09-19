# Household hh_s4 — five days, Wednesday to Sunday

Seed-generated household. Times are clock times; ids are the receptacle and object ids used in events.jsonl. A line indented under an activity says where an object went when the activity ended and why. WHIM marks a placement that landed somewhere other than where the decision was heading. Text in [brackets] names the hidden cause the decision is attributed to.

## Household

Type: flatmates. Rooms: bathroom, bedroom_1, bedroom_2, bedroom_3, entry, kitchen, living.

Residents:

- **Marco** (resident_1): works from home; untidy (tidiness 0.42); erratic timing (jitter scale 1.41); rarely forgets pocket items; mood barely affects behaviour (sensitivity 0.25); sleeps in bedroom_1, works at the bedroom_1 desk
- **Nora** (resident_2): works outside the home; very tidy (tidiness 0.93); average timing (jitter scale 0.89); often forgets pocket items; mood moderately affects behaviour (sensitivity 0.64); sleeps in bedroom_2, works at the bedroom_2 desk
- **Tomas** (resident_3): retired; fairly tidy (tidiness 0.71); average timing (jitter scale 0.93); often forgets pocket items; mood moderately affects behaviour (sensitivity 0.45); sleeps in bedroom_3, works at the bedroom_3 desk

Objects and their usual place (primary slot first):

- Marco's: book_marco → nightstand_b1 / bookshelf_l1; glasses_marco → nightstand_b1 / desk_b1; gym_bag_marco → wardrobe_b1 / bedroom_floor_b1; jacket_marco → entry_hook_e1 / wardrobe_b1; keys_marco → entry_table_e1 / nightstand_b1; laptop_marco → desk_b1 / bookshelf_l1; mug_marco → cupboard_k1 / dish_rack_k1 / sink_k1; notebook_marco → desk_b1 / bookshelf_l1; phone_marco → nightstand_b1 / coffee_table_l1; shoes_marco → entry_floor_e1 / wardrobe_b1; towel_marco → towel_rack_ba1 / bathroom_shelf_ba1; umbrella_marco → entry_floor_e1 / entry_hook_e1; wallet_marco → nightstand_b1 / desk_b1; water_bottle_marco → dish_rack_k1 / counter_k1 / sink_k1
- Nora's: backpack_nora → entry_hook_e1 / bedroom_floor_b2 / desk_b2; book_nora → nightstand_b2 / bookshelf_l1; charger_nora → desk_b2 / nightstand_b2; gym_bag_nora → wardrobe_b2 / bedroom_floor_b2; headphones_nora → desk_b2 / nightstand_b2; jacket_nora → entry_hook_e1 / wardrobe_b2; keys_nora → entry_table_e1 / nightstand_b2; laptop_nora → desk_b2 / bookshelf_l1; mug_nora → cupboard_k1 / dish_rack_k1 / sink_k1; phone_nora → nightstand_b2 / coffee_table_l1; shoes_nora → entry_floor_e1 / wardrobe_b2; towel_nora → towel_rack_ba1 / bathroom_shelf_ba1; umbrella_nora → entry_floor_e1 / entry_hook_e1; wallet_nora → entry_table_e1 / desk_b2; water_bottle_nora → dish_rack_k1 / counter_k1 / sink_k1
- Tomas's: book_tomas → nightstand_b3 / bookshelf_l1; glasses_tomas → nightstand_b3 / desk_b3; headphones_tomas → desk_b3 / nightstand_b3; jacket_tomas → entry_hook_e1 / wardrobe_b3; keys_tomas → entry_table_e1 / nightstand_b3; mug_tomas → cupboard_k1 / dish_rack_k1 / sink_k1; phone_tomas → nightstand_b3 / coffee_table_l1; shoes_tomas → entry_floor_e1 / wardrobe_b3; towel_tomas → towel_rack_ba1 / bathroom_shelf_ba1; umbrella_tomas → entry_floor_e1 / entry_hook_e1; wallet_tomas → nightstand_b3 / desk_b3; water_bottle_tomas → dish_rack_k1 / counter_k1 / sink_k1
- Shared: blanket_shared → couch_l1 / armchair_l1; laundry_basket_shared → bathroom_shelf_ba1 / bedroom_floor_b1; remote_shared → tv_stand_l1 / coffee_table_l1; watering_can_shared → cupboard_k1 / counter_k1

Object groups (things that travel together):

- backpack_nora carries charger_nora, laptop_nora on trips to work and errands
- gym_bag_marco carries water_bottle_marco on gym trips
- gym_bag_nora carries water_bottle_nora on gym trips


## Day 0 — Wednesday

**Active causes**

- `grocery_delivery` (household): A grocery delivery arrives in the early evening. someone unpacks groceries; the kitchen counter is covered with bags, so things that would go there land on the table instead.
- `late_work:resident_2` (Nora): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `running_late:resident_2`: Nora is running late all day (1.00): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Marco energy 0.53, hurriedness 0.08, distraction 0.51; Nora energy 0.61, hurriedness 1.00, distraction 0.41; Tomas energy 0.53, hurriedness 0.43, distraction 0.30

**Timeline**

```
07:04  Marco — morning routine in the bathroom; brings phone_marco from nightstand_b1, glasses_marco from nightstand_b1
07:10  Nora — morning routine in the bathroom; brings phone_nora from nightstand_b2
07:29  Marco finishes morning routine
          glasses_marco → nightstand_b1: put back in its usual place
07:32  Marco — breakfast in the kitchen; brings mug_marco from cupboard_k1
07:35  Nora — breakfast in the kitchen; brings mug_nora from cupboard_k1
07:44  Tomas — morning routine in the bathroom; brings phone_tomas from nightstand_b3, glasses_tomas from nightstand_b3
08:00  Nora finishes breakfast
          keeps phone_nora for work
08:11  Nora leaves for work (back 19:41); takes backpack_nora (with charger_nora, laptop_nora), keys_nora, phone_nora, wallet_nora, jacket_nora, shoes_nora
08:14  Tomas finishes morning routine
          glasses_tomas → nightstand_b3: put back in its usual place
08:14  Tomas — breakfast in the kitchen; brings mug_tomas from cupboard_k1
08:59  Marco — work session in the bedroom_1 (bout 1/2); brings mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
10:19  Tomas — chores in the kitchen (bout 1/3); brings watering_can_shared from cupboard_k1
10:38  Marco finishes work session
          glasses_marco → nightstand_b1: put back in its usual place
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
10:38  Marco — a short break in the kitchen
10:55  Tomas finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
10:55  Tomas — a short break in the kitchen
11:08  Tomas — chores in the kitchen (bout 2/3); brings watering_can_shared from cupboard_k1
11:18  Tomas finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_marco (from kitchen_table_k1) → dish_rack_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on dish_rack_k1 instead [grocery_delivery]
11:18  Tomas — a short break in the kitchen
11:31  Tomas — chores in the kitchen (bout 3/3); brings watering_can_shared from cupboard_k1
11:38  Marco — work session in the bedroom_1 (bout 2/2); brings mug_marco from dish_rack_k1, glasses_marco from nightstand_b1
11:49  Tomas finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
12:18  Marco finishes work session
          glasses_marco → nightstand_b1: put back in its usual place
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          keeps phone_marco for lunch out
12:44  Tomas — lunch in the kitchen
13:10  Marco leaves for lunch out (back 14:10); takes keys_marco, phone_marco, wallet_marco, jacket_marco, shoes_marco
13:29  Tomas — reading in the bedroom_3; brings book_tomas from nightstand_b3, glasses_tomas from nightstand_b3
14:10  Marco is back from lunch out
          jacket_marco → entry_hook_e1: put away in its usual place after the trip
          keys_marco → entry_hook_e1: WHIM — was heading for entry_table_e1 (put away in its usual place after the trip) but landed on entry_hook_e1 instead
          shoes_marco → entry_floor_e1: put away in its usual place after the trip
          wallet_marco → entry_table_e1: dropped at the door instead of being put away
          keeps phone_marco for work session
14:44  Tomas finishes reading
          book_tomas → nightstand_b3: put back in its usual place
          glasses_tomas → nightstand_b3: put back in its usual place
          keeps phone_tomas for errands
14:45  Marco — work session in the bedroom_1 (bout 1/3); brings mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
15:44  Marco finishes work session
          glasses_marco → bed_b1: left where it was used; desk_b1 was full, so it went to bed_b1
          laptop_marco → bed_b1: WHIM — was heading for desk_b1 (put back in its usual place) but landed on bed_b1 instead
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
15:44  Marco — a short break in the kitchen
15:54  Tomas leaves for errands (back 17:24); takes phone_tomas, jacket_tomas, shoes_tomas; never takes keys_tomas, wallet_tomas on errands
16:18  Marco — work session in the bedroom_1 (bout 2/3); brings laptop_marco from bed_b1, mug_marco from kitchen_table_k1, glasses_marco from bed_b1
16:47  Marco finishes work session
          glasses_marco → bed_b1: left where it was used; desk_b1 was full, so it went to bed_b1
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
16:47  Marco — a short break in the kitchen
17:21  Marco — work session in the bedroom_1 (bout 3/3); brings mug_marco from kitchen_table_k1, glasses_marco from bed_b1
17:24  Tomas is back from errands
          jacket_tomas → entry_hook_e1: put away in its usual place after the trip
          shoes_tomas → entry_floor_e1: put away in its usual place after the trip
          keeps phone_tomas for cooking dinner
18:33  Marco finishes work session
          glasses_marco → nightstand_b1: WHIM — was heading for bed_b1 (left where it was used; desk_b1 was full, so it went to bed_b1) but landed on nightstand_b1 instead
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          keeps phone_marco for a walk
18:45  Tomas — cooking dinner in the kitchen [shifted by grocery_delivery]
19:30  Tomas finishes cooking dinner
          phone_tomas → nightstand_b3: put back in its usual place
19:30  Tomas — unpacking groceries in the kitchen [because of grocery_delivery]; brings water_bottle_tomas from dish_rack_k1
19:41  Nora is back from work
          backpack_nora → entry_floor_e1: bag dumped by the door, home late [late_work:resident_2]
          charger_nora → entry_floor_e1: stays in the backpack
          jacket_nora → couch_l1: jacket thrown over the couch, home late [late_work:resident_2]
          keys_nora → entry_table_e1: put away in its usual place after the trip
          laptop_nora → entry_floor_e1: stays in the backpack
          shoes_nora → wardrobe_b2: put away in its usual place after the trip; entry_floor_e1 was full, so it went to wardrobe_b2
          wallet_nora → entry_table_e1: put away in its usual place after the trip
          keeps phone_nora for dinner
19:41  Nora — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_nora from dish_rack_k1
20:00  Tomas — dinner in the kitchen [shifted by grocery_delivery]; brings phone_tomas from nightstand_b3
20:21  Nora finishes dinner
          water_bottle_nora → counter_k1: WHIM — was heading for dish_rack_k1 (counter full of shopping; bottle put on the dish rack) but landed on counter_k1 instead [grocery_delivery]
20:21  Nora — evening TV in the living [shifted by late_work:resident_2]; brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_nora from kitchen_table_k1
20:45  Tomas finishes dinner
          water_bottle_tomas → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
21:09  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_nora → nightstand_b2: put back in its usual place
          remote_shared → couch_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on couch_l1 instead
21:44  Marco leaves for a walk (back 22:24); takes keys_marco, wallet_marco, jacket_marco, shoes_marco; never takes phone_marco on a walk
21:45  Tomas — evening TV in the living (bout 1/2); brings remote_shared from couch_l1, blanket_shared from couch_l1, mug_tomas from kitchen_table_k1, glasses_tomas from nightstand_b3
22:14  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
22:14  Tomas — a short break in the kitchen
22:24  Marco is back from a walk
          jacket_marco → entry_hook_e1: put away in its usual place after the trip
          keys_marco → entry_table_e1: put away in its usual place after the trip
          shoes_marco → entry_floor_e1: put away in its usual place after the trip
          wallet_marco → nightstand_b1: put away in its usual place after the trip
22:24  Marco — cooking dinner in the kitchen [shifted by grocery_delivery]
22:50  Tomas — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_tomas from kitchen_table_k1
22:59  Marco — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_marco from dish_rack_k1
23:06  Nora — bed in the bedroom_2
23:39  Marco finishes dinner
          water_bottle_marco → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
23:39  Marco — evening TV in the living; brings mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
23:44  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_tomas → desk_b3: WHIM — was heading for nightstand_b3 (put back in its usual place) but landed on desk_b3 instead
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_tomas → nightstand_b3: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
23:45  Tomas — bed in the bedroom_3
23:59  Marco finishes evening TV
          glasses_marco → nightstand_b1: put back in its usual place
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_marco → coffee_table_l1: left where it was used
```

## Day 1 — Thursday

**Active causes**

- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `low_energy:resident_3`: Tomas has low energy (0.30): leaves things where they were used instead of putting them back.
- `running_late:resident_2`: Nora is running late all day (0.92): rushed putdowns, things dumped at the door, more whim.
- `running_late:resident_3`: Tomas is running late all day (0.71): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Marco energy 0.78, hurriedness 0.22, distraction 0.58; Nora energy 0.63, hurriedness 0.92, distraction 0.19; Tomas energy 0.30, hurriedness 0.71, distraction 0.42

**Timeline**

```
06:26  Nora — morning routine in the bathroom; brings phone_nora from nightstand_b2
06:57  Nora — breakfast in the kitchen
07:22  Nora finishes breakfast
          mug_nora → sink_k1: used, so it goes in the sink
          keeps phone_nora for work
07:52  Tomas — morning routine in the bathroom; brings phone_tomas from nightstand_b3, glasses_tomas from desk_b3
08:14  Nora leaves for work (back 17:44); takes backpack_nora (with charger_nora, laptop_nora), keys_nora, phone_nora, wallet_nora, jacket_nora, shoes_nora, umbrella_nora
08:19  Marco — morning routine in the bathroom; brings phone_marco from coffee_table_l1, glasses_marco from nightstand_b1
08:22  Tomas finishes morning routine
          glasses_tomas → nightstand_b3: put back in its usual place
08:22  Tomas — breakfast in the kitchen
08:44  Marco finishes morning routine
          glasses_marco → nightstand_b1: put back in its usual place
08:44  Marco — breakfast in the kitchen
09:02  Tomas finishes breakfast
          mug_tomas → sink_k1: used, so it goes in the sink
10:15  Marco — work session in the bedroom_1 (bout 1/2); brings mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
10:43  Marco finishes work session
          glasses_marco → bed_b1: left where it was used; desk_b1 was full, so it went to bed_b1
          mug_marco → sink_k1: used, so it goes in the sink
10:43  Marco — a short break in the kitchen
10:52  Tomas — chores in the kitchen (bout 1/2); brings watering_can_shared from cupboard_k1
11:27  Tomas finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_nora (from sink_k1) → cupboard_k1: tidied away to its usual place
          mug_tomas (from sink_k1) → cupboard_k1: tidied away to its usual place
          water_bottle_nora (from counter_k1) → dish_rack_k1: tidied away to its usual place
11:27  Tomas — a short break in the kitchen
11:40  Tomas — chores in the kitchen (bout 2/2); brings watering_can_shared from cupboard_k1
11:43  Marco — work session in the bedroom_1 (bout 2/2); brings mug_marco from sink_k1, glasses_marco from bed_b1
12:04  Tomas finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
13:19  Tomas — lunch in the kitchen
13:34  Marco finishes work session
          glasses_marco → bed_b1: left where it was used; desk_b1 was full, so it went to bed_b1
          mug_marco → sink_k1: used, so it goes in the sink
13:35  Marco — lunch in the kitchen
14:04  Tomas — reading in the bedroom_3; brings book_tomas from nightstand_b3, glasses_tomas from nightstand_b3
14:15  Marco — work session in the bedroom_1; brings mug_marco from sink_k1, glasses_marco from bed_b1
15:19  Tomas finishes reading
          book_tomas → desk_b3: WHIM — was heading for nightstand_b3 (put back in its usual place) but landed on desk_b3 instead
          glasses_tomas → nightstand_b3: put back in its usual place
17:44  Nora is back from work
          backpack_nora → entry_floor_e1: wet bag left by the door [rain]
          charger_nora → entry_floor_e1: stays in the backpack
          jacket_nora → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_nora → entry_table_e1: put away in its usual place after the trip
          laptop_nora → entry_floor_e1: stays in the backpack
          shoes_nora → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          umbrella_nora → entry_table_e1: WHIM — was heading for entry_hook_e1 (wet umbrella propped by the door; entry_floor_e1 was full, so it went to entry_hook_e1) but landed on entry_table_e1 instead [rain]
          wallet_nora → entry_table_e1: put away in its usual place after the trip
          keeps phone_nora for cooking dinner
18:05  Marco finishes work session
          glasses_marco → bed_b1: left where it was used; desk_b1 was full, so it went to bed_b1
          mug_marco → sink_k1: used, so it goes in the sink
18:26  Tomas — cooking dinner in the kitchen
19:11  Tomas — dinner in the kitchen; brings water_bottle_tomas from dish_rack_k1
19:13  Marco — cooking dinner in the kitchen
19:18  Nora — cooking dinner in the kitchen
19:53  Nora — dinner in the kitchen; brings water_bottle_nora from dish_rack_k1
19:56  Tomas finishes dinner
          water_bottle_tomas → sink_k1: used, so it goes in the sink
19:56  Tomas — evening TV in the living (bout 1/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_tomas from cupboard_k1, glasses_tomas from nightstand_b3
20:30  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_tomas → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
20:30  Tomas — a short break in the kitchen
20:33  Nora finishes dinner
          water_bottle_nora → sink_k1: used, so it goes in the sink
20:33  Nora — evening TV in the living (bout 1/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_nora from cupboard_k1
20:39  Marco — dinner in the kitchen; brings water_bottle_marco from dish_rack_k1
20:42  Tomas — evening TV in the living (bout 2/4); brings mug_tomas from sink_k1
21:00  Tomas finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          glasses_tomas → desk_b3: left where it was used; coffee_table_l1 was full, so it went to desk_b3
          mug_tomas → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
21:00  Tomas — a short break in the kitchen
21:12  Tomas — evening TV in the living (bout 3/4); brings remote_shared from tv_stand_l1, blanket_shared from armchair_l1, mug_tomas from sink_k1, glasses_tomas from desk_b3
21:19  Marco — evening TV in the living; brings mug_marco from sink_k1, glasses_marco from bed_b1
21:24  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
21:24  Nora — a short break in the kitchen
21:29  Tomas finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
          glasses_tomas → nightstand_b3: put back in its usual place
          mug_tomas → sink_k1: used, so it goes in the sink
          remote_shared → coffee_table_l1: left where it was used
21:29  Tomas — a short break in the kitchen
21:38  Nora — evening TV in the living (bout 2/2); brings blanket_shared from armchair_l1, mug_nora from sink_k1
21:41  Tomas — evening TV in the living (bout 4/4); brings mug_tomas from sink_k1, glasses_tomas from nightstand_b3
21:48  Nora finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
          mug_nora → sink_k1: used, so it goes in the sink
          phone_nora → nightstand_b2: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
21:55  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_tomas → bed_b3: WHIM — was heading for nightstand_b3 (put back in its usual place) but landed on bed_b3 instead
          mug_tomas → counter_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on counter_k1 instead
          phone_tomas → bed_b3: WHIM — was heading for nightstand_b3 (put back in its usual place) but landed on bed_b3 instead
22:08  Nora — bed in the bedroom_2
22:17  Tomas — bed in the bedroom_3
22:49  Marco finishes evening TV
          mug_marco → sink_k1: used, so it goes in the sink
22:49  Marco — reading in the bedroom_1; brings book_marco from nightstand_b1, glasses_marco from coffee_table_l1
23:19  Marco finishes reading
          book_marco → nightstand_b1: put back in its usual place
          glasses_marco → nightstand_b1: put back in its usual place
          phone_marco → nightstand_b1: put back in its usual place
23:19  Marco — bed in the bedroom_1
```

## Day 2 — Friday

**Active causes**

- `grocery_delivery` (household): A grocery delivery arrives in the early evening. someone unpacks groceries; the kitchen counter is covered with bags, so things that would go there land on the table instead.
- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `low_energy:resident_1`: Marco has low energy (0.15): leaves things where they were used instead of putting them back.
- `running_late:resident_2`: Nora is running late all day (1.00): rushed putdowns, things dumped at the door, more whim.
- `running_late:resident_3`: Tomas is running late all day (0.89): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Marco energy 0.15, hurriedness 0.42, distraction 0.65; Nora energy 0.69, hurriedness 1.00, distraction 0.00; Tomas energy 0.52, hurriedness 0.89, distraction 0.45

**Timeline**

```
06:53  Tomas — morning routine in the bathroom; brings phone_tomas from bed_b3, glasses_tomas from bed_b3
07:23  Tomas finishes morning routine
          glasses_tomas → nightstand_b3: put back in its usual place
07:28  Tomas — breakfast in the kitchen; brings mug_tomas from counter_k1
07:38  Nora — morning routine in the bathroom; brings phone_nora from nightstand_b2
07:58  Nora finishes morning routine
          keeps phone_nora for work
07:58  Nora leaves for work (back 17:28); takes backpack_nora (with charger_nora, laptop_nora), keys_nora, phone_nora, wallet_nora, jacket_nora, shoes_nora, umbrella_nora
08:12  Marco — morning routine in the bathroom; brings phone_marco from nightstand_b1, glasses_marco from nightstand_b1
08:37  Marco finishes morning routine
          glasses_marco → nightstand_b1: put back in its usual place
08:37  Marco — breakfast in the kitchen; brings mug_marco from sink_k1
09:14  Tomas — chores in the kitchen (bout 1/4); brings watering_can_shared from cupboard_k1
09:24  Tomas finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_nora (from sink_k1) → dish_rack_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on dish_rack_k1 instead [grocery_delivery]
          water_bottle_marco (from kitchen_table_k1) → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
          water_bottle_nora (from sink_k1) → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
          water_bottle_tomas (from sink_k1) → kitchen_table_k1: WHIM — was heading for dish_rack_k1 (counter full of shopping; bottle put on the dish rack) but landed on kitchen_table_k1 instead [grocery_delivery]
09:24  Tomas — a short break in the kitchen
09:34  Tomas — chores in the kitchen (bout 2/4); brings watering_can_shared from cupboard_k1
09:44  Tomas finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_nora (from dish_rack_k1) → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          water_bottle_tomas (from kitchen_table_k1) → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
09:44  Tomas — a short break in the kitchen
09:47  Marco — work session in the bedroom_1; brings mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
09:54  Tomas — chores in the kitchen (bout 3/4); brings watering_can_shared from cupboard_k1
10:12  Tomas finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
10:12  Tomas — a short break in the kitchen
10:22  Tomas — chores in the kitchen (bout 4/4); brings watering_can_shared from cupboard_k1
10:44  Tomas finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
12:56  Tomas — lunch in the kitchen
13:07  Marco finishes work session
          glasses_marco → nightstand_b1: put back in its usual place
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          keeps phone_marco for lunch out
13:07  Marco leaves for lunch out (back 14:07); takes keys_marco, phone_marco, wallet_marco, jacket_marco, shoes_marco, umbrella_marco
14:07  Marco is back from lunch out
          jacket_marco → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_marco → entry_table_e1: put away in its usual place after the trip
          shoes_marco → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          umbrella_marco → entry_floor_e1: wet umbrella propped by the door [rain]
          wallet_marco → desk_b1: WHIM — was heading for nightstand_b1 (put away in its usual place after the trip) but landed on desk_b1 instead
          keeps phone_marco for work session
14:07  Marco — work session in the bedroom_1 (bout 1/6); brings mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
14:16  Tomas — reading in the bedroom_3; brings book_tomas from desk_b3, glasses_tomas from nightstand_b3
14:17  Marco finishes work session
          glasses_marco → bed_b1: left where it was used, too tired to put it away; desk_b1 was full, so it went to bed_b1 [low_energy:resident_1]
          laptop_marco → bookshelf_l1: put back in its usual place; desk_b1 was full, so it went to bookshelf_l1
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
14:17  Marco — a short break in the kitchen
14:30  Marco — work session in the bedroom_1 (bout 2/6); brings laptop_marco from bookshelf_l1, mug_marco from kitchen_table_k1, glasses_marco from bed_b1
15:31  Tomas finishes reading
          glasses_tomas → bedroom_floor_b3: WHIM — was heading for nightstand_b3 (put back in its usual place) but landed on bedroom_floor_b3 instead
          keeps phone_tomas for errands
15:31  Tomas leaves for errands (back 16:25); takes phone_tomas, jacket_tomas, shoes_tomas, umbrella_tomas; never takes keys_tomas, wallet_tomas on errands
16:09  Marco finishes work session
          glasses_marco → nightstand_b1: put back in its usual place
          laptop_marco → bookshelf_l1: put back in its usual place; desk_b1 was full, so it went to bookshelf_l1
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
16:09  Marco — a short break in the kitchen
16:22  Marco — work session in the bedroom_1 (bout 3/6); brings laptop_marco from bookshelf_l1, mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
16:25  Tomas is back from errands
          jacket_tomas → entry_hook_e1: wet jacket hung on the hook [rain]
          shoes_tomas → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          umbrella_tomas → entry_floor_e1: wet umbrella propped by the door [rain]
          keeps phone_tomas for cooking dinner
16:32  Marco finishes work session
          glasses_marco → nightstand_b1: put back in its usual place
          laptop_marco → couch_l1: WHIM — was heading for bookshelf_l1 (put back in its usual place; desk_b1 was full, so it went to bookshelf_l1) but landed on couch_l1 instead
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
16:32  Marco — a short break in the kitchen
16:45  Marco — work session in the bedroom_1 (bout 4/6); brings laptop_marco from couch_l1, mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
16:56  Marco finishes work session
          glasses_marco → bed_b1: left where it was used; desk_b1 was full, so it went to bed_b1
          laptop_marco → bookshelf_l1: put back in its usual place; desk_b1 was full, so it went to bookshelf_l1
          mug_marco → dish_rack_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on dish_rack_k1 instead [grocery_delivery]
16:56  Marco — a short break in the kitchen
17:09  Marco — work session in the bedroom_1 (bout 5/6); brings laptop_marco from bookshelf_l1, mug_marco from dish_rack_k1, glasses_marco from bed_b1
17:28  Nora is back from work
          backpack_nora → entry_hook_e1: WHIM — was heading for entry_floor_e1 (wet bag left by the door) but landed on entry_hook_e1 instead [rain]
          charger_nora → entry_hook_e1: stays in the backpack
          jacket_nora → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_nora → entry_table_e1: put away in its usual place after the trip
          laptop_nora → entry_hook_e1: stays in the backpack
          shoes_nora → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          umbrella_nora → entry_floor_e1: wet umbrella propped by the door [rain]
          wallet_nora → entry_table_e1: put away in its usual place after the trip
          keeps phone_nora for cooking dinner
17:32  Tomas — cooking dinner in the kitchen [shifted by grocery_delivery]
17:34  Marco finishes work session
          glasses_marco → nightstand_b1: put back in its usual place
          laptop_marco → bookshelf_l1: put back in its usual place; desk_b1 was full, so it went to bookshelf_l1
          mug_marco → sink_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on sink_k1 instead [grocery_delivery]
17:34  Marco — a short break in the kitchen
17:47  Marco — work session in the bedroom_1 (bout 6/6); brings laptop_marco from bookshelf_l1, mug_marco from sink_k1, glasses_marco from nightstand_b1
17:57  Marco finishes work session
          glasses_marco → nightstand_b1: put back in its usual place
          laptop_marco → bookshelf_l1: put back in its usual place; desk_b1 was full, so it went to bookshelf_l1
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_marco → desk_b1: left where it was used
17:57  Marco — unpacking groceries in the kitchen [because of grocery_delivery]; brings water_bottle_marco from dish_rack_k1
18:27  Marco finishes unpacking groceries
          water_bottle_marco → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
18:50  Marco — cooking dinner in the kitchen [shifted by grocery_delivery]; brings phone_marco from desk_b1
18:57  Nora — cooking dinner in the kitchen [shifted by grocery_delivery]
19:02  Tomas — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_tomas from dish_rack_k1
19:25  Marco — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_marco from dish_rack_k1
19:46  Nora — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_nora from dish_rack_k1
19:47  Tomas finishes dinner
          water_bottle_tomas → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
19:47  Tomas — evening TV in the living (bout 1/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_tomas from kitchen_table_k1, glasses_tomas from bedroom_floor_b3
19:57  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_tomas → nightstand_b3: put back in its usual place
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
19:57  Tomas — a short break in the kitchen
20:05  Marco finishes dinner
          water_bottle_marco → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
20:05  Marco — evening TV in the living (bout 1/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
20:26  Nora finishes dinner
          water_bottle_nora → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
20:26  Nora — evening TV in the living (bout 1/2); brings mug_nora from kitchen_table_k1
20:33  Tomas — evening TV in the living (bout 2/2); brings mug_tomas from kitchen_table_k1, glasses_tomas from nightstand_b3
20:45  Marco finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          glasses_marco → nightstand_b1: put back in its usual place
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
20:45  Marco — a short break in the kitchen
20:58  Marco — evening TV in the living (bout 2/3); brings remote_shared from armchair_l1, blanket_shared from armchair_l1, mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
21:08  Marco finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
          glasses_marco → nightstand_b1: put back in its usual place
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
21:08  Marco — a short break in the kitchen
21:20  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
21:20  Nora — a short break in the kitchen
21:21  Marco — evening TV in the living (bout 3/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
21:35  Marco finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
21:47  Tomas finishes evening TV
          glasses_tomas → nightstand_b3: put back in its usual place
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_tomas → nightstand_b3: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
21:47  Tomas — bed in the bedroom_3
21:48  Nora — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_nora from kitchen_table_k1
22:00  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
22:01  Nora — reading in the bedroom_2; brings book_nora from nightstand_b2
22:26  Marco — reading in the bedroom_1; brings book_marco from nightstand_b1, glasses_marco from coffee_table_l1
22:31  Nora finishes reading
          book_nora → nightstand_b2: put back in its usual place
          phone_nora → nightstand_b2: put back in its usual place
22:31  Nora — bed in the bedroom_2
22:56  Marco finishes reading
          book_marco → nightstand_b1: put back in its usual place
          glasses_marco → nightstand_b1: put back in its usual place
          phone_marco → bed_b1: left where it was used
22:56  Marco — bed in the bedroom_1
```

## Day 3 — Saturday

**Active causes**

- `grocery_delivery` (household): A grocery delivery arrives in the early evening. someone unpacks groceries; the kitchen counter is covered with bags, so things that would go there land on the table instead.
- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `running_late:resident_2`: Nora is running late all day (0.70): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Marco energy 0.32, hurriedness 0.61, distraction 0.62; Nora energy 0.53, hurriedness 0.70, distraction 0.00; Tomas energy 0.53, hurriedness 0.48, distraction 0.44

**Timeline**

```
07:30  Tomas — morning routine in the bathroom; brings phone_tomas from nightstand_b3, glasses_tomas from nightstand_b3
08:00  Tomas finishes morning routine
          glasses_tomas → nightstand_b3: put back in its usual place
08:00  Tomas — breakfast in the kitchen
08:57  Nora — morning routine in the bathroom; brings phone_nora from nightstand_b2
09:34  Nora — breakfast in the kitchen
09:49  Marco — morning routine in the bathroom; brings phone_marco from bed_b1, glasses_marco from nightstand_b1
10:09  Nora — chores in the kitchen (bout 1/2); brings watering_can_shared from cupboard_k1
10:14  Marco finishes morning routine
          glasses_marco → nightstand_b1: put back in its usual place
10:14  Marco — breakfast in the kitchen
10:32  Nora finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
10:32  Nora — a short break in the kitchen
10:56  Nora — chores in the kitchen (bout 2/2); brings watering_can_shared from cupboard_k1
11:28  Nora finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
12:25  Tomas — lunch in the kitchen
13:10  Tomas — reading in the bedroom_3; brings glasses_tomas from nightstand_b3
14:40  Tomas finishes reading
          book_tomas → nightstand_b3: put back in its usual place
          glasses_tomas → nightstand_b3: put back in its usual place
14:40  Nora — lunch in the kitchen
14:55  Marco — chores in the kitchen (bout 1/2); brings watering_can_shared from cupboard_k1
15:41  Marco finishes chores
          watering_can_shared → dish_rack_k1: WHIM — was heading for cupboard_k1 (tidied away to its usual place) but landed on dish_rack_k1 instead
          mug_nora (from kitchen_table_k1) → sink_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on sink_k1 instead [grocery_delivery]
15:41  Marco — a short break in the kitchen
16:05  Marco — chores in the kitchen (bout 2/2); brings watering_can_shared from dish_rack_k1
16:15  Marco finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_nora (from sink_k1) → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
16:15  Marco — lunch in the kitchen
16:55  Marco finishes lunch
          phone_marco → kitchen_table_k1: left where it was used
17:44  Tomas — cooking dinner in the kitchen [shifted by grocery_delivery]
18:03  Marco — unpacking groceries in the kitchen [because of grocery_delivery]; brings water_bottle_marco from dish_rack_k1
18:33  Marco finishes unpacking groceries
          water_bottle_marco → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
18:41  Marco — cooking dinner in the kitchen [shifted by grocery_delivery]; brings phone_marco from kitchen_table_k1
18:51  Nora — cooking dinner in the kitchen [shifted by grocery_delivery]
19:04  Tomas — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_tomas from dish_rack_k1
19:21  Marco — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_marco from dish_rack_k1
19:31  Nora — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_nora from dish_rack_k1
19:54  Tomas finishes dinner
          water_bottle_tomas → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
19:54  Tomas — evening TV in the living (bout 1/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_tomas from kitchen_table_k1, glasses_tomas from nightstand_b3
20:04  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_tomas → nightstand_b3: put back in its usual place
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
20:04  Tomas — a short break in the kitchen
20:06  Marco finishes dinner
          water_bottle_marco → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
20:16  Nora finishes dinner
          water_bottle_nora → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
20:16  Nora — evening TV in the living (bout 1/4); brings blanket_shared from couch_l1, mug_nora from kitchen_table_k1
20:16  Tomas — evening TV in the living (bout 2/4); brings mug_tomas from kitchen_table_k1, glasses_tomas from nightstand_b3
20:26  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
20:26  Tomas finishes evening TV
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
20:26  Nora — a short break in the kitchen
20:26  Tomas — a short break in the kitchen
20:36  Nora — evening TV in the living (bout 2/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_nora from kitchen_table_k1
20:38  Tomas — evening TV in the living (bout 3/4); brings mug_tomas from kitchen_table_k1
20:46  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
20:46  Nora — a short break in the kitchen
20:51  Marco — evening TV in the living (bout 1/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
20:56  Nora — evening TV in the living (bout 3/4); brings mug_nora from kitchen_table_k1
21:06  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
21:06  Nora — a short break in the kitchen
21:09  Marco finishes evening TV
          glasses_marco → nightstand_b1: put back in its usual place
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
21:09  Marco — a short break in the kitchen
21:16  Nora — evening TV in the living (bout 4/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_nora from kitchen_table_k1
21:20  Marco — evening TV in the living (bout 2/3); brings mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
21:26  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_tomas → bedroom_floor_b3: WHIM — was heading for nightstand_b3 (put back in its usual place) but landed on bedroom_floor_b3 instead
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
21:26  Tomas — a short break in the kitchen
21:38  Tomas — evening TV in the living (bout 4/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_tomas from kitchen_table_k1, glasses_tomas from bedroom_floor_b3
21:43  Marco finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_marco → bedroom_floor_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bedroom_floor_b1 instead
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
21:43  Marco — a short break in the kitchen
21:54  Tomas finishes evening TV
          glasses_tomas → nightstand_b3: put back in its usual place
          mug_tomas → counter_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on counter_k1 instead [grocery_delivery]
          phone_tomas → nightstand_b3: put back in its usual place
          remote_shared → coffee_table_l1: left where it was used
21:54  Marco — evening TV in the living (bout 3/3); brings blanket_shared from couch_l1, mug_marco from kitchen_table_k1, glasses_marco from bedroom_floor_b1
22:00  Tomas — bed in the bedroom_3
22:06  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_nora → bedroom_floor_b2: WHIM — was heading for nightstand_b2 (put back in its usual place) but landed on bedroom_floor_b2 instead
          remote_shared → tv_stand_l1: put back in its usual place
22:18  Nora — bed in the bedroom_2
22:22  Marco finishes evening TV
          mug_marco → sink_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on sink_k1 instead [grocery_delivery]
22:41  Marco — reading in the bedroom_1; brings book_marco from nightstand_b1, glasses_marco from coffee_table_l1
23:11  Marco finishes reading
          glasses_marco → nightstand_b1: put back in its usual place
          phone_marco → nightstand_b1: put back in its usual place
23:11  Marco — bed in the bedroom_1
```

## Day 4 — Sunday

**Active causes**

- `grocery_delivery` (household): A grocery delivery arrives in the early evening. someone unpacks groceries; the kitchen counter is covered with bags, so things that would go there land on the table instead.
- `laundry_day` (household): Laundry day. the laundry basket travels, towels and the blanket get washed and end up airing in the bedroom rather than where they live.
- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `distracted:resident_1`: Marco is distracted (0.78): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `low_energy:resident_1`: Marco has low energy (0.29): leaves things where they were used instead of putting them back.
- `running_late:resident_1`: Marco is running late all day (1.00): rushed putdowns, things dumped at the door, more whim.
- `running_late:resident_3`: Tomas is running late all day (0.72): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Marco energy 0.29, hurriedness 1.00, distraction 0.78; Nora energy 0.62, hurriedness 0.48, distraction 0.35; Tomas energy 0.54, hurriedness 0.72, distraction 0.31

**Timeline**

```
06:44  Tomas — morning routine in the bathroom; brings phone_tomas from nightstand_b3, glasses_tomas from nightstand_b3
07:14  Tomas finishes morning routine
          glasses_tomas → nightstand_b3: put back in its usual place
08:45  Marco — morning routine in the bathroom; brings phone_marco from nightstand_b1, glasses_marco from nightstand_b1
08:57  Tomas — breakfast in the kitchen; brings mug_tomas from counter_k1
09:10  Marco finishes morning routine
          glasses_marco → nightstand_b1: put back in its usual place
09:11  Marco — breakfast in the kitchen; brings mug_marco from sink_k1
09:46  Marco — chores in the kitchen (bout 1/3); brings watering_can_shared from cupboard_k1
09:47  Nora — morning routine in the bathroom; brings phone_nora from bedroom_floor_b2
10:00  Marco finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_nora (from kitchen_table_k1) → dish_rack_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on dish_rack_k1 instead [grocery_delivery]
10:00  Marco — a short break in the kitchen
10:10  Marco — chores in the kitchen (bout 2/3); brings watering_can_shared from cupboard_k1
10:12  Nora — breakfast in the kitchen; brings mug_nora from dish_rack_k1
10:29  Marco finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_nora (from kitchen_table_k1) → counter_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on counter_k1 instead [grocery_delivery]
          mug_tomas (from kitchen_table_k1) → sink_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on sink_k1 instead [grocery_delivery]
10:29  Marco — a short break in the kitchen
10:39  Marco — chores in the kitchen (bout 3/3); brings watering_can_shared from cupboard_k1
10:47  Nora finishes breakfast
          mug_nora → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
10:47  Nora — chores in the kitchen
10:51  Marco finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_tomas (from sink_k1) → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
11:30  Marco — laundry in the bathroom [because of laundry_day]; brings towel_marco from towel_rack_ba1, blanket_shared from couch_l1
12:07  Nora finishes chores
          mug_marco (from kitchen_table_k1) → counter_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on counter_k1 instead [grocery_delivery]
          mug_nora (from kitchen_table_k1) → sink_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on sink_k1 instead [grocery_delivery]
12:17  Tomas — lunch in the kitchen
13:00  Marco finishes laundry
          blanket_shared → bed_b1: washed blanket airing on the bed [laundry_day]
          laundry_basket_shared → bedroom_floor_b1: basket left in the bedroom while things dry [laundry_day]
          towel_marco → bed_b1: clean towel folded on the bed [laundry_day]
13:20  Tomas — reading in the bedroom_3; brings book_tomas from nightstand_b3, glasses_tomas from nightstand_b3
14:12  Marco — lunch in the kitchen
14:33  Nora — lunch in the kitchen
14:50  Tomas finishes reading
          book_tomas → nightstand_b3: put back in its usual place
          glasses_tomas → nightstand_b3: put back in its usual place
14:52  Marco — work session in the bedroom_1; brings laptop_marco from bookshelf_l1, mug_marco from counter_k1, glasses_marco from nightstand_b1
16:22  Marco finishes work session
          glasses_marco → nightstand_b1: put back in its usual place
          laptop_marco → bookshelf_l1: put back in its usual place; desk_b1 was full, so it went to bookshelf_l1
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          notebook_marco → bedroom_floor_b1: WHIM — was heading for desk_b1 (put back in its usual place) but landed on bedroom_floor_b1 instead
          phone_marco → desk_b1: left where it was used
16:30  Marco — unpacking groceries in the kitchen [because of grocery_delivery]; brings water_bottle_marco from dish_rack_k1
16:38  Tomas — cooking dinner in the kitchen [shifted by grocery_delivery]
17:00  Marco finishes unpacking groceries
          water_bottle_marco → cupboard_k1: WHIM — was heading for dish_rack_k1 (counter full of shopping; bottle put on the dish rack) but landed on cupboard_k1 instead [grocery_delivery]
17:07  Nora — reading in the bedroom_2; brings book_nora from nightstand_b2
18:07  Nora finishes reading
          book_nora → nightstand_b2: put back in its usual place
18:44  Tomas — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_tomas from dish_rack_k1
19:23  Nora — cooking dinner in the kitchen [shifted by grocery_delivery]
19:34  Tomas finishes dinner
          water_bottle_tomas → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
19:46  Marco — cooking dinner in the kitchen [shifted by grocery_delivery]; brings phone_marco from desk_b1
19:53  Tomas — evening TV in the living (bout 1/4); brings remote_shared from tv_stand_l1, blanket_shared from bed_b1, mug_tomas from kitchen_table_k1, glasses_tomas from nightstand_b3
20:03  Nora — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_nora from dish_rack_k1
20:16  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_tomas → bedroom_floor_b3: WHIM — was heading for nightstand_b3 (put back in its usual place) but landed on bedroom_floor_b3 instead
          mug_tomas → dish_rack_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on dish_rack_k1 instead [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
20:16  Tomas — a short break in the kitchen
20:26  Marco — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_marco from cupboard_k1
20:28  Tomas — evening TV in the living (bout 2/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_tomas from dish_rack_k1, glasses_tomas from bedroom_floor_b3
20:38  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_tomas → nightstand_b3: put back in its usual place
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
20:38  Tomas — a short break in the kitchen
20:48  Nora finishes dinner
          water_bottle_nora → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
20:48  Nora — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_nora from sink_k1
20:50  Tomas — evening TV in the living (bout 3/4); brings mug_tomas from kitchen_table_k1, glasses_tomas from nightstand_b3
21:11  Marco finishes dinner
          water_bottle_marco → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
21:11  Marco — evening TV in the living (bout 1/2); brings mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
21:21  Marco finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_marco → nightstand_b1: put back in its usual place
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
21:21  Tomas finishes evening TV
          glasses_tomas → nightstand_b3: put back in its usual place
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
21:21  Marco — a short break in the kitchen
21:21  Tomas — a short break in the kitchen
21:33  Tomas — evening TV in the living (bout 4/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_tomas from kitchen_table_k1, glasses_tomas from nightstand_b3
21:53  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_tomas → nightstand_b3: put back in its usual place
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_tomas → nightstand_b3: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
21:53  Tomas — bed in the bedroom_3
21:54  Marco — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_marco from kitchen_table_k1, glasses_marco from nightstand_b1
22:38  Nora finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_nora → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_nora → nightstand_b2: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
23:01  Marco finishes evening TV
          blanket_shared → coffee_table_l1: left where it was used
          mug_marco → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
23:01  Marco — reading in the bedroom_1; brings glasses_marco from coffee_table_l1
23:01  Nora — bed in the bedroom_2
23:31  Marco finishes reading
          book_marco → bookshelf_l1: left where it was used; bed_b1 was full, so it went to bookshelf_l1
          phone_marco → nightstand_b1: put back in its usual place
```
