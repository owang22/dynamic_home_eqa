"""Prompt text. Residents are addressed as themselves; nothing here tells them
where objects should end up."""
from __future__ import annotations

HOMES = [
    "a two-bedroom apartment in a city, one bedroom used as a home office",
    "a small two-storey terraced house with a back garden",
    "a one-bedroom flat with an open kitchen and living room and a balcony",
    "a three-bedroom suburban house with a garage and a laundry room",
    "an older rented house with a cellar and a sunroom",
]

CREATE_SYSTEM = """You design believable homes and households for a simulation of
everyday home life. Two adults share the home. Write them and their home as
specific people and a specific place with its own quirks, not as averages.
Everything you write must fit together."""

LAYOUT_USER = """Design the home: {home}.

List the rooms, the furniture in each room, and every spot on or in each piece
of furniture where a person could put something down or put something away:
each shelf of a bookshelf, each drawer, the left and right ends of a counter,
the top of the fridge, the couch cushions, under the bed, hooks by the door,
the floor next to the shoe rack. Aim for {lo} to {hi} spots in total.

- Room ids: short, lowercase, underscores (kitchen, main_bedroom).
- Spot ids: unique across the home, lowercase with underscores, starting with
  the room id (kitchen_counter_left_end, main_bedroom_nightstand_left_drawer).
- Do not name the residents yet; describe furniture by where it is (the left
  nightstand, the window side of the bed), not by who uses it.
- name: what the spot is, in a few words.
- kind: surface if things on it are out in the open; container if it closes
  (a drawer, cabinet, fridge, closet, hamper, lidded bin).
- hidden: true for a surface that someone standing in the room cannot see,
  like under the bed, behind the couch, or under the couch cushions.
- descriptions: 2 to 4 ways a person would say where something is when it is
  there ("the counter by the stove", "next to the kettle", "left of the sink").
- entry_spot: the spot id just inside the front door, where someone coming
  home first stands."""

RESIDENTS_USER = """The home: {home}

Its rooms and spots:
{layout}

Write the two adults who live here. For each:
- id: their first name in lowercase; name, age, job, personality.
- sleeps_at: the spot id of the bed where they sleep.
- weekly_routine: what they usually do on which weekdays, with times (HH:MM)
  and rooms; use out_of_house for time away.
- object_habits: specific, personal habits about where they keep, leave or
  carry things ("my reading glasses live on my nightstand", "I drop my keys
  wherever I am when my phone rings", "my work laptop goes to the office with
  me in my backpack").
- response_habits: how they tend to respond to how they feel or to what
  happens ("when stressed I take a long walk", "when tired I skip cooking and
  order food", "when someone is sick I make them tea"). Give each a short id
  and how often it holds.
- scheduled_stressors: recurring things in their week that stress them."""

OBJECTS_USER = """The home:
{layout}

The residents:
{residents}

Now fill the {room}. Its spots:
{spots}

Add {lo} to {hi} more things that are in the {room} at the start, besides
any already placed there (listed at the end). Every thing you list is a new,
separate thing: the things these two people own and move around in daily
life (phones, keys, mugs,
glasses, books, medicine, chargers, bags, cooking things, hobby things,
clothes they leave lying around). Skip furniture, appliances and anything
fixed in place.

{fields}{taken}"""

SITUATIONS_USER = """The residents:
{residents}

Write:
1. 15 to 25 situations that could happen to this household, fitted to these
   two people. Mix one-off events (a dinner guest, a late night at work),
   recurring ones that come and go (a cold, a deadline week, a visiting
   relative), and lasting changes (a new hobby, a new job schedule). Include
   one recurring situation with id "sick" where one resident gets sick for a
   few days. For each:
   - what_it_is_like: what it is like for the people it happens to, from the
     inside: how they feel, what is on their mind, how their energy and day
     change.
   - what_others_notice: how those people seem to the other resident: their
     mood, energy, how they talk and move.
   Describe people, not things: do not mention objects, where things are or
   what anyone does with them; how the home changes is for the residents to
   work out themselves.
2. 12 to 24 small disturbances of an ordinary day (a call from a parent, a
   package at the door, running out of milk). who is a resident id or
   "anyone"."""

