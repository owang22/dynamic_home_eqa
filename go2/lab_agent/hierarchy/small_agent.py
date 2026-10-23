"""The small model's agent loop: one JSON action per step (tool call or final answer), over a narrow toolset.

    from llm import LLM; from small_agent import SmallAgent, MemEnv
    agent = SmallAgent(LLM("http://127.0.0.1:8301/v1"), MemEnv(memory), tools=MEMORY_TOOLS)
    trace = agent.run("where is the grey backpack?")

The loop never decides to escalate by itself: every step is recorded with the signals the router looks at
(router.step_signals / answer_signals), and `on_step` may end the run early (live use). For offline evaluation
the run continues to the end, so one small run serves every routing policy.

Pictures: tool results that carry pictures (show_pictures, and photos from moves) are sent to the model as images
in the next user message; only the newest `max_images` stay as images, older ones become a text note.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime

from llm import LLM, image_part

PIC = re.compile(r"\b([tpl]\d{9,}(?:_\d+)?)\b")

MEMORY_TOOLS = ["search_memory", "show_pictures", "people_seen", "list_places", "status", "ask_expert", "answer"]
PLACE_TOOLS = ["status", "list_places", "go_to", "stop", "release", "ask_expert", "answer"]
DRIVE_TOOLS = ["status", "list_places", "go_to", "turn", "move", "look_around", "photo", "stop", "release",
               "search_memory", "show_pictures", "people_seen", "locate", "ask_expert", "answer"]
MOVES = {"go_to", "turn", "move", "look_around", "photo"}

TOOL_DOC = {
    "status": "status {}: console up?, dog pose, who has control, memory size, time now",
    "list_places": "list_places {}: the saved places (ids for go_to)",
    "go_to": "go_to {place} or {x, y, yaw_deg}: walk to a saved place id, or map coordinates (metres; yaw 0 = +x, "
             "counter-clockwise). Returns a photo from where it ended",
    "turn": "turn {deg}: turn in place, positive = left. Returns a photo",
    "move": "move {metres}: straight ahead (negative = back), at most 1.5 m. Returns a photo",
    "look_around": "look_around {views}: turn a full circle taking 2-8 photos",
    "photo": "photo {look_deg}: photo from where the dog stands (look_deg up to +16 up, -5 down)",
    "stop": "stop {}: stop the dog now",
    "release": "release {}: give control back when the request is done",
    "search_memory": "search_memory {query, since?, until?, place?, limit?}: word search over picture descriptions. "
                     "since/until: 'HH:MM' (today), 'YYYY-MM-DD HH:MM', 'today'. place: a place id",
    "show_pictures": "show_pictures {ids}: look at up to 6 remembered pictures yourself",
    "people_seen": "people_seen {since?, until?}: people per picture over time, pictures per hour",
    "locate": "locate {thing, ids}: map position of a thing from pictures you opened and confirmed",
    "ask_expert": "ask_expert {reason}: hand this request to a stronger model (use it when unsure or the request "
                  "is beyond these tools)",
    "answer": "answer {text, cited_ids}: your final reply to Oliver; cited_ids = picture ids you opened that "
              "support it",
}

SYSTEM = """You are the lab agent for a Unitree Go2 robot dog in a university robotics lab. Oliver asks questions \
about what the dog has seen, or asks you to drive the dog. Time now: {now}.
Reply with exactly one JSON action per message: one tool call, or the final answer.

Answering questions
- Answer from pictures, not guesses. search_memory with two or three wordings ("grey backpack", "backpack", \
"bag"), then show_pictures on the best ids and check them with your own eyes. The stored descriptions were \
written by another model and are sometimes wrong.
- Say when and where, with the ids of pictures you opened: "at 14:12, near desk_kang (t179...)".
- If you did not find it, say what you searched and the time span the memory covers. Never invent a sighting.
- "near <place>" is where the dog stood, not where the thing is.
- Count distinct people by where they sit and what they wear, not by adding up pictures.
- The memory only shows the past. For questions about now, give the latest pictures with their times.
- Keep answers short, plain words.

Driving the dog
- Move only when Oliver asks. go_to a place id from the list below.
- If a tool says REFUSED, blocked or no_route, tell Oliver what it said; do not work around it.
- If Oliver says stop, call stop at once. When his request is done, call release, then answer.

If the request needs more than these tools, or you are unsure, call ask_expert.

Places (id: where the dog stands):
{places}

