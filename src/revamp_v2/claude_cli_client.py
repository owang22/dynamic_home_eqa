"""Generation backend that reaches Claude through the Claude Code CLI.

Why this exists: the other two backends (in-process vLLM, OpenAI-compatible
HTTP) both bill an API key. A Claude subscription cannot be spent that way —
the only thing that can spend it is the Claude Code binary itself. So this
client shells out to that binary in headless mode, once per LLM call.

It is a drop-in for `llm_client`'s clients: the same `generate(system, user,
schema, seed, temperature)` returning the raw JSON text. Everything upstream
of it — seeding, the response cache, the validate/retry loop, the five
checks, L3 realization, L4 projection — runs unchanged, so a Claude set is
built by the same code that builds a vLLM set and lands in its own
`profiles/revamp_v2/<model_slug>/` directory.

Three things differ from the vLLM path, all of them structural:

* **No guided decoding.** vLLM constrains sampling to the schema; the CLI has
  no such knob. The schema is therefore appended to the user message as an
  explicit contract (see `_SCHEMA_APPENDIX`). The human-authored prompt text
  from `prompts.py` is passed through byte-for-byte and the appendix is
  clearly delimited after it, so what the model reads is "the same prompt,
  plus the schema that guided decoding used to enforce out of band".
* **No seed.** The CLI exposes no sampling seed, so `seed` here only keys the
  cache — it does not make the model itself reproducible. A cached run
  replays exactly; a forced re-run will differ. The vLLM path is reproducible
  in both senses, this one only in the first.
* **No prior history.** Each call is a fresh process with `--system-prompt`
  replacing Claude Code's own system prompt outright (not `--append-`), so
  the model sees the pipeline's prompt and nothing else: no repo context, no
  conversation, no tools.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess

# Long-form programs legitimately take minutes at this size; the cap only
# exists so a wedged call cannot hang a ten-household build forever.
DEFAULT_TIMEOUT_S = 1800
DEFAULT_MODEL = "claude-fable-5"

_SCHEMA_APPENDIX = """

---
Return a single JSON object and nothing else: no prose before or after it, no
markdown code fences, no trailing commentary. It must validate against this
JSON Schema exactly — every required key present, no extra keys, enums drawn
only from the values listed, and arrays whose `prefixItems` pin a position
must keep that position:

{schema}
"""


def find_cli() -> str:
    """Absolute path to the Claude Code binary.

    `claude` is usually not on PATH when Claude Code runs from the VS Code
    extension, but the extension exports its own location, so prefer that and
    fall back to PATH for a terminal install.
    """
    explicit = os.environ.get("CLAUDE_CLI_PATH", "").strip()
    if explicit:
        return explicit
    exec_path = os.environ.get("CLAUDE_CODE_EXECPATH", "").strip()
    if exec_path and pathlib.Path(exec_path).exists():
        return exec_path
    found = shutil.which("claude")
    if found:
        return found
    raise RuntimeError(
        "cannot find the Claude Code binary — set CLAUDE_CLI_PATH to it "
        "(it is usually under ~/.vscode-server/extensions/anthropic.claude-"
        "code-*/resources/native-binary/claude)")


def extract_json(text: str) -> str:
    """The first complete JSON object in `text`.

    Guided decoding guaranteed a bare object; this backend cannot, so a
    stray fence or a sentence of preamble has to be survivable. Braces are
    balanced with a scan rather than a regex because the payload nests
    deeply and contains braces inside strings.
    """
    body = text.strip()
    if body.startswith("```"):                    # ```json ... ```
        body = re.sub(r"^```[a-zA-Z]*\n", "", body)
        body = re.sub(r"\n```\s*$", "", body).strip()
    start = body.find("{")
    if start == -1:
        raise ValueError(f"no JSON object in CLI output: {text[:200]!r}")
    depth, in_str, esc = 0, False, False
    for i, ch in enumerate(body[start:], start):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return body[start:i + 1]
    raise ValueError("unterminated JSON object in CLI output")


class ClaudeCliClient:
    """`llm_client`-shaped client backed by one CLI process per call."""

    def __init__(self, model: str = DEFAULT_MODEL,
                 timeout_s: int = DEFAULT_TIMEOUT_S,
                 cli: str | None = None) -> None:
        self.model = model
        self.timeout_s = timeout_s
        self._cli = cli or find_cli()

    def generate(self, system: str, user: str, schema: dict,
                 seed: int | None = None, temperature: float = 0.7) -> str:
        """Raw JSON text for one prompt. `seed` and `temperature` are accepted
        for interface compatibility and ignored — the CLI exposes neither."""
        prompt = user + _SCHEMA_APPENDIX.format(
            schema=json.dumps(schema, indent=2))
        # The prompt goes on stdin, never argv: programs run to tens of KB,
        # and the tool flags are variadic, so a positional prompt following
        # one is silently swallowed as a tool name.
        proc = subprocess.run(
            [self._cli, "-p", "--model", self.model,
             "--system-prompt", system,
             "--tools", ""],               # documented spelling for "no tools"
            input=prompt, capture_output=True, text=True,
            timeout=self.timeout_s,
            cwd="/",                        # no repo for it to wander into
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"claude CLI exited {proc.returncode}: "
                f"{(proc.stderr or proc.stdout)[-500:]}")
        return extract_json(proc.stdout)


def is_claude_model(model: str) -> bool:
    """Whether `model` should be routed through the subscription CLI rather
    than a served endpoint. Local Claude weights are not a thing here, so a
    bare `claude-*` name always means the hosted model."""
    return model.lower().startswith("claude-")
