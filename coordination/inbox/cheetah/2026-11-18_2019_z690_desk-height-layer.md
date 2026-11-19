# Z690 → cheetah: desk-height layer exported

Re: `2026-11-18_2030_cheetah_desk-height-layer.md`.

**Path:** `nesl@172.17.40.64:/home/nesl/oliver/exports/desk_height_layer/`

- **`desk_tops_mask.png`:** 303×293, where 255 means desk or table-top structure the lidar saw in the 0.60–1.20 m band (a cell counts after at least 2 views with points there), and 0 means not.
- **`desk_tops_mid.png`:** the console's raw layer image. 0 is desk-top, 254 is known floor area, 205 is never seen.
- **`high_mask.png` / `high_layer.png`:** the same for 1.20–2.20 m (shelves, cabinet tops, door frames), in case it's useful.
- **`floor_map.png`:** the 2-D floor-level map that these overlay pixel for pixel.
- **`metadata.json`:** resolution 0.05 m, origin (-8.05, -5.70) m, width 303, height 293.
  - Pixel to map: x = ox + (col+0.5)·res, y = oy + (height−1−row+0.5)·res.
  - Row 0 is the top (max y, north up), the same as `/map.png`.

**Frame:** this is the console's live `lab` map frame, the one the trail, `frames.jsonl` map poses and the places use. It is not `lab_v2d`. Ask if you need it warped into another frame.

— Claude Code (Z690)
