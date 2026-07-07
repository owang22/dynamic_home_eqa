"""
LLM agent for Dynamic EQA using vLLM with guided JSON output.

Two prompt modes:
  standalone  — semantic slot descriptions, no WorldGraph (default).
  partnr      — uses WorldGraph.get_world_descr() for richer house context,
                matching the language style PARTNR's planners use.

Model config (swap in one line):
    MODEL_3B  = "Qwen/Qwen2.5-3B-Instruct"    # fast iteration
    MODEL_14B = "Qwen/Qwen3-14B-AWQ"           # production
    MODEL_32B = "Qwen/Qwen2.5-32B-Instruct"    # maximum capacity

Agent decision: given a stale observation and a question, decide
  ANSWER  — commit to an option from the stale observation (free)
  RESENSE — spend 1 budget token to get a fresh observation

The budget is a session-level pool shared across all questions in the eval.
"""
from __future__ import annotations

import json
from typing import Optional, TYPE_CHECKING

from .protocol import Agent, Decision, DecisionKind, Observation

if TYPE_CHECKING:
    from vllm import LLM, SamplingParams

MODEL_3B   = "Qwen/Qwen2.5-3B-Instruct"
MODEL_14B  = "Qwen/Qwen3-14B-AWQ"
MODEL_32B  = "Qwen/Qwen2.5-32B-Instruct"
DEFAULT_MODEL = MODEL_14B

_MODEL_CACHE = "/mnt/nvme/oliver/robot/models"

DECISION_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "kind":         {"type": "string", "enum": ["answer", "resense"]},
        "option_index": {"type": "integer", "minimum": 0},
        "confidence":   {"type": "number",  "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["kind"],
    "if":   {"properties": {"kind": {"const": "answer"}}},
    "then": {"required": ["option_index", "confidence"]},
}

_SYSTEM_PROMPT = """\
You are an embodied robot agent in a household. You observed the scene at time t0.
You are now asked a question about the scene at a LATER time (t0 + Δ). Your
last observation may be stale — objects may have moved since you observed them.

Each turn you receive:
  • Household type (lifestyle / occupancy pattern)
  • Region and what you observed there at t0 (observed_states)
  • Current query time and staleness Δ
  • An MCQ question + answer options
  • Remaining resense budget and questions left in the session

You have two actions:
  ANSWER  — commit to an answer option using your stale observation plus
             world knowledge of how households like this one typically behave.
  RESENSE — spend one budget token to obtain a fresh ground-truth observation;
             you will be asked again immediately with the updated state.

Use world knowledge to decide:
  • High Δ + volatile category (phone, keys, wallet) → consider RESENSE
  • Low Δ or stable category (chair, plant) → ANSWER confidently from stale data
  • If budget_rate < 0.2, be very selective — only resense when uncertain about
    a volatile item at high staleness. Stable objects never need resensing.

CRITICAL: Budget is SHARED across all questions. Spending here means one fewer
token for a potentially harder question later.

Respond ONLY with valid JSON:
  {"kind": "answer",  "option_index": <int>, "confidence": <0-1>}
  {"kind": "resense"}
"""

_SYSTEM_PROMPT_PARTNR = """\
You are an embodied robot agent (Spot) operating in a household alongside a human partner.
You observed the scene at time t0. You are now asked about the scene at a LATER time.
Your last observation may be stale — the human partner or household activity may have
moved objects since you last observed them.

You have two actions:
  ANSWER  — answer from stale knowledge + world reasoning (free).
  RESENSE — navigate to re-observe the scene (costs 1 budget token).

Think about:
  • Staleness Δ: how long ago did you observe?
  • Object volatility: phones/keys/wallets move constantly; chairs/plants rarely do.
  • Household type: a family with kids has more chaotic object movement than a single adult.
  • Budget: resense tokens are shared across all questions. Spend wisely.

Respond ONLY with valid JSON:
  {"kind": "answer",  "option_index": <int>, "confidence": <0-1>}
  {"kind": "resense"}
"""


def _fmt_hour(t: float) -> str:
    h = int(t) % 24
    m = int(round((t % 1) * 60))
    if m == 60:
        h, m = (h + 1) % 24, 0
    return f"{h:02d}:{m:02d}"


