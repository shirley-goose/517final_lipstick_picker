import argparse
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--num", type=int, default=1000)
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    dst.mkdir(parents=True, exist_ok=True)

    images = sorted(src.glob("*.jpg"))

    if len(images) == 0:
        raise RuntimeError(f"No jpg images found in {src}")

    if args.num >= len(images):
        selected = images
    else:
        step = len(images) / args.num
        selected = [images[int(i * step)] for i in range(args.num)]

    for image_path in selected:
        shutil.copy2(image_path, dst / image_path.name)

    print(f"Total source images: {len(images)}")
    print(f"Copied {len(selected)} images to {dst}")


if __name__ == "__main__":
    main()
