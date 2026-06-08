#!/usr/bin/env python3
"""
Merge YOLO-highlight datasets into one final training dataset.

Sources:
1. lipstick_picking_all_merged_365_yolo_highlight
2. lipstick_picking0520_merged_batch1_20_yolo_highlight_conf075
3. lipstick_picking0521_merged_batch1_20_yolo_highlight_conf075
4. lipstick_picking0522_merged_batch1_20_yolo_highlight_conf075

Output:
lipstick_picking_yolo_highlight_final
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

SOURCE_NAMES = [
    "lipstick_picking_all_merged_365_yolo_highlight",
    "lipstick_picking0520_merged_batch1_20_yolo_highlight_conf075",
    "lipstick_picking0521_merged_batch1_20_yolo_highlight_conf075",
    "lipstick_picking0522_merged_batch1_20_yolo_highlight_conf075",
]

OUTPUT_NAME = "lipstick_picking_yolo_highlight_final"


def main():
    roots = [LOCAL_DIR / name for name in SOURCE_NAMES]
    repo_ids = [f"local/{name}" for name in SOURCE_NAMES]

    dst_root = LOCAL_DIR / OUTPUT_NAME

    missing = [p for p in roots if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing source datasets: {missing}")

    if dst_root.exists():
        raise FileExistsError(
            f"Output dataset already exists: {dst_root}\n"
            f"If you want to recreate it, run:\n"
            f"rm -rf {dst_root}"
        )

    log.info("Merging YOLO-highlight datasets:")
    for root in roots:
        log.info(f"  {root}")

    log.info(f"Output dataset: {dst_root}")

    aggregate_datasets(
        repo_ids=repo_ids,
        aggr_repo_id=f"local/{OUTPUT_NAME}",
        roots=roots,
        aggr_root=dst_root,
    )

    log.info(f"Done. Final YOLO-highlight dataset at: {dst_root}")
    print(f"\n✓ Final YOLO-highlight dataset ready at:\n  {dst_root}")


if __name__ == "__main__":
    main()