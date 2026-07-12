# D1: kernel generalization — status and scope

## What's built

1. **Semantic slot types** (`rooms.slot_type_for(category, anchor) -> (category, room)`):
   the cross-scene-portable key D1 needs — two scenes' differently-named
   anchors serving the same functional role (e.g. scene A's
   `kitchen.counter` vs scene B's `kitchen.counter_tucked`) now resolve to
   the same `(category, room)` pair via the existing `rooms.slot_room()`
   resolver. No new room taxonomy was needed; `CANONICAL_ROOMS` already is
   one.
2. **Per-scene anchor mapping, failing at scene qualification**
   (`rooms.unmapped_slots`, wired into `embodied.sampling.qualify_labels`
   as a third qualification property alongside the existing
   `exists_at_patrol_start`/`unreachable_slots` checks): a label with any
   historical anchor `rooms.slot_room` can't resolve now fails
   qualification outright (`LabelQualification.qualifies` is `False`,
   `.reason()` reports which slot(s)), instead of that anchor silently
   falling out of a kernel's room-pooling step at belief-fitting time with
   nothing to notice the gap.
3. **3-level count-weighted backoff** (`posterior.HierarchicalStat`,
   `posterior.shrink_hierarchical`): scene -> profile -> global, reusing
   `posterior._shrink`'s existing weighted-average rule at each level (no
   new smoothing math) — nested so a category thin or absent in one scene
   backs off to other scenes sharing its household profile before falling
   all the way back to the global pool. Verified exact-fallback behavior:
   a zero-weight scene reduces to exactly the profile value; a zero-weight
   scene AND profile reduces to exactly the global value; a
   strongly-weighted scene stays close to its own value regardless of
   profile/global.

All of the above is unit-tested (`tests/test_transition_kernel.py`'s new
`shrink_hierarchical` section, `tests/test_rooms.py`'s new `slot_type_for`/
`unmapped_slots` section, `tests/test_label_qualification.py` — pure logic,
no habitat_sim needed for any of it).

## What's deliberately deferred

`shrink_hierarchical` takes three `HierarchicalStat(value, weight)` inputs
generically — it does not itself know how to compute a "profile-level" or
"global-level" statistic from real data. Doing that for real requires:

- A scene -> household-profile mapping across the full scene pool (the
  scene-pool expansion's own state file has this, but it isn't yet read by
  anything on the belief-fitting side).
- An aggregation step analogous to `attribution.fit_location_kernels_from_
  train`, but reading `category_location_change_stats` from EVERY scene
  sharing a profile (for the profile level) and from the WHOLE pool (for
  the global level), grouped by the new `(category, room)` slot type
  instead of by bare category — a category with different real anchor
  names in different scenes needs its stats pooled through the slot-type
  key, not the anchor string.
- A `fit_transition_kernels_hierarchical`-style entry point that replaces
  `fit_transition_kernels`'s single scene-level pooling step with the
  3-level chain, called from a gate script once enough profile-diverse
  scenes exist to make "profile-level" pooling mean anything.

This is intentionally not built yet: the scene pool was still landing new
profiles as of this phase (see the scene-pool expansion agent's own
progress), and wiring real multi-scene aggregation against a pool that is
still growing would need re-deriving as soon as more scenes/profiles land.
The generalizable, testable core (slot types, qualification-time mapping
validation, the backoff math itself) is complete and stable regardless of
how many scenes eventually populate each profile; only the data-aggregation
plumbing is deferred, and it has one clear next entry point
(`fit_transition_kernels_hierarchical`, not yet written) rather than being
an open-ended gap.
