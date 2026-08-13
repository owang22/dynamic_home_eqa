#!/usr/bin/env python3
"""Read an IPUMS ATUS hierarchical extract and pull one respondent's diary.

The extract (`atus_00001.dat.gz`) arrived WITHOUT its DDI codebook, so the
fixed-width layout below was inferred from the data and then VALIDATED
against ATUS invariants (see :func:`validate`) — every diary must start and
end at 04:00, activities must tile the day contiguously, and durations must
sum to 1440 minutes. All 6,146 respondents pass, which is strong evidence
the column offsets are right; if a codebook (.xml/.cbk) turns up, prefer it.

Record layout, inferred (0-indexed columns):

    RECTYPE 1 household, width 27
    RECTYPE 2 person,    width 69   (demographics; fields NOT decoded — they
                                     need the DDI, and this tool does not
                                     guess at them)
    RECTYPE 3 activity,  width 55
        0      RECTYPE
        1-5    YEAR                 (zero-padded, e.g. "02025")
        6-19   CASEID               (14 digits; ONE respondent-day = what a
                                     "household" means in ATUS)
        20-28  person + activity-line counters
        29-34  ACTIVITY             6-digit ATUS lexicon code
        35-38  WHERE                IPUMS location code (9999 = NIU, e.g.
                                     while asleep)
        39-46  START                HH:MM:SS
        47-54  STOP                 HH:MM:SS

Usage:
    python atus/read_extract.py --list                 # candidate diaries
    python atus/read_extract.py --caseid 20250101250011
    python atus/read_extract.py --caseid ... --csv out.csv
"""

from __future__ import annotations

import argparse
import csv
import gzip
import pathlib
from dataclasses import dataclass
from typing import Dict, Iterator, List

DEFAULT_EXTRACT = pathlib.Path(__file__).with_name("atus_00001.dat.gz")

COL = {"year": (1, 6), "caseid": (6, 20), "counters": (20, 29),
       "activity": (29, 35), "where": (35, 39),
       "start": (39, 47), "stop": (47, 55)}

DAY_START_MIN = 4 * 60          # ATUS diaries run 04:00 -> 04:00 next day
DAY_MINUTES = 1440
DAY_END_MIN = DAY_START_MIN + DAY_MINUTES
"""End of the diary window (28:00 = 04:00 the next morning). The LAST record
of a diary keeps the respondent's real reported stop, which usually runs
past this boundary (5,353 of 6,146 diaries here) — clip it to the window
and every diary tiles exactly 1440 minutes."""

# IPUMS ATUS WHERE codes. Without the DDI these were assigned from the raw
# ATUS TEWHERE order (places 1-11 -> 101-110 then the late additions bank/
# gym/post office -> 111-113, other/unspecified -> 114-115; travel modes
# 12-21 -> 230-239) and CONFIRMED against what each code actually hosts in
# this extract: 990 grocery-shopping records at 106, 51 banking at 111, 116
# workouts at 112, work-main-job concentrated at 102, sleeping at 9999. The
# three low-volume codes (113 post office, 115 unspecified place, 9998) are
# the least certain — flagged so a codebook can settle them.
WHERE_LABELS: Dict[int, str] = {
    9999: "—  (not asked: asleep / personal care)",
    101: "Respondent's home or yard", 102: "Respondent's workplace",
    103: "Someone else's home", 104: "Restaurant or bar",
    105: "Place of worship", 106: "Grocery store",
    107: "Other store or mall", 108: "School",
    109: "Outdoors away from home", 110: "Library", 111: "Bank",
    112: "Gym or health club", 113: "Post office (inferred)",
    114: "Other place", 115: "Unspecified place (inferred)",
    230: "Car, truck, or motorcycle (driver)",
    231: "Car, truck, or motorcycle (passenger)",
    232: "Walking", 233: "Bus", 234: "Subway or train", 235: "Bicycle",
    236: "Boat or ferry", 237: "Taxi or rideshare", 238: "Airplane",
    239: "Other mode of transportation",
    9998: "Unspecified (inferred)",
}

