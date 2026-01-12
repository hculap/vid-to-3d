# Video to 3D Room Pipeline

Build a pipeline that converts a video of a room into a walkable 3D point cloud scene viewable in Three.js.

## Context

- Test video: `input/room.MOV` (114MB)
- Target: PoC quality, M1 Mac with MPS acceleration
- Dependencies already installed: torch, opencv, open3d, transformers, numpy, pillow, tqdm

## Task

Implement the pipeline by completing tasks in `@fix_plan.md` in order.

For each task:
1. Read the task requirements
2. Implement the code
3. Verify acceptance criteria (run --help, typecheck, smoke test)
4. Commit with format: `US-XXX: short description`
5. Mark task complete in `@fix_plan.md`
6. Update `progress.txt` with what was done

## Architecture

```
input/room.MOV → [01_extract_frames.py] → frames/
frames/ → [02_estimate_depth.py] → depth/
frames/ + depth/ → [03_generate_pointcloud.py] → output/point_cloud.ply
output/point_cloud.ply → [viewer.html] → 3D walkthrough
```

## Scripts to Create

1. `01_extract_frames.py` - Extract frames from video (OpenCV)
2. `02_estimate_depth.py` - Generate depth maps (Depth-Anything-Small)
3. `03_generate_pointcloud.py` - Create colored point cloud (Open3D)
4. `viewer.html` - Three.js first-person viewer
5. `run_pipeline.sh` - One-command runner

## Code Standards

- Python: argparse CLI with --help
- snake_case naming
- Clear error messages
- Small focused scripts

## Verification

After all tasks complete:
```bash
./run_pipeline.sh input/room.MOV
python -m http.server 8000
# Open http://localhost:8000/viewer.html
```

## Definition of Done

Pipeline produces `output/point_cloud.ply` from input video, viewer renders it with WASD first-person controls.
