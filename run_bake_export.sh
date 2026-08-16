#!/usr/bin/env bash
# Reusable bake-export driver: adapter -> merged HF -> Q8 GGUF (auto-clean bf16 + HF dir).
# Usage: run_bake_export.sh <adapter_dir> <tag>
#   produces merged_models/<tag>-q8_0.gguf
set -euo pipefail
ADAPTER="$1"; TAG="$2"
ROOT="$(cd "$(dirname "$0")" && pwd)"
LL="${LLAMA_CPP:-/var/home/deucebucket/ai-drive/llama.cpp-pr24260}"
MODELS="${BRAINLOOP_MODELS:-/var/home/deucebucket/games/brainloop-models}"
HFDIR="${MODELS}/${TAG}_hf"
BF16="${MODELS}/${TAG}-bf16.gguf"
Q8="${MODELS}/${TAG}-q8_0.gguf"

cd "$ROOT"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
echo "[1/3] merge $ADAPTER -> $HFDIR"
python3 brainloop_merge_lora_model.py \
  --adapter "$ADAPTER" --output-dir "$HFDIR" \
  --out-dir "brainloop_runs/${TAG}_merge" --run-id "${TAG}_merge" >/dev/null
echo "[2/3] convert -> bf16 GGUF"
python3 "$LL/convert_hf_to_gguf.py" "$HFDIR" --outfile "$BF16" --outtype bf16 >/dev/null
echo "[3/3] quantize -> Q8_0, clean intermediates"
"$LL/build-cpu/bin/llama-quantize" "$BF16" "$Q8" q8_0 >/dev/null
rm -rf "$HFDIR" "$BF16"
echo "DONE -> $Q8"
ls -la "$Q8"
