| cause | mechanism | records | episodes | record ids | ok on current planner | ok on proto C |
|---|---|---|---|---|---|---|
| narrow aisle on saved map (fixed 10-23 19:00) | smear specks pinch aisles to 0.14 m < 0.20 m tight; speck filter + squeeze fix it | 36 | 16 | 9..44 (36) | 36 | 36 |
| start pocket: squeeze not allowed near the dog | exit narrower than 0.20 m within 1.5 m of the dog (door_outside) | 11 | 5 | 46..65 (11) | 0 | 9 |
| temporary blocks close the aisle | two 0.15 m block discs (+0.20-0.28 m clearance) close the aisle | 11 | 3 | 52..89 (11) | 0 | 11 |
| localization lost | live cells / blocks on a mis-placed map view | 10 | 6 | 69..83 (10) | 0 | 9 |
| obsolete map (14:44 unstraightened save) | batch of /nav/plan previews seconds after saving; map superseded at 15:15 | 8 | 8 | 1..8 (8) | 5 | 5 |
| live cells + blocks | each alone closes the route; live cells free-standing (object, person or smear) | 4 | 2 | 68,84,85,86 | 0 | 4 |
| localization lost | dog's own pose inside a mapped obstacle | 4 | 1 | 72,73,74,75 | 0 | 4 |
| live lidar cells close the route | live-new cells within 1.2 m: wall-hugging (pose offset / smear) | 2 | 1 | 66,67 | 0 | 0 |
| obsolete map + localization (10-19 map) | 251 live cells, 77% hugging mapped walls: map/pose mismatch | 1 | 1 | 0 | 0 | 1 |
| live lidar cells close the route | live-new cells within 1.2 m: free-standing (object, person or smear) | 1 | 1 | 45 | 0 | 1 |
| live cells + blocks | each alone closes the route; live cells wall-hugging (pose offset / smear) | 1 | 1 | 51 | 0 | 1 |
| localization lost | goal off the map | 1 | 1 | 81 | 0 | 0 |
