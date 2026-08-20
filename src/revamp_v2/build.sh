#!/usr/bin/env bash
# End-to-end revamp_v2 build: L1+L2 generation (all four checks inside the
# accept/reject loop) -> L3 simulation -> L4 bank export -> viewer configs
# -> realism panel (reporting only).
#
# Requires GENERATION_ENDPOINT: an OpenAI-compatible server for the
# generation model, e.g.
#   CUDA_VISIBLE_DEVICES=2 HF_HOME=/data/oliver/huggingface_cache \
#     /data/oliver/venvs/vllm-v4-cu129/bin/vllm serve Qwen/Qwen3.6-35B-A3B-FP8 \
#     --host 127.0.0.1 --port 8300 --max-model-len 16384 \
#     --gpu-memory-utilization 0.92 --max-num-seqs 32 \
#     --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}'
#   GENERATION_ENDPOINT=http://127.0.0.1:8300 bash src/revamp_v2/build.sh
#
# Determinism: same cache dir -> byte-identical artifacts (responses replay
# from cache); --force with the same seeds against the same serving stack
# regenerates the same content. Extra args are passed to generate.py
# (e.g. --scene 102343992, --force, --cache-dir ...).
set -euo pipefail
cd "$(dirname "$0")/../.."

: "${GENERATION_ENDPOINT:?set GENERATION_ENDPOINT (see header)}"
#MODEL="${GENERATION_MODEL:-Qwen/Qwen3.6-35B-A3B-FP8}"
MODEL="${GENERATION_MODEL:-Qwen/Qwen3.8-27B}"
SEED="${SEED:-0}"
SLUG=$(python3 -c "from dynamic_home_eqa.generation.llm_client import model_slug; print(model_slug('$MODEL'))")
OUT="profiles/revamp_v2/$SLUG"

# Generation failures are recorded, not fatal here: the surviving
# households still build, and the script exits nonzero at the end so a
# partial set can never be mistaken for a complete one.
GEN_OK=1
python3 src/revamp_v2/generate.py --all --model "$MODEL" "$@" || GEN_OK=0

built=()
for hh in "$OUT"/hh*/; do
    [ -f "$hh/routine_program.yaml" ] || { echo "skip $hh (no program)"; continue; }
    python3 src/revamp_v2/simulate.py "$hh" --seed "$SEED"
    built+=("$hh")
done

mkdir -p banks/baselines
for hh in "${built[@]}"; do
    name=$(basename "$hh")
    python3 -m baselines.export_bank \
        --timeline "$hh/timeline_seed$SEED" \
        --spec "$hh/routine_program.yaml" \
        --seed "$SEED" \
        --out "banks/baselines/revamp_v2_${name}_21d.jsonl"
done

python3 src/revamp_v2/make_viewer_configs.py --slug "$SLUG" --seed "$SEED"
for hh in "${built[@]}"; do
    name=$(basename "$hh")
    python3 visualization/spatialize.py \
        "visualization/configs/revamp_v2_${name}_102343992.yaml" \
        --timeline "$hh/timeline_seed$SEED"
done
python3 src/revamp_v2/realism_panel.py \
    "${built[@]/%//timeline_seed$SEED}" --out "$OUT/realism_panel.md"
echo
echo "to look at them:  python visualization/serve.py   # -> 127.0.0.1:8710"
echo "build complete: ${#built[@]} household(s) -> $OUT"
[ "$GEN_OK" = 1 ] || { echo "WARNING: some households failed generation"; exit 1; }