HOME, TRAVEL_FLOOR = 101, 230
"""101 is home; codes >= 230 are travel modes (everything between is 'out')."""

# ATUS major activity categories (first two digits of the 6-digit code).
MAJOR_LABELS: Dict[str, str] = {
    "01": "Personal care", "02": "Household activities",
    "03": "Caring for household members",
    "04": "Caring for non-household members", "05": "Work",
    "06": "Education", "07": "Consumer purchases",
    "08": "Professional/personal care services",
    "09": "Household services", "10": "Government services",
    "11": "Eating and drinking", "12": "Socializing, relaxing, leisure",
    "13": "Sports, exercise, recreation", "14": "Religious/spiritual",
    "15": "Volunteering", "16": "Telephone calls", "18": "Travel",
    "50": "Data codes (unable to code / gap)",
}

# Detailed labels for the codes this extract actually uses most; anything
# else falls back to its major category so a row is never unlabeled.
ACTIVITY_LABELS: Dict[str, str] = {
    "010101": "Sleeping", "010102": "Sleeplessness",
    "010201": "Washing, dressing, grooming", "010299": "Personal care, n.e.c.",
    "010301": "Health-related self care", "010401": "Personal activities",
    "020101": "Interior cleaning", "020102": "Laundry",
    "020103": "Sewing, repairing textiles", "020104": "Storing interior items",
    "020201": "Food and drink preparation", "020202": "Food presentation",
    "020203": "Kitchen and food clean-up", "020301": "Interior maintenance",
    "020401": "Exterior cleaning", "020501": "Lawn, garden, houseplants",
    "020681": "Care for animals/pets", "020699": "Pet care, n.e.c.",
    "020701": "Vehicle repair/maintenance (by self)",
    "020801": "Household management: financial",
    "020902": "Household organization and planning",
    "029999": "Household activities, n.e.c.",
    "030101": "Physical care for household children",
    "030103": "Reading to/with household children",
    "030104": "Playing with household children (not sports)",
    "030186": "Talking with/listening to household children",
    "030201": "Homework (household children)",
    "030301": "Providing medical care to household children",
    "040101": "Physical care for non-household children",
    "050101": "Work, main job", "050102": "Work, other job",
    "050201": "Work-related activities", "059999": "Work, n.e.c.",
    "060101": "Taking class for degree",
    "060301": "Research/homework for class",
    "070101": "Grocery shopping", "070102": "Purchasing gas",
    "070103": "Purchasing food (not groceries)",
    "070104": "Shopping, except groceries/food/gas",
    "080101": "Using paid childcare services",
    "080201": "Banking", "080401": "Using legal services",
    "080601": "Using medical services",
    "080702": "Using personal care services",
    "090101": "Using interior cleaning services",
    "100101": "Using government services",
    "110101": "Eating and drinking",
    "110201": "Waiting associated with eating/drinking",
    "120101": "Socializing with others",
    "120199": "Socializing, n.e.c.",
    "120201": "Attending/hosting social events",
    "120301": "Relaxing, thinking", "120302": "Tobacco and drug use",
    "120303": "Television and movies (not religious)",
    "120304": "Television (religious)", "120305": "Listening to the radio",
    "120306": "Listening to/playing music (not radio)",
    "120307": "Playing games", "120308": "Computer use for leisure",
    "120309": "Arts and crafts as a hobby",
    "120310": "Collecting as a hobby", "120311": "Hobbies, except collecting",
    "120312": "Reading for personal interest",
    "120313": "Writing for personal interest",
    "120399": "Relaxing and leisure, n.e.c.",
    "120401": "Attending performing arts",
    "120403": "Attending museums", "120404": "Attending movies/film",
    "130101": "Doing aerobics", "130103": "Bicycling",
    "130124": "Running", "130128": "Walking",
    "130131": "Weightlifting/strength training",
    "130133": "Working out, unspecified",
    "140101": "Attending religious services",
    "140102": "Participation in religious practices",
    "150101": "Computer use (volunteer)",
    "150201": "Food preparation/presentation (volunteer)",
    "160101": "Telephone calls to/from family",
    "160102": "Telephone calls to/from friends/neighbors",
    "160103": "Telephone calls to/from education services",
    "160106": "Telephone calls to/from medical services",
    "180101": "Travel related to personal care",
    "180201": "Travel related to household activities",
    "180301": "Travel related to caring for household children",
    "180401": "Travel related to caring for non-household members",
    "180501": "Travel related to work",
    "180601": "Travel related to education",
    "180701": "Travel related to consumer purchases",
    "180801": "Travel related to personal care services",
    "180802": "Travel related to medical services",
    "180901": "Travel related to household services",
    "181101": "Travel related to eating and drinking",
    "181201": "Travel related to socializing/leisure",
    "181301": "Travel related to sports/exercise",
    "181401": "Travel related to religious activities",
    "181501": "Travel related to volunteering",
    "181801": "Security procedures related to travel",
    "189999": "Travel, n.e.c.",
    "500101": "Insufficient detail in verbatim",
    "500103": "Missing travel or destination", "500105": "Respondent refused",
    "500106": "Gap/can't remember", "500107": "Unable to code",
}


