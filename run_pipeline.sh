#!/bin/bash
# Full pipeline: merge → yolo highlight → extract frames → prepare dataset → train
# Run with: nohup bash run_pipeline.sh > pipeline.log 2>&1 &

set -e  # stop on any error

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

# ── Step 3: Extract frames ────────────────────────────────────────────────────
log "=== STEP 3: Extracting frames ==="
$PYTHON $YOLO_DIR/scripts/extract_yolo_frames.py \
    --dataset $LOCAL/lipstick_picking_all_merged_665_yolo_highlight \
    --out $YOLO_DIR/frames_665
log "=== STEP 3 DONE ==="

# ── Step 4: Prepare YOLO dataset ──────────────────────────────────────────────
log "=== STEP 4: Preparing YOLO dataset ==="
$PYTHON $YOLO_DIR/scripts/prepare_yolo_dataset.py \
    --src $YOLO_DIR/label_images \
    --dst $YOLO_DIR/yolo_dataset_665
log "=== STEP 4 DONE ==="

# ── Step 5: Train YOLO ────────────────────────────────────────────────────────
log "=== STEP 5: Training YOLO ==="
/home/ubuntu/miniforge3/envs/lerobot/bin/yolo train \
    model=yolov8n.pt \
    data=$YOLO_DIR/yolo_dataset_665/data.yaml \
    epochs=80 \
    batch=16 \
    imgsz=640 \
    project=$YOLO_DIR/models \
    name=black_lipstick_yolo_665 \
    device=0
log "=== STEP 5 DONE — Training complete ==="
