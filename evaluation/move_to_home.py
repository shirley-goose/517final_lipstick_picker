#!/usr/bin/env python3
"""
move_to_home.py

Move bi-manual SO follower robot to a saved home pose.

This script loads the desired home position from configs/home_pose.json.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path

import draccus

# Force-register robot configs.
import lerobot.robots.so_follower
import lerobot.robots.bi_so_follower

from lerobot.robots import RobotConfig, make_robot_from_config


@dataclass
class MoveToHomeConfig:
    robot: RobotConfig
    home_pose_path: str = "configs/home_pose.json"
    duration_s: float = 3.0
    fps: int = 30


def load_home_action(path: str):
    home_pose_path = Path(path)

    if not home_pose_path.exists():
        raise FileNotFoundError(
            f"Home pose file not found: {home_pose_path}\n"
            "Run capture_home_pose.py first."
        )

    with home_pose_path.open("r") as f:
        action = json.load(f)

    # Basic validation.
    for key in action.keys():
        if not key.endswith(".pos"):
            raise ValueError(f"Invalid action key: {key}. Expected key ending with '.pos'.")
        if not (key.startswith("left_") or key.startswith("right_")):
            raise ValueError(f"Invalid action key: {key}. Expected left_ or right_ prefix.")

    return action


@draccus.wrap()
def move_to_home(cfg: MoveToHomeConfig):
    robot = make_robot_from_config(cfg.robot)

    home_action = load_home_action(cfg.home_pose_path)

    print(f"Connecting to robot: {cfg.robot.type}")
    robot.connect()
    print("Robot connected.")

    print(f"Loaded home pose from: {cfg.home_pose_path}")
    for key, value in home_action.items():
        print(f"  {key}: {value}")

    dt = 1.0 / cfg.fps
    num_steps = int(cfg.duration_s * cfg.fps)

    try:
        for _ in range(num_steps):
            robot.send_action(home_action)
            time.sleep(dt)

        print("Home pose reached.")

    finally:
        robot.disconnect()
        print("Robot disconnected.")


if __name__ == "__main__":
    move_to_home()