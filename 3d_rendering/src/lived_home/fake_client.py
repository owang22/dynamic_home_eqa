"""Offline stand-in for the model. Returns schema-valid answers with random but
plausible choices, so household creation, the loop, the world rules and the
outputs can be tested without a model."""
from __future__ import annotations

import json
import random
import re

TYPES = [("mug", "none"), ("phone", "none"), ("keys", "none"), ("book", "none"),
         ("reading glasses", "none"), ("phone charger", "none"), ("backpack", "closed"),
         ("fruit bowl", "open"), ("wallet", "none"), ("laptop", "none"), ("pen", "none"),
         ("tote bag", "closed"), ("water bottle", "none"), ("medicine bottle", "none")]
POCKETABLE = {"phone", "keys", "wallet", "pen", "reading glasses"}


class FakeClient:
    last_meta = None

    def generate(self, system, user, schema, seed=None, max_tokens=0, temperature=0.7):
        rng = random.Random(seed)
        props = schema["properties"]
        if "rooms" in props:
            return json.dumps(self._layout())
        if "additions" in props:
            spots = [{"id": f"kitchen_{w}", "name": w.replace("_", " "), "kind": k, "hidden": False,
                      "descriptions": [w, f"the {w}"]}
                     for w, k in (("stovetop", "surface"), ("sink_basin", "surface"),
                                  ("oven", "container"), ("dish_rack", "surface"))]
            return json.dumps({"thinking": "fake", "additions": [
                {"room": "kitchen", "fixture": "range and sink", "spots": spots}]})
        if "residents" in props:
            return json.dumps(self._residents(props))
        if "objects" in props:
            return json.dumps(self._objects(props, rng))
        if "situations" in props:
            return json.dumps(self._situations())
        if "activities" in props:
            return json.dumps(self._plan(props, rng))
        return json.dumps(self._act(props, rng, user))

    @staticmethod
    def _state(rng):
        return {"stress": rng.randint(0, 3), "tiredness": rng.randint(0, 3),
                "mood": rng.randint(0, 3), "health": 3, "reason": "fake"}

    def _layout(self):
        rooms = []
        names = ["entryway", "kitchen", "living_room", "main_bedroom", "office",
                 "bathroom", "dining_area", "spare_room", "laundry", "balcony"]
        for room in names:
            furniture = []
            for f in range(3):
                spots = [{"id": f"{room}_f{f}_s{s}", "name": f"spot {s} of piece {f}",
                          "kind": "container" if s == 3 else "surface",
                          "hidden": s == 2 and f == 0,
                          "descriptions": [f"spot {s}", f"piece {f} spot {s}"]}
                         for s in range(4)]
                furniture.append({"name": f"{room} piece {f}", "spots": spots})
            rooms.append({"id": room, "furniture": furniture})
        return {"thinking": "fake", "home": "fake flat", "rooms": rooms,
                "entry_spot": "entryway_f0_s0"}

    def _residents(self, props):
        item = props["residents"]["items"]["properties"]
        places = item["sleeps_at"]["enum"]
        bed = next(p for p in places if p.startswith("main_bedroom") and p.endswith("s0"))
        residents = []
        for rid in ("ana", "ben"):
            residents.append({
                "id": rid, "name": rid.title(), "age": 40, "job": "teacher",
                "personality": "calm.", "sleeps_at": bed,
                "weekly_routine": [{"days": ["mon", "tue"], "start": "07:00", "end": "08:00",
                                    "activity": "breakfast", "room": "kitchen"}] * 10,
                "object_habits": ["keys in the bowl"] * 5,
                "response_habits": [{"id": f"habit_{i}", "trigger": "stressed",
                                     "behavior": "walk", "how_often": "most times"}
                                    for i in range(4)],
                "scheduled_stressors": ["monday meeting"]})
        return {"thinking": "fake", "residents": residents}

    def _objects(self, props, rng):
        arr = props["objects"]
        item = arr["items"]["properties"]
        places = item["place"]["enum"]
        owners = item["owner"]["enum"]
        room = places[0].split("_f")[0]
        out, carriers = [], []
        for i in range(arr["minItems"]):
            kind, carrier = TYPES[(i + len(room)) % len(TYPES)]
            n = i + 1
            place = rng.choice([p for p in places if not p.endswith("s3")] or places)
            relation, ref = "on", 0
            here = [c for c in carriers if c[1] == place]
            if carrier == "none" and here and rng.random() < 0.5:
                relation, ref = "in", here[0][0]
            out.append({"n": n, "type": kind, "looks": f"{room} {i}", "color": "red", "material": "plastic",
                        "size": "small", "pattern": "plain", "condition": "worn",
                        "owner": rng.choice(owners), "pocketable": kind in POCKETABLE,
                        "carrier": carrier, "place": place, "relation": relation, "ref": ref})
            if carrier != "none":
                carriers.append((n, place))
        return {"thinking": "fake", "objects": out}

    def _situations(self):
        situations = [{"id": "sick" if i == 0 else f"situation_{i}", "kind": "recurring",
                       "how_often": "about monthly", "typical_days": 3, "happens_to": ["ben"],
                       "what_it_is_like": "you feel unwell", "what_others_notice": "Ben seems unwell"}
                      for i in range(15)]
        disturbances = [{"who": "anyone", "text": f"the doorbell rings ({i})"} for i in range(12)]
        return {"thinking": "fake", "situations": situations, "small_disturbances": disturbances}

    def _plan(self, props, rng):
        item = props["activities"]["items"]["properties"]
        rooms = item["room"]["enum"]
        types = item["uses"]["items"]["enum"]
        acts, hour = [], 7
        for name in ("breakfast", "work", "lunch", "errand", "dinner", "relax", "sleep"):
            end = "06:30" if name == "sleep" else f"{hour + 2:02d}:00"
            acts.append({"start": f"{hour:02d}:00", "end": end, "activity": name,
                         "room": "out_of_house" if name == "errand" else rng.choice(rooms),
                         "intention": name, "uses": rng.sample(types, 2)})
            hour += 2
        return {"thinking": "fake", "inner_state": self._state(rng), "activities": acts}

    def _act(self, props, rng, user):
        item = props["actions"]["items"]["properties"]
        objects = [o for o in item["object"]["enum"] if o] if "enum" in item["object"] else []
        places = [p for p in item["place"]["enum"] if p] if "enum" in item["place"] else []
        people = [p for p in item["person"]["enum"] if p]
        view = user.split("In your hands:")[0]
        seen = [o for o in objects if re.search(rf"\b{re.escape(o)}\b", view)]
        held = user.split("In your hands:")[1].split("\n")[0]
        held = [o for o in objects if re.search(rf"\b{re.escape(o)}\b", held)]
        actions = []

        def act(verb, **kw):
            base = {"verb": verb, "object": "", "place": "", "relation": "", "ref": "",
                    "person": "", "minutes": 0, "text": "", "why": "fake"}
            base.update(kw)
            actions.append(base)
        for _ in range(rng.randint(3, 8)):
            verb = rng.choice(["go", "pick_up", "put_down", "do", "pocket", "say", "give",
                               "put_down"])
            if verb == "go":
                act("go", place=rng.choice(places))
            elif verb in ("pick_up", "pocket"):
                act(verb, object=rng.choice(seen or objects))
            elif verb == "put_down" and held:
                o = held.pop()
                rel = rng.choice(["", "on", "in", "behind", "under", "next_to"])
                ref = rng.choice(seen) if seen and rel in ("behind", "next_to", "in") else ""
                act("put_down", object=o, relation=rel, ref=ref)
            elif verb == "give" and held:
                act("give", object=held.pop(), person=rng.choice(people))
            elif verb == "do":
                act("do", minutes=rng.randint(5, 40), text="something")
            else:
                act("say", person=rng.choice(people), text="hello")
        if "Now: errand" in user:
            act("leave_home", minutes=60, text="errand")
        habits = props["habit_followed"]["enum"]
        return {"thinking": "fake", "inner_state": self._state(rng),
                "habit_triggers_now": [h for h in habits if h != "none"][:1],
                "habit_followed": rng.choice(habits), "actions": actions}
