# Objaverse asset sourcing for keys/wallet — CLOSED: 0/5 pass even under the production pose search, PERCEPTUAL-TIER-EXCLUDED

**STATUS (final, round 3): decision closed per standing instruction — "if 0/5 still fail under the
real search, PERCEPTUAL-TIER-EXCLUDED, attempted-and-documented." 0/5 candidates find a passing pose
anywhere in the standard production ring, including the nearest radius (1.5m). `NO_ASSET_CATEGORIES`
(keys/wallet) is UNCHANGED — nothing was ever promoted, so this changes nothing about the live render
pool's behavior; it closes round 1's "awaiting owner pick" with a final, documented answer. See
"Round 3" below for the full production-search re-verification AND an independent diagnostic
(requested alongside this re-verification) that found the SAME structural floor issue already
affects two currently-shipping native categories (candle, drinkware/cup) — surfaced with numbers,
not resolved unilaterally.**

Round 1 (below, unedited) is kept for provenance — it explains where the 10 candidates came from,
the scale/reorientation pipeline, and registration. Its own mechanical-acceptance table used the
pixel-diff check that this round's standing rule identifies as an inverted guard (see
`results/reports/human_realism_study.md`'s round-4 section) and is superseded by Round 2's numbers,
not by editing the table below out of the historical record.

## Where the candidates came from

LVIS-Objaverse (`objaverse.load_lvis_annotations()`) has exact category labels `"key"` (82 UIDs) and
`"wallet"` (13 UIDs) — no guessing needed for the category keys themselves. But the category
assignment inside LVIS is demonstrably noisy: `"key"` includes literal non-matches like `"Jones Light
Post"` and `"Taser Gun"`, confirmed directly by inspecting all 82 names before downloading anything.
Rather than blindly take a positional "top 5," every name was inspected and 5 per category were
picked by plausibility + license + a sane (not absurdly high-poly) mesh:

- **keys**: `7dd0e287…` "Key", `f5550185…` "Key from Poly by Google", `6d2b485f…` "Low Poly Key for
  Games", `aaccd2b9…` "Keys", `9835dac4…` "small key"
- **wallet**: `2c46e958…` "LEATHER WALLET … WALLY", `d938d2ab…` "walllet", `45e06179…` "DOMPET 2"
  (Indonesian for wallet), `4d63cef3…` "wallet.fbx", `12129cce…` "Card Holder"

All 10 are licensed `by` (CC-BY) — confirmed via `objaverse.load_annotations()`'s `license` field
before download, per the reject-immediately-if-unclear instruction. None rejected on licensing.

## Config generation — units were exactly as untrustworthy as expected

Raw trimesh-reported extents ranged from 0.28 to 188.5 with no consistent unit convention across
candidates (confirmed directly, see `data/objects/external_props/mapping.json`) — exactly why scale
is computed per-asset from the target real-world size (`0.12m` keys, `0.11m` wallet) divided by the
raw max extent, never trusting the raw units. Also confirmed **most candidates were not lying flat**:
of 10, only 1 (`aaccd2b9…`) already had its thinnest AABB axis vertical; the other 9 needed a
computed `up`/`front` remap (thin-axis detection -> new local up vector -> an orthogonal front
vector) to lie flat once scaled. Verified directly, not assumed: a live spawn of `7dd0e287…` showed
a post-scale bounding box of `(0.033, 0.0085, 0.12)` — max extent exactly 0.12m (the key target) and
the thinnest axis (Y, 8.5mm) now vertical, confirming both the scale and reorientation math.

## Registration

