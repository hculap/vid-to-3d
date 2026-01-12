# vid-to-3d — Video to 3D Room (Point Cloud)

A local prototype pipeline that turns a room walkthrough video into a colored point cloud (`.ply`) and a browser-based walkthrough viewer (`viewer.html`) built on Three.js.

This repo is intentionally “small pieces, composable scripts”: each stage writes artifacts to disk so you can inspect and debug intermediate results.

## Outputs

Given an input video, the pipeline produces:

- `frames/frame_000000.jpg` … extracted RGB frames
- `depth/frame_000000.npy` … depth map aligned to the frame (float32)
- `depth/frame_000000_viz.png` … depth visualization for sanity checks
- `output/point_cloud.ply` … combined colored point cloud
- `viewer.html` … Three.js viewer for navigation

## Requirements

- Python 3.10+ recommended
- macOS (Apple Silicon) via PyTorch MPS, or CUDA, or CPU
- Disk space: frames + depth maps can be large (GBs for longer videos)

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Quickstart (happy path)

1) Put a video at `input/room.mp4`.

2) Extract frames:

```bash
python 01_extract_frames.py --video input/room.mp4 --out_dir frames --every 15 --width 640 --height 480
```

3) Estimate depth:

```bash
python 02_estimate_depth.py \
  --frames_dir frames \
  --out_dir depth \
  --model depth-anything/Depth-Anything-V2-Metric-Indoor-Small-hf \
  --device auto
```

4) Generate point cloud:

```bash
python 03_generate_pointcloud.py \
  --frames_dir frames \
  --depth_dir depth \
  --out_ply output/point_cloud.ply \
  --fov_deg 60 \
  --pixel_stride 2
```

5) View it:

Browsers typically block loading files from `file://`. Serve the repo directory:

```bash
python -m http.server 8000
```

Open:

```text
http://localhost:8000/viewer.html
```

Controls:
- Click to lock pointer
- WASD to move
- Mouse to look
- ESC to unlock

## Recommended capture tips

This pipeline works better when the input video is “depth-friendly”:

- Move slowly; avoid motion blur.
- Keep exposure stable (avoid large auto-exposure jumps).
- Prefer scenes with texture (blank walls are hard).
- For MVP fusion, a slow rotation from one spot tends to look better than walking.

## Known limitations (MVP)

- Monocular depth can be scale-ambiguous. Metric depth models help, but results can drift.
- Without camera pose estimation, merging multiple frames may cause ghosting/duplicates if the camera moves significantly.
- The viewer renders a point cloud (no mesh, no collision, no physics).

## Project structure

```text
vid-to-3d/
├── 01_extract_frames.py
├── 02_estimate_depth.py
├── 03_generate_pointcloud.py
├── viewer.html
├── requirements.txt
├── PRD.md
├── AGENTS.md
├── ARCHITECTURE.md
├── DEVELOPMENT.md
├── input/          # put videos here (ignored by git)
├── frames/         # generated
├── depth/          # generated depth maps
└── output/         # generated PLY
```

## Docs

- `PRD.md` — backlog + acceptance criteria
- `ARCHITECTURE.md` — pipeline design notes
- `DEVELOPMENT.md` — dev workflow, debugging, checks
- `AGENTS.md` — guidance for coding agents / contributors
