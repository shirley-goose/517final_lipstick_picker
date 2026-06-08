import argparse
import hashlib
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()

    dataset = Path(args.dataset)
    videos = sorted(dataset.rglob("*.mp4"))

    print(f"Found {len(videos)} videos\n")

    for video_path in videos:
        video_hash = hashlib.md5(str(video_path).encode()).hexdigest()[:8]
        print(f"{video_hash}  {video_path}")


if __name__ == "__main__":
    main()
