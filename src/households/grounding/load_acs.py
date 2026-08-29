"""Census household-composition and employment marginals, hard-coded.

Per the plan: published table values with source comments, no API
client. Every number carries its table of origin; update by editing in
place with a new retrieval date.

Sources (retrieved 2026-08-28):
- US Census Bureau, "America's Families and Living Arrangements: 2023",
  table HH-1 / AVG-1 lineage (households by type). The coarse split the
  sampler targets: ~29% one-person households, ~35% married/cohabiting
  couple without children at home, ~19% households with children under
  18, remainder other family/nonfamily arrangements.
- BLS "Job Flexibilities and Work Schedules" (2017-2018 ATUS module,
  latest published): ~84% of full-time wage and salary workers mainly
  work a daytime schedule; evening ~4-6%, night ~4%, rotating ~2-3%,
  irregular/other the rest. These are the tier-2 oversampling baseline
  rates — tier 2 deliberately exceeds them and says so.
- BLS CPS annual averages 2024: labor force participation ~62-63% of the
  16+ population; ~80% of the employed work full time.
"""
from __future__ import annotations

# Household composition marginals (fractions of all US households).
# Coarse on purpose: the sampler checks tier-1 slots against these within
# +/- 10 points, nothing finer.
COMPOSITION_MARGINALS = {
    "single_adult": 0.29,
    "couple": 0.35,                        # no children at home
    "couple_with_children": 0.13,
    "single_parent_with_children": 0.06,
    "roommates": 0.09,                     # nonfamily, 2+ person
    "multigenerational": 0.08,             # other family arrangements
}

# Work-schedule prevalence among workers (BLS module above). POPULATION
# rates — tier 2 oversamples the non-daytime rows deliberately.
SCHEDULE_PREVALENCE = {
    "fixed_daytime": 0.84,
    "fixed_evening": 0.05,
    "fixed_night_shift": 0.04,
    "rotating_shift": 0.03,
    "irregular_gig": 0.04,
}

EMPLOYED_SHARE_OF_ADULTS = 0.62    # CPS participation, coarse
FULL_TIME_SHARE_OF_EMPLOYED = 0.80


def composition_targets() -> dict:
    assert abs(sum(COMPOSITION_MARGINALS.values()) - 1.0) < 1e-9
    return dict(COMPOSITION_MARGINALS)


def schedule_prevalence() -> dict:
    assert abs(sum(SCHEDULE_PREVALENCE.values()) - 1.0) < 1e-9
    return dict(SCHEDULE_PREVALENCE)
