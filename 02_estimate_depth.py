#!/usr/bin/env python3
"""Generate depth maps from frames using Depth-Anything model."""

import argparse
import sys
from pathlib import Path
from typing import List

from PIL import Image
from transformers import pipeline


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate depth maps from image frames.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--frames_dir",
        type=Path,
        required=True,
        help="Directory containing input frames",
    )
    parser.add_argument(
        "--out_dir",
        type=Path,
        required=True,
        help="Output directory for depth maps",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="LiheYoung/depth-anything-small-hf",
        help="Model ID for depth estimation",
    )
    return parser.parse_args()


def validate_frames_dir(frames_dir: Path) -> List[Path]:
    """Validate frames directory and return list of image files.

    Args:
        frames_dir: Directory containing frames

    Returns:
        List of image file paths

    Raises:
        SystemExit: If directory is missing or empty
    """
    if not frames_dir.exists():
        print(f"Error: Frames directory not found: {frames_dir}", file=sys.stderr)
        sys.exit(1)

    if not frames_dir.is_dir():
        print(f"Error: Not a directory: {frames_dir}", file=sys.stderr)
        sys.exit(1)

    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    frames = sorted(
        f for f in frames_dir.iterdir()
        if f.suffix.lower() in image_extensions
    )

    if not frames:
        print(f"Error: No image files found in: {frames_dir}", file=sys.stderr)
        print("Supported formats: JPG, JPEG, PNG, BMP, TIFF", file=sys.stderr)
        sys.exit(1)

    return frames


def load_model(model_id: str):
    """Load depth estimation model via transformers pipeline.

    Args:
        model_id: HuggingFace model ID

    Returns:
        Depth estimation pipeline
    """
    print(f"Loading model: {model_id}")
    pipe = pipeline(task="depth-estimation", model=model_id)
    print("Model loaded successfully")
    return pipe


def process_frame(pipe, frame_path: Path) -> Image.Image:
    """Process a single frame and return depth map.

    Args:
        pipe: Depth estimation pipeline
        frame_path: Path to input frame

    Returns:
        Depth map as PIL Image
    """
    image = Image.open(frame_path)
    result = pipe(image)
    return result["depth"]


def main() -> None:
    """Main entry point."""
    args = parse_args()
    frames = validate_frames_dir(args.frames_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Found {len(frames)} frames in {args.frames_dir}")
    print(f"Output directory: {args.out_dir}")

    pipe = load_model(args.model)

    # Process first frame to verify model works
    if frames:
        print(f"Testing with first frame: {frames[0].name}")
        depth = process_frame(pipe, frames[0])
        print(f"Depth map size: {depth.size}")
        print("Model verification complete")


if __name__ == "__main__":
    main()
