#!/bin/bash
# Conch Shell Proof of Concept — Full Pipeline
#
# Runs on single 3090. Total time: ~2-4 hours.
# Uses WikiText-2 for initial training, then NIM teacher data for Phase 2+

set -e
cd "$(dirname "$0")"

WIKI_DATA="/var/home/deucebucket/games/osmosis-quants/wiki.test.raw"
CHECKPOINTS="./checkpoints"
BASE_MODEL="HuggingFaceTB/SmolLM-135M"

echo "============================================"
echo "CONCH SHELL PROOF OF CONCEPT"
echo "============================================"
echo "Base: $BASE_MODEL (135M params)"
echo "Data: $WIKI_DATA"
echo ""

# Step 0: Verify model loads and show architecture
echo "--- Step 0: Architecture verification ---"
python3 model.py
echo ""

# Step 1: Phase 1 training (2 fixed loops)
echo "--- Step 1: Phase 1 — Fixed 2 revolutions ---"
python3 train.py \
    --phase 1 \
    --data "$WIKI_DATA" \
    --output "$CHECKPOINTS" \
    --epochs 3 \
    --batch-size 8 \
    --lr 5e-5 \
    --block-size 512 \
    --base-model "$BASE_MODEL"

# Step 2: Phase 2 training (4 fixed loops, resume from phase 1)
echo ""
echo "--- Step 2: Phase 2 — Fixed 4 revolutions ---"
python3 train.py \
    --phase 2 \
    --data "$WIKI_DATA" \
    --output "$CHECKPOINTS" \
    --epochs 3 \
    --batch-size 4 \
    --lr 2e-5 \
    --block-size 512 \
    --base-model "$BASE_MODEL" \
    --resume "$CHECKPOINTS/phase1/best_checkpoint.pt"

# Step 3: Evaluate
echo ""
echo "--- Step 3: Evaluation ---"
python3 evaluate.py \
    --checkpoint "$CHECKPOINTS/phase2/best_checkpoint.pt" \
    --base-model "$BASE_MODEL" \
    --data "$WIKI_DATA"

echo ""
echo "============================================"
echo "POC COMPLETE"
echo "============================================"
