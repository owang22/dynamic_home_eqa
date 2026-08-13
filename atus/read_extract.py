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
import datetime
import gzip
import pathlib
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Set, Tuple

DEFAULT_EXTRACT = pathlib.Path(__file__).with_name("atus_00002.dat.gz")
"""The richer extract (all years, with diary dates). The first extract
(atus_00001.dat.gz, 2025 only, no date field) still parses — the layout is
chosen from the record width."""

# Two extracts, two variable sets, so column offsets are keyed by the
# ACTIVITY record's width. Shared prefix in both: RECTYPE(1) YEAR(5)
# CASEID(14) counters(9) ACTIVITY(6) WHERE(4).
LAYOUTS = {
    55: {"year": (1, 6), "caseid": (6, 20), "counters": (20, 29),
         "activity": (29, 35), "where": (35, 39),
         "start": (39, 47), "stop": (47, 55)},
    # The richer extract inserts duration/other variables before the times.
    # Verified: the record's own duration field equals stop - start on
    # 199,999 of 200,000 sampled records.
    82: {"year": (1, 6), "caseid": (6, 20), "counters": (20, 29),
         "activity": (29, 35), "where": (35, 39), "duration": (39, 43),
         "start": (66, 74), "stop": (74, 82)},
}

# Person-record widths that carry the DIARY DATE (YYYYMMDD). Confirmed by
# ATUS's sampling design: reading offset 40 as a date yields Sat 25.8% /
# Sun 25.1% / weekdays ~10% each — the survey's deliberate weekend
# oversampling. The small extract's 69-char person record has no date.
PERSON_DATE_AT = {662: 40}

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

# ATUS codes are hierarchical: 2-digit major, 4-digit subcategory, 6-digit
# detail. Labelling falls back 6 -> 4 -> 2, so an unlabelled detail code
# still reads as its subcategory ("Travel related to consumer purchases")
# rather than the near-useless major ("Travel"). The 4-digit tier below is
# the published ATUS lexicon's second level.
TIER2_LABELS: Dict[str, str] = {
    "0101": "Sleeping", "0102": "Grooming",
    "0103": "Health-related self care", "0104": "Personal activities",
    "0105": "Personal care emergencies", "0199": "Personal care, n.e.c.",
    "0201": "Housework", "0202": "Food and drink prep, presentation, clean-up",
    "0203": "Interior maintenance, repair, decoration",
    "0204": "Exterior maintenance, repair, decoration",
    "0205": "Lawn, garden, houseplants", "0206": "Animals and pets",
    "0207": "Vehicles", "0208": "Appliances, tools, toys",
    "0209": "Household management", "0299": "Household activities, n.e.c.",
    "0301": "Caring for and helping household children",
    "0302": "Household children's education",
    "0303": "Household children's health",
    "0304": "Caring for household adults",
    "0305": "Helping household adults",
    "0399": "Caring for household members, n.e.c.",
    "0401": "Caring for and helping non-household children",
    "0402": "Non-household children's education",
    "0403": "Non-household children's health",
    "0404": "Caring for non-household adults",
    "0405": "Helping non-household adults",
    "0499": "Caring for non-household members, n.e.c.",
    "0501": "Working", "0502": "Work-related activities",
    "0503": "Other income-generating activities",
    "0504": "Job search and interviewing", "0599": "Work, n.e.c.",
    "0601": "Taking class", "0602": "Extracurricular school activities",
    "0603": "Research and homework", "0604": "Registration, administrative",
    "0699": "Education, n.e.c.",
    "0701": "Shopping (store, telephone, internet)",
    "0702": "Comparison shopping, researching purchases",
    "0703": "Security procedures (consumer purchases)",
    "0799": "Consumer purchases, n.e.c.",
    "0801": "Using childcare services",
    "0802": "Using financial services and banking",
    "0803": "Using legal services", "0804": "Using medical services",
    "0805": "Using personal care services", "0806": "Using real estate services",
    "0807": "Using veterinary services",
    "0808": "Security procedures (professional services)",
    "0899": "Using professional services, n.e.c.",
    "0901": "Using household services",
    "0902": "Using home maintenance/repair/construction services",
    "0903": "Using pet services", "0904": "Using lawn and garden services",
    "0905": "Using vehicle maintenance and repair services",
    "0999": "Using household services, n.e.c.",
    "1001": "Using government services",
    "1002": "Civic obligations and participation",
    "1003": "Waiting (government services)",
    "1004": "Security procedures (government services)",
    "1099": "Government services, n.e.c.",
    "1101": "Eating and drinking", "1102": "Waiting (eating and drinking)",
    "1199": "Eating and drinking, n.e.c.",
    "1201": "Socializing and communicating",
    "1202": "Attending or hosting social events",
    "1203": "Relaxing and leisure",
    "1204": "Arts and entertainment (other than sports)",
    "1205": "Waiting (socializing, leisure)",
    "1299": "Socializing and leisure, n.e.c.",
    "1301": "Participating in sports, exercise, recreation",
    "1302": "Attending sporting or recreational events",
    "1303": "Waiting (sports, exercise, recreation)",
    "1304": "Security procedures (sports)",
    "1399": "Sports and recreation, n.e.c.",
    "1401": "Religious and spiritual practices",
    "1499": "Religious and spiritual activities, n.e.c.",
    "1501": "Administrative and support (volunteer)",
    "1502": "Social service and care (volunteer)",
    "1503": "Maintenance, building, clean-up (volunteer)",
    "1504": "Performance and cultural activities (volunteer)",
    "1505": "Meetings, conferences, training (volunteer)",
    "1506": "Public health and safety (volunteer)",
    "1507": "Waiting (volunteer activities)",
    "1508": "Security procedures (volunteer)",
    "1599": "Volunteer activities, n.e.c.",
    "1601": "Telephone calls", "1602": "Waiting (telephone calls)",
    "1699": "Telephone calls, n.e.c.",
    "1801": "Travel: personal care", "1802": "Travel: household activities",
    "1803": "Travel: caring for household members",
    "1804": "Travel: caring for non-household members",
    "1805": "Travel: work", "1806": "Travel: education",
    "1807": "Travel: consumer purchases",
    "1808": "Travel: professional and personal care services",
    "1809": "Travel: household services",
    "1810": "Travel: government services and civic obligations",
    "1811": "Travel: eating and drinking",
    "1812": "Travel: socializing, relaxing, leisure",
    "1813": "Travel: sports, exercise, recreation",
    "1814": "Travel: religious and spiritual activities",
    "1815": "Travel: volunteer activities",
    "1816": "Travel: telephone calls",
    "1818": "Security procedures related to travelling",
    "1899": "Travel, n.e.c.",
    "5001": "Data codes (gap, refusal, unable to code)",
    "5099": "Data codes, n.e.c.",
}

