# HSSD scene taxonomy by named-room count

Surveyed **168** HSSD scenes from their `semantics/scenes/*.semantic_config.json` region annotations. Per-scene detail in `hssd_room_taxonomy.csv`.

**Method:** region names carry `.001/.002` instance suffixes (bedroom + bedroom.001 = 2 bedrooms); these are stripped and counted. Names are normalised onto our `CANONICAL_ROOMS` where possible.

> **Caveat — annotated, not navmesh-verified.** These are HSSD's semantic region labels, i.e. named locations, not a guarantee each is reachable on the agent navmesh. If 'navigable' must be strict, I can cross-check each region centroid against the scene's navmesh island (heavier — needs habitat-sim per scene). For stratification the annotation count is the standard and stable axis.

## Stratification tables (room count : #scenes)

- **Bedrooms** — **0**: 15 | **1**: 34 | **2**: 54 | **3**: 37 | **4**: 15 | **5**: 10 | **6**: 2 | **7**: 1
- **Bathrooms** — **0**: 9 | **1**: 51 | **2**: 69 | **3**: 22 | **4**: 10 | **5**: 5 | **6**: 2
- **Canonical habitable-room instances** (kitchen/dining/living/office/bedroom/bath/laundry, excl. outdoor) — min 2, median 7, max 16
- **All named regions** (incl. hallway/closet/garage/outdoor) — min 4, median 12, max 36

### Suggested stratification axis: **bedroom count** (cleanest, well-spread)

| bedrooms | # scenes | good for |
|---|---|---|
| 0 | 15 | studios / non-residential |
| 1 | 34 | small |
| 2 | 54 | **modal — medium** |
| 3 | 37 | family |
| 4 | 15 | large |
| 5+ | 13 | very large |

Bedroom count is the most interpretable size proxy and every stratum has enough scenes for a balanced draw. If you'd rather stratify by total footprint, use canonical habitable-room instances (spread 2–17).

## Our 3 working scenes (for calibration)

| scene | bedrooms | bathrooms | canonical instances | note |
|---|---|---|---|---|
| 102344022 | 2 | 2 | 7 | roommates — small (2bd) |
| 102344049 | 3 | 3 | 8 | family — medium (3bd) |
| 102343992 | 5 | 2 | 12 | single-parent — large (5bd) |
