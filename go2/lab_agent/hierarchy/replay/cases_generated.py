"""30 generated memory questions with answer keys checked by eye on contact sheets (replay/sheets/, 2026-10-23
~00:45). Memory: the whole index snapshot; "now" = Thu 2026-10-22 16:40 (newest picture 16:36).
kind: find (thing seen), attr (a property you must look at), people, neg (no description mentions it; the
answer key is "not seen", checked only against the descriptions, not every picture), trap (descriptions name it,
the pictures do not show it).    python3 cases_generated.py  -> cases_generated.json
"""
import json
from datetime import datetime
from pathlib import Path

NOW = datetime(2026, 10, 22, 16, 40).timestamp()
Q = [
 ("G01", "find", "Have you seen a vacuum cleaner anywhere? Where?",
  "Yes. A purple-and-grey upright vacuum stands against the wall next to two red fire extinguishers, by a door near the podium (Mon 16:04-16:45). A grey Hoover floor cleaner also stood by a door near desk_gaofeng/door_outside (Mon 16:00-17:04). Either one with a right place is correct.",
  ["t1792451103553", "t1792453497260", "t1792453515809", "t1792450826469", "t1792451309930", "t1792454665934"]),
 ("G02", "find", "When did you last see the grey vacuum cleaner?",
  "Monday 19 Oct around 17:04, near door_outside / the desks by the door (t1792454665934); earlier Mon 16:00-16:08 by a door with a fire extinguisher. Not seen after Monday.",
  ["t1792454665934", "t1792450826469", "t1792451309930"]),
 ("G03", "find", "Is there a red backpack in the lab? Where did you see it?",
  "Yes: a red-and-black backpack on the floor under the conference table among the chairs (seen from near desk_pragya, Mon 16:01-16:25 and Tue 20 Oct 19:29).",
  ["t1792450918129", "t1792452309551", "t1792549786506"]),
 ("G04", "find", "Where is the red broom?",
  "Leaning against the wall beside the two red fire extinguishers and the purple vacuum, by a door near the podium. Seen Mon 16:05-16:45.",
  ["t1792451103553", "t1792452728749", "t1792453515809"]),
 ("G05", "find", "Have you seen a fridge?",
  "Yes: a white/beige mini fridge next to a wooden door, near the workbench (shelves on its left), Mon 16:03-16:04.",
  ["t1792451008237", "t1792451009704", "t1792451040304", "t1792451042566"]),
 ("G06", "attr", "What is on top of the mini fridge?",
  "A black microwave (Mon 16:03, near the workbench). The descriptions do not mention it; it shows in the pictures.",
  ["t1792451008237", "t1792451042566"]),
 ("G07", "find", "Have you seen a silver thermos or flask?",
  "Yes: a steel thermos on top of a desk (on the desk edge/partition) where a person with glasses works, in the desk rows; Mon 16:00, Tue 11:46 and Tue 19:32.",
  ["t1792450808687", "t1792521971802", "t1792549969148"]),
 ("G08", "find", "Where is the server rack?",
  "A tall black server rack on wheels near the workbench, beside a table with boxes under it; a mini fridge and door behind. Mon 16:03.",
  ["t1792450996752", "t1792450998980"]),
 ("G09", "find", "Did you see a yellow cabinet for flammable things?",
  "Yes: a yellow 'FLAMMABLE - keep fire away' cabinet on the floor beside the door near the mini fridge / workbench, Mon 16:03.",
  ["t1792451014962", "t1792451030498"]),
 ("G10", "find", "Is there a plant in the lab?",
  "Yes: a small green potted plant on top of a black low cabinet by the wall near the podium/conference table (Mon 16:04-16:44); also seen Thu 15:53 on that cabinet.",
  ["t1792451097858", "t1792452727073", "t1792453473171", "p1792709591_5"]),
 ("G11", "find", "Where did you see a blue plaid shirt?",
  "Hanging over the back of an office chair at a desk (the one by desk_oliver where a person in a teal t-shirt sits), Thu 15:46-16:12.",
  ["t1792709219533", "p1792709651_7", "t1792710707314", "p1792710737_10", "t1792710748063"]),
 ("G12", "find", "Have you seen a green patterned cushion?",
  "Yes: a green-and-white leaf-patterned cushion (or cloth) on an office chair at the desk drawers, near desk_brian/desk_gaofeng/desk_pragya, Mon 16:30-16:52 and Tue 11:46.",
  ["t1792452601962", "t1792453934230", "t1792453401960", "t1792522019985"]),
 ("G13", "find", "Where is the blue mop bucket?",
  "On the floor at the end of the long wooden filing cabinets, with a mop standing in it (Thu 15:46-15:54, e.g. p1792709241_4); on Tue 11:53 one stood next to the black water cooler.",
  ["p1792709241_4", "t1792709402556", "t1792709219533", "t1792522397058"]),
 ("G14", "find", "Is there a blue mop pad lying on the floor somewhere?",
  "Yes: a round blue-and-white mop pad on the floor at the foot of a black tripod, beside the wooden filing cabinets (near the sofa/conference table side). Mon 16:06, Thu 15:42 and 16:11.",
  ["t1792451162497", "t1792708975359", "t1792709597914", "t1792710672632"]),
 ("G15", "attr", "What colour is the podium?",
  "Dark red / mahogany (reddish-brown wood).",
  ["t1792451066353", "t1792454120542", "t1792709673122", "p1792710686_8"]),
 ("G16", "find", "Have you seen a portable power station?",
  "Yes: a boxed portable power station (cardboard box printed 'PORTABLE POWER STATION') on the floor by the whiteboard wall, next to a tripod and the purple vacuum, near the podium. Mon 16:05-16:45.",
  ["t1792451103553", "t1792452734166", "t1792453478205", "t1792453513631"]),
 ("G17", "find", "Did you see any fire extinguishers?",
  "Yes: two red fire extinguishers on the wall beside a door near the podium, next to the vacuum (Mon 16:04-16:45); another by a door near desk_gaofeng (Mon 16:00-16:08).",
  ["t1792451103553", "t1792452734166", "t1792450826469", "t1792451309930"]),
 ("G18", "attr", "What colour is the backpack on the floor by Oliver's desk today?",
  "Grey (light grey with black), Thu 15:43-16:25.",
  ["t1792709219533", "p1792709651_7", "t1792710748063", "t1792709072510"]),
 ("G19", "trap", "Is there a robot arm in the lab?",
  "Not confirmed: the only pictures described as showing a robot arm (Mon 16:30, 16:44 near the conference table) show an open grey equipment case and office chairs, no robot arm. A correct answer says it has not seen one (or could not confirm one).",
  []),
 ("G20", "find", "Did you see an open equipment case on the floor?",
  "Yes: a large open grey hard-shell case with foam inserts on the floor near the conference table / podium, Mon 16:05-16:45 (also in Thursday pictures near the conference table).",
  ["t1792452653707", "t1792453464354", "t1792454120542"]),
 ("G21", "people", "Was anybody in the lab on Tuesday morning?",
  "Yes: people were at the desks from about 11:28 to noon on Tue 20 Oct (often 1, at most 2 in one picture; e.g. a person in a white shirt near desk_yuyang 11:44, a person with glasses 11:46).",
  ["t1792521852682", "t1792521971802", "t1792521383653"]),
 ("G22", "people", "Who was sitting at Oliver's desk at 16:11 today?",
  "A person with dark hair and glasses in a teal t-shirt and grey trousers, working on a laptop (t1792710707314), with a blue plaid shirt over the chair.",
  ["t1792710707314", "p1792710737_10"]),
 ("G23", "people", "How many people were at the desks around 16:12 today?",
  "Three: the person in the teal t-shirt at desk_oliver, plus two further along the row (one in a grey t-shirt, one with glasses in a white top).",
  ["p1792710737_10", "t1792710748063"]),
 ("G24", "neg", "Have you seen an umbrella?", "Not seen (no picture description mentions one).", []),
 ("G25", "neg", "Is there a bicycle in the lab?", "Not seen.", []),
 ("G26", "neg", "Did you see a guitar anywhere?", "Not seen.", []),
 ("G27", "neg", "Where is the pizza box?", "Not seen.", []),
 ("G28", "neg", "Have you seen a banana?", "Not seen.", []),
 ("G29", "neg", "Where did I leave my bike helmet?", "Not seen.", []),
 ("G30", "find", "Is there a whiteboard in the lab?",
  "Yes: a whiteboard wall behind the purple vacuum and tripod, near the podium / door (Mon 16:32-16:45); whiteboards also on the far wall behind the conference table.",
  ["t1792452734166", "t1792452745715", "t1792453478205", "t1792453513631"]),
]

if __name__ == "__main__":
    out = [{"id": i, "kind": k, "text": q, "key": key, "accept_ids": ids, "t": NOW, "K": None, "history": []}
           for i, k, q, key, ids in Q]
    p = Path(__file__).with_name("cases_generated.json")
    p.write_text(json.dumps(out, indent=1))
    print(len(out), "->", p)
