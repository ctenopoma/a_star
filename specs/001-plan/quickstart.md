# Quickstart: Execution Time Profiling

## Install the profiler (dev dependency)
```powershell
uv add --dev viztracer
```

## Run profiling
```powershell
uv run python -m viztracer -o specs/001-plan/artifacts/viztracer-main.json main.py
```

## Inspect the trace
```powershell
vizviewer specs/001-plan/artifacts/viztracer-main.json
```

## Notes
- If you want to profile a different script, replace main.py with the target file.
- The trace file is stored under specs/001-plan/artifacts/ to keep profiling outputs isolated.
- The report lives at specs/001-plan/runtime-profiling-report.md.
