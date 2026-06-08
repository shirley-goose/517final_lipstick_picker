#!/usr/bin/env python3

import argparse
import csv
import subprocess
import time
from datetime import datetime
from pathlib import Path


def ensure_csv_header(csv_path: Path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    if csv_path.exists():
        return

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "trial_number",
                "state_label",
                "success",
                "completion_time_s",
                "failure_mode",
                "observation",
            ],
        )
        writer.writeheader()


def append_result(csv_path: Path, row: dict):
    with csv_path.open("a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "trial_number",
                "state_label",
                "success",
                "completion_time_s",
                "failure_mode",
                "observation",
            ],
        )
        writer.writerow(row)


def run_home(home_command: str):
    print("\n[RUN] Move to home pose")
    print(home_command)
    subprocess.run(home_command, shell=True)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--states", nargs="+", default=["center", "left_shift", "right_shift"])
    parser.add_argument("--trials-per-state", type=int, default=10)
    parser.add_argument("--timeout-s", type=float, default=30.0)
    parser.add_argument("--csv", type=str, required=True)
    parser.add_argument("--home-command", type=str, required=True)

    args = parser.parse_args()

    csv_path = Path(args.csv)
    ensure_csv_header(csv_path)

    trial_number = 1

    print("\nLipstick Evaluation Logger")
    print("This script only logs results. Run the policy manually in another terminal.")
    print("-" * 80)

    for state in args.states:
        for _ in range(args.trials_per_state):
            print("\n" + "=" * 80)
            print(f"Trial {trial_number}")
            print(f"State: {state}")
            print("=" * 80)

            run_home(args.home_command)

            print("\nPlace the lipstick for this state.")
            input("Press Enter when workspace is ready...")

            print("\nNow start policy manually in another terminal.")
            input("When the robot starts moving, press Enter here to start timing...")

            start_time = time.time()

            print("\nDuring execution:")
            print("  s = success")
            print("  f = failure")
            print("  d = object dropped")
            print("  w = wrong grasp / wrong object")
            print("  t = timeout")
            print("  q = quit")

            label = input("Enter result label: ").strip().lower()
            elapsed = round(time.time() - start_time, 2)

            if label == "s":
                success = 1
                failure_mode = ""
            elif label == "d":
                success = 0
                failure_mode = "object_dropped"
            elif label == "w":
                success = 0
                failure_mode = "wrong_grasp"
            elif label == "t":
                success = 0
                failure_mode = "timeout"
                elapsed = args.timeout_s
            elif label == "q":
                print("Stopped by user.")
                return
            else:
                success = 0
                failure_mode = "manual_failure"

            observation = input("Optional observation: ").strip()

            row = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "trial_number": trial_number,
                "state_label": state,
                "success": success,
                "completion_time_s": elapsed,
                "failure_mode": failure_mode,
                "observation": observation,
            }

            append_result(csv_path, row)

            print("\n[LOGGED]")
            for k, v in row.items():
                print(f"{k}: {v}")

            print("\nStop policy manually with Ctrl+C in the policy terminal.")
            input("After policy is stopped, press Enter to reset home...")

            run_home(args.home_command)

            trial_number += 1

    print("\nEvaluation complete.")
    print(f"Results saved to: {csv_path}")


if __name__ == "__main__":
    main()
