# Development Guide — vid-to-3d

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Running each stage

### 1) Extract frames

```bash
python 01_extract_frames.py --video input/room.mp4 --out_dir frames --every 15 --width 640 --height 480
```

### 2) Estimate depth

```bash
python 02_estimate_depth.py --frames_dir frames --out_dir depth --device auto
```

Tip: keep `--max-frames 10` during iteration so you’re not waiting on the full video.

### 3) Generate point cloud

```bash
python 03_generate_pointcloud.py --frames_dir frames --depth_dir depth --out_ply output/point_cloud.ply
```

### 4) Run the viewer

```bash
python -m http.server 8000
```

Open `http://localhost:8000/viewer.html`.

## Debugging and sanity checks

- Always inspect `depth/*_viz.png` before generating a point cloud.
- If the point cloud is “inside out” or mirrored:
  - confirm the sign conventions in the y-axis mapping
  - confirm cx/cy and image size are consistent
- If output is enormous:
  - increase frame stride
  - increase pixel stride
  - add voxel downsample

## Suggested checks (guardrails)

- Syntax check:
  - `python -m compileall .`

Optional additions as the repo matures:
- `ruff check .`
- `pytest -q`

## Working with agents (Ralph-style)

- Source of truth: `PRD.md`
- Session memory: `progress.txt` (keep concise)
- Commit after each PRD item so the git history becomes usable “memory”.
