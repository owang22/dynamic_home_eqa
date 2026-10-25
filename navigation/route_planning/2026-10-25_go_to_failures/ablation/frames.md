# What is at the live cells the thin tiers routed past? (camera check)

**Method**
* For each replay fixed by D's tier 1/2 ("thin" live relaxation), take the live cell its route passed closest to:
  `ablation.json` → `D_full…` → `closest_live`. That gives the cell, its distance from the route, and its distance
  and map bearing from the dog.
* Look for trail frames (`~/oliver/go2_maps/lab_trail/<day>/index.jsonl`: `t`, map `x, y, yaw`, file) within
  ±60 s. Compute the cell's distance and bearing in each frame (camera ±40°, 640 px). Draw a red vertical line at
  that bearing: `frames_annotate.py` → `frames/`.
* I opened each frame and classified what sits on the line at the given distance.
* **Rule:** a classification counts only if a frame within about 10 s shows the spot within 2 m. Otherwise it's
  "unclear: no frame", and anything seen in a later or earlier frame is noted separately.
* Trail frames are kept only when the dog moves 0.3 m or turns 20°. A standing dog produces no new frames, which
  is why several records have none within 10 s.
* Frame poses are the console's map poses, same frame as the cells. None of these records is in a lost window.
  The poses can still be off by about 0.1–0.3 m and a few degrees, so a line that just misses an object doesn't
  prove the spot was empty.

"Needs thin after B/C": does the fix disappear when live cells keep full clearance (variants B and C)?

| records | D tier | route→cell (D) | needs thin after B/C | cell (map) | frame (offset) | cell in frame: dist, bearing | what's there | conf. |
|---|---|---|---|---|---|---|---|---|
| 45 | thin_live | 0.10 m | **yes** | (−0.35, 2.95) | `20261023/1792808658477.jpg` (+1.5 s) | 1.14 m, +62° (outside the ±40° view) | **unclear: no frame** shows the spot within 10 s | – |
| 48–50 | thin_live_noblocks | 0.67 m | no (B fixes it) | (1.25, −2.95) | – | – | n/a: the route never comes near a live cell; only the block was relaxed | – |
| 51 | thin_live_noblocks | 0.07 m | no (B: 0.14 m) | (1.85, −1.45) | `20261023/1792809500249.jpg` (+7.2 s) | 1.12 m, −36° (right edge) | **chair**: an office chair base at the right edge, about 1 m | medium (edge of view) |
| 52 | thin_live_noblocks | 0.14 m | no (B: 0.21 m) | (1.35, −0.05) | `20261023/1792809548220.jpg` (−3.8 s) | 0.85 m, +28° | **unclear**: an object right in front of the lens covers most of the view; the line runs along its left edge | – |
| 53 | thin_live_noblocks | 0.16 m | no (B: 0.28 m) | (1.25, 0.05) | `…548220.jpg` (−18.5 s) | 0.98 m, +24° | **unclear: no frame** within 10 s (the −18.5 s frame is the occluded one) | – |
| 54–55 | thin_live_noblocks | 0.16 m | no (B: 0.28 m) | (1.75, −0.05) | `…548220.jpg` (−20.6 s) | 0.48 m, +14° | **unclear: no frame** within 10 s | – |
| 56–59 | thin_live_noblocks | 0.20 m | no (B: 0.23 m) | (1.75, −0.05) | `20261023/1792809610049.jpg` (+18.8 to +29.8 s) | 0.53 m, −6° | **unclear: no frame** within 10 s. *Outside the window:* the +19–30 s frame shows a **blue mop bucket** on the line at about 0.5 m (cheetah's #24 mop bucket) | – |
| 68 | thin_live | 0.09 m | **yes** | (−0.35, 2.85) | `20261024/1792882583356.jpg` (−5.7 s), `…581459.jpg` (−7.6 s), `…597794.jpg` (+8.8 s) | 1.25 m −15°, 1.29 m +20°, 1.14 m +8° | **unclear**: the line crosses open floor in all three, but there are objects within a few tenths of a metre of it (a stand base and boxes; tripod and desk legs). A 0.2 m pose error decides it | – |
| 84 | thin_live_noblocks | 0.07 m | **yes** | (−0.25, 2.95) | `20261024/1792885782969.jpg` (+1.4 s) | 0.40 m, −1° | **other object**: a wooden panel with a black cable bundle right in front of the dog (the "workbench" panel from board #24) | high |
| 85–86 | thin_live_noblocks | 0.07 m | **yes** | (−0.55, 3.05) | `…782969.jpg` (−2.8 s) | 0.64 m, −24° | **other object**: the same wooden panel and cable bundle | high |
| 87–88 | thin_live_noblocks | 0.14 m | no (B: 0.21 m) | (−0.55, 2.85) | `…782969.jpg` (−6.8 / −8.9 s) | 0.70 m, −8° | **other object**: the same wooden panel | high |
| 89 | thin_live_noblocks | 0.14 m | no (B: 0.21 m) | (−0.55, 2.85) | `20261024/1792885804041.jpg` (+10.2 s) | 0.68 m, −15° | **other object**: cardboard boxes (CyberPower) on the line at about 0.7 m | medium (10.2 s) |

**Counts over the 20 records D fixed with tier 1/2:**
* other object (panel, boxes): 6 (#84–89);
* chair: 1 (#51);
* person: 0;
* nothing visible (smear or ghost): 0;
* unclear: 10 (#45, #52–59, #68). 7 of those have no frame within 10 s;
* n/a (the route isn't near a live cell): 3 (#48–50).

**The 5 records that still need the thin relaxation after B/C (#45, #68, #84, #85, #86):**
* In 3 (#84–86) the live cell is a **real wooden panel with cables**, and D's route passes 0.07 m from it.
* The other 2 are unclear.
* No frame showed a live cell to be smear.

Annotated frames (640×360, red line = the cell's bearing) are in `frames/`. Their index, with frame time and pose,
is in `frames_index.json`.
