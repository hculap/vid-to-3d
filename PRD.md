# PRD — Video to 3D Room (vid-to-3d)

Last updated: 2026-01-12

## 1. Summary

Build a local pipeline that converts a short video of a room into a walkable 3D scene rendered in the browser.

MVP output:
- A colored point cloud (PLY)
- A self-contained Three.js viewer (`viewer.html`) with first-person controls (WASD + mouse look)

This repo is designed to work well with “Ralph-style” agent loops:
- Small, atomic PRD items
- Clear verify steps
- One task per commit
- Progress tracked in `progress.txt`

## 2. Users / Use-cases

Primary user:
- A developer/creator with a phone video of a room who wants a quick 3D walkthrough.

Secondary user:
- A researcher/prototyper evaluating monocular depth → 3D reconstruction quality.

## 3. Goals

- Input: a single MP4/MOV video placed under `input/` (or passed by path).
- Output artifacts:
  - `frames/` — extracted RGB frames (JPG)
  - `depth/` — depth maps aligned to frames (`.npy`) plus visualization PNGs
  - `output/point_cloud.ply` — merged colored point cloud
  - `viewer.html` — loads the PLY and supports navigation
- Runs locally on:
  - macOS Apple Silicon using PyTorch MPS when available
  - CUDA when available
  - CPU fallback
- Re-runnable and resumable (skip work if outputs already exist).

## 4. Non-goals (for MVP)

- Photorealistic textured mesh reconstruction
- SLAM-grade camera tracking and globally accurate geometry
- Multi-room / multi-video stitching
- Cloud hosting / deployment
- Guaranteed metric scale correctness across devices

## 5. Key decisions

- Depth model: Depth Anything (Small) via Hugging Face Transformers (configurable model id).
- Geometry representation: colored point cloud (not a mesh).
- Exchange format: PLY with per-vertex RGB.
- Viewer: Three.js + PLYLoader + first-person controls.

## 6. Constraints / assumptions

- Video is indoor, mostly stable lighting, minimal motion blur.
- Camera intrinsics are unknown; we approximate focal length from a configurable FOV unless provided.
- Multi-frame fusion is “best effort” unless camera pose estimation is implemented (stretch goal).

## 7. Risks & mitigations

- Monocular depth can be scale-ambiguous
  - Mitigation: allow selecting a metric indoor model; support a global scale factor.
- Multi-frame alignment is hard without camera pose
  - Mitigation: MVP may use naive merge with clear documentation; stretch adds ICP/VO.
- Memory / file size can explode
  - Mitigation: frame sampling (`--every N`), pixel subsampling (`--pixel-stride`), voxel downsampling.

## 8. Definition of Done (MVP)

- Running the 3 python scripts produces:
  - non-empty `frames/`
  - corresponding `depth/*.npy` and `depth/*_viz.png`
  - a non-empty `output/point_cloud.ply`
- Opening `viewer.html` via a local static server renders the point cloud and allows navigation.
- README documents the full workflow and troubleshooting.

## 9. Backlog (Ralph-friendly)

Agent rules:
- Implement exactly ONE unchecked item per iteration/commit.
- After completion, append a short entry to `progress.txt` referencing the PRD item id.
- Do not “bundle” multiple PRD items into one commit.
- If a task is too large, split it into smaller tasks by editing this PRD.

### 9.0 Bootstrap (must exist before loops)

- [x] BOOT-01 Add initial docs: README.md, ARCHITECTURE.md, DEVELOPMENT.md, AGENTS.md
- [x] BOOT-02 Add loop state files: progress.txt, ralph-once.sh, afk-ralph.sh
- [x] BOOT-03 Add .gitignore to exclude generated artifacts (frames/, depth/, output/, input videos)

### 9.1 P0 — Core pipeline (must-have)

Repo conventions & shared behavior
- [ ] CORE-01 Define a single filename convention for frames and depth (e.g., `frame_000123.jpg` ↔ `frame_000123.npy`) and ensure all scripts follow it.
  - Verify:
    - After FE steps + DE steps, for each `frames/frame_*.jpg` there is a `depth/frame_*.npy`.
- [ ] CORE-02 Standardize CLI flags across scripts: `--input/--video`, `--out_dir`, `--overwrite/--skip-existing`, `--max-items`, `--log-level`.
  - Verify:
    - `python <script>.py --help` is consistent across scripts.

Frame extraction (01_extract_frames.py)
- [ ] FE-01 Implement CLI + basic video decode using OpenCV.
  - Verify:
    - `python 01_extract_frames.py --video input/room.mp4 --out_dir frames/` exits 0.
- [ ] FE-02 Add frame sampling (`--every N`, default 15) and optional `--start/--end` bounds.
  - Verify:
    - Extracted frame count is roughly `total_frames / every` (rounded).
