import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

import cv2
from ultralytics import YOLO


def run_cmd(cmd):
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        print("Command failed:")
        print(" ".join(cmd))
        print(result.stderr)
        raise RuntimeError("Command failed")
    return result.stdout.strip()


def get_fps(video_path):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=r_frame_rate",
        "-of",
        "default=nokey=1:noprint_wrappers=1",
        str(video_path),
    ]
    fps = run_cmd(cmd)
    if not fps:
        return "30"
    return fps


def extract_frames(video_path, frames_dir):
    frames_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-hwaccel",
        "none",
        "-i",
        str(video_path),
        "-q:v",
        "2",
        str(frames_dir / "frame_%06d.jpg"),
    ]
    run_cmd(cmd)


def encode_video(frames_dir, output_path, fps):
    temp_output = output_path.with_suffix(".tmp.mp4")

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-y",
        "-framerate",
        fps,
        "-start_number",
        "1",
        "-i",
        str(frames_dir / "frame_%06d.jpg"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        str(temp_output),
    ]

    run_cmd(cmd)
    shutil.move(str(temp_output), str(output_path))


def find_target_box(result, target_class_name, conf_thres):
    names = result.names
    target_ids = [class_id for class_id, name in names.items() if name == target_class_name]

    if not target_ids:
        raise ValueError(f"Target class {target_class_name} not found. Model names: {names}")

    if result.boxes is None or len(result.boxes) == 0:
        return None

    boxes = result.boxes.xyxy.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy().astype(int)
    confs = result.boxes.conf.cpu().numpy()

    candidates = []

    for box, cls_id, conf in zip(boxes, classes, confs):
        if cls_id in target_ids and conf >= conf_thres:
            candidates.append((box, conf))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[1], reverse=True)
    return candidates[0]


def draw_highlight(frame, box, conf):
    x1, y1, x2, y2 = [int(v) for v in box]

    h, w = frame.shape[:2]
    x1 = max(0, min(w - 1, x1))
    x2 = max(0, min(w - 1, x2))
    y1 = max(0, min(h - 1, y1))
    y2 = max(0, min(h - 1, y2))

    # Green bbox for the target black lipstick.
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

    # Center point.
    cx = int((x1 + x2) / 2)
    cy = int((y1 + y2) / 2)
    cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

    # Small label.
    label = f"black_lipstick {conf:.2f}"
    cv2.putText(
        frame,
        label,
        (x1, max(20, y1 - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    return frame


def process_video(video_path, model, target_class_name, conf_thres, use_last_box):
    fps = get_fps(video_path)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        raw_dir = tmp / "raw"
        out_dir = tmp / "out"
        raw_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        extract_frames(video_path, raw_dir)

        frames = sorted(raw_dir.glob("frame_*.jpg"))
        if not frames:
            print(f"No frames extracted from {video_path}")
            return

        last_box = None
        last_conf = 0.0
        detected = 0

        for frame_path in frames:
            frame = cv2.imread(str(frame_path))
            if frame is None:
                continue

            result = model.predict(
                frame,
                imgsz=640,
                conf=conf_thres,
                verbose=False,
            )[0]

            found = find_target_box(result, target_class_name, conf_thres)

            if found is not None:
                box, conf = found
                last_box = box
                last_conf = conf
                detected += 1
                frame = draw_highlight(frame, box, conf)
            elif use_last_box and last_box is not None:
                frame = draw_highlight(frame, last_box, last_conf)

            cv2.imwrite(str(out_dir / frame_path.name), frame)

        encode_video(out_dir, video_path, fps)

        print(
            f"Processed {video_path.name}: "
            f"detected {detected}/{len(frames)} frames = {detected / len(frames):.1%}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--target_class", default="black_lipstick")
    parser.add_argument("--conf", type=float, default=0.20)
    parser.add_argument(
        "--camera_keywords",
        default="observation.images.realsense,observation.images.right_wrist",
    )
    parser.add_argument("--use_last_box", action="store_true")
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)

    if dst.exists():
        raise FileExistsError(f"Destination already exists: {dst}")

    print(f"Copying dataset:\n  from: {src}\n  to:   {dst}")
    shutil.copytree(src, dst)

    model = YOLO(args.weights)

    camera_keywords = [x.strip() for x in args.camera_keywords.split(",") if x.strip()]

    videos = sorted(dst.rglob("*.mp4"))
    selected_videos = [
        v for v in videos
        if any(keyword in str(v) for keyword in camera_keywords)
    ]

    print(f"Total videos found: {len(videos)}")
    print(f"Videos selected for YOLO highlight: {len(selected_videos)}")

    for video in selected_videos:
        print(f"\nProcessing: {video}")
        process_video(
            video_path=video,
            model=model,
            target_class_name=args.target_class,
            conf_thres=args.conf,
            use_last_box=args.use_last_box,
        )

    print("\nDone.")
    print(f"YOLO-highlight dataset saved to: {dst}")


if __name__ == "__main__":
    main()
