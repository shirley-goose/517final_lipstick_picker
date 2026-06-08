#!/bin/bash
# Prepare new 300 episodes for labeling:
# Step 2: YOLO highlight on 0520/0521/0522 (sequential to avoid CPU overload)
# Step 3: Extract frames from each highlight dataset
# Run with: nohup bash run_new300_label_prep.sh > new300_label_prep.log 2>&1 &

set -e

PYTHON=/home/ubuntu/miniforge3/envs/lerobot/bin/python
LOCAL=/home/ubuntu/techin517/datasets/local
YOLO_DIR=/home/ubuntu/techin517/lipstick_yolo
WEIGHTS=$YOLO_DIR/models/black_lipstick_yolo/weights/best.pt
FRAMES_OUT=$YOLO_DIR/frames_new300

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

for DATE in 0520 0521 0522; do
    SRC=$LOCAL/lipstick_picking${DATE}_merged_batch1_20
    DST=$LOCAL/lipstick_picking${DATE}_merged_batch1_20_yolo_highlight

    # ── Step 2: YOLO highlight ────────────────────────────────────────────────
    log "=== STEP 2 [$DATE]: YOLO highlight ==="
    if [ -d "$DST" ]; then
        log "Skipping $DATE highlight — already exists"
    else
        $PYTHON $YOLO_DIR/scripts/make_yolo_highlight_dataset.py \
            --src $SRC \
            --dst $DST \
            --weights $WEIGHTS \
            --use_last_box
    fi
    log "=== STEP 2 [$DATE] DONE ==="

    # ── Step 3: Extract frames ────────────────────────────────────────────────
    log "=== STEP 3 [$DATE]: Extracting frames ==="
    $PYTHON $YOLO_DIR/scripts/extract_yolo_frames.py \
        --dataset $DST \
        --out $FRAMES_OUT
    log "=== STEP 3 [$DATE] DONE ==="
done

log "=========================================="
log "All done. Frames saved to:"
log "  $FRAMES_OUT"
log ""
log "Next: label frames in frames_new300/, add to label_images/"
log "Then run: nohup bash run_pipeline_part2.sh > pipeline_part2.log 2>&1 &"
log "=========================================="
