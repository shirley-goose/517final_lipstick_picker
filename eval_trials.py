"""
Lipstick Picking Robot - Evaluation Trial Recorder
Records trial results to CSV for quantitative analysis.
"""

import csv
import time
import os
from datetime import datetime

CSV_FILE = "eval_results.csv"

STATES = {
    "1": "State1_NormalLight_StandardPos",
    "2": "State2_DimLight_StandardPos",
    "3": "State3_NormalLight_DifferentPos",
}

FAILURE_MODES = {
    "1": "timeout",
    "2": "object_dropped",
    "3": "missed_grasp",
    "4": "wrong_position",
    "5": "robot_stopped",
    "6": "other",
}

SUCCESS_DEFINITION = (
    "Robot successfully picks up the lipstick and moves it to the target position "
    "without dropping it."
)


def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "trial_number", "state_label", "success",
                "completion_time_s", "failure_mode", "observations", "timestamp",
            ])
        print(f"Created new results file: {CSV_FILE}")
    else:
        print(f"Appending to existing file: {CSV_FILE}")


def get_trial_count():
    if not os.path.exists(CSV_FILE):
        return 0
    with open(CSV_FILE, "r") as f:
        return sum(1 for row in csv.reader(f)) - 1


def select_state():
    print("\n--- Select State ---")
    for key, label in STATES.items():
        print(f"  {key}. {label}")
    while True:
        choice = input("Enter state (1/2/3): ").strip()
        if choice in STATES:
            return STATES[choice]
        print("Invalid input, enter 1, 2, or 3.")


def run_trial(trial_num, state_label):
    print(f"\n{'='*50}")
    print(f"Trial #{trial_num}  |  {state_label}")
    print("="*50)

    input("Press Enter to START the robot...")
    start_time = time.time()
    print("Robot running... Press Enter when trial is DONE.")
    input()
    elapsed = round(time.time() - start_time, 2)
    print(f"Time: {elapsed}s")

    success = input("Success? (y/n): ").strip().lower() == "y"

    failure_mode = ""
    if not success:
        print("\n--- Failure Mode ---")
        for key, mode in FAILURE_MODES.items():
            print(f"  {key}. {mode}")
        choice = input("Select failure mode (1-6): ").strip()
        failure_mode = FAILURE_MODES.get(choice, "other")

    observations = input("Observations? (Enter to skip): ").strip()

    return {
        "trial_number": trial_num,
        "state_label": state_label,
        "success": success,
        "completion_time_s": elapsed,
        "failure_mode": failure_mode,
        "observations": observations,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def save_trial(data):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        writer.writerow(data)
    print(f"Saved to {CSV_FILE}")


def print_summary():
    if not os.path.exists(CSV_FILE):
        return
    with open(CSV_FILE, "r") as f:
        trials = list(csv.DictReader(f))
    if not trials:
        return

    print(f"\n{'='*50}")
    print(f"SUMMARY — {len(trials)} trials recorded")
    print("="*50)
    for state in STATES.values():
        state_trials = [t for t in trials if t["state_label"] == state]
        if not state_trials:
            continue
        successes = sum(1 for t in state_trials if t["success"] == "True")
        rate = successes / len(state_trials) * 100
        times = [float(t["completion_time_s"]) for t in state_trials if t["success"] == "True"]
        avg_time = round(sum(times) / len(times), 2) if times else "N/A"
        print(f"{state}: {successes}/{len(state_trials)} ({rate:.0f}%) | avg time: {avg_time}s")


def main():
    print("Lipstick Picking Robot — Evaluation Recorder")
    init_csv()
    while True:
        print_summary()
        trial_num = get_trial_count() + 1
        state_label = select_state()
        data = run_trial(trial_num, state_label)
        save_trial(data)
        if input("\nRun another trial? (y/n): ").strip().lower() != "y":
            break
    print("\nDone! Results saved to", CSV_FILE)


if __name__ == "__main__":
    main()
