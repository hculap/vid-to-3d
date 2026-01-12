# CLAUDE.md — Instructions for Claude Code

## Project type

Prototype (PoC) for video-to-3D reconstruction. Must remain runnable, debuggable, and safe to iterate.

## Source of truth

- `prd.json` — Ralph task queue (user stories with acceptance criteria)
- `progress.txt` — Loop memory (what was completed)

## Loop rules

1. Work on ONE user story per iteration (check `prd.json` for next `passes: false`)
2. Keep diffs small and focused
3. Before committing: run sanity check (--help, import check, or smoke test)
4. Commit message format: `US-XXX: short description`
5. After completing a story, update `prd.json`: set `passes: true`, add notes if needed

## Code standards

- Consistent naming (snake_case for Python, camelCase for JS)
- Clear error messages with actionable guidance
- Small, readable scripts (no monoliths)
- Avoid duplicating logic — extract helpers when needed

## File structure

```
01_extract_frames.py    # Video → frames
02_estimate_depth.py    # Frames → depth maps
03_generate_pointcloud.py  # Frames + depth → PLY
viewer.html             # Three.js walkthrough
input/                  # Source videos (gitignored)
frames/                 # Extracted frames (gitignored)
depth/                  # Depth maps (gitignored)
output/                 # Point clouds (gitignored)
```

## Commands

```bash
# Extract frames from video
python 01_extract_frames.py --video input/room.MOV --out_dir frames/

# Generate depth maps
python 02_estimate_depth.py --frames_dir frames/ --out_dir depth/

# Create point cloud
python 03_generate_pointcloud.py --frames_dir frames/ --depth_dir depth/ --out_dir output/

# View result
python -m http.server 8000
# Open http://localhost:8000/viewer.html
```

## Safety

- Generated artifacts stay out of git (frames/, depth/, output/, input/)
- All scripts should have --help with clear usage

## Definition of done

Pipeline produces `output/point_cloud.ply` from input video, viewer renders it with first-person controls.