Tools:
{tools}"""


# v1 (2026-10-23 01:00): rules for the failures seen in the v0 replay of the logged turns (time filters that cut
# the memory to today, 'until: now', searching the word 'people' instead of people_seen, giving up after one wording).
SYSTEM_V1 = SYSTEM.replace("""Answering questions
""", """Answering questions
- The memory covers several days. Leave since and until EMPTY unless Oliver names a day or time. since="today" \
means from midnight today. Never put "now" or "today" in until.
- Questions about people (who, how many, anyone, busy): call people_seen first (since = the day asked about), \
then show_pictures on the pictures with people.
- If a search finds nothing, try other words (the object type alone, other names) before saying "not seen".
""").replace("- Say when and where, with the ids", "- Always cite the ids of the pictures you opened that show it. Say when and where, with the ids")
# v2 (2026-10-23 02:10): v1's prompt rules did not stop the 8B from adding since="today" / place="lab" on the
# generated set, so v2 takes the choice away in the schema (constrained decoding): search_memory has since/until
# only when the question names a time (TIME_WORDS), and place must be a real place id.
SYSTEM_V2 = SYSTEM_V1.replace("""- The memory covers several days. Leave since and until EMPTY unless Oliver names a day or time. since="today" \
means from midnight today. Never put "now" or "today" in until.
""", """- The memory covers several days: search all of it unless Oliver names a day or time.
""")
PROMPTS = {"v0": SYSTEM, "v1": SYSTEM_V1, "v2": SYSTEM_V2}
TIME_WORDS = re.compile(r"\b(today|yesterday|tonight|monday|tuesday|wednesday|thursday|friday|saturday|sunday|morning|"
                        r"afternoon|evening|last night|this week|\d{1,2}:\d{2}|\d{1,2} ?(am|pm)|o'clock|hour)\b", re.I)


def normalize_args(tool, args):
    """v1 guardrail: drop until='now'/'today' (until 'today' is midnight this morning, which hides today)."""
    a = dict(args)
    if tool in ("search_memory", "people_seen"):
        if str(a.get("until", "")).strip().lower() in ("now", "today"):
            a["until"] = ""
        if str(a.get("since", "")).strip().lower() == "now":
            a["since"] = ""
    return a


def action_schema(tools: list[str], place_ids: list[str], time_filters: bool = True, strict_place: bool = False) -> dict:
    S, N = {"type": "string"}, {"type": "number"}
    empty = {"type": "object", "properties": {}}
    args = {
        "status": empty, "list_places": empty, "stop": empty, "release": empty,
        "go_to": {"type": "object", "properties": {"place": {"type": "string", "enum": place_ids + [""]},
                                                    "x": N, "y": N, "yaw_deg": N}, "required": ["place"]},
        "turn": {"type": "object", "properties": {"deg": N}, "required": ["deg"]},
        "move": {"type": "object", "properties": {"metres": N}, "required": ["metres"]},
        "look_around": {"type": "object", "properties": {"views": {"type": "integer", "minimum": 2, "maximum": 8}},
                        "required": ["views"]},
        "photo": {"type": "object", "properties": {"look_deg": N}, "required": ["look_deg"]},
        "search_memory": {"type": "object", "properties": {
            "query": {"type": "string", "maxLength": 80}, "since": {"type": "string", "maxLength": 20},
            "until": {"type": "string", "maxLength": 20}, "place": {"type": "string", "maxLength": 30},
            "limit": {"type": "integer", "minimum": 1, "maximum": 30}}, "required": ["query"]},
        "show_pictures": {"type": "object", "properties": {"ids": {"type": "array", "items": {"type": "string", "maxLength": 24},
                                                                   "minItems": 1, "maxItems": 6}}, "required": ["ids"]},
        "people_seen": {"type": "object", "properties": {"since": {"type": "string", "maxLength": 20},
                                                          "until": {"type": "string", "maxLength": 20}}},
        "locate": {"type": "object", "properties": {"thing": {"type": "string", "maxLength": 80},
                                                     "ids": {"type": "array", "items": {"type": "string", "maxLength": 24},
                                                             "maxItems": 12}}, "required": ["thing", "ids"]},
        "ask_expert": {"type": "object", "properties": {"reason": {"type": "string", "maxLength": 200}},
                       "required": ["reason"]},
        "answer": {"type": "object", "properties": {"text": {"type": "string", "maxLength": 1500},
                                                     "cited_ids": {"type": "array", "items": {"type": "string", "maxLength": 24},
                                                                   "maxItems": 12}},
                   "required": ["text", "cited_ids"]},
    }
    if not time_filters:
        for k in ("since", "until"):
            args["search_memory"]["properties"].pop(k)
    if strict_place:
        args["search_memory"]["properties"]["place"] = {"type": "string", "enum": place_ids + [""]}
    return {"anyOf": [{"type": "object", "properties": {
        "thought": {"type": "string", "maxLength": 240}, "tool": {"const": t}, "args": args[t]},
        "required": ["thought", "tool", "args"]} for t in tools]}


def system_prompt(tools, now: float, places_text: str, version: str = "v0") -> str:
    return PROMPTS[version].format(now=datetime.fromtimestamp(now).strftime("%a %Y-%m-%d %H:%M"), places=places_text,
                         tools="\n".join("- " + TOOL_DOC[t] for t in tools))


class MemEnv:
    """Memory-only tools over a memtools.Memory (no console)."""

    def __init__(self, memory, dog_status: str | None = None, expert_reply: str | None = None, vlm=None):
        self.m, self.dog_status, self.vlm = memory, dog_status, vlm
        self.expert_reply = expert_reply or "No expert is available right now: answer as best you can."

    def call(self, tool, args) -> tuple[str, list]:
        m = self.m
        try:
            if tool == "search_memory":
                return m.search_memory(**{k: v for k, v in args.items() if k in ("query", "since", "until", "place", "limit")}), []
            if tool == "show_pictures":
                return m.show_pictures(args.get("ids") or [])
            if tool == "people_seen":
                return m.people_seen(args.get("since", "today") or "", args.get("until", "") or ""), []
            if tool == "list_places":
                return m.list_places(), []
            if tool == "status":
                return m.status(self.dog_status), []
            if tool == "locate" and self.vlm is not None:
                return m.locate(args.get("thing", ""), args.get("ids") or [], self.vlm), []
            if tool == "ask_expert":
                return self.expert_reply, []
            return f"ERROR: {tool} is not available here (memory-only)", []
        except Exception as e:  # noqa: BLE001
            return f"ERROR: {type(e).__name__}: {e}", []


class SmallAgent:
    def __init__(self, llm: LLM, env, tools=MEMORY_TOOLS, max_steps: int = 10, max_images: int = 6,
                 place_ids: list[str] | None = None, places_text: str = "", now: float | None = None,
                 on_step=None, image_width: int = 768, prompt: str = "v0"):
        self.llm, self.env, self.tools = llm, env, list(tools)
        self.max_steps, self.max_images, self.image_width = max_steps, max_images, image_width
        self.place_ids = place_ids or []
        self.places_text = places_text
        self.now = now or time.time()
        self.on_step = on_step
        self.prompt = prompt
        if prompt == "v2":
            self.strict_place = True
        self.schema = action_schema(self.tools, self.place_ids)

    def messages(self, question: str, history: list[tuple[str, str]] | None = None) -> list:
        if self.prompt == "v2":      # the schema depends on the question: time filters only if it names a time
            self.schema = action_schema(self.tools, self.place_ids, time_filters=bool(TIME_WORDS.search(question)),
                                        strict_place=True)
        hist = "".join(f"Oliver (earlier): {q}\nYou (earlier): {a}\n\n" for q, a in (history or []))
        return [{"role": "system", "content": system_prompt(self.tools, self.now, self.places_text, self.prompt)},
                {"role": "user", "content": (hist + f"Oliver: {question}").strip()}]

    @staticmethod
    def trim_images(msgs, keep):
        """Keep only the newest `keep` images; older ones become a text note."""
        n = 0
        for m in reversed(msgs):
            if isinstance(m["content"], list):
                new = []
                for p in reversed(m["content"]):
                    if p.get("type") == "image_url":
                        n += 1
                        if n > keep:
                            p = {"type": "text", "text": "[picture shown earlier]"}
                    new.append(p)
                m["content"] = list(reversed(new))

    def next_action(self, msgs) -> dict:
        r = self.llm.chat(msgs, schema=self.schema, max_tokens=900)
        return r

    def run(self, question: str, history=None) -> dict:
        msgs = self.messages(question, history)
        steps, opened, t0 = [], [], time.time()
        answer = None
        for i in range(self.max_steps):
            try:
                r = self.next_action(msgs)
            except Exception as e:  # noqa: BLE001
                steps.append({"i": i, "tool": None, "error": f"{type(e).__name__}: {e}", "t": round(time.time() - t0, 2)})
                break
            a = r.get("json")
            if not a or "tool" not in a:
                steps.append({"i": i, "tool": None, "invalid": r["text"][:300], "secs": r["secs"],
                              "t": round(time.time() - t0, 2)})
                msgs += [{"role": "assistant", "content": r["text"]},
                         {"role": "user", "content": "That was not one valid JSON action. Reply with one JSON action."}]
                continue
            tool, args = a["tool"], a.get("args") or {}
            step = {"i": i, "tool": tool, "args": args, "thought": a.get("thought", ""), "secs": r["secs"],
                    "tokens": r["usage"].get("completion_tokens")}
            msgs.append({"role": "assistant", "content": json.dumps(a)})
            if tool == "answer":
                answer = args
                step["t"] = round(time.time() - t0, 2)
                steps.append(step)
                if self.on_step and self.on_step(step, steps, opened):
                    break
                break
            if self.prompt != "v0":
                args = normalize_args(tool, args)
                step["args"] = args
            text, pics = self.env.call(tool, args)
            if tool == "show_pictures":
                opened += [i_ for i_, _ in pics]
            elif pics:                                   # photos from moves count as seen too
                opened += [i_ for i_, _ in pics]
            step["result"] = text[:4000]
            step["pics"] = [i_ for i_, _ in pics]
            step["t"] = round(time.time() - t0, 2)
            steps.append(step)
            content = [{"type": "text", "text": f"Result of {tool}:\n{text}"}]
            for pid, jpg in pics:
                content += [{"type": "text", "text": f"picture {pid}:"}, image_part(jpg, self.image_width)]
            msgs.append({"role": "user", "content": content if pics else content[0]["text"]})
            self.trim_images(msgs, self.max_images)
            if self.on_step and self.on_step(step, steps, opened):
                break
        return {"question": question, "model": self.llm.name, "steps": steps, "answer": answer,
                "opened": opened, "secs": round(time.time() - t0, 2)}
