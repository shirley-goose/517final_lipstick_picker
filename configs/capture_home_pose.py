#!/usr/bin/env python3
"""
capture_home_pose.py

Read the current joint positions of the bi-manual SO follower robot
and save them as a reusable home pose.

Use this after manually moving the robot to the desired home position.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import draccus
import numpy as np

# Force-register robot configs.
import lerobot.robots.so_follower
import lerobot.robots.bi_so_follower

from lerobot.robots import RobotConfig, make_robot_from_config


@dataclass
class CaptureHomePoseConfig:
    robot: RobotConfig
    output: str = "configs/home_pose.json"


def to_float(value):
    if isinstance(value, np.ndarray):
        return float(value.item())
    if isinstance(value, np.generic):
        return float(value)
    return float(value)


@draccus.wrap()
def capture_home_pose(cfg: CaptureHomePoseConfig):
    robot = make_robot_from_config(cfg.robot)

    print(f"Connecting to robot: {cfg.robot.type}")
    robot.connect()
    print("Robot connected.")

    try:
        observation = robot.get_observation()

        home_action = {}

        for key, value in observation.items():
            # Keep only joint position keys for the two follower arms.
            if key.endswith(".pos") and (key.startswith("left_") or key.startswith("right_")):
                home_action[key] = to_float(value)

        if not home_action:
            print("No joint position keys found.")
            print("Available observation keys:")
            for key in observation.keys():
                print(" ", key)
            return

        output_path = Path(cfg.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w") as f:
            json.dump(home_action, f, indent=2)

        print(f"\nSaved home pose to: {output_path}")
        print("\nCaptured home action:")
        for key, value in home_action.items():
            print(f"  {key}: {value}")

    finally:
        robot.disconnect()
        print("Robot disconnected.")


if __name__ == "__main__":
    capture_home_pose()
