#!/bin/bash
# Part 1: merge → yolo highlight → extract frames
# Run with: nohup bash run_pipeline_part1.sh > pipeline_part1.log 2>&1 &

set -e

PYTHON=/home/ubuntu/miniforge3/envs/lerobot/bin/python
LEROBOT_SRC=/home/ubuntu/techin517/lerobot/src
DATASETS=/home/ubuntu/techin517/datasets
LOCAL=$DATASETS/local
YOLO_DIR=/home/ubuntu/techin517/lipstick_yolo
WEIGHTS=$YOLO_DIR/models/black_lipstick_yolo/weights/best.pt

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# ── Step 1: Merge batches ─────────────────────────────────────────────────────
log "=== STEP 1: Merging datasets ==="
PYTHONPATH=$LEROBOT_SRC $PYTHON /home/ubuntu/techin517/merge_datasets.py
log "=== STEP 1 DONE ==="

# ── Step 2: YOLO highlight ────────────────────────────────────────────────────
log "=== STEP 2: YOLO highlight ==="
$PYTHON $YOLO_DIR/scripts/make_yolo_highlight_dataset.py \
    --src $LOCAL/lipstick_picking_all_merged_665 \
    --dst $LOCAL/lipstick_picking_all_merged_665_yolo_highlight \
    --weights $WEIGHTS \
    --use_last_box
log "=== STEP 2 DONE ==="

# ── Step 3: Extract frames for labeling ──────────────────────────────────────
log "=== STEP 3: Extracting frames ==="
$PYTHON $YOLO_DIR/scripts/extract_yolo_frames.py \
    --dataset $LOCAL/lipstick_picking_all_merged_665_yolo_highlight \
    --out $YOLO_DIR/frames_665
log "=== STEP 3 DONE ==="

log "=========================================="
log "Part 1 complete. Frames saved to:"
log "  $YOLO_DIR/frames_665"
log ""
log "Next: label the frames, save to label_images/"
log "Then run: nohup bash run_pipeline_part2.sh > pipeline_part2.log 2>&1 &"
log "=========================================="
