import argparse
import random
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--val_ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)

    image_train = dst / "images" / "train"
    image_val = dst / "images" / "val"
    label_train = dst / "labels" / "train"
    label_val = dst / "labels" / "val"

    for p in [image_train, image_val, label_train, label_val]:
        p.mkdir(parents=True, exist_ok=True)

    pairs = []

    for txt in sorted(src.glob("*.txt")):
        jpg = txt.with_suffix(".jpg")
        if jpg.exists() and txt.stat().st_size > 0:
            pairs.append((jpg, txt))

    if not pairs:
        raise RuntimeError("No valid image-label pairs found.")

    random.seed(args.seed)
    random.shuffle(pairs)

    val_count = int(len(pairs) * args.val_ratio)
    val_pairs = pairs[:val_count]
    train_pairs = pairs[val_count:]

    def copy_pairs(pairs, image_dir, label_dir):
        for jpg, txt in pairs:
            shutil.copy2(jpg, image_dir / jpg.name)
            shutil.copy2(txt, label_dir / txt.name)

    copy_pairs(train_pairs, image_train, label_train)
    copy_pairs(val_pairs, image_val, label_val)

    data_yaml = dst / "data.yaml"
    data_yaml.write_text(
        f"""path: {dst}
train: images/train
val: images/val

names:
  0: black_lipstick
"""
    )

    print(f"Total labeled pairs: {len(pairs)}")
    print(f"Train: {len(train_pairs)}")
    print(f"Val: {len(val_pairs)}")
    print(f"Wrote: {data_yaml}")


if __name__ == "__main__":
    main()