def build_prompt(obs: Observation, use_world_graph: bool = False) -> str:
    """Serialise an Observation to the LLM user message.

    If obs.world_graph is set and use_world_graph=True, uses PARTNR's
    get_world_descr() for a richer house description (rooms, furniture, all
    object locations) that matches PARTNR's own planner prompts.
    """
    lines: list[str] = []
    lines.append("=== SCENE CONTEXT ===")

    if obs.household_type:
        lines.append(f"Household type  : {obs.household_type.replace('_', ' ')}")
    lines.append(f"Region          : {obs.region}")
    lines.append(f"Last observed at: {_fmt_hour(obs.observed_at)}")
    lines.append(f"Current time    : {_fmt_hour(obs.query_time)}")
    lines.append(f"Staleness (Δ)   : {obs.delta:.2f} h")
    if obs.region_prior is not None:
        rate = obs.region_prior.get("typical_change_rate", "?")
        lines.append(f"Region prior    : typical_change_rate = {rate}")
    lines.append(
        f"Resense budget  : {obs.remaining_budget} remaining / "
        f"{obs.questions_remaining} questions left "
        f"({obs.budget_rate:.2f} tokens/question)"
    )

    # Rich house description from WorldGraph (PARTNR mode)
    if use_world_graph and obs.world_graph is not None:
        lines.append("")
        lines.append("=== FULL HOUSE STATE (at t0) ===")
        try:
            lines.append(obs.world_graph.get_world_descr())
        except Exception as e:
            lines.append(f"(world graph unavailable: {e})")
    else:
        lines.append("")
        lines.append("=== LAST OBSERVED STATE (at t0) ===")
        if obs.observed_states:
            for iid, slot in obs.observed_states.items():
                lines.append(f"  {iid}: {slot}")
        else:
            lines.append("  (no tracked objects in region at t0)")

    lines.append("")
    lines.append("=== QUESTION ===")
    lines.append(obs.prompt)
    lines.append("")
    lines.append("=== OPTIONS ===")
    for i, opt in enumerate(obs.options):
        lines.append(f"  {i}) {opt}")
    lines.append("")
    if obs.remaining_budget > 0:
        lines.append("You may RESENSE (get fresh observation) or ANSWER now.")
    else:
        lines.append("No budget remaining — you must ANSWER now.")

    return "\n".join(lines)


def _parse(raw: str, n_options: int) -> Decision:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return Decision(kind=DecisionKind.ANSWER, option_index=0, confidence=0.0)
    kind_str = data.get("kind", "answer")
    kind = DecisionKind.RESENSE if kind_str == "resense" else DecisionKind.ANSWER
    if kind == DecisionKind.RESENSE:
        return Decision(kind=DecisionKind.RESENSE)
    idx  = max(0, min(n_options - 1, int(data.get("option_index", 0))))
    conf = float(max(0.0, min(1.0, data.get("confidence", 0.5))))
    return Decision(kind=DecisionKind.ANSWER, option_index=idx, confidence=conf)


class LLMAgent(Agent):
    """vLLM-backed Dynamic EQA agent with guided JSON output.

    Args:
        model:          vLLM model identifier (default: Qwen3-14B-AWQ).
        use_world_graph: When True and obs.world_graph is set, uses PARTNR's
                         get_world_descr() for richer house context.
        partnr_mode:    Use PARTNR-flavoured system prompt (robot/human framing).
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        use_world_graph: bool = False,
        partnr_mode: bool = False,
    ) -> None:
        self.model           = model
        self.use_world_graph = use_world_graph
        self.partnr_mode     = partnr_mode
        self._llm: Optional["LLM"] = None
        self._params: Optional["SamplingParams"] = None

    def _load(self) -> None:
        import os
        os.environ.setdefault("HF_HOME", _MODEL_CACHE)
        from vllm import LLM, SamplingParams
        from vllm.sampling_params import StructuredOutputsParams

        self._llm = LLM(
            model=self.model,
            quantization="awq" if "AWQ" in self.model else None,
            disable_log_stats=True,
        )
        self._params = SamplingParams(
            temperature=0.0,
            max_tokens=128,
            structured_outputs=StructuredOutputsParams(json=DECISION_SCHEMA),
        )

    def _system_prompt(self) -> str:
        return _SYSTEM_PROMPT_PARTNR if self.partnr_mode else _SYSTEM_PROMPT

    def act(self, obs: Observation) -> Decision:
        return self.batch_act([obs])[0]

    def batch_act(self, observations: list[Observation]) -> list[Decision]:
        """Process a list of observations in a single vLLM batch call."""
        if self._llm is None:
            self._load()

        sys_prompt = self._system_prompt()
        conversations = [
            [
                {"role": "system", "content": sys_prompt},
                {"role": "user",   "content": build_prompt(obs, self.use_world_graph)},
            ]
            for obs in observations
        ]
        outputs = self._llm.chat(conversations, sampling_params=self._params)
        return [
            _parse(o.outputs[0].text.strip(), n_options=len(obs.options))
            for o, obs in zip(outputs, observations)
        ]


# ---------------------------------------------------------------------------
# OpenAI-backed variant (no GPU required)
# ---------------------------------------------------------------------------

class OpenAIAgent(Agent):
    """OpenAI-backed agent for quick experiments without a GPU.

    Requires OPENAI_API_KEY in environment.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        use_world_graph: bool = False,
        partnr_mode: bool = False,
    ) -> None:
        self.model           = model
        self.use_world_graph = use_world_graph
        self.partnr_mode     = partnr_mode
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def _system_prompt(self) -> str:
        return _SYSTEM_PROMPT_PARTNR if self.partnr_mode else _SYSTEM_PROMPT

    def act(self, obs: Observation) -> Decision:
        client = self._get_client()
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user",   "content": build_prompt(obs, self.use_world_graph)},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=128,
        )
        raw = resp.choices[0].message.content or ""
        return _parse(raw.strip(), n_options=len(obs.options))

    def batch_act(self, observations: list[Observation]) -> list[Decision]:
        return [self.act(obs) for obs in observations]
