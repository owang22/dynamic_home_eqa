"""VERSION22 banks + reflect config.

Version22 doubles the confirmatory household count (6 -> 12), varies the
personas far more broadly than the regime_v1 set, and pushes objects into
idiosyncratic-but-realistic uses (a mug holding paintbrushes for an artistic
kid, a bath towel as a proofing couche, a TV remote stored out of toddler
reach, keys clipped to a bike pannier). Every profile also carries a set of
STATIC DISTRACTOR objects (a chair by the dining table, a pillow on a bed...)
that never move: the distractor observation system (reflect/run.py) emits
sightings of them to inflate observations/day WITHOUT adding information.
Distractor objects never appear in queries.

Banks (built with profiles/bank.py BankSpec, --allow-draft until the profiles
are human-verified):
  version22       12 confirmatory households (below)
  version22_dev   4 dev households — alpha sweep only (dev/test wall)

CFG maps household -> {"targets": [(object, query_hour) x3],
                       "distractors": [static objects for the sighting pool]}.
"""
from __future__ import annotations

V22_BANK = "version22"
V22_DEV_BANK = "version22_dev"
V22B_BANK = "version22b"      # bank-expansion (Change 0): 3 NEW confusable pairs,
                             # each persona instantiated at 2 seeds (12 households),
                             # to lift clusters/tercile past 15 so day-14 CIs can
                             # separate. version22 (12 hh) stays FROZEN; the
                             # "expanded" numbers pool version22 + version22b.

_DIST8 = ["dining_chair", "bed_pillow", "wall_clock", "floor_lamp",
          "doormat", "waste_bin", "picture_frame", "bath_mat"]

V22_CFG = {
    "v22_artist_kid_family": {
        "targets": [("coffee_mug", 17), ("scissors", 17), ("tablet", 17)],
        "distractors": _DIST8},
    "v22_homeschool_family": {
        "targets": [("coffee_mug", 10), ("scissors", 10), ("tablet", 10)],
        "distractors": _DIST8},
    "v22_open_water_swimmer": {
        "targets": [("towel", 21), ("water_bottle", 21), ("keys", 10)],
        "distractors": _DIST8},
    "v22_dawn_bread_baker": {
        "targets": [("towel", 6), ("water_bottle", 6), ("keys", 11)],
        "distractors": _DIST8},
    "v22_gamer_streamer": {
        "targets": [("phone", 23), ("blanket", 23), ("bowl", 23)],
        "distractors": _DIST8},
    "v22_backyard_astronomer": {
        "targets": [("phone", 23), ("blanket", 23), ("coffee_mug", 23)],
        "distractors": _DIST8},
    "v22_plant_collector": {
        "targets": [("watering_can", 8), ("scissors", 15), ("notebook", 8)],
        "distractors": _DIST8},
    "v22_reptile_keeper": {
        "targets": [("watering_can", 8), ("scissors", 15), ("notebook", 20)],
        "distractors": _DIST8},
    "v22_food_truck_owner": {
        "targets": [("keys", 8), ("thermos", 21), ("laptop", 22)],
        "distractors": _DIST8},
    "v22_teacher_coach": {
        "targets": [("keys", 10), ("thermos", 21), ("laptop", 21)],
        "distractors": _DIST8},
    "v22_twin_toddlers": {
        "targets": [("remote", 10), ("cushion", 10), ("tablet", 14)],
        "distractors": _DIST8},
    "v22_elder_care": {
        "targets": [("remote", 11), ("cushion", 11), ("tablet", 16)],
        "distractors": _DIST8},
}

V22_DEV_CFG = {
    "v22dev_home_potter": {
        "targets": [("coffee_mug", 10), ("towel", 10), ("phone", 10)],
        "distractors": _DIST8},
    "v22dev_bike_courier": {
        "targets": [("keys", 12), ("water_bottle", 12), ("phone", 23)],
        "distractors": _DIST8},
    "v22dev_knitting_host": {
        "targets": [("reading_glasses", 15), ("scissors", 15), ("coffee_mug", 15)],
        "distractors": _DIST8},
    "v22dev_room_renovator": {
        "targets": [("coffee_mug", 20), ("radio", 20), ("phone", 20)],
        "distractors": _DIST8},
}


# version22b: 3 NEW confusable pairs (regime-legible; each pair shares an object
# set and differs in ONE activity, so the differing-activity prediction stays
# testable). Two seed-INSTANCES per persona (i1, i2) grow clusters with no new
# authoring — the cheapest band-shrinker. Targets are the SHARED, regime-flipped
# dependent objects (a naive prior mislocates them; a persona-aware memory does not).
_V22B_TARGETS = {
    "v22_retiree_gardener":  [("coffee_mug", 10), ("phone", 10), ("reading_glasses", 10)],
    "v22_wfh_senior":        [("coffee_mug", 10), ("phone", 10), ("reading_glasses", 10)],
    "v22_toddler_home":      [("cushion", 10), ("blanket", 10), ("ball", 16)],
    "v22_pet_heavy":         [("cushion", 10), ("blanket", 10), ("ball", 16)],
    "v22_shift_rotator":     [("laptop", 20), ("phone", 22), ("keys", 20)],
    "v22_frequent_traveler": [("laptop", 20), ("phone", 22), ("keys", 20)],
}
V22B_PERSONAS = list(_V22B_TARGETS)
V22B_INSTANCES = [1, 2]     # seed-variants per persona

V22B_CFG = {
    f"{p}__i{i}": {"targets": t, "distractors": _DIST8}
    for p, t in _V22B_TARGETS.items() for i in V22B_INSTANCES
}


def bank_specs():
    """BankSpecs for the version22 banks (seed distinct from the v1 banks)."""
    from dynbelief.profiles.bank import BankSpec, HouseholdSpec
    return {
        V22_BANK: BankSpec(V22_BANK,
                           [HouseholdSpec(hh) for hh in V22_CFG],
                           seed=20260722),
        V22_DEV_BANK: BankSpec(V22_DEV_BANK,
                               [HouseholdSpec(hh) for hh in V22_DEV_CFG],
                               seed=20260722),
        V22B_BANK: BankSpec(V22B_BANK,
                            [HouseholdSpec(p, instance=i)
                             for p in V22B_PERSONAS for i in V22B_INSTANCES],
                            seed=20260722),
    }


def main():
    import argparse
    import pathlib
    from dynamic_home_eqa.paths import REPO_ROOT
    from dynbelief.profiles.bank import build_bank
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--allow-draft", action="store_true")
    ap.add_argument("--only", default=None,
                    help="build only this bank name (e.g. version22b)")
    ap.add_argument("--banks-root", type=pathlib.Path, default=REPO_ROOT / "banks")
    ap.add_argument("--manual-dir", type=pathlib.Path,
                    default=REPO_ROOT / "profiles" / "manual")
    args = ap.parse_args()
    for name, spec in bank_specs().items():
        if args.only and name != args.only:
            continue
        m = build_bank(spec, args.manual_dir, args.banks_root,
                       allow_draft=args.allow_draft)
        flag = " [NON-REPORTABLE]" if m["non_reportable"] else " [reportable]"
        print(f"[bank] {name}{flag}: {len(m['households'])} households")
        for h in m["households"]:
            print(f"    {h['household']:32s} objs={h['n_objects']} events={h['n_events']}"
                  f" ({h['n_events']/30:.1f}/day)")


if __name__ == "__main__":
    main()
