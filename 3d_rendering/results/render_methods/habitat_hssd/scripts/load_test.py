"""Step 1: can habitat-sim 0.3.3 open the ARTICULATED HSSD home of household A, and can a
drawer be opened? Prints timings, counts, and the joints of every articulated object."""
import json
import sys
import time

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import common  # noqa: E402

t0 = time.time()
sim = common.open_home([dict(uuid="colour", kind="colour", width=640, height=480, hfov=75)])
print(f"loaded in {time.time() - t0:.1f} s")
rom = sim.get_rigid_object_manager()
aom = sim.get_articulated_object_manager()
print("rigid objects", rom.get_num_objects(), "articulated objects", aom.get_num_objects())
out = []
for handle, ao in aom.get_objects_by_handle_substring("").items():
    links = {i: ao.get_link_name(i) for i in ao.get_link_ids()}
    joints = []
    for i in ao.get_link_ids():
        jt = ao.get_link_joint_type(i)
        if str(jt) not in ("JointType.Fixed",):
            joints.append({"link": links[i], "type": str(jt), "pos_offset": ao.get_link_joint_pos_offset(i),
                           "dofs": ao.get_link_num_joint_pos(i)})
    lo, hi = ao.joint_position_limits
    out.append({"handle": handle, "translation": list(ao.translation), "n_links": len(links),
                "joints": joints, "limits_low": list(lo), "limits_high": list(hi),
                "joint_positions": list(ao.joint_positions)})
print(json.dumps(out[:3], indent=1, default=str))
json.dump(out, open(common.OUT / "checks/articulated_objects.json", "w"), indent=1, default=str)
print("written", len(out))
sim.close()
