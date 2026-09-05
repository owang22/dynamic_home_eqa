"""Offline batch generation for the LLM belief (runs in the vLLM venv).

Reads a prompts JSONL (``{"key": ..., "messages": [...]}`` per line),
writes a completions JSONL (``{"key", "text", "prompt_tokens",
"completion_tokens", "finish_reason"}``) and a stats JSON with wall time
and tokens per second. Keys already present in the output file are
skipped, so a warmup run and the full run are the same command with a
different ``--limit``. One vLLM instance, greedy decoding, seeded.

This file imports nothing from the repo on purpose: the vLLM venv
(``/data/oliver/venvs/vllm-v4-cu129``) does not carry the project's
dependencies, and the CPU-side evaluation does not carry vLLM.

Usage (from the driver, or by hand):
  CUDA_VISIBLE_DEVICES=0,1 VLLM_ALLREDUCE_USE_SYMM_MEM=0 \\
  /data/oliver/venvs/vllm-v4-cu129/bin/python src/baselines/llm_generate.py \\
      --prompts prompts.jsonl --out completions.jsonl --stats stats.json \\
      --model Qwen/Qwen3.8-27B --tensor-parallel 2 --limit 200
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
from typing import Any, Dict, List

JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "ranking": {"type": "array", "items": {"type": "string"},
                    "minItems": 1, "maxItems": 5},
        "p_top": {"type": "number"},
    },
    "required": ["ranking", "p_top"],
    "additionalProperties": False,
}
"""Duplicate of ``baselines.beliefs.llm_belief.JSON_SCHEMA`` (this script
cannot import the package); the driver asserts the two agree."""


def _read_jsonl(path: pathlib.Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompts", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--stats", type=pathlib.Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen3.8-27B")
    ap.add_argument("--tensor-parallel", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0,
                    help="answer at most this many NEW prompts (0 = all)")
    ap.add_argument("--max-tokens", type=int, default=160)
    ap.add_argument("--max-model-len", type=int, default=8192)
    ap.add_argument("--gpu-memory-utilization", type=float, default=0.90)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-num-seqs", type=int, default=256,
                    help="concurrent sequences; the hybrid Mamba/attention "
                         "Qwen3.5-family models need one Mamba cache block "
                         "per sequence and refuse vLLM's 1024 default")
    ap.add_argument("--chunk", type=int, default=2048,
                    help="prompts per LLM.chat call (progress is written "
                         "after every chunk)")
    ap.add_argument("--no-guided", action="store_true",
                    help="free-form decoding instead of the JSON grammar")
    args = ap.parse_args()

    from vllm import LLM, SamplingParams
    from vllm.sampling_params import StructuredOutputsParams

    done = {r["key"] for r in _read_jsonl(args.out)}
    prompts = [r for r in _read_jsonl(args.prompts) if r["key"] not in done]
    if args.limit:
        prompts = prompts[:args.limit]
    print(f"llm_generate: {len(done)} done, {len(prompts)} to answer with "
          f"{args.model} (tp={args.tensor_parallel}, guided="
          f"{not args.no_guided})", flush=True)
    if not prompts:
        return

    t_load = time.time()
    llm = LLM(model=args.model, tensor_parallel_size=args.tensor_parallel,
              seed=args.seed, max_model_len=args.max_model_len,
              gpu_memory_utilization=args.gpu_memory_utilization,
              limit_mm_per_prompt={"image": 0, "video": 0},
              structured_outputs_config={"backend": "xgrammar",
                                         "disable_any_whitespace": True},
              enable_prefix_caching=True, max_num_seqs=args.max_num_seqs,
              # TP>1 on this box: the symmetric-memory and custom all-reduce
              # paths both hit illegal memory accesses; plain NCCL works.
              disable_custom_all_reduce=args.tensor_parallel > 1)
    load_s = time.time() - t_load
    structured = (None if args.no_guided
                  else StructuredOutputsParams(json=JSON_SCHEMA))
    params = SamplingParams(temperature=0.0, max_tokens=args.max_tokens,
                            seed=args.seed, structured_outputs=structured)

    n_prompt_tokens = n_completion_tokens = n_answered = 0
    n_truncated = 0
    t_gen = time.time()
    with args.out.open("a") as out:
        for start in range(0, len(prompts), args.chunk):
            chunk = prompts[start:start + args.chunk]
            outputs = llm.chat([r["messages"] for r in chunk],
                               sampling_params=params, use_tqdm=True,
                               chat_template_kwargs={"enable_thinking": False})
            for rec, o in zip(chunk, outputs):
                comp = o.outputs[0]
                n_prompt_tokens += len(o.prompt_token_ids or [])
                n_completion_tokens += len(comp.token_ids)
                n_answered += 1
                n_truncated += int(comp.finish_reason == "length")
                out.write(json.dumps({
                    "key": rec["key"], "text": comp.text,
                    "prompt_tokens": len(o.prompt_token_ids or []),
                    "completion_tokens": len(comp.token_ids),
                    "finish_reason": comp.finish_reason}) + "\n")
            out.flush()
            elapsed = time.time() - t_gen
            print(f"llm_generate: {n_answered}/{len(prompts)} answered, "
                  f"{elapsed:.0f}s, {n_answered / elapsed:.2f} q/s, "
                  f"{(n_prompt_tokens + n_completion_tokens) / elapsed:.0f} "
                  f"tok/s", flush=True)
    gen_s = time.time() - t_gen
    stats = {
        "model": args.model, "tensor_parallel": args.tensor_parallel,
        "guided_json": not args.no_guided, "seed": args.seed,
        "max_tokens": args.max_tokens, "cuda_visible_devices":
        os.environ.get("CUDA_VISIBLE_DEVICES"),
        "n_answered": n_answered, "n_previously_done": len(done),
        "n_truncated": n_truncated,
        "prompt_tokens": n_prompt_tokens,
        "completion_tokens": n_completion_tokens,
        "prompt_tokens_per_question": n_prompt_tokens / n_answered,
        "completion_tokens_per_question": n_completion_tokens / n_answered,
        "load_seconds": round(load_s, 1), "generate_seconds": round(gen_s, 1),
        "questions_per_second": n_answered / gen_s,
        "tokens_per_second": (n_prompt_tokens + n_completion_tokens) / gen_s,
    }
    args.stats.write_text(json.dumps(stats, indent=2))
    print("llm_generate: " + json.dumps(stats), flush=True)


if __name__ == "__main__":
    main()
