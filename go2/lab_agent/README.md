# lab_agent: talk to the lab dog (2026-10-22)

Ask in plain language, and the agent answers from what the dog has seen or drives the dog to look:

- "walk to the water cooler"
- "where is the grey backpack?"
- "go to the grey backpack"
- "how many people are in the lab, is it a busy day?"

The agent is Opus (`claude` on Oliver's Max plan), and it has only the tools in `server.py`. It runs on cheetah
and drives the dog through the control PC's agent API, as client `cheetah-lab-agent` (plan: board #20).

## Start

| how | command |
|---|---|
| phone page | `python3 go2/lab_agent/web.py`, then open the printed `http://172.17.31.231:8410/?k=...` on the lab network |
| terminal | `bash go2/lab_agent/chat.sh` |
| console page, from anywhere | `python3 go2/lab_agent/console_page.py` (port 8420), then `~/bin/cloudflared tunnel --no-autoupdate --url http://localhost:8420`; the public `https://<words>.trycloudflare.com` address is in the tunnel's output (`go2/data/lab_agent/tunnel.log`) and changes on every restart |

The console page shows the live camera, the map with the dog and its route, status, STOP, place buttons and the
same chat. It is reachable from outside the lab (Oliver's call, 2026-10-22), behind a password login (the password
is in `go2/data/lab_agent/console_password`, mode 600; wrong tries lock an address out for 15 min). A quick tunnel
needs no Cloudflare account and has no uptime guarantee. Only one agent turn runs at a time across both pages.

The phone page has a STOP button. It posts `/agent/stop` to the console directly, even while the agent is busy.
`web.py` also indexes new console trail frames every 2 minutes.

## How it answers

1. **Memory** (`memory.py`, stored in `go2/data/lab_agent/`). Every picture is kept: the console's trail frames
   and every photo the agent takes. The local Qwen3.8-27B (vLLM, port 8300) describes each one once: the objects
   with their colour, what they sit on and where they are in the picture; how many people; and states such as a
   light on or a door open. Each picture also keeps its time and map pose.
2. **Search** (`search_memory`) joins two rankings: SigLIP picture similarity (`embeddings.py`, every picture
   embedded once, three views each) and word matching on the descriptions, with a small synonym map
   (`memory.CANON`, "office chair" = chair). It finds things the descriptions missed (the blue tape, the computer
   tower's lights). `mode="words"` is the old search. The agent still opens the pictures (`show_pictures`) before
   it answers, because both rankings can be wrong. Numbers: `memory_notes/NOTES.md`.
3. **Objects over time** (`memory_instances.py`, tool `where_is`). Within a day, sightings of the same kind and
   colour that land within about 1.5 m on the map are one object; objects on different days at the same spot are
   linked as "probably the same one". Each has first and last seen, newer pictures that looked at the spot
   without it, and P(still there) from a simple persistence model. `where_is` suggests answer / answer with a
   caveat / go and look, with the walk length on the saved map. About 3 in 4 objects are one physical thing when
   checked by eye; positions are rough (median +-0.6 m, more where map poses jumped).
4. **Where a thing is** (`locate`). Each confirmed picture gives a sight line from the camera pose. Two or more
   lines from different directions give a map position. With one line, the position is placed at the vision
   model's distance guess, which is rough. `locate` also suggests a standing spot 0.7-1.5 m away, facing the
   thing, and checks it with the console's route preview.
5. **People and busy-ness** (`people_seen`). This counts people per picture and pictures per hour, so "nobody
   seen" can be told apart from "no pictures taken".

## Tools (server.py)

| tool | moves the dog | notes |
|---|---|---|
| `status`, `list_places` | no | console up?, lined up with the map?, who has control; place ids |
| `go_to`, `turn`, `move`, `look_around` | yes | each ends with a photo, which is remembered |
| `photo` | no | photo from where the dog stands (camera tilt optional) |
| `stop`, `release` | - | stop is always allowed |
| `search_memory`, `show_pictures`, `people_seen`, `locate`, `where_is` | no | memory only |

Every console call is logged to `go2/data/lab_agent/calls.jsonl`.

## Tested (2026-10-22, dog not moving)

- Memory: 615 trail frames from 2026-10-19 were indexed with none failing. The descriptions were checked by eye
  on three pictures, and the object lists matched.
- Agent: "is there a computer tower with coloured lights?" and "did you see people on Monday?" were answered with
  times, places and picture ids, and the pictures were checked by eye.
- Phone page: loads over the lab network, refuses without the key, streams answers with pictures.
- Not yet tested on the dog: `go_to`, `turn`, `move`, `look_around`, `photo`, `locate`'s standing spot.

## Known limits

- Most 2026-10-19 trail frames were taken before the 16:54 map fix, so their poses are less trustworthy.
  Frames from new walks are fine.
- The memory only knows the parts of the lab the dog has looked at, at the times it looked.
- `/trail/near` returns at most 12 frames per 0.35 m, so some older frames in busy spots may never be fetched.
