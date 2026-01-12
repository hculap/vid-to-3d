#!/usr/bin/env python3
"""Generate colored point cloud from frames and depth maps."""

import argparse
import math
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import open3d as o3d
from PIL import Image


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
    parser.add_argument(
        "--fov_deg",
        type=float,
        default=60.0,
        help="Field of view in degrees (for computing focal length)",
    )
    parser.add_argument(
        "--fx",
        type=float,
        default=None,
        help="Explicit focal length x (overrides --fov_deg)",
    )
    parser.add_argument(
        "--fy",
        type=float,
        default=None,
        help="Explicit focal length y (overrides --fov_deg)",
    )
    parser.add_argument(
        "--cx",
        type=float,
        default=None,
        help="Principal point x (default: image width / 2)",
    )
    parser.add_argument(
        "--cy",
        type=float,
        default=None,
        help="Principal point y (default: image height / 2)",
    )
    parser.add_argument(
        "--pixel_stride",
        type=int,
        default=2,
        help="Sample every Nth pixel in each dimension",
    )
    parser.add_argument(
        "--max_points_per_frame",
        type=int,
        default=None,
        help="Maximum points to keep per frame (random subsample)",
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


def compute_intrinsics(
    width: int,
    height: int,
    fov_deg: float,
    fx: Optional[float] = None,
    fy: Optional[float] = None,
    cx: Optional[float] = None,
    cy: Optional[float] = None,
) -> Tuple[float, float, float, float]:
    """Compute camera intrinsics from FOV or explicit values.

    Args:
        width: Image width
        height: Image height
        fov_deg: Field of view in degrees
        fx: Explicit focal length x (optional)
        fy: Explicit focal length y (optional)
        cx: Principal point x (optional)
        cy: Principal point y (optional)

    Returns:
        Tuple of (fx, fy, cx, cy)
    """
    if fx is None:
        fx = width / (2 * math.tan(math.radians(fov_deg) / 2))
    if fy is None:
        fy = fx
    if cx is None:
        cx = width / 2.0
    if cy is None:
        cy = height / 2.0

    return fx, fy, cx, cy


def depth_to_pointcloud(
    rgb_path: Path,
    depth_path: Path,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    pixel_stride: int = 2,
    max_points: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Convert a single frame + depth to 3D points with colors.

    Uses the pinhole camera model to project depth pixels to 3D:
        X = (u - cx) * Z / fx
        Y = (v - cy) * Z / fy
        Z = depth

    Args:
        rgb_path: Path to RGB image
        depth_path: Path to depth .npy file
        fx, fy: Focal lengths
        cx, cy: Principal point
        pixel_stride: Sample every Nth pixel in each dimension
        max_points: Maximum number of points to return (random subsample)

    Returns:
        Tuple of (points [N, 3], colors [N, 3] normalized 0-1)
    """
    rgb = np.array(Image.open(rgb_path))
    depth = np.load(depth_path)

    # Resize RGB to match depth if needed
    if rgb.shape[:2] != depth.shape:
        rgb_pil = Image.open(rgb_path).resize((depth.shape[1], depth.shape[0]))
        rgb = np.array(rgb_pil)

    height, width = depth.shape

    # Apply pixel stride subsampling
    u, v = np.meshgrid(
        np.arange(0, width, pixel_stride),
        np.arange(0, height, pixel_stride)
    )
    depth_sub = depth[::pixel_stride, ::pixel_stride]
    rgb_sub = rgb[::pixel_stride, ::pixel_stride]

    z = depth_sub.flatten()
    x = ((u.flatten() - cx) * z) / fx
    y = ((v.flatten() - cy) * z) / fy

    points = np.stack([x, -y, -z], axis=-1)  # Flip Y and Z for standard 3D coords

    colors = rgb_sub.reshape(-1, 3) / 255.0

    # Filter out invalid depth (zeros or too far)
    valid = z > 0
    points = points[valid]
    colors = colors[valid]

    # Random subsample if max_points specified
    if max_points is not None and len(points) > max_points:
        indices = np.random.choice(len(points), max_points, replace=False)
        points = points[indices]
        colors = colors[indices]

    return points, colors


def save_ply(points: np.ndarray, colors: np.ndarray, out_path: Path) -> None:
    """Save point cloud as PLY file.

    Args:
        points: [N, 3] array of xyz positions
        colors: [N, 3] array of RGB colors (0-1)
        out_path: Output PLY file path
    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    o3d.io.write_point_cloud(str(out_path), pcd)


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

    # Process first frame to get dimensions for intrinsics
    rgb_path, depth_path = pairs[0]
    depth = np.load(depth_path)
    height, width = depth.shape

    fx, fy, cx, cy = compute_intrinsics(
        width, height, args.fov_deg, args.fx, args.fy, args.cx, args.cy
    )
    print(f"Camera intrinsics: fx={fx:.2f}, fy={fy:.2f}, cx={cx:.2f}, cy={cy:.2f}")

    # Generate point cloud from single frame
    print(f"Processing: {rgb_path.name}")
    print(f"Subsampling: pixel_stride={args.pixel_stride}, max_points_per_frame={args.max_points_per_frame}")
    points, colors = depth_to_pointcloud(
        rgb_path, depth_path, fx, fy, cx, cy,
        args.pixel_stride, args.max_points_per_frame
    )
    print(f"Generated {len(points)} points")

    out_path = args.out_dir / "point_cloud.ply"
    save_ply(points, colors, out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
