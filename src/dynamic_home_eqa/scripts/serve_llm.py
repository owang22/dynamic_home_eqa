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

from dynamic_home_eqa.paths import MODEL_CACHE_DIR

_HOST = "127.0.0.1"  # loopback only — see module docstring


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help="vLLM model string, e.g. Qwen/Qwen3-235B-A22B-GPTQ-Int4")
    ap.add_argument("--port", type=int, default=8123)
    ap.add_argument("--gpus", default=None,
                    help="Comma-separated GPU indices to pin the server to, e.g. '2,3' "
                         "(sets CUDA_VISIBLE_DEVICES). Default: whatever the shell already exposes.")
    ap.add_argument("--tensor-parallel-size", "--tp", type=int, default=None, dest="tp",
                    help="Tensor parallel degree. Default: the number of GPUs in --gpus "
                         "when given, else vLLM's own default (1).")
    ap.add_argument("--max-model-len", type=int, default=None,
                    help="Context length cap; lower it to trade context for KV-cache "
                         "headroom on tightly packed multi-GPU quantized loads.")
    ap.add_argument("--gpu-memory-utilization", type=float, default=None)
    ap.add_argument("--max-num-seqs", type=int, default=None,
                    help="Concurrent-sequence cap. Hybrid Mamba-layer models "
                         "(Qwen3.5/3.6 MoE) allocate one Mamba cache block per decode "
                         "sequence, and vLLM's 1024 default can exceed what fits after "
                         "weights + KV; a single-client generation run needs far less.")
    ap.add_argument("--moe-backend", default=None,
                    help="Force a fused-MoE kernel backend (e.g. 'triton'). Needed on "
                         "this machine's sm_120 (RTX PRO 6000 Blackwell) GPU: the default "
                         "FlashInfer CUTLASS path JIT-compiles per-arch kernels and there "
                         "is no CUDA >=12.8 nvcc installed, so it dies with 'No supported "
                         "CUDA architectures found for major versions [12]'.")
    ap.add_argument("--compact-guided-json", action="store_true",
                    help="Pass structured-outputs config {'disable_any_whitespace': "
                         "true} so guided-JSON grammars only admit compact JSON. "
                         "Without it the grammar admits unbounded whitespace between "
                         "JSON tokens, and low-temperature guided calls (the strict "
                         "realism judge) can degenerate into a whitespace loop that "
                         "burns the whole max_tokens budget after '{\"scores\": [' — "
                         "observed with Qwen3.6-35B-A3B, poisoning judge scores to "
                         "the 0.0 fallback.")
    ap.add_argument("--trust-remote-code", action="store_true")
    args = ap.parse_args()

    env = dict(os.environ)
    env.setdefault("HF_HOME", MODEL_CACHE_DIR)
    if args.gpus:
        env["CUDA_VISIBLE_DEVICES"] = args.gpus
        if args.tp is None:
            args.tp = len([g for g in args.gpus.split(",") if g.strip()])

    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", args.model, "--host", _HOST, "--port", str(args.port),
    ]
    if args.tp:
        cmd += ["--tensor-parallel-size", str(args.tp)]
    if args.max_model_len:
        cmd += ["--max-model-len", str(args.max_model_len)]
    if args.gpu_memory_utilization:
        cmd += ["--gpu-memory-utilization", str(args.gpu_memory_utilization)]
    if args.max_num_seqs:
        cmd += ["--max-num-seqs", str(args.max_num_seqs)]
    if args.moe_backend:
        cmd += ["--moe-backend", args.moe_backend]
    if args.compact_guided_json:
        # backend must be pinned explicitly: 'auto' rejects the flag at
        # config validation ("only supported for xgrammar and guidance").
        cmd += ["--structured-outputs-config",
                '{"backend": "xgrammar", "disable_any_whitespace": true}']
    if args.trust_remote_code:
        cmd.append("--trust-remote-code")

    print(f"Launching {args.model} on http://{_HOST}:{args.port} (loopback only)"
          + (f" — GPUs {args.gpus}, TP={args.tp}" if args.gpus else ""))
    os.execvpe(cmd[0], cmd, env)


if __name__ == "__main__":
    main()
