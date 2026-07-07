#!/usr/bin/env python3
"""
serve_llm.py — launches vLLM's OpenAI-compatible server for Phase A's
FMDecisionPolicy to reach over HTTP from the explore-eqa (habitat_sim)
env, which has no vllm installed (see llm_prior/http_client.py's own
docstring for why the two envs are decoupled this way instead of merged).

Always binds to 127.0.0.1 — never 0.0.0.0 — this is a local inference
endpoint for this machine's own habitat_sim process to reach, not a
served model. --host is deliberately not exposed as a CLI flag here;
change the constant below, with the same care, if that ever needs to
change.

Run from the env that has vllm installed (this repo's default python3,
NOT explore-eqa). Leave running in the foreground or background for the
duration of an A1 sweep; scripts/a1_fm_decision_sweep.py (run separately,
under explore-eqa) is the client.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

_HOST = "127.0.0.1"  # loopback only — see module docstring


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help="vLLM model string, e.g. casperhansen/llama-3.3-70b-instruct-awq")
    ap.add_argument("--port", type=int, default=8123)
    ap.add_argument("--trust-remote-code", action="store_true")
    args = ap.parse_args()

    env = dict(os.environ)
    env.setdefault("HF_HOME", "/mnt/nvme/oliver/robot/models")

    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", args.model, "--host", _HOST, "--port", str(args.port),
    ]
    if args.trust_remote_code:
        cmd.append("--trust-remote-code")

    print(f"Launching {args.model} on http://{_HOST}:{args.port} (loopback only)")
    os.execvpe(cmd[0], cmd, env)


if __name__ == "__main__":
    main()
