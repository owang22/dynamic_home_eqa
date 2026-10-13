"""choose_views.py with the eye at 1.4 m: same lens, picture size, candidate rings, tilt limits
and score. Writes spot_views_1p4.json here and, under hssd_a_1p4/, spot_views/ check pictures.

    ~/miniconda3/envs/dynamic_eqa/bin/python choose_views_1p4.py
"""
import json
import sys

import lib_1p4  # noqa: F401  (sets lib.EYE_HEIGHT = 1.4 and the 1.4 m paths)
import lib
import choose_views

choose_views.__doc__ = ("EYE HEIGHT FOR THIS FILE: 1.4 m (choose_views_1p4.py). The rule text below was "
                        "written for the 1.0 m set; everything else in it applies unchanged.\n\n"
                        + choose_views.__doc__)

if __name__ == "__main__":
    choose_views.main()
    # one fixed string in choose_views.py names 1.0 m; correct it in both copies
    for path in (lib.SPOT_VIEWS, lib.PICS / "spot_views.json"):
        d = json.load(open(path))
        for s in d["skipped"]:
            s["reason"] = s["reason"].replace("at 1.0 m", "at 1.4 m")
        lib.json_dump(d, path)
    sys.exit(0)
