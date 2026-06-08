import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--every_n", type=int, default=20)
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found. Please run: sudo apt install -y ffmpeg")

    dataset = Path(args.dataset)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    videos = list(dataset.rglob("*.mp4"))
    print(f"Found {len(videos)} videos")

    for video_path in videos:
        video_hash = hashlib.md5(str(video_path).encode()).hexdigest()[:8]
        output_pattern = out_dir / f"{video_path.stem}_{video_hash}_f%06d.jpg"

        # Extract every N frames.
        # The comma in mod(n\,N) must be escaped for ffmpeg filter syntax.
        vf = f"select=not(mod(n\\,{args.every_n}))"

        cmd = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-hwaccel",
            "none",
            "-i",
            str(video_path),
            "-vf",
            vf,
            "-vsync",
            "vfr",
            "-q:v",
            "2",
            str(output_pattern),
        ]

        print(f"Extracting from: {video_path}")
        result = subprocess.run(cmd, text=True, capture_output=True)

        if result.returncode != 0:
            print(f"Failed: {video_path}")
            print(result.stderr)

    saved = len(list(out_dir.glob("*.jpg")))
    print(f"Saved {saved} frames to {out_dir}")


if __name__ == "__main__":
    main()