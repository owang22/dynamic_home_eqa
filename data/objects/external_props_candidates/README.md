# External-prop candidates — visual review

Review with the webapp (keep/reject, per-asset rename, tags, per-category
"fetch more candidates" with guidance notes; decisions land in
review_decisions.json, `/api/export` groups keeps by final name):

    python -m uvicorn dynamic_home_eqa.webapp.asset_review.app:app --port 8010

Renders are tabletop-context (wood surface, gray backdrop, shadows,
real-world size normalization) — two views per candidate. The pool covers
17 NEW categories, fresh candidates for the 15 EXISTING categories
(phone candidates come from LVIS `cellular_telephone` — no iphone/smartphone
key exists), and the already-ACCEPTED external_props meshes (tagged
`existing`) so pools can be curated in one place. Meshes stay in the
Objaverse cache (`/mnt/nvme/oliver/robot/objaverse_cache`) until promoted;
nothing here is wired into generation yet.

TAGS feed the planned LLM-informed asset binder (Strategy 2+): at
realized-day build, owner-bound items get assigned by an LLM that reads
each kept asset's tags against the occupant's persona (teen -> the
"gaming, red" headphones; grandma -> the "wired, old-fashioned" pair),
seeded + cached + recorded in the artifact; shared clutter still draws
without replacement for visible variety. Tag with appearance + who it
suits in mind.

`candidates_mapping.json` mirrors `external_props/mapping.json`'s entry shape
(`{uid, category, source, objaverse_uid}`, plus a `faces` count for triage) —
promoting a candidate = copy its entry over, copy/decimate the glb into
`external_props/meshes/`, build a collider + `object_config.json` (up/front/
scale — most candidates lie on their side; set `up` the way the existing
key config does), and delete the losers.

## Proposed classification (to review alongside the renders)

| category | proposed tier | spawn/abundance | placement | movability | age skew |
|---|---|---|---|---|---|
| plate | Tier-2b clutter | abundant (cap 4) | surface | daily (meals) | all |
| mug | Tier-2b clutter | abundant (cap 4) | surface | daily (hot drinks) | adult/senior |
| toy | Tier-2b clutter | abundant (cap 4) | surface | daily, scattered | young child |
| towel | Tier-2b clutter | abundant (cap 3) | surface | daily-ish | all |
| newspaper | Tier-2b clutter | abundant-ish (cap 2) | surface | daily for readers | senior |
| remote_control | Tier-2b clutter | scarce (cap 2) | surface | daily (TV) | all |
| tray | Tier-2b clutter | scarce (cap 2) | surface | occasional (serving) | adult/senior |
| scissors | Tier-2b clutter | scarce (cap 1) | surface | occasional need | adult |
| teapot | Tier-2b clutter | scarce (cap 1) | surface | daily-for-some | senior |
| alarm_clock | Tier-2b clutter | scarce (cap 2) | surface | rarely moved | all |
| watering_can | Tier-2b clutter | scarce (cap 1) | surface/floor | occasional routine (plants) | senior |
| umbrella | Tier-2b clutter | scarce (cap 2) | proximity (leans) | weather-driven occasional | all |
| laundry_basket | Tier-2a-style FLOOR object | scarce (cap 1) | floor only (proximity) | chore-driven occasional | adult |
| medicine | Tier-3-like (owner-bound) | one per owner | surface | daily routine | senior |
| sunglasses | Tier-3 personal | one per owner | surface/carried | daily carried | teen/adult |
| headphones | Tier-3 personal | one per owner | surface/carried | daily carried | teen/young adult |
| backpack | Tier-3 personal | one per owner | surface/floor | daily (school) | child/teen |

Movability spread (the design axis requested): daily-carried = mug, plate,
toy, newspaper, remote_control, sunglasses, headphones, backpack, medicine;
occasional-specific-need = umbrella, scissors, watering_can, laundry_basket,
tray; rarely-moved = alarm_clock, teapot (daily only for tea-drinking
households), towel (semi-fixed).

Integration notes against the existing rules:
- ABUNDANT_STORAGE_CATEGORIES additions: plate, mug, toy, towel (a home holds
  spares in storage; fresh-one-out is normal). NOT newspaper (one copy),
  and none of the scarce/personal rows.
- FLOOR_BOUND_CATEGORIES addition: laundry_basket (slides/carries on the
  floor, never on a table — same surface-relation ban as chair/stool).
- Tier-3 additions (sunglasses, headphones, backpack, medicine) need
  ownership.py support (per-occupant labels + age-aware assignment: backpack
  to school-age kids, medicine to seniors, etc.) before they can spawn/despawn
  like phone/wallet/keys/laptop.
- mug vs cup/drinkware overlap: keep all three (cup = generic, drinkware =
  glassware, mug = handled hot-drink vessel) or fold mug into cup at
  promotion — reviewer's call.

## Screening notes from spot checks (full pass is yours)

- teapot__57766f87: untextured pink abstract blob — REJECT.
- medicine__0e507675: flat plane — REJECT. medicine__dda9d74c: single low-poly
  pill, not a bottle — reject unless a "pill" prop is wanted.
  medicine__429536ff / __d83f35ad: excellent labeled pill bottles.
- umbrella__7bdbfbab: untextured grey — weak. umbrella__d2c529d5: multi-object
  scene, not an umbrella — REJECT. __40d7491a / __54daa7a3: good (note both
  are OPEN umbrellas; fine visually, slightly odd indoors — a closed/folded
  one may be worth hunting later).
- mug: all three fine (mug__922cd7d1 dark navy, __93ad19db plain white,
  __e5e87ddb decorated).
- 3 candidates were auto-rejected before render for >800k faces (see
  source script output): one mug, one backpack, one toy.