PERSONAL_CARE = "01"
"""Major category treated as at-home by definition (sleeping, grooming,
health self-care): ATUS does not ask WHERE for these."""


@dataclass(frozen=True)
class Block:
    """A home activity, or one merged span spent out of the house.

    The home/away collapse keeps full activity detail INSIDE the home — the
    only place object state can change — and reduces everything else to a
    single "Out of house" span, however fragmented the diary was out there.
    That matches how the simulated households model absence (one ELSEWHERE),
    and it is what makes an ATUS day comparable to them.
    """

    start_min: int
    stop_min: int
    at_home: bool
    code: str = ""
    label: str = "Out of house"
    imputed: bool = False        # location carried forward (see home_blocks)

    @property
    def duration(self) -> int:
        return self.stop_min - self.start_min

    @property
    def start_hms(self) -> str:
        m = self.start_min % DAY_MINUTES
        return f"{m // 60:02d}:{m % 60:02d}"

    @property
    def stop_hms(self) -> str:
        m = min(self.stop_min, DAY_END_MIN) % DAY_MINUTES
        return f"{m // 60:02d}:{m % 60:02d}"


@dataclass(frozen=True)
class Activity:
    """One diary entry. Times are minutes since midnight of the diary day;
    entries after 24:00 belong to the next calendar morning (ATUS days run
    04:00 -> 04:00), so ``start_min`` may exceed 1440 after unwrapping."""

    caseid: str
    line: int
    code: str
    where: int
    start_hms: str
    stop_hms: str
    start_min: int
    stop_min: int

    @property
    def duration(self) -> int:
        """Minutes inside the diary window (the final record is clipped)."""
        return min(self.stop_min, DAY_END_MIN) - self.start_min

    @property
    def is_home(self) -> bool:
        return self.where == HOME

    @property
    def is_travel(self) -> bool:
        return self.where >= TRAVEL_FLOOR and self.where < 9000

    @property
    def label(self) -> str:
        return ACTIVITY_LABELS.get(
            self.code, MAJOR_LABELS.get(self.code[:2], "?") + " (detail n.e.c.)")

    @property
    def major(self) -> str:
        return MAJOR_LABELS.get(self.code[:2], "?")

    @property
    def where_label(self) -> str:
        return WHERE_LABELS.get(self.where, f"code {self.where}")


def _hms_to_min(hms: str) -> int:
    h, m, _ = hms.split(":")
    return int(h) * 60 + int(m)


