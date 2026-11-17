"""Host side: logged sightings (all tags) from auto sessions' events.jsonl -> sightings.json"""
import glob, json, sys
out = []
for f in sorted(glob.glob("/home/nesl/oliver/go2_recordings/auto_*/events.jsonl")):
    sess = f.split("/")[-2]
    seen = set()
    for line in open(f):
        if '"yaw_deg"' not in line: continue
        d = json.loads(line)
        if d.get("kind") != "state": continue
        mk = d.get("markers") or {}
        ft = mk.get("frame_t")
        for m in mk.get("list") or []:
            if m.get("held"): continue
            key = (m["id"], ft)
            if key in seen: continue          # same detector frame logged on several state lines
            seen.add(key)
            loc = d.get("loc") or {}
            out.append({"session": sess, "t": d["t"], "frame_t": ft, "m": m, "map_pose": d.get("map_pose"), "odom": d.get("odom"),
                        "track_fit": loc.get("track_fit"), "fresh_fit": loc.get("fresh_fit"), "lost": loc.get("lost"), "suspect": loc.get("suspect")})
json.dump(out, open(sys.argv[1], "w"))
print(len(out), "sightings")
