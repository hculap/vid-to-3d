# Fix Plan - Video to 3D Pipeline

## Frame Extraction (01_extract_frames.py)

- [ ] US-001: Create frame extraction CLI with argparse (--video, --out_dir, --help)
- [ ] US-002: Add frame sampling (--every N, --start, --end flags)
- [ ] US-003: Add resize and quality options (--width, --height, --quality flags)

## Depth Estimation (02_estimate_depth.py)

- [ ] US-004: Create depth estimation CLI with argparse (--frames_dir, --out_dir, --help)
- [ ] US-005: Load Depth-Anything-Small model via transformers pipeline
- [ ] US-006: Add device selection (--device auto|mps|cuda|cpu)
- [ ] US-007: Save depth maps as .npy + visualization .png
- [ ] US-008: Add batch processing with tqdm progress bar and --max-frames

## Point Cloud Generation (03_generate_pointcloud.py)

- [ ] US-009: Create point cloud CLI with argparse (--frames_dir, --depth_dir, --out_dir)
- [ ] US-010: Implement camera intrinsics (--fov_deg, --fx, --fy, --cx, --cy)
- [ ] US-011: Generate colored point cloud from single frame using pinhole model
- [ ] US-012: Add subsampling controls (--pixel_stride, --max_points_per_frame)
- [ ] US-013: Merge multiple frames into one point cloud

## Three.js Viewer (viewer.html)

- [ ] US-014: Create viewer.html with Three.js PLYLoader from CDN
- [ ] US-015: Add PointerLockControls for WASD + mouse look navigation
- [ ] US-016: Add UI overlay with controls help, point size slider, reset button

## Pipeline Runner

- [ ] US-017: Create run_pipeline.sh that runs 01→02→03 scripts in sequence