def read_activities(path: pathlib.Path) -> Iterator[Activity]:
    """Yield every activity record, unwrapping past-midnight times."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        prev_case, offset, prev_stop = None, 0, 0
        for raw in f:
            if not raw.startswith("3"):
                continue
            g = {k: raw[a:b] for k, (a, b) in COL.items()}
            caseid = g["caseid"]
            if caseid != prev_case:
                prev_case, offset, prev_stop = caseid, 0, 0
            start, stop = _hms_to_min(g["start"]), _hms_to_min(g["stop"])
            # A diary crosses midnight: once the clock wraps, keep adding a
            # day so durations and ordering stay monotone within a case.
            if start + offset < prev_stop:
                offset += DAY_MINUTES
            start += offset
            stop += offset
            if stop < start:
                stop += DAY_MINUTES
            prev_stop = stop
            yield Activity(caseid=caseid, line=int(g["counters"][-2:]),
                           code=g["activity"], where=int(g["where"]),
                           start_hms=g["start"][:5], stop_hms=g["stop"][:5],
                           start_min=start, stop_min=stop)


def by_case(path: pathlib.Path) -> Dict[str, List[Activity]]:
    out: Dict[str, List[Activity]] = {}
    for a in read_activities(path):
        out.setdefault(a.caseid, []).append(a)
    return out


def validate(diaries: Dict[str, List[Activity]]) -> Dict[str, int]:
    """Check the inferred layout against ATUS's structural guarantees."""
    bad = {"starts_late": 0, "not_contiguous": 0, "wrong_total": 0,
           "overruns_window": 0, "unknown_major": 0, "unknown_where": 0}
    for acts in diaries.values():
        if acts[0].start_min != DAY_START_MIN:
            bad["starts_late"] += 1
        if any(a.stop_min != b.start_min for a, b in zip(acts, acts[1:])):
            bad["not_contiguous"] += 1
        if sum(a.duration for a in acts) != DAY_MINUTES:
            bad["wrong_total"] += 1
        if any(a.start_min >= DAY_END_MIN for a in acts):
            bad["overruns_window"] += 1
        for a in acts:
            if a.code[:2] not in MAJOR_LABELS:
                bad["unknown_major"] += 1
            if a.where not in WHERE_LABELS:
                bad["unknown_where"] += 1
    return bad


def home_blocks(acts: List[Activity]) -> List[Block]:
    """Collapse a diary to home-detail plus merged out-of-house spans.

    A record counts as at home when its location is the respondent's home
    or yard, OR when location was not asked and the activity is personal
    care (asleep, washing, dressing) — awake or not, that happens at home.
    A not-asked record that is NOT personal care is a diary gap or data
    code; its location carries forward from the previous block (the
    respondent did not teleport) and the block is flagged ``imputed`` so
    the imputation is never invisible.
    """
    blocks: List[Block] = []
    at_home = True                      # diaries open at 04:00, asleep
    for a in acts:
        imputed = False
        if a.where == HOME:
            at_home = True
        elif a.where >= 9000:
            if a.code[:2] == PERSONAL_CARE:
                at_home = True
            else:
                imputed = True          # keep the previous location
        else:
            at_home = False
        stop = min(a.stop_min, DAY_END_MIN)
        if at_home:
            blocks.append(Block(start_min=a.start_min, stop_min=stop,
                                at_home=True, code=a.code, label=a.label,
                                imputed=imputed))
        elif blocks and not blocks[-1].at_home:
            prev = blocks[-1]           # merge consecutive time away
            blocks[-1] = Block(start_min=prev.start_min, stop_min=stop,
                               at_home=False,
                               imputed=prev.imputed or imputed)
        else:
            blocks.append(Block(start_min=a.start_min, stop_min=stop,
                                at_home=False, imputed=imputed))
    return blocks


