#!/bin/bash
# Part 2: prepare YOLO dataset → train
# Run AFTER labeling frames in label_images/
# Run with: nohup bash run_pipeline_part2.sh > pipeline_part2.log 2>&1 &

set -e

PYTHON=/home/ubuntu/miniforge3/envs/lerobot/bin/python
YOLO_DIR=/home/ubuntu/techin517/lipstick_yolo

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

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
log "Model saved to: $YOLO_DIR/models/black_lipstick_yolo_665/weights/best.pt"
