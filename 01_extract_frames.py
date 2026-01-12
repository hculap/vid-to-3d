#!/usr/bin/env python3
"""Extract frames from a video file using OpenCV."""

import argparse
import sys
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract frames from a video file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--video",
        type=Path,
        required=True,
        help="Path to input video file",
    )
    parser.add_argument(
        "--out_dir",
        type=Path,
        required=True,
        help="Output directory for extracted frames",
    )
    return parser.parse_args()


def extract_frames(video_path: Path, out_dir: Path) -> int:
    """Extract all frames from video and save as JPG files.

    Args:
        video_path: Path to input video file
        out_dir: Directory to save extracted frames

    Returns:
        Number of frames extracted
    """
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Could not open video: {video_path}", file=sys.stderr)
        sys.exit(1)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video has {total_frames} frames")

    frame_idx = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        out_path = out_dir / f"frame_{frame_idx:06d}.jpg"
        cv2.imwrite(str(out_path), frame)
        saved_count += 1
        frame_idx += 1

    cap.release()
    print(f"Extracted {saved_count} frames to {out_dir}")
    return saved_count


def main() -> None:
    """Main entry point."""
    args = parse_args()
    extract_frames(args.video, args.out_dir)


if __name__ == "__main__":
    main()