`data/objects/external_props/` mirrors YCB's on-disk layout (`configs/` + `meshes/` +
`external_props.scene_dataset_config.json`, checked directly against
`.../objects/ycb/ycb.scene_dataset_config.json` for the convention). Loads into the SAME render sim
that already has HSSD loaded via a plain `object_template_manager.load_object_configs(path)` call —
no dataset-merge machinery needed, confirmed empirically (the exact mechanism
`scripts/realism_render_job.py`'s own `spawn_object` already uses for HSSD assets).

## Mechanical acceptance — 5/10 passed, and the failures are informative, not arbitrary

| Category | UID (short) | Scale (target) | Changed px (≥200) | Supported | **Result** |
|---|---|---|---|---|---|
| key | `7dd0e287b963` | 0.120m (0.12m) ✓ | 87 ✗ | ✓ | REJECT |
| key | `f55501852734` | 0.120m (0.12m) ✓ | 151 ✗ | ✓ | REJECT |
| key | `6d2b485fc3d5` | 0.120m (0.12m) ✓ | 183 ✗ | ✓ | REJECT |
| key | `aaccd2b9848d` | 0.120m (0.12m) ✓ | 19 ✗ | ✓ | REJECT |
| key | `9835dac44cd9` | 0.120m (0.12m) ✓ | **290** ✓ | ✓ | **PASS** |
| wallet | `2c46e958b57f` | 0.110m (0.11m) ✓ | **909** ✓ | ✓ | **PASS** |
| wallet | `d938d2abefb8` | 0.110m (0.11m) ✓ | 170 ✗ | ✓ | REJECT |
| wallet | `45e061790f36` | 0.110m (0.11m) ✓ | **958** ✓ | ✓ | **PASS** |
| wallet | `4d63cef3d4c3` | 0.127m (0.11m, 15% over — within tolerance) | **938** ✓ | ✓ | **PASS** |
| wallet | `12129ccec914` | 0.110m (0.11m) ✓ | **662** ✓ | ✓ | **PASS** |

**All 10/10 passed scale and support** — the scale/reorientation pipeline works correctly across
every candidate, not just cherry-picked ones. **The pixel-diff check was the actual discriminator**,
and the pattern is real, not noise: every rejected key candidate failed on visibility (19-183 changed
pixels, under the 200 threshold), while the one surviving key (290 px) and all-but-one wallets (662-958
px) cleared it comfortably. This is an honest reflection of real-world scale — keys ARE small and hard
to see from a normal viewing distance, more so than wallets. It is not evidence the check is
miscalibrated; the one key that DID pass (`9835dac4…`, "small key", 3076 faces) visually confirmed
flat, correctly-scaled, genuinely visible resting on a table (see the render).

Full machine-readable log: `results/reports/asset_candidates_result.json`. Survivor renders (2x1:
egocentric + top-down, captioned with scale/diff/support numbers): `results/reports/asset_candidates/`.

## Standing constraint — encoded and verified against the real pool

`scripts/realism_render_job.py`'s `assert_category_has_asset_coverage(category)` raises
`UncoveredCategoryError` for any category in none of: `SPAWNABLE_ASSET_BY_CATEGORY`,
`_ALREADY_INSTANTIATED_CATEGORIES`, `NO_ASSET_CATEGORIES`. Wired into the render job's pool-
construction step (fails before any rendering starts, not mid-batch). Verified directly against the
full 211-folder generation pool (not just the 80-item sample), not assumed: all 18 real object
categories present anywhere in the pool are covered by one of the three buckets — the render job
would not have broken had this check existed from the start, and it will now catch a genuinely new,
never-evaluated category the moment a future profile's persona invents one, rather than silently
rendering an empty scene with a star sticker again (round 3's original finding).

Scoped to render-job pool construction only, per this task's own instructions ("render-job scope
only"). A fuller version wired into scene/question qualification (catching a bad category before a
study runs, not while rendering) would touch `generation/`'s scene-validation code — flagged as a
natural extension, not built this batch.

## Round 2 — license audit (6a) and mask-predicate re-verification (6b)

### 6a: license audit — all 5 survivors confirmed, none rejected

Re-fetched directly (not reused from memory) via `objaverse.load_annotations()` for exactly the 5
round-1 survivor UIDs, 2026-07-08:

| Category | UID (short) | Name | License | Creator |
|---|---|---|---|---|
| key | `9835dac44cd9` | "small key" | `by` (CC-BY) | `Frybrix` |
| wallet | `2c46e958b57f` | "LEATHER WALLET 4.5x3.5 WALLY" | `by` (CC-BY) | `eeelabvisual` |
| wallet | `45e061790f36` | "DOMPET 2" | `by` (CC-BY) | `eeelabvisual` |
| wallet | `4d63cef3d4c3` | "wallet.fbx" | `by` (CC-BY) | `realvjy` |
| wallet | `12129ccec914` | "Card Holder" | `by` (CC-BY) | `eeelabvisual` |

All 5 are clearly CC-BY with an identifiable creator. **None rejected on licensing.**

### 6b: re-verification under the mask predicate — 0/5 pass

All 5 survivors re-run through `scripts/asset_candidate_acceptance.py` (now rewired to the SAME
`evaluate_object_mask` predicate `scripts/realism_render_job.py`'s `render_event_grid` uses — see
that module's docstring — instead of the deleted pixel-diff check), at the same standard anchor
(`dining.table`):

| Category | UID (short) | Scale (target) | Mask area (px / % of frame) | Mask floor (0.5%) | Supported | **Result** |
|---|---|---|---|---|---|---|
| key | `9835dac44cd9` | 0.120m (0.12m) ✓ | 187px / 0.108% | ✗ | ✓ | **REJECT** |
| wallet | `2c46e958b57f` | 0.110m (0.11m) ✓ | 496px / 0.287% | ✗ | ✓ | **REJECT** |
| wallet | `45e061790f36` | 0.110m (0.11m) ✓ | 550px / 0.318% | ✗ | ✓ | **REJECT** |
| wallet | `4d63cef3d4c3` | 0.127m (0.11m, within tolerance) | 531px / 0.307% | ✗ | ✓ | **REJECT** |
| wallet | `12129ccec914` | 0.110m (0.11m) ✓ | 381px / 0.220% | ✗ | ✓ | **REJECT** |

**All 5 fail the exact same clause: `mask_too_small`** (area under the 0.5%-of-frame floor). Scale
and support both still pass cleanly for all 5 — the scale/reorientation pipeline is not in question,
only visibility at the standard viewing distance. As anticipated going into this re-verification:
*"the key's margin was thin (290 px vs a 200 px bar); it may not clear the 0.5% mask-area floor —
that is a legitimate rejection, not a calibration target"* — and it didn't (187px, 0.108%, well under
the 2,592px/0.5% floor for a 480x360 frame).

**What changed the numbers this much:** the deleted pixel-diff check counted ANY pixel that differed
between the with/without renders above a small per-channel threshold — shadow and ambient-occlusion
changes the object's presence casts on the table count there too, inflating the number well past the
object's own silhouette. The mask predicate counts only pixels the semantic sensor attributes to the
object's own reserved instance ID — its real footprint, nothing else. The 662-958px pixel-diff
numbers round 1 reported were never a measurement of "how much of the frame does this object occupy"
— they were doing something looser, which is exactly what this round's standing rule is about.

**This is a legitimate rejection, not a check to loosen.** No candidate's mask area was edited,
widened, or the floor relaxed to pass any of these 5 — per the standing rule, the failing number is
reported as-is. The underlying, category-level finding (not specific to any one mesh): small handheld
props (keys, wallets) may simply be too small to clear a reasonable "is this genuinely visible in the
frame" bar from this render job's standard viewing distances (1.5-3.5m tiers) — a distance/scale
mismatch, not a per-candidate quality problem. A closer standard viewpoint for small-object categories
specifically is a plausible follow-up, but changing the render job's viewpoint-distance policy is a
decision for the owner, not something this round makes unilaterally while re-verifying assets.

## Round 3 — production pose search (closes the decision) + native-small-category diagnostic

### Production pose search: 0/5, confirmed at every standard distance, not just the one test pose

Round 2's re-verification used a single fixed test pose. Re-run via `scripts/asset_candidate_acceptance.py
--mode production_search`, which calls the SAME `viewpoint_for_render` production code path
`render_event_grid` uses (standard `_VIEWPOINT_RADII` ring: 1.5/2.0/2.5/3.0/3.5m, farthest-passing
preference within the first radius tier with any sightline) — not a custom search. When the
production pose itself doesn't clear the mask predicate, every standard radius was additionally
swept (diagnostic only, beyond what production itself tries) to build a real mask-area-vs-distance
curve rather than guess:

| Category | UID (short) | 1.5m | 2.0m | 2.5m | 3.0m | 3.5m | Best |
|---|---|---|---|---|---|---|---|
| key | `9835dac44cd9` | 0.108% | 0.040% | 0.018% | 0.006% | 0.008% | REJECT |
| wallet | `2c46e958b57f` | 0.287% | 0.086% | 0.076% | 0.035% | 0.020% | REJECT |
| wallet | `45e061790f36` | 0.318% | 0.094% | 0.047% | 0.014% | 0.016% | REJECT |
| wallet | `4d63cef3d4c3` | 0.307% | 0.097% | 0.051% | 0.015% | 0.016% | REJECT |
| wallet | `12129ccec914` | 0.220% | 0.063% | 0.031% | 0.010% | 0.008% | REJECT |

(all percentages = mask area / frame area; floor is 0.5%)

**0/5 pass at ANY standard radius, including the nearest (1.5m)** — this isn't a farthest-preference
artifact; the closest producible camera position in the standard ring is already insufficient, and
area falls off sharply (roughly 3-4x per radius step) as expected from perspective. No candidate
proceeds to identifiability review — none has a passing pose to review. Full curves:
`results/reports/asset_candidates_production_search_result.json`.

**Per the standing instruction, the decision closes here: `keys`/`wallet` are PERCEPTUAL-TIER-EXCLUDED,
attempted and documented.** `NO_ASSET_CATEGORIES` already reflects this — no code change needed.
This is not revisited without new candidates or a change to the render job's viewing-distance policy
(see the diagnostic below for why the latter is a real, separate design question, not a quick fix).

### Diagnostic: is 0.5% an Objaverse problem or a small-object problem? (Answer: size/shape-dependent, and it already affects 2 shipping categories)

Sampled real generation events (not synthetic) for 3 native HSSD spawnable categories across 3
distinct scenes (36 events, both before/after anchors each = up to 72 panel attempts), run through
the exact same production functions `render_event_grid` uses (no custom logic):

| Category | OK panels | Mask area (min/median/mean/max) | object_spawn_failed panels | ...of which `mask_too_small` |
|---|---|---|---|---|
| phone | 13/13 resolved-and-attempted-OK | 1.016% / 1.066% / 1.112% / 1.305% | 4 (of 24 total) | 2 |
| candle | 0/24 | — (no OK panels) | 20 (of 24) | 19 |
| drinkware | 0/24 | — (no OK panels) | 18 (of 24) | 14 |

**Finding: the 0.5% floor is compatible with reasonably-sized objects, and structurally incompatible
with a specific small/thin-footprint size class — independent of Objaverse.** `phone` clears the
floor comfortably every time it's attempted (2-2.6x margin). `candle` (real extents ~0.075m x 0.095m
x 0.075m, spot-checked directly) and `drinkware`/`cup` (real extents ~0.08m x 0.22m x 0.08m — tall
and thin) fail almost every attempt, overwhelmingly on `mask_too_small`, at the SAME standard
production distance — not a hypothetical, this is what the render job produces for these categories
TODAY. `keys` (0.12m target) and `wallet` (0.11m target) sit in the same small/thin size class as
candle and drinkware/cup, not a size class unique to Objaverse's mesh quality.

**This is a genuine design decision, surfaced with the numbers, not resolved here:** the render job's
standard viewing distance (nearest ring tier 1.5m) makes objects under roughly 0.1m footprint
structurally unable to clear a 0.5%-of-frame visibility floor, regardless of source. Two currently-
shipping categories (`candle`, `drinkware` — and by extension `cup`, which shares the drinkware asset)
are affected right now, not just the keys/wallet candidates evaluated this round. Options for the
owner to weigh (none implemented): (a) accept this as correct — these items genuinely are hard to
see from a normal room-scale distance, and OBJECT_SPAWN_FAILED is an honest reflection of that; (b) a
closer standard viewpoint specifically for a defined small-object category set; (c) a lower area
floor for that same defined set. Per the standing rule, none of these were chosen unilaterally to
make a number look better — this needs an owner call, and applies beyond keys/wallet.
Full data: `results/reports/native_small_mask_diagnostic_result.json`.

## What happens next (owner action required)

**Keys/wallet themselves: nothing — the decision is closed (PERCEPTUAL-TIER-EXCLUDED, documented,
`NO_ASSET_CATEGORIES` already reflects this).** What remains open is the broader, independent
finding above:

1. **Decide** whether to act on the native-small-category floor finding (candle/drinkware/cup) — the
   three options above, or explicitly defer it.
2. If deferred: no other action needed: this report stands as the documented attempt for keys/wallet,
   the render pool is otherwise unaffected (nothing here changes any currently-shipping category's
   behavior), and the standing coverage constraint
   (`assert_category_has_asset_coverage`) already treats keys/wallet as a documented, non-silent
   exclusion.

## Round 4 (Replatform round, item 4): OVMM cross-reference — keys near-miss, wallet FINAL, cup promoted

Triggered by `receptacle_investigation.md`'s Section 3 (OVMM's `object_categories.csv`, 2,404
objects/108 categories, metadata-only fetch — see that report for how it was obtained).

**keys → `keychain` (OVMM/AI2-THOR): real, close, but not yet passing.** No exact `keys` category
exists in OVMM either, but `keychain` (3 candidates, source=ovmm) does. Downloaded and spawned both
habitat-ready ones (`Keychain_1`: 0.128m max extent; `Keychain_2`: 0.130m — both within 8% of
`_CATEGORY_TARGET_M["key"]=0.12`, comfortably inside the 20% scale tolerance) and ran them through
the real `asset_candidate_acceptance.py` pipeline (scale + spectator-camera mask predicate + support
check) at `dining.table`, scene 102343992. Both PASS scale and support; both FAIL
`mask_off_center` (`Keychain_1`: 4.2% area, off-center; `Keychain_2`: 3.6% area, off-center) — the
object is visible and correctly sized, just not framed centrally by the automatic spectator-camera
pick for this specific asset's geometry. **Not promoted this round** — `NO_ASSET_CATEGORIES` is
UNCHANGED, `keys` stays excluded. This is a materially different, more promising state than the
closed Objaverse finding (0/5, none even cleared the area floor) and worth a follow-up look at the
centering issue specifically, not a repeat of the Objaverse dead end. Full result:
`results/reports/asset_candidates_result.json` (uids `keychain_1`/`keychain_2`).

**wallet: FINAL.** Checked directly against OVMM's full 108-category list — no `wallet` match, no
`purse`/`billfold` synonym either. Combined with the closed Objaverse finding (0/5), this category
has now been checked against two independent, real asset sources (10 total candidates across both)
and found nothing in either. `NO_ASSET_CATEGORIES` stays as the honest, closed answer — no further
sourcing planned or recommended.

**cup: promoted.** The native-small-category floor finding above (this file's Round 3) flagged `cup`
as riding the substituted `drinkware` asset, itself only a 0.94% frame-area pass under direct
re-measurement with the current (Spectator Camera round) camera — small but no longer the outright
`mask_too_small` failure originally documented (that finding predates the Spectator Camera round's
closer framing). OVMM's `cup` category (87 candidates) includes several assets already present in
our own local HSSD copy under `train_val/hssd/` naming — no download needed. Measured
`547c0a77b74f52c4e6c4a0a52f14f6c9c7a57b49` ("Artisan Fair Trade mug", HSSD semantics wnsynsetkey
`cup.n.01` — a genuine native match, not a substitution) directly through the real spectator-camera +
mask-predicate pipeline at the same anchor: **5.7% frame area vs. the substitution's 0.94%, both
passing, the new one far more legible.** `SPAWNABLE_ASSET_BY_CATEGORY["cup"]` now points to this
asset; `CATEGORY_SUBSTITUTED` is empty (cup is no longer a substitution — `drinkware` itself is
untouched, still mapped to the old asset for its own, separate events). All 4 rebuilt folders and the
full test suite + gold set confirm this swap is safe (no placement-outcome regressions — the two
assets are similar enough in scale that build-time collision/footprint behavior is unaffected).

## Round 5 (Pre-Pool-Build Remediation round, Carried): keychain `mask_off_center` diagnostic

Round 4 flagged `keychain_1`/`keychain_2` as "worth a follow-up look at the centering issue
specifically" rather than a repeat of the closed Objaverse dead end. This round's Carried section
budgeted one diagnostic render (`keychain_1`, `dining.table`, scene 102343992) with both the mask
centroid (from the actual rendered/segmented pixels) and the AABB-center projection (the point
`spectator_viewpoint`'s camera-aim uses, derived from `get_world_aabb`'s collision geometry) drawn on
the same frame, to test whether the object's visual mesh and its collision AABB disagree about where
the object actually is.

**Confirmed, visually, not just by pixel distance: they disagree, by a lot.** The AABB-center
projection (blue cross) lands near the table's back edge, in open space — nowhere near the object.
The keychain itself (small reflective/metallic blob with a bright specular highlight, bottom of
frame) sits close to the raw anchor projection (green X, the table-surface point used for placement),
118px away from the AABB-center in a 360px-tall frame (33% of frame height). Since
`spectator_viewpoint` aims the camera at the AABB center by construction, the camera is provably
aiming at a point in empty air above the table, not at the keychain — `mask_off_center` isn't a
marginal framing miss, it's the direct, mechanical consequence of aiming at the wrong 3D point.
Render: `results/reports/asset_candidates/keychain_1_mask_off_center_diagnostic.png`.

**Root cause not fully isolated within this diagnostic's ten-minute budget** — plausible candidates
are the same class of dual-mesh divergence this round's item 1/3 findings describe for HSSD
furniture (an OVMM-sourced asset's collision proxy could equally be authored independently of its
visual mesh, with its own pivot/extent), or a genuinely oversized/mispositioned collision AABB on
this specific asset. Not enough evidence yet to say which. **Not promoted** — this is a real,
disclosed negative finding, not a clean pass; `NO_ASSET_CATEGORIES` stays unchanged, `keys` stays
excluded. If `keychain` is revisited, the next diagnostic step is checking whether
`spectator_viewpoint`/`get_world_aabb` should be computing the aim point from the RENDER mesh's own
bounds instead of the collision AABB for small spawned props generally (a fix with broader value,
not keychain-specific), rather than patching this one asset.

## Out of scope, confirmed unchanged

No agent/belief/policy code touched. No historical `generation_out/` results modified or regenerated
— existing keys/wallet events in past folders remain exactly as they were (symbolic-tier,
caption-annotated). No asset hunting beyond the 5-per-category timebox (10 total candidates
evaluated, not more).
