"""E2 one-shot prior elicitation.

Source models: gpt-5.4-mini and gpt-5.5 ONLY. NEVER Claude — Claude drafted the
typical profiles, so using it as the prior source would be circular (stated in
methods). Inputs to the model: the object-class list, the receptacle
vocabulary, and a GENERIC household descriptor (e.g. "a single working adult's
home") — never the profile YAML/prose, never observations. One-shot = zero
household-specific data. 5 samples per model, mixture-averaged; every raw
output logged; the elicitation prompt is fixed and hashed.

Elicited per object class (feeds the C3 GLM + C1 transforms downstream):
  home            most likely resting receptacle
  secondary       up to 3 other receptacles with relative occupancy weights
  active_windows  time-of-day buckets when the object is likely in use/moving
  weekday_weekend "same" | "more_weekday" | "more_weekend" occupancy skew
  move_rate       qualitative daily movement: "static"|"low"|"medium"|"high"
"""
from __future__ import annotations

import hashlib
import json
import pathlib

TOD_BUCKETS = ["night(0-6)", "morning(6-10)", "midday(10-14)",
               "afternoon(14-18)", "evening(18-22)", "latenight(22-24)"]
MOVE_RATE_PER_DAY = {"static": 0.0, "low": 0.6, "medium": 2.0, "high": 4.0}

_SYSTEM = (
    "You are estimating, from general world knowledge only, where household "
    "objects typically rest and how often they move in a home of a given type. "
    "You are given the object classes and the receptacle names in this home. "
    "Do NOT assume any specific household's schedule beyond the generic "
    "descriptor. Answer with population-typical estimates."
)


def build_prompt(descriptor: str, classes: list[str], receptacles: list[str]) -> str:
    return (
        f"Household type: {descriptor}.\n\n"
        f"Receptacles in this home: {', '.join(receptacles)}, elsewhere.\n\n"
        f"Object classes: {', '.join(classes)}.\n\n"
        f"Time-of-day buckets: {', '.join(TOD_BUCKETS)}.\n\n"
        "For EACH object class give population-typical estimates:\n"
        "- home: the single most likely resting receptacle.\n"
        "- secondary: up to 3 other receptacles it is often found at, each with "
        "a relative weight in [0,1] (home implicitly gets the rest).\n"
        "- active_windows: the time-of-day buckets when it is most likely to be "
        "in use or moving.\n"
        "- weekday_weekend: 'same' | 'more_weekday' | 'more_weekend'.\n"
        "- move_rate: 'static' | 'low' | 'medium' | 'high'."
    )


SCHEMA = {
    "type": "object",
    "properties": {
        "classes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "object_class": {"type": "string"},
                    "home": {"type": "string"},
                    "secondary": {
                        "type": "array", "maxItems": 3,
                        "items": {"type": "object",
                                  "properties": {"receptacle": {"type": "string"},
                                                 "weight": {"type": "number",
                                                            "minimum": 0, "maximum": 1}},
                                  "required": ["receptacle", "weight"],
                                  "additionalProperties": False}},
                    "active_windows": {"type": "array",
                                       "items": {"type": "string"}},
                    "weekday_weekend": {"type": "string",
                                        "enum": ["same", "more_weekday", "more_weekend"]},
                    "move_rate": {"type": "string",
                                  "enum": ["static", "low", "medium", "high"]},
                },
                "required": ["object_class", "home", "secondary", "active_windows",
                             "weekday_weekend", "move_rate"],
                "additionalProperties": False}},
    },
    "required": ["classes"],
    "additionalProperties": False,
}

ALLOWED_MODELS = ("gpt-5.4-mini", "gpt-5.5")


def prompt_hash(descriptor, classes, receptacles) -> str:
    payload = _SYSTEM + build_prompt(descriptor, classes, receptacles) + json.dumps(SCHEMA)
    return hashlib.sha256(payload.encode()).hexdigest()[:12]


def elicit(model: str, descriptor: str, classes: list[str], receptacles: list[str],
           n_samples: int = 5, out_dir: pathlib.Path | None = None) -> list[dict]:
    """Returns n_samples raw parsed outputs; logs raw JSON if out_dir given.
    Refuses any model outside ALLOWED_MODELS (the anti-circularity rule)."""
    if not any(model.startswith(m) for m in ALLOWED_MODELS):
        raise ValueError(f"E2 elicitation source must be one of {ALLOWED_MODELS} "
                         f"(never Claude — circular); got {model!r}")
    from dynbelief.llm_agent.clients import OpenAIClient
    client = OpenAIClient(model=model)
    system, user = _SYSTEM, build_prompt(descriptor, classes, receptacles)
    raw_samples = []
    for s in range(n_samples):
        txt = client.generate(system, user, SCHEMA, seed=1000 + s, temperature=0.7)
        raw_samples.append(json.loads(txt))
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"raw_{model.replace('/', '_')}.json").write_text(json.dumps({
            "model": model, "descriptor": descriptor,
            "prompt_hash": prompt_hash(descriptor, classes, receptacles),
            "system": system, "user": user, "samples": raw_samples}, indent=1))
    return raw_samples


def mixture_average(all_samples: list[dict], classes: list[str],
                    receptacles: list[str]) -> dict:
    """Average the (multi-model, multi-sample) elicitations into one prior per
    class: mean secondary weights, most-common home/weekday_weekend/move_rate,
    union-with-fraction of active windows."""
    from collections import Counter, defaultdict
    per_class: dict[str, list] = defaultdict(list)
    for sample in all_samples:
        for c in sample.get("classes", []):
            per_class[c["object_class"]].append(c)
    out = {}
    for cls in classes:
        recs = per_class.get(cls, [])
        if not recs:
            out[cls] = None
            continue
        homes = Counter(r["home"] for r in recs if r["home"] in receptacles)
        home = homes.most_common(1)[0][0] if homes else (receptacles[0])
        sec = defaultdict(list)
        for r in recs:
            for s in r.get("secondary", []):
                if s["receptacle"] in receptacles:
                    sec[s["receptacle"]].append(float(s["weight"]))
        secondary = {k: sum(v) / len(recs) for k, v in sec.items()}
        aw = Counter()
        for r in recs:
            for w in r.get("active_windows", []):
                aw[w] += 1
        active = {w: aw[w] / len(recs) for w in aw}
        ww = Counter(r["weekday_weekend"] for r in recs).most_common(1)[0][0]
        mr = Counter(r["move_rate"] for r in recs).most_common(1)[0][0]
        out[cls] = {"home": home, "secondary": secondary, "active_windows": active,
                    "weekday_weekend": ww, "move_rate": mr, "n": len(recs)}
    return out
