import argparse
import re
import shutil
from pathlib import Path


HASH_RE = re.compile(r"_([0-9a-f]{8})_f")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--hashes", required=True)
    parser.add_argument("--num", type=int, default=1000)
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    dst.mkdir(parents=True, exist_ok=True)

    selected_hashes = set(h.strip() for h in args.hashes.split(",") if h.strip())

    images = []
    for img_path in sorted(src.glob("*.jpg")):
        match = HASH_RE.search(img_path.name)
        if not match:
            continue

        h = match.group(1)
        if h in selected_hashes:
            images.append(img_path)

    print(f"Selected hashes: {sorted(selected_hashes)}")
    print(f"Found {len(images)} matching images")

    if len(images) == 0:
        raise RuntimeError("No matching images found. Check your hash values.")

    if args.num >= len(images):
        selected = images
    else:
        step = len(images) / args.num
        selected = [images[int(i * step)] for i in range(args.num)]

    for img_path in selected:
        shutil.copy2(img_path, dst / img_path.name)

    print(f"Copied {len(selected)} images to {dst}")


if __name__ == "__main__":
    main()
