#!/usr/bin/env python3
"""Generate colored point cloud from frames and depth maps."""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate colored point cloud from frames and depth maps.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--frames_dir",
        type=Path,
        required=True,
        help="Directory containing input frames",
    )
    parser.add_argument(
        "--depth_dir",
        type=Path,
        required=True,
        help="Directory containing depth maps (.npy files)",
    )
    parser.add_argument(
        "--out_dir",
        type=Path,
        required=True,
        help="Output directory for point cloud",
    )
    return parser.parse_args()


def find_pairs(frames_dir: Path, depth_dir: Path) -> Tuple[List[Tuple[Path, Path]], List[str]]:
    """Find matching frame/depth pairs by basename.

    Args:
        frames_dir: Directory containing frames
        depth_dir: Directory containing depth maps

    Returns:
        Tuple of (list of (frame_path, depth_path) pairs, list of missing basenames)
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

    frames = {
        f.stem: f for f in frames_dir.iterdir()
        if f.suffix.lower() in image_extensions
    }

    depth_files = {
        f.stem: f for f in depth_dir.iterdir()
        if f.suffix == ".npy"
    }

    pairs = []
    missing = []

    for basename in sorted(frames.keys()):
        if basename in depth_files:
            pairs.append((frames[basename], depth_files[basename]))
        else:
            missing.append(basename)

    return pairs, missing


def validate_directories(frames_dir: Path, depth_dir: Path) -> None:
    """Validate input directories exist.

    Args:
        frames_dir: Directory containing frames
        depth_dir: Directory containing depth maps
    """
    if not frames_dir.exists():
        print(f"Error: Frames directory not found: {frames_dir}", file=sys.stderr)
        sys.exit(1)

    if not depth_dir.exists():
        print(f"Error: Depth directory not found: {depth_dir}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    args = parse_args()
    validate_directories(args.frames_dir, args.depth_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    pairs, missing = find_pairs(args.frames_dir, args.depth_dir)

    print(f"Found {len(pairs)} frame/depth pairs")

    if missing:
        print(f"Warning: {len(missing)} frames without matching depth maps:")
        for basename in missing[:5]:
            print(f"  - {basename}")
        if len(missing) > 5:
            print(f"  ... and {len(missing) - 5} more")

    if not pairs:
        print("Error: No matching frame/depth pairs found", file=sys.stderr)
        sys.exit(1)

    print(f"Output directory: {args.out_dir}")


if __name__ == "__main__":
    main()
