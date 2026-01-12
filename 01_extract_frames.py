#!/usr/bin/env python3
"""Extract frames from a video file using OpenCV."""

import argparse
import sys
from pathlib import Path
from typing import Optional

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
    parser.add_argument(
        "--every",
        type=int,
        default=15,
        help="Sample every Nth frame",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=None,
        help="Start frame index (0-based)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="End frame index (exclusive)",
    )
    return parser.parse_args()


def extract_frames(
    video_path: Path,
    out_dir: Path,
    every: int = 15,
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> int:
    """Extract frames from video with sampling.

    Args:
        video_path: Path to input video file
        out_dir: Directory to save extracted frames
        every: Sample every Nth frame
        start: Start frame index (0-based, inclusive)
        end: End frame index (exclusive)

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
    start_frame = start if start is not None else 0
    end_frame = end if end is not None else total_frames

    print(f"Video has {total_frames} frames")
    print(f"Extracting frames {start_frame} to {end_frame}, every {every} frames")

    frame_idx = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx >= end_frame:
            break

        if frame_idx >= start_frame and (frame_idx - start_frame) % every == 0:
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
    extract_frames(args.video, args.out_dir, args.every, args.start, args.end)


if __name__ == "__main__":
    main()