def render_home_table(blocks: List[Block]) -> str:
    """The collapsed view: home activities in detail, away as single spans."""
    rows = [f"{'START':>5} {'STOP':>5} {'MIN':>4}  {'WHERE':<14} ACTIVITY",
            "-" * 78]
    for b in blocks:
        where = "home/yard" if b.at_home else "OUT OF HOUSE"
        flag = " *" if b.imputed else ""
        rows.append(f"{b.start_hms:>5} {b.stop_hms:>5} {b.duration:>4}  "
                    f"{where:<14} {b.label}{flag}")
    home = sum(b.duration for b in blocks if b.at_home)
    rows += ["-" * 78,
             f"{len(blocks)} blocks · home {home / 60:.1f} h "
             f"({home / 14.4:.0f}% of the day), out of house "
             f"{(DAY_MINUTES - home) / 60:.1f} h"]
    if any(b.imputed for b in blocks):
        rows.append("* location carried forward across a diary gap/data code")
    return "\n".join(rows)


def render_table(acts: List[Activity]) -> str:
    rows = [f"{'#':>3}  {'START':>5} {'STOP':>5} {'MIN':>4}  "
            f"{'ACTIVITY':<44} {'CODE':<7} WHERE",
            "-" * 118]
    for a in acts:
        rows.append(f"{a.line:>3}  {a.start_hms:>5} {a.stop_hms:>5} "
                    f"{a.duration:>4}  {a.label[:44]:<44} {a.code:<7} "
                    f"{a.where_label}")
    rows.append("-" * 118)
    rows.append(f"     {len(acts)} activities, "
                f"{sum(a.duration for a in acts)} minutes total")
    return "\n".join(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--extract", type=pathlib.Path, default=DEFAULT_EXTRACT)
    ap.add_argument("--caseid", default=None)
    ap.add_argument("--list", action="store_true",
                    help="show candidate diaries (most activities first)")
    ap.add_argument("--csv", type=pathlib.Path, default=None)
    ap.add_argument("--home-only", action="store_true",
                    help="collapse to home detail + merged out-of-house spans")
    args = ap.parse_args()

    diaries = by_case(args.extract)
    bad = validate(diaries)
    print(f"{len(diaries)} respondent-days parsed; layout validation: "
          + ("ALL PASS" if not any(bad.values()) else f"FAILURES {bad}"))

    if args.list or not args.caseid:
        ranked = sorted(diaries.items(), key=lambda kv: -len(kv[1]))
        print("\ncaseid           n_act  distinct places  n_travel  first activity")
        for caseid, acts in ranked[:15]:
            places = len({a.where for a in acts if a.where != 9999})
            travel = sum(a.code[:2] == "18" for a in acts)
            print(f"{caseid}  {len(acts):>5}  {places:>15}  {travel:>8}  "
                  f"{acts[0].label}")
        if not args.caseid:
            return

    acts = diaries[args.caseid]
    if args.home_only:
        blocks = home_blocks(acts)
        print(f"\nDIARY (home-collapsed) — caseid {args.caseid}\n")
        print(render_home_table(blocks))
        if args.csv:
            with open(args.csv, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["start", "stop", "duration_min", "where",
                            "activity_code", "activity", "location_imputed"])
                for b in blocks:
                    w.writerow([b.start_hms, b.stop_hms, b.duration,
                                "home/yard" if b.at_home else "out_of_house",
                                b.code, b.label, b.imputed])
            print(f"\nwrote {args.csv}")
        return
    print(f"\nDIARY — caseid {args.caseid} "
          f"({len(acts)} activities, 04:00 to 04:00)\n")
    print(render_table(acts))
    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["line", "activity_code", "activity", "major",
                        "start", "stop", "duration_min", "where_code", "where"])
            for a in acts:
                w.writerow([a.line, a.code, a.label, a.major, a.start_hms,
                            a.stop_hms, a.duration, a.where, a.where_label])
        print(f"\nwrote {args.csv}")


if __name__ == "__main__":
    main()
