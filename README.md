# Astar アルゴルズム

Rust-backed A* pathfinding with a Python fallback pathfinder.

## Usage

```python
from a_star import AStarPathfinder

finder = AStarPathfinder(3000, 0.1, 42)
path, duration, nodes = finder.find_path()
telemetry = finder.telemetry

print(len(path) if path else 0, duration, nodes)
print(
	telemetry.nodes_evaluated,
	telemetry.heap_pushes,
	telemetry.heap_pops,
	telemetry.neighbors_checked,
)
```

## Runtime toggles

- Set `A_STAR_FORCE_PYTHON=1` to force the pure Python implementation.

## Telemetry

`AStarPathfinder.telemetry` exposes the metrics from the latest run:

- `duration`
- `nodes_evaluated`
- `heap_pushes`
- `heap_pops`
- `neighbors_checked`