# Exact 6-digit labels for the codes that carry most of the minutes; the
# tier-2 map above covers the long tail.
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


def label_for(code: str) -> str:
    """Best available label: exact detail, else subcategory, else major."""
    if code in ACTIVITY_LABELS:
        return ACTIVITY_LABELS[code]
    if code[:4] in TIER2_LABELS:
        return TIER2_LABELS[code[:4]]
    return MAJOR_LABELS.get(code[:2], "?") + " (uncoded detail)"


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
        return label_for(self.code)

    @property
    def major(self) -> str:
        return MAJOR_LABELS.get(self.code[:2], "?")

    @property
    def where_label(self) -> str:
        return WHERE_LABELS.get(self.where, f"code {self.where}")


def _hms_to_min(hms: str) -> int:
    h, m, _ = hms.split(":")
    return int(h) * 60 + int(m)


def _open(path: pathlib.Path):
    return (gzip.open if path.suffix == ".gz" else open)(path, "rt")


def layout_of(path: pathlib.Path) -> Dict[str, Tuple[int, int]]:
    """Column spec for this extract, chosen by its activity-record width."""
    with _open(path) as f:
        for raw in f:
            if raw.startswith("3"):
                width = len(raw.rstrip("\n"))
                if width not in LAYOUTS:
                    raise SystemExit(
                        f"{path}: unknown activity-record width {width}; "
                        f"known: {sorted(LAYOUTS)}. A DDI codebook would "
                        f"settle the layout — add the .xml alongside the .dat")
                return LAYOUTS[width]
    raise SystemExit(f"{path}: no activity records found")


def diary_dates(path: pathlib.Path) -> Dict[str, datetime.date]:
    """caseid -> the date the diary describes; empty if the extract lacks it.

    ATUS asks about "yesterday", so this is the diary day itself, and its
    weekday distribution is the survey's weekend-oversampled design.
    """
    out: Dict[str, datetime.date] = {}
    with _open(path) as f:
        for raw in f:
            if not raw.startswith("2"):
                continue
            width = len(raw.rstrip("\n"))
            at = PERSON_DATE_AT.get(width)
            if at is None:
                return {}
            caseid, d = raw[6:20], raw[at:at + 8]
            out[caseid] = datetime.date(int(d[:4]), int(d[4:6]), int(d[6:8]))
    return out