RESIDENT_SYSTEM = """You are {name}, {age}, {job}. {personality}
You live with {others}. You are taking part in a simulation of everyday life at
home: act as yourself, in ordinary detail. You move things with your hands, so
you carry them from place to place, put them down when you need your hands
free or when you are done, and sometimes leave them where you were rather than
in their usual spot, as people do. When you use something (a plate, a mug, a
pot, a book), pick it up and take it where you use it rather than only saying
you used it. You have two hands and pockets. A bag or basket you carry holds
what you put in it.

Your habits with things:
{object_habits}

How you tend to respond to things:
{response_habits}

Things in your week that stress you:
{stressors}

Kinds of things in the home, by whose they are (how many):
{types}

The home (room: furniture: spot id (name)):
{layout}"""

PLAN_USER = """It is {weekday}, day {day}.

Your usual {weekday}:
{routine}

What you know of the others' usual {weekday}:
{others_routine}

What is going on today:
{situations}
{variation}
Yesterday: {yesterday}

Plan today from when you wake up until you go to sleep, as a list of your own
activities with start and end times (HH:MM). Count on what the others usually
do (who cooks, who is out when), but do not plan their actions for them; they
plan their own day. Follow your usual routine unless
something today gives you a reason to change it. For each activity, list the
kinds of things you expect to use (from the kinds in the home). Say how you
feel this morning: stress, tiredness, mood and health from 0 to 3 (mood 0 is
bad, health 0 is very unwell)."""

ACT_USER = """It is {time} on {weekday}, day {day}.
Now: {activity} ({start} to {end}, {room}). You meant to: {intention}
Rest of your day: {rest}

What is going on today:
{situations}
{events}
{view}
In your hands: {hands}. In your pockets: {pocket}. Wearing: {worn}.

Where you remember things being (what matters now):
{memory}
Everything else is where you last saw it.
{problem}{bedtime}
Write what you do, step by step, until this activity ends around {end} or you
finish it. Actions:
  go (place): walk to a spot
  pick_up (object, optional place): take it from the spot you are at (or the
    spot you name, and you walk there), from a bag you hold, or from your
    pocket; you need a free hand
  put_down (object, optional place, relation, ref): put it at the spot you are
    at (or the spot you name, and you walk there). relation: on, in, under, behind,
    next_to, on_top_of; ref: an object at that spot ("behind" the toaster, "on
    top of" the books). To put something in a bag, a basket, or the pocket of
    a jacket or pants lying here: relation in, ref that thing.
  pocket (object): put something small in a pocket of what you are wearing
  wear (object): put on clothes, shoes, a watch, glasses or a backpack, or
    clip something on (keys on a belt, a badge on a lanyard); to take it off,
    pick_up or put_down
  give (object, person): hand it to someone in the same room
  do (minutes, text): spend time on something, like "cook pasta" or "read"
  say (person, text): say something to someone
  leave_home (minutes, text): go out until you are back home; minutes is the
    whole time away, covering every out-of-house activity in a row (commute
    and work together). What is in your hands, pockets and the bags you hold
    comes along.
Use empty strings and 0 for fields an action does not need. If you look for
something and it is not where you expected, you will be told what you see
there instead. Say how you feel now (stress 0 calm to 3 very stressed; tiredness 0 rested to 3 exhausted; mood 0
bad to 3 good; health 0 very unwell to 3 well), which of
your response habits' triggers are true for you right now, and which habit
you are following, if any."""

BEDTIME = """
After this activity you go to sleep. Before you sleep, put down whatever you
are still holding and take off what you have been wearing today."""

