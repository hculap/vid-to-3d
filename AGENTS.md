# AGENTS.md — Working Agreement for Agents and Contributors

This file is written for coding agents and humans.

## Repo type and quality bar

This is a prototype (PoC), but it must remain:
- runnable end-to-end
- debuggable (artifacts on disk, clear logging)
- safe to iterate on (no giant commits, no surprise side effects)

Do not cut corners that permanently degrade maintainability:
- consistent naming conventions
- clear error messages
- avoid duplicating logic when a tiny helper is sufficient
- keep scripts small and readable

## Source of truth

- `PRD.md` defines the intended end state and backlog.
- `progress.txt` records what was completed and why (short, factual notes).

## Loop rules (critical)

1. Implement EXACTLY ONE unchecked PRD item per iteration.
2. Keep diffs small and focused.
3. Before committing: run at least a minimal sanity check (help output, import check, or smoke run).
4. Commit with a message referencing the PRD item id (e.g., "FE-03: add resize and jpeg quality").
5. Append to `progress.txt`:
   - PRD item id
   - what changed (1–3 bullets)
   - files changed
   - any notes / next steps

If a task is too large:
- split it into smaller PRD items by editing `PRD.md` (do not brute-force it).

## Safety

- Generated artifacts must stay out of git: frames/, depth/, output/, and input videos.
- For AFK loops, prefer running inside a container sandbox.

## Repo map

```text
/
├── PRD.md
├── progress.txt
├── requirements.txt
├── 01_extract_frames.py
├── 02_estimate_depth.py
├── 03_generate_pointcloud.py
├── viewer.html
├── input/
├── frames/
├── depth/
└── output/
```

## Definition of done (MVP)

- The pipeline produces `output/point_cloud.ply` from an input video.
- The viewer renders it and supports first-person controls.
- README documents the steps and common pitfalls.
