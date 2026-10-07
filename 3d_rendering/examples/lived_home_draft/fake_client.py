"""Offline stand-in for the model. Returns schema-valid answers with random but
plausible choices, so the loop, the world rules and the outputs can be tested."""
from __future__ import annotations

import json
import random


class FakeClient:
    last_meta = None

    def generate(self, system, user, schema, seed=None, max_tokens=0, temperature=0.7):
        rng = random.Random(seed)
        props = schema["properties"]
        if "residents" in props:
            return json.dumps(self._household(props))
        if "activities" in props:
            return json.dumps(self._plan(props, rng))
        return json.dumps(self._act(props, rng, user))

    @staticmethod
    def _state(rng):
        return {"stress": rng.randint(0, 3), "tiredness": rng.randint(0, 3),
                "mood": rng.randint(0, 3), "health": 3, "reason": "fake"}

    def _household(self, props):
        places = props["objects"]["items"]["properties"]["home"]["enum"]
        rng = random.Random(1)
        residents = []
        for rid in ("ana", "ben"):
            residents.append({
                "id": rid, "name": rid.title(), "age": 40, "job": "teacher",
                "personality": "calm.",
                "weekly_routine": [{"days": ["mon", "tue"], "start": "07:00", "end": "08:00",
                                    "activity": "breakfast", "room": "kitchen"}] * 10,
                "object_habits": ["keys in the bowl"] * 4,
                "response_habits": [{"id": f"habit_{i}", "trigger": "stressed",
                                     "behavior": "walk", "how_often": "most times"}
                                    for i in range(4)],
                "scheduled_stressors": ["monday meeting"]})
        objects = [{"id": f"thing_{i}", "name": f"thing {i}", "owner": rng.choice(["ana", "ben", "shared"]),
                    "home": rng.choice(places), "pocketable": i % 3 == 0} for i in range(50)]
        situations = [{"id": "sick" if i == 0 else f"situation_{i}", "kind": "recurring",
                       "how_often": "about monthly", "typical_days": 3, "happens_to": ["ben"],
                       "what_it_is_like": "you feel unwell", "what_others_notice": "Ben seems unwell"}
                      for i in range(15)]
        disturbances = [{"who": "anyone", "text": f"the doorbell rings ({i})"} for i in range(12)]
        return {"thinking": "fake", "residents": residents, "objects": objects,
                "situations": situations, "small_disturbances": disturbances}

    def _plan(self, props, rng):
        rooms = props["activities"]["items"]["properties"]["room"]["enum"]
        acts, hour = [], 7
        for name in ("breakfast", "work", "lunch", "errand", "dinner", "relax", "sleep"):
            end = "06:30" if name == "sleep" else f"{hour + 2:02d}:00"
            acts.append({"start": f"{hour:02d}:00", "end": end, "activity": name,
                         "room": "out_of_house" if name == "errand" else rng.choice(rooms),
                         "intention": name})
            hour += 2
        return {"thinking": "fake", "inner_state": self._state(rng), "activities": acts}

    def _act(self, props, rng, user):
        item = props["actions"]["items"]["properties"]
        objects = item["object"]["anyOf"][0]["enum"]
        places = item["place"]["anyOf"][0]["enum"]
        people = item["person"]["anyOf"][0]["enum"]
        seen = [o for o in objects if o in user]
        actions = []
        for _ in range(rng.randint(3, 8)):
            verb = rng.choice(["go", "pick_up", "put_down", "do", "pocket", "say", "give"])
            act = {"verb": verb, "object": None, "place": None, "person": None,
                   "minutes": None, "text": None, "why": "fake"}
            if verb == "go":
                act["place"] = rng.choice(places)
            elif verb in ("pick_up", "put_down", "pocket", "give"):
                act["object"] = rng.choice(seen or objects)
                act["person"] = rng.choice(people) if verb == "give" else None
            elif verb == "do":
                act.update(minutes=rng.randint(5, 40), text="something")
            else:
                act.update(person=rng.choice(people), text="hello")
            actions.append(act)
        if "Now: errand" in user:
            actions.append({"verb": "leave_home", "object": None, "place": None, "person": None,
                            "minutes": 60, "text": None, "why": "fake"})
        habits = props["habit_followed"]["enum"]
        return {"thinking": "fake", "inner_state": self._state(rng),
                "habit_followed": rng.choice(habits), "actions": actions}
