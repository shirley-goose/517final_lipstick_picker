#!/usr/bin/env python3
"""
Merge new 0520/0521/0522 batch datasets and combine with all_merged_365.

Step 1: Merge each day's 20 batches into one daily dataset (in local/)
Step 2: Merge all three daily datasets + all_merged_365 → all_merged_665
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/techin517/lerobot/src")

from lerobot.datasets.aggregate import aggregate_datasets
from lerobot.utils.utils import init_logging

init_logging()
log = logging.getLogger(__name__)

DATASETS_DIR = Path("/home/ubuntu/techin517/datasets")
LOCAL_DIR = DATASETS_DIR / "local"

# ── 0520 batches (batch1–batch20) ────────────────────────────────────────────
BATCH_0520 = [
    DATASETS_DIR / f"lipstick_picking0520_batch{i}"
    for i in range(1, 21)
]

# ── 0521 batches (batch1–batch20) ────────────────────────────────────────────
BATCH_0521 = [
    DATASETS_DIR / f"lipstick_picking0521_batch{i}"
    for i in range(1, 21)
]

# ── 0522 batches: batch1–9 use "batch", batch10–20 use "batc" (typo) ─────────
BATCH_0522 = [DATASETS_DIR / f"lipstick_picking0522_batch{i}" for i in range(1, 10)] + \
             [DATASETS_DIR / f"lipstick_picking0522_batc{i}" for i in range(10, 21)]


def merge_day(batch_paths: list[Path], day_name: str, repo_prefix: str) -> Path:
    """Merge 20 per-batch datasets into one daily dataset."""
    dst_root = LOCAL_DIR / day_name
    if dst_root.exists():
        log.warning(f"Skipping {day_name} — already exists at {dst_root}")
        return dst_root

    # Verify all source directories exist
    missing = [p for p in batch_paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing source dirs: {missing}")

    log.info(f"Merging {len(batch_paths)} batches → {dst_root}")
    repo_ids = [f"local/{repo_prefix}_{p.name}" for p in batch_paths]
    roots = batch_paths

    aggregate_datasets(
        repo_ids=repo_ids,
        aggr_repo_id=f"local/{day_name}",
        roots=roots,
        aggr_root=dst_root,
    )
    return dst_root


def main():
    # ── Step 1: merge each day ────────────────────────────────────────────────
    dst_0520 = merge_day(BATCH_0520, "lipstick_picking0520_merged_batch1_20", "0520")
    dst_0521 = merge_day(BATCH_0521, "lipstick_picking0521_merged_batch1_20", "0521")
    dst_0522 = merge_day(BATCH_0522, "lipstick_picking0522_merged_batch1_20", "0522")

    # ── Step 2: merge all three days + existing 365 → 665 ────────────────────
    dst_665 = LOCAL_DIR / "lipstick_picking_all_merged_665"
    if dst_665.exists():
        log.warning(f"Skipping all_merged_665 — already exists at {dst_665}")
    else:
        src_365 = LOCAL_DIR / "lipstick_picking_all_merged_365"

        all_roots = [src_365, dst_0520, dst_0521, dst_0522]
        all_repo_ids = [
            "local/lipstick_picking_all_merged_365",
            "local/lipstick_picking0520_merged_batch1_20",
            "local/lipstick_picking0521_merged_batch1_20",
            "local/lipstick_picking0522_merged_batch1_20",
        ]

        log.info(f"Merging 365 + three day-merged → {dst_665}")
        aggregate_datasets(
            repo_ids=all_repo_ids,
            aggr_repo_id="local/lipstick_picking_all_merged_665",
            roots=all_roots,
            aggr_root=dst_665,
        )

    log.info(f"Done. Final merged dataset at: {dst_665}")
    print(f"\n✓ Merged 665 dataset ready at:\n  {dst_665}")
    print("\nNext steps:")
    print("  1. Run make_yolo_highlight_dataset.py (see below)")
    print("  2. Extract frames + retrain YOLO")


if __name__ == "__main__":
    main()