def read_activities(path: pathlib.Path,
                    keep: Optional[Set[str]] = None) -> Iterator[Activity]:
    """Yield activity records, unwrapping past-midnight times.

    ``keep`` restricts to a set of caseids — worth using on the large
    extract, whose 3.8 M activity records do not need to be materialized to
    look at a handful of diaries.
    """
    col = layout_of(path)
    with _open(path) as f:
        prev_case, offset, prev_stop = None, 0, 0
        for raw in f:
            if not raw.startswith("3"):
                continue
            if keep is not None and raw[6:20] not in keep:
                continue
            g = {k: raw[a:b] for k, (a, b) in col.items()}
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


def by_case(path: pathlib.Path,
            keep: Optional[Set[str]] = None) -> Dict[str, List[Activity]]:
    out: Dict[str, List[Activity]] = {}
    for a in read_activities(path, keep=keep):
        out.setdefault(a.caseid, []).append(a)
    return out


@dataclass(frozen=True)
class Profile:
    """Per-diary summary from one streaming pass (no diaries materialized)."""

    caseid: str
    n_activities: int
    work_min: int
    home_min: int
    n_home_activities: int
    n_away_spans: int


def scan_profiles(path: pathlib.Path) -> Dict[str, Profile]:
    """Summarize every diary in one pass — cheap enough for 3.8 M records."""
    col = layout_of(path)
    cur: Dict[str, object] = {}
    out: Dict[str, Profile] = {}

    def flush() -> None:
        if not cur:
            return
        out[str(cur["caseid"])] = Profile(
            caseid=str(cur["caseid"]), n_activities=int(cur["n"]),
            work_min=int(cur["work"]), home_min=int(cur["home"]),
            n_home_activities=len(cur["labels"]),      # type: ignore[arg-type]
            n_away_spans=int(cur["spans"]))

    with _open(path) as f:
        at_home, prev_away = True, False
        for raw in f:
            if not raw.startswith("3"):
                continue
            caseid = raw[6:20]
            if caseid != cur.get("caseid"):
                flush()
                cur = {"caseid": caseid, "n": 0, "work": 0, "home": 0,
                       "labels": set(), "spans": 0}
                at_home, prev_away = True, False
            code = raw[col["activity"][0]:col["activity"][1]]
            where = int(raw[col["where"][0]:col["where"][1]])
            start = _hms_to_min(raw[col["start"][0]:col["start"][1]])
            stop = _hms_to_min(raw[col["stop"][0]:col["stop"][1]])
            dur = (stop - start) % DAY_MINUTES or DAY_MINUTES
            if where == HOME:
                at_home = True
            elif where >= 9000:
                at_home = at_home if code[:2] != PERSONAL_CARE else True
            else:
                at_home = False
            cur["n"] = int(cur["n"]) + 1                     # type: ignore[call-overload]
            if code[:2] == "05":
                cur["work"] = int(cur["work"]) + dur         # type: ignore[call-overload]
            if at_home:
                cur["home"] = int(cur["home"]) + dur         # type: ignore[call-overload]
                cur["labels"].add(label_for(code))            # type: ignore[union-attr]
                prev_away = False
            else:
                if not prev_away:
                    cur["spans"] = int(cur["spans"]) + 1     # type: ignore[call-overload]
                prev_away = True
        flush()
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

    dates = diary_dates(args.extract)
    if args.list or not args.caseid:
        profiles = scan_profiles(args.extract)
        ranked = sorted(profiles.values(),
                        key=lambda p: -p.n_home_activities)
        print(f"{len(profiles)} respondent-days"
              + (f"; diary dates {min(dates.values())} .. {max(dates.values())}"
                 if dates else "; no diary-date field in this extract"))
        print("\ncaseid           date        day  n_act  home_h  work_h  "
              "home_acts  away_spans")
        for p in ranked[:15]:
            d = dates.get(p.caseid)
            print(f"{p.caseid}  {d or '—':<10}  "
                  f"{d.strftime('%a') if d else '—':<3}  {p.n_activities:>5}  "
                  f"{p.home_min / 60:>6.1f}  {p.work_min / 60:>6.1f}  "
                  f"{p.n_home_activities:>9}  {p.n_away_spans:>10}")
        if not args.caseid:
            return

    diaries = by_case(args.extract, keep={args.caseid})
    if args.caseid not in diaries:
        raise SystemExit(f"caseid {args.caseid} not in extract")
    bad = validate(diaries)
    when = dates.get(args.caseid)
    print(f"layout validation on this diary: "
          + ("PASS" if not any(bad.values()) else f"FAILURES {bad}")
          + (f"; diary day {when} ({when.strftime('%A')})" if when else ""))
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
