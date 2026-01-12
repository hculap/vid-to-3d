# Agent Instructions

## Build & Run

```bash
# Extract frames
python 01_extract_frames.py --video input/room.MOV --out_dir frames/

# Generate depth maps
python 02_estimate_depth.py --frames_dir frames/ --out_dir depth/

# Create point cloud
python 03_generate_pointcloud.py --frames_dir frames/ --depth_dir depth/ --out_dir output/

# View result
python -m http.server 8000
# Open http://localhost:8000/viewer.html
```

## Verification Commands

```bash
# Check CLI help works
python 01_extract_frames.py --help
python 02_estimate_depth.py --help
python 03_generate_pointcloud.py --help

# Typecheck
python -m py_compile 01_extract_frames.py
python -m py_compile 02_estimate_depth.py
python -m py_compile 03_generate_pointcloud.py
```

## Commit Format

`US-XXX: short description`

Example: `US-001: Create frame extraction CLI script`

## After Each Task

1. Run verification commands
2. Commit changes
3. Mark task complete in @fix_plan.md (change `[ ]` to `[x]`)
4. Append entry to progress.txt
