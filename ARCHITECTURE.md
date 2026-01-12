# Architecture — vid-to-3d

## High-level pipeline

```text
video.(mp4|mov)
  -> 01_extract_frames.py
      -> frames/frame_000000.jpg ...
  -> 02_estimate_depth.py
      -> depth/frame_000000.npy
      -> depth/frame_000000_viz.png
  -> 03_generate_pointcloud.py
      -> output/point_cloud.ply
  -> viewer.html (Three.js)
      -> walkable point cloud
```

Each stage produces disk artifacts to keep the system debuggable and restartable.

## Contracts between stages

### Naming convention

All stages must agree on a shared basename:

- Frame: `frames/frame_000123.jpg`
- Depth: `depth/frame_000123.npy`
- Viz:   `depth/frame_000123_viz.png`

This avoids fragile “sort order” coupling.

### Manifests

Two optional JSON manifests provide “paper trail” metadata:

- `frames/manifest.json`: video source, fps, sampling stride, resize, list of frames with timestamps
- `depth/manifest.json`: model id, device, dtype, list of depth outputs

## Depth estimation

### Model family

Depth Anything models can be used via Transformers. The model id must be configurable via CLI.

Recommended defaults for indoor scenes:
- `depth-anything/Depth-Anything-V2-Metric-Indoor-Small-hf` (metric indoor)
- or `depth-anything/Depth-Anything-V2-Small-hf` (relative depth)

### Output format

- `.npy` should store float32 depth aligned to the RGB frame’s resolution.
- `_viz.png` is a normalized visualization for humans; it is not used downstream.

## Point cloud generation

### Pinhole projection

Given pixel coordinates (u, v), depth d, and intrinsics (fx, fy, cx, cy):

- x = (u - cx) * d / fx
- y = -(v - cy) * d / fy   (negative to make +Y up in a typical viewer)
- z = d

Notes:
- Depth scale depends on the depth model. With relative depth you can still get plausible geometry, but scale will be arbitrary.
- Intrinsics are approximated from FOV if not provided.

### Colors

Per-point RGB is sampled from the original frame at (u, v).

### Fusion (multi-frame)

MVP fusion:
- Concatenate points from multiple frames into one PLY.
- This is only visually stable when camera motion is limited.

Stretch fusion:
- Estimate per-frame poses (VO) or align with ICP, then transform each frame’s point cloud into a shared world frame.

### Output format

`output/point_cloud.ply` should contain:
- vertex positions (x, y, z)
- vertex colors (r, g, b)

## Viewer (Three.js)

- Loads the PLY via PLYLoader.
- Renders as points with adjustable point size.
- Uses pointer lock first-person controls for navigation (WASD + mouse).
- Must work when served via a local static server (not file://).

## Performance levers

- Frame sampling (`--every N`) during extraction
- Resize (e.g., 640x480)
- Pixel subsampling (`--pixel_stride`)
- `--max_points_per_frame`
- Voxel downsampling (`--voxel_size`) when Open3D is available