FIELDS = """- n: number the things 1, 2, 3, ... in the order you list them.
- type: a plain lowercase noun shared by every instance of that kind of thing
  ("mug", "phone charger", "reading glasses", "tote bag").
- looks: 1 to 4 words that tell this one apart from the others of its type by
  how it looks ("red ceramic", "white chipped", "usb c braided"). Not who owns
  it. Its name in the simulation is made from type and looks (mug_red_ceramic).
- Many types have several instances across the home: a home has 4 to 8 mugs,
  several chargers, 2 pairs of reading glasses. Put each where it belongs.
- color, material, size, pattern ("plain" if none), condition ("new", "worn",
  "chipped", ...).
- owner: a resident id only where people in the home would say whose it is
  ("her work laptop", "his running watch", her phone, his work boots). Most
  things are none: mugs, chargers, mail, kitchen things, shared toiletries,
  books on a shared shelf.
- pocketable: fits in a trouser or jacket pocket.
- carrier: whether what is put inside it can be seen: open for things that
  hold other things in the open (a basket, a tray, a bowl, a mug); closed for
  bags, backpacks, boxes with lids and cases; pockets for clothes with pockets
  (jeans, work pants, jackets, hoodies); none for everything else.
- place: the spot it is at. relation and ref: where it is at that spot. With
  ref 0, relation is on (a surface) or in (a container). With ref set to the n
  of another thing in your list at the same spot, it is relative to that
  thing: behind the toaster, on top of the stack of books, next to the
  kettle, or inside another thing (a pen case in a backpack, a bookmark in a
  book, a wallet in the pocket of jeans): relation in, ref its n.
"""

PERSONAL_USER = """The home: {home}

Its rooms and spots:
{layout}

The residents:
{residents}

{name}'s weekly routine:
{routine}

List {name}'s own things: what {name} carries or uses and would call theirs,
including everything their routine and habits call for (the bag they take to
work and what goes in it, their sports or hobby gear), and the clothes they
wear and change into over a day: for work, at home in the evening, and to
sleep in, at least one of each. Everyone has their
phone; most people have a wallet or purse, keys, the bags they carry (and
what is kept in them), glasses if they wear them, work things, medicine they
take, the charger by their bed, clothes and shoes they leave out, hobby
things. One of each where a person has one; several only where people really
keep several. {lo} to {hi} things; owner is {rid} for all of them.
{others}
It is early morning and both are still asleep: put each thing where it would
be right now, following {name}'s habits with things. Any spot in the home.
worn_now: true only for what {name} is wearing in bed right now (their
sleepwear); false for everything else.

{fields}"""

ESSENTIALS_USER = """The home's rooms and spots:
{layout}

{name} ({rid}): {about}

{name}'s things listed so far have no {missing}. Add exactly that: {missing},
owned by {rid}, where it would be right now in the early morning while
everyone is asleep, following {name}'s habits.

{fields}"""

FIXTURES_USER = """The home: {home}

Its rooms and spots so far:
{layout}

Some fixtures and appliances that people put things on or in every day may be
missing as spots: in a kitchen the stovetop or its burners, the oven, the
sink, a dish rack or drying mat, the dishwasher, the microwave; in a bathroom
the sink, the bathtub edge, a shower shelf; in a laundry room the washer and
dryer drums; anything similar elsewhere. List the ones this home has that are
not yet spots, grouped under the room and the fixture they belong to, as spots
with the same fields as before (id starting with the room id, name, kind,
hidden, 2 to 4 descriptions). Add only what is missing; {lo} to {hi} spots."""

INTERRUPTED = """
You are in the middle of this activity. So far you have: {done}.
Something just happened (see above). Decide what to do now: carry on, deal
with it, or stop this activity early.
"""

SUPPLIES_USER = """The home: {home}

Its rooms and spots:
{layout}

The residents:
{residents}

Their own things are already placed (type: names):
{taken}

Now the household's shared everyday supplies: things that belong to nobody in
particular and that either of them reaches for when needed. Painkillers and
cold or flu medicine, a thermometer, tissues, plasters and a first-aid kit,
cleaning things, batteries, tape, scissors, a flashlight, spare chargers, a
water bottle or thermos anyone can take, laundry supplies, a spare umbrella,
whatever this household would keep. {lo} to {hi} things, owner none, each where
this household keeps it. Any spot in the home.

{fields}"""
