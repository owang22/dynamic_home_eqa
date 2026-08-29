# Household generation prompt (revamp_v1, stage 1: narrative profiles)

Verbatim instructions used to generate the files in `households/`.

---

You are writing profiles of fictional households for a research simulation.
The simulation will later animate each household: objects will move around
the home over days and weeks, driven by what the residents do. Right now we
are only writing WHO lives in each home and WHAT objects they own. Daily
schedules with clock times come in a later step — do not write any times of
day or hour-by-hour routines.

You will write many households in this one session, one at a time. Each new
household must be clearly different from every household you have already
written — different personalities, ages, living situations, and habits, not
just different names.

For each household I will tell you its TYPE and the number of residents.
Keep the type and headcount I give you; do not change them. Invent a
specific, believable household of that type.

Output format (YAML):

household_id: <as given>
household_type: <as given, copy exactly>
residents:
  - id: resident_1
    name: ...
    age: ...
    occupation: ...        # or "student", "retired", "stay-at-home parent"
    personality: ...       # 2-3 traits that affect how they treat objects
                           # (e.g. tidy, forgetful, always in a hurry)
    habits:                # 5-8 concrete habits about how they use and
                           # leave objects around the home. At least 2 must
                           # involve another resident. Examples:
                           # - "reads in bed, leaves the book on the
                           #    nightstand"
                           # - "borrows resident_2's charger from the desk
                           #    and rarely returns it"
                           # - "clears everyone's mugs to the kitchen when
                           #    tidying in the evening"
      - ...
relationships: ...         # 2-3 sentences: who these people are to each
                           # other, and how they divide or share chores,
                           # spaces, and belongings. Include at least one
                           # point of friction or coordination (e.g. who
                           # does dishes, who loses the remote, whose stuff
                           # spreads into shared spaces).
home_layout_notes: ...     # 2-3 sentences: rooms and surfaces each person
                           # uses most, and which spaces are shared.
object_inventory:
  - id: mug_1              # indexed ids: mug_1, mug_2, laptop_sam
    class: mug             # pick classes from the vocabulary below
    owner: resident_1      # or "shared"
    role: ...              # one short phrase: what this object is FOR in
                           # this household and how it tends to move. For
                           # shared objects, say who moves it and why.
                           # Example: "shared TV remote; the kids carry it
                           # off, resident_1 hunts it down nightly."
daily_life_summary: ...    # 3-4 sentences describing a typical day in
                           # plain words, still without clock times.
                           # Mention how the residents' days overlap or
                           # miss each other (who is home when others are
                           # out, who crosses paths where).
quirks: ...                # 1-2 ways this household differs from the
                           # stereotype of its type

Object vocabulary (choose from these; do not invent new classes):
[mug, bowl, plate, laptop, phone, keys, book, water_bottle, remote,
charger, backpack, jacket, headphones, glasses, notebook, pen,
medication_bottle, toy, blanket, towel, gaming_controller, dog_leash,
lunchbox, umbrella, wallet]

Inventory rules:
- Not every household owns every class. Small households own few objects.
- Object counts should match household size (a family of five owns more
  bowls and backpacks than a person living alone). Per-person items like
  phones, keys, and wallets should exist per resident.
- Suggestive objects are allowed (medication_bottle, toy, dog_leash), but
  write the "role" field so the object's meaning comes from how it is
  used, not from the fact that it exists. The same object class should
  mean different things in different households.
- Shared objects are encouraged in multi-person homes; their "role" should
  name which residents move them.
