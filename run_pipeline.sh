#!/bin/bash
# run_pipeline.sh - Run the full video-to-3D pipeline
# Usage: ./run_pipeline.sh <video_path>

set -e

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <video_path>"
    echo "Example: $0 input/room.MOV"
    exit 1
fi

VIDEO_PATH="$1"

# Check if video exists
if [ ! -f "$VIDEO_PATH" ]; then
    echo "Error: Video file not found: $VIDEO_PATH"
    exit 1
fi

echo "=== Video to 3D Pipeline ==="
echo "Input video: $VIDEO_PATH"
echo ""

# Step 1: Extract frames
echo "=== Step 1/3: Extracting frames ==="
python3 01_extract_frames.py \
    --video "$VIDEO_PATH" \
    --out_dir frames/
echo ""

# Step 2: Estimate depth
echo "=== Step 2/3: Estimating depth ==="
python3 02_estimate_depth.py \
    --frames_dir frames/ \
    --out_dir depth/
echo ""

# Step 3: Generate point cloud
echo "=== Step 3/3: Generating point cloud ==="
python3 03_generate_pointcloud.py \
    --frames_dir frames/ \
    --depth_dir depth/ \
    --out_dir output/
echo ""

echo "=== Pipeline complete! ==="
echo "Output: output/point_cloud.ply"
echo ""
echo "To view the result:"
echo "  python3 -m http.server 8000"
echo "  Open http://localhost:8000/viewer.html"
