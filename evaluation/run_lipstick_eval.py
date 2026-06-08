#!/usr/bin/env python3
"""
run_lipstick_eval.py

Manual evaluation controller for lipstick grasping.

Better flow:
1. Move robot to home pose.
2. Human places lipstick.
3. Start policy subprocess.
4. Wait until policy is loaded / robot starts moving.
5. Human presses Enter to start trial timer.
6. Human labels success/failure, or timeout happens.
7. Stop policy.
8. Log CSV.
9. Move robot back to home pose.
"""

import argparse
import csv
import os
import select
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def run_command(command: str, name: str) -> int:
    print(f"\n[RUN] {name}")
    print(command)
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"[WARNING] {name} exited with code {result.returncode}")
    return result.returncode


def start_policy(command: str) -> subprocess.Popen:
    print("\n[RUN] Policy")
    print(command)

    # Important: stdin=DEVNULL prevents the policy subprocess from consuming
    # the keyboard input meant for this evaluation script.
    process = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )
    return process


def stop_process(process: subprocess.Popen):
    if process is None or process.poll() is not None:
        return

    print("\n[STOP] Stopping policy process...")

    try:
        os.killpg(os.getpgid(process.pid), signal.SIGINT)
        time.sleep(2)
    except Exception:
        pass

    if process.poll() is None:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            time.sleep(1)
        except Exception:
            pass

    if process.poll() is None:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except Exception:
            pass


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


def wait_for_label_or_timeout(timeout_s: float, policy_process: subprocess.Popen) -> dict:
    print("\nTrial timer started.")
    print("Press one key then Enter:")
    print("  s = success")
    print("  f = failure")
    print("  d = object dropped")
    print("  w = wrong grasp / wrong object")
    print("  q = quit evaluation")
    print(f"\nExecution timeout: {timeout_s} seconds")

    start_time = time.time()

    while True:
        elapsed = time.time() - start_time

        if elapsed >= timeout_s:
            return {
                "success": 0,
                "completion_time_s": round(timeout_s, 2),
                "failure_mode": "timeout",
                "quit": False,
            }

        if policy_process.poll() is not None:
            return {
                "success": 0,
                "completion_time_s": round(elapsed, 2),
                "failure_mode": "policy_exited_before_label",
                "quit": False,
            }

        readable, _, _ = select.select([sys.stdin], [], [], 0.2)

        if readable:
            label = sys.stdin.readline().strip().lower()
            elapsed = time.time() - start_time

            if label == "s":
                return {
                    "success": 1,
                    "completion_time_s": round(elapsed, 2),
                    "failure_mode": "",
                    "quit": False,
                }

            if label == "f":
                return {
                    "success": 0,
                    "completion_time_s": round(elapsed, 2),
                    "failure_mode": "manual_failure",
                    "quit": False,
                }

            if label == "d":
                return {
                    "success": 0,
                    "completion_time_s": round(elapsed, 2),
                    "failure_mode": "object_dropped",
                    "quit": False,
                }

            if label == "w":
                return {
                    "success": 0,
                    "completion_time_s": round(elapsed, 2),
                    "failure_mode": "wrong_grasp",
                    "quit": False,
                }

            if label == "q":
                return {
                    "success": 0,
                    "completion_time_s": round(elapsed, 2),
                    "failure_mode": "user_quit",
                    "quit": True,
                }

            print("Unknown input. Use s, f, d, w, or q.")


def run_trial(
    trial_number: int,
    state_label: str,
    timeout_s: float,
    csv_path: Path,
    home_command: str,
    policy_command: str,
) -> bool:
    print("\n" + "=" * 80)
    print(f"Trial {trial_number}")
    print(f"State: {state_label}")
    print("=" * 80)

    # 1. Reset robot.
    run_command(home_command, "Move to home pose before trial")

    # 2. Human places object.
    print("\nPlace the lipstick according to this state:")
    print(f"  State label: {state_label}")
    input("Press Enter when the workspace is ready...")

    # 3. Start policy.
    policy_process = start_policy(policy_command)

    print("\nPolicy is starting.")
    print("Wait until checkpoint/cameras finish loading and the robot is ready.")
    print("When the robot starts executing, press Enter to start the evaluation timer.")
    input("Press Enter to START TIMER...")

    # 4. Wait for success/failure/timeout.
    result = wait_for_label_or_timeout(timeout_s, policy_process)

    # 5. Stop policy.
    stop_process(policy_process)

    # 6. Notes.
    observation = input("Optional observation for this trial: ").strip()

    # 7. Save result.
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "trial_number": trial_number,
        "state_label": state_label,
        "success": result["success"],
        "completion_time_s": result["completion_time_s"],
        "failure_mode": result["failure_mode"],
        "observation": observation,
    }

    append_result(csv_path, row)

    print("\n[LOGGED]")
    for key, value in row.items():
        print(f"{key}: {value}")

    # 8. Reset after trial.
    run_command(home_command, "Move to home pose after trial")

    return result["quit"]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--states",
        nargs="+",
        default=["center", "left_shift", "right_shift"],
    )

    parser.add_argument(
        "--trials-per-state",
        type=int,
        default=10,
    )

    parser.add_argument(
        "--timeout-s",
        type=float,
        default=30.0,
        help="Execution timeout after the timer starts, not including policy loading time.",
    )

    parser.add_argument(
        "--csv",
        type=str,
        default="results/lipstick_eval.csv",
    )

    parser.add_argument(
        "--home-command",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--policy-command",
        type=str,
        required=True,
    )

    args = parser.parse_args()

    csv_path = Path(args.csv)
    ensure_csv_header(csv_path)

    print("\nLipstick Grasping Evaluation")
    print("-" * 80)
    print(f"States: {args.states}")
    print(f"Trials per state: {args.trials_per_state}")
    print(f"Total planned trials: {len(args.states) * args.trials_per_state}")
    print(f"Execution timeout: {args.timeout_s} seconds")
    print(f"CSV output: {csv_path}")
    print("-" * 80)

    trial_number = 1

    for state_label in args.states:
        for _ in range(args.trials_per_state):
            should_quit = run_trial(
                trial_number=trial_number,
                state_label=state_label,
                timeout_s=args.timeout_s,
                csv_path=csv_path,
                home_command=args.home_command,
                policy_command=args.policy_command,
            )

            if should_quit:
                print("\nEvaluation stopped by user.")
                print(f"Partial results saved to: {csv_path}")
                return

            trial_number += 1

    print("\nEvaluation complete.")
    print(f"Results saved to: {csv_path}")


if __name__ == "__main__":
    main()