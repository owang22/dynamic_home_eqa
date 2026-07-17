"""
Per-label render-asset binding — "Strategy 2+".

A category can have MANY render assets (data/objects/external_props/
mapping.json holds a reviewer-curated pool per category, each entry
carrying free-text `tags` from the review webapp). Identity requirements
differ by tier:

  Tier-3 owner items (phone, headphones, ...): each owner's item is a
    specific asset, stable for the household and never interchanged —
    Ana's headphones are ALWAYS the purple gamer pair. Assigned HERE at
    generation time by an LLM that reads each candidate's tags against the
    occupant's persona (age/role/habits), so the choice is in character
    (the teen gets the gaming headset, grandma the classic black pair).
    One guided call per household; deterministic seeded fallback on any
    failure. Stored in generation_result["asset_bindings"] and carried on
    the manifest, so build_realized_day just obeys.

  Tier-2 shared clutter (cups, plates, ...): instances need visible
    VARIETY but no persona reasoning — build_realized_day draws per label
    from the pool without replacement (seeded), recorded in the artifact.
    Not handled here.

The LLM sees only reviewer-authored tag strings and picks from an
enum-constrained uid list, so it cannot invent an asset; a binding whose
category doesn't match its item is rejected in validate (retry path).
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from .cache import ResponseCache, make_seed
from .llm_client import DEFAULT_MODEL, _get_client, generate_json
from .ownership import tier3_instance_label
from .prompt_registry import ASSET_BINDING as _BINDING_T

_logger = logging.getLogger(__name__)


def load_asset_pools() -> dict[str, list[dict]]:
    """{category: [{uid, tags, note?}, ...]} from external_props/mapping.json.
    Entries without tags still participate (empty tag list). Categories not
    present simply have no pool — callers fall back to the legacy
    single-asset default (build_realized_day.SPAWNABLE_ASSET_BY_CATEGORY)."""
    from dynamic_home_eqa.paths import REPO_ROOT
    path = REPO_ROOT / "data" / "objects" / "external_props" / "mapping.json"
    if not path.exists():
        return {}
    pools: dict[str, list[dict]] = {}
    for e in json.loads(path.read_text()):
        pools.setdefault(e["category"], []).append(
            {"uid": e["uid"], "tags": e.get("tags", []), "note": e.get("note", "")})
    return pools


def _fallback_pick(pool: list[dict], household_id: str, label: str) -> str:
    """Deterministic stateless pick — the no-LLM/failure path."""
    idx = make_seed(household_id, 0, f"assetbind_{label}", 0) % len(pool)
    return pool[idx]["uid"]


def bind_owner_assets(
    persona: dict,
    ownership: dict[str, list[str]],
    household_id: str,
    model: str = DEFAULT_MODEL,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
) -> dict[str, str]:
    """{owner label ('ana_headphones') -> asset uid} for every owned Tier-3
    item that has a multi-asset pool. Single-asset pools bind trivially;
    absent pools bind to nothing (legacy default applies downstream)."""
    pools = load_asset_pools()
    items: list[tuple[str, str, str]] = []   # (occupant, category, label)
    bindings: dict[str, str] = {}
    for occ, owned in ownership.items():
        for cat in owned:
            label = tier3_instance_label(occ, cat)
            pool = pools.get(cat, [])
            if not pool:
                continue
            if len(pool) == 1:
                bindings[label] = pool[0]["uid"]
            else:
                items.append((occ, cat, label))
    if not items:
        return bindings

    occ_by_name = {o.get("name"): o for o in persona.get("occupants", [])}
    lines = []
    all_uids: list[str] = []
    for occ, cat, label in items:
        o = occ_by_name.get(occ, {})
        cands = pools[cat]
        all_uids += [c["uid"] for c in cands]
        cand_txt = "; ".join(f"{c['uid']}: {', '.join(c['tags']) or 'no tags'}" for c in cands)
        lines.append(
            f"- {label}: {occ}'s {cat} ({occ} is {o.get('age_band', 'adult')}, "
            f"{o.get('role', 'member')}; habits: {o.get('habits', 'none given')})\n"
            f"    candidates: {cand_txt}")
    user = ("Assign each person's item ONE asset from its own candidate list, "
            "matching who they are:\n" + "\n".join(lines))

    schema = {
        "type": "object",
        "properties": {
            "bindings": {
                "type": "array",
                "minItems": len(items), "maxItems": len(items),
                "items": {
                    "type": "object",
                    "properties": {
                        "label":     {"type": "string", "enum": [lbl for _, _, lbl in items]},
                        "asset_uid": {"type": "string", "enum": sorted(set(all_uids))},
                    },
                    "required": ["label", "asset_uid"],
                },
            },
        },
        "required": ["bindings"],
    }

    valid_by_label = {lbl: {c["uid"] for c in pools[cat]} for _, cat, lbl in items}

    def _validate(result: dict) -> dict[str, str]:
        out: dict[str, str] = {}
        for b in result.get("bindings", []):
            lbl, uid = b.get("label"), b.get("asset_uid")
            if lbl in valid_by_label and uid in valid_by_label[lbl]:
                out[lbl] = uid
        missing = [lbl for lbl in valid_by_label if lbl not in out]
        if missing:
            raise ValueError(f"binding missing/invalid for {missing!r}")
        return out

    pool_key = json.dumps({lbl: sorted(valid_by_label[lbl]) for lbl in sorted(valid_by_label)},
                          sort_keys=True)
    import hashlib
    stage = _BINDING_T.tag("assetbind_p" + hashlib.sha256(pool_key.encode()).hexdigest()[:8],
                           builder=True)
    seed = make_seed(household_id, 0, stage, 0)
    client = _get_client(model)
    try:
        llm_bound = generate_json(
            client, _BINDING_T.text, user, schema,
            seed=seed, stage=stage, cache=cache, force=force, validate=_validate,
            temperature=0.3,
        )
    except Exception as e:
        _logger.error("[%s] asset binding failed after retries (%s) — seeded fallback", stage, e)
        llm_bound = {lbl: _fallback_pick(pools[cat], household_id, lbl)
                     for _, cat, lbl in items}
    bindings.update(llm_bound)
    return bindings
