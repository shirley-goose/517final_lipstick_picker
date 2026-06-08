#!/bin/bash
set -e

export PYTHONPATH=/home/ubuntu/techin517/lerobot/src:$PYTHONPATH

POLICY="/home/ubuntu/techin517/outputs/train/lipstick_act_yolo_highlight_final/checkpoints/100000/pretrained_model"

python /home/ubuntu/techin517/lerobot/src/lerobot/scripts/lerobot_record.py \
  --config_path /home/ubuntu/techin517/lerobot/evaluation/eval_with_cams.yaml \
  --policy.path="$POLICY" \
  --dataset.repo_id=local/eval_lipstick_yolo_act \
  --dataset.root=/home/ubuntu/techin517/lerobot/evaluation/results_recording/eval_lipstick_yolo_act_4.2 \
  --dataset.single_task="grasp the lipstick" \
  --dataset.num_episodes=1 \
  --dataset.episode_time_s=15
  --dataset.reset_time_s=0 \
  --dataset.video=true \
  --dataset.push_to_hub=false \
  --play_sounds=false \
  --display_data=false