- [ ] FE-03 Add resize support (`--width/--height`, default 640x480) and JPEG quality setting.
  - Verify:
    - Output JPG dimensions match configured size.
- [ ] FE-04 Generate `frames/manifest.json` including:
  - source video path
  - fps
  - stride
  - resize settings
  - list of extracted frames with original frame index + timestamp
  - Verify:
    - `frames/manifest.json` exists and references all extracted JPGs.
- [ ] FE-05 Add resume behavior: by default skip existing frames; `--overwrite` recreates them.
  - Verify:
    - Rerun is fast and does not rewrite files unless overwrite is set.

Depth estimation (02_estimate_depth.py)
- [ ] DE-01 Implement CLI + frame enumeration + output directory creation.
  - Verify:
    - Script exits with a clear error if `frames/` is missing/empty.
- [ ] DE-02 Load a Depth Anything model via Transformers (configurable `--model`).
  - Verify:
    - First run downloads model and processes at least 1 frame.
- [ ] DE-03 Implement device selection: `--device auto|mps|cuda|cpu` (default auto).
  - Verify:
    - Logs show which device is being used.
- [ ] DE-04 For one frame, produce:
  - `depth/<basename>.npy` (float32 depth aligned to frame resolution)
  - `depth/<basename>_viz.png` (human-viewable depth visualization)
  - Verify:
    - `.npy` loads as HxW float array.
    - `_viz.png` exists.
- [ ] DE-05 Add batch processing with a progress bar and `--max-frames` for quick runs.
  - Verify:
    - `--max-frames 5` processes only 5 frames.
- [ ] DE-06 Add `--skip-existing` default behavior and `--overwrite` mode.
  - Verify:
    - Rerun only processes missing depth maps by default.
- [ ] DE-07 Generate `depth/manifest.json` containing:
  - model id
  - device
  - dtype
  - list of outputs
  - Verify:
    - Depth manifest exists; counts match processed frames.

Point cloud generation (03_generate_pointcloud.py)
- [ ] PC-01 Implement CLI + input pairing logic (match frame basenames to depth basenames).
  - Verify:
    - Missing pairs are reported clearly.
- [ ] PC-02 Implement intrinsics:
  - default from FOV (`--fov_deg`, default 60)
  - optional explicit `--fx --fy --cx --cy`
  - Verify:
    - Intrinsics are logged and stable between runs.
- [ ] PC-03 Generate a colored point cloud from ONE frame+depth (camera coordinates) and export a PLY.
  - Verify:
    - Output PLY exists and has point count > 0.
- [ ] PC-04 Add subsampling controls (`--pixel_stride`, `--max_points_per_frame`) to control size.
  - Verify:
    - Changing stride changes output point count materially.
- [ ] PC-05 Merge multiple frames into one point cloud (MVP: naive concatenation in a shared frame) and document limitations.
  - Verify:
    - Multi-frame output has more points than single-frame output.
- [ ] PC-06 Add optional voxel downsample (`--voxel_size`) when Open3D is installed.
  - Verify:
    - Voxel downsample reduces point count.

Viewer (viewer.html)
- [ ] VIEW-01 Implement minimal Three.js viewer that loads `output/point_cloud.ply` using PLYLoader.
  - Verify:
    - Point cloud renders when served via `python -m http.server`.
- [ ] VIEW-02 Add first-person navigation (PointerLockControls) with WASD + mouse look.
  - Verify:
    - User can move and look around; ESC unlocks pointer.
- [ ] VIEW-03 Add basic UI overlay:
  - Controls instructions
  - Point size slider
  - Reset view button
  - Verify:
    - Slider changes point size without reload.

End-to-end ergonomics
- [ ] E2E-01 Add `run_pipeline.sh` (or `pipeline.py`) to run steps 1→2→3 with consistent defaults.
  - Verify:
    - One command produces `output/point_cloud.ply`.
- [ ] E2E-02 Add a “happy path” section to README including exact commands and expected outputs.
  - Verify:
    - A new user can follow README and succeed.

### 9.2 P1 — Guardrails & developer experience (recommended)

- [ ] QA-01 Add lightweight smoke tests (no large model inference) for:
  - frame extraction CLI (synthetic video)
  - point cloud export (synthetic depth)
  - Verify:
    - `pytest` exits 0.
- [ ] QA-02 Add linting (`ruff`) and a minimal `pyproject.toml` configuration.
  - Verify:
    - `ruff check .` exits 0 on clean repo.

### 9.3 P2 — Better reconstruction (stretch)

- [ ] FUSION-01 Add optional sequential alignment (ICP) between frame point clouds to reduce ghosting.
  - Verify:
    - For a slow-pan video, merged cloud looks less duplicated than naive merge.
- [ ] FUSION-02 Add optional visual odometry pose estimation (OpenCV feature tracking) to place frames in a global coordinate system.
  - Verify:
    - Camera trajectory + cloud are plausible; limitations documented.
