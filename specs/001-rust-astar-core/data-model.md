# Data Model — Rust A* Core Rewrite

## GridConfig
| Field            | Type              | Description                                                  | Validation                                                                                  |
| ---------------- | ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `size`           | `int`             | Square grid dimension (same for X/Y).                        | `size >= 10` and `size <= 5000`; must match CLI defaults for parity tests.                  |
| `obstacle_ratio` | `float`           | Fraction of grid cells to mark as obstacles.                 | `0.0 <= ratio < 0.5`; Python and Rust share identical rounding rules when computing counts. |
| `seed`           | `int`             | RNG seed to deterministically generate obstacle coordinates. | Accepts 32-bit signed range; required to keep parity with Python baseline.                  |
| `start`          | `tuple[int, int]` | Always `(0, 0)` for current CLI.                             | Auto-derived; validate it is never blocked.                                                 |
| `goal`           | `tuple[int, int]` | Always `(size-1, size-1)` for current CLI.                   | Auto-derived; validate it is never blocked.                                                 |

**Relationships**: `GridConfig` feeds both the Python and Rust pathfinder constructors. It determines the bounds enforced by `ObstacleStore` and the heuristic radius for `SearchTelemetry`.

## ObstacleStore
| Field   | Type                                                          | Description                                                    | Validation                                                                        |
| ------- | ------------------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `cells` | `HashSet<(i32, i32)>` (Rust) / `set[tuple[int,int]]` (Python) | Blocked coordinates; cached inside the Rust PyClass for reuse. | Must exclude `start`/`goal`; cardinality equals `floor(size^2 * obstacle_ratio)`. |
| `owner` | `Arc<RwLock<ObstacleStore>>` or Py-owned handle               | Ensures reuse across multiple `find_path` invocations.         | Must guard mutation between runs; cleared via explicit reset.                     |

**Relationships**: `ObstacleStore` is created from `GridConfig` once per `RustPathfinder` instance and consumed by the native neighbor expansion loop.

## SearchTelemetry
| Field               | Type              | Description                              | Validation                                                                       |
| ------------------- | ----------------- | ---------------------------------------- | -------------------------------------------------------------------------------- |
| `duration`          | `float` (seconds) | Wall-clock elapsed time of the search.   | Non-negative; recorded with `Instant::elapsed`.                                  |
| `nodes_evaluated`   | `int`             | Count of nodes popped from the open set. | Matches Python baseline within ±1%.                                              |
| `heap_pushes`       | `int`             | Number of pushes onto the BinaryHeap.    | Always `>= nodes_evaluated`; increments whenever a neighbor enters the open set. |
| `heap_pops`         | `int`             | Number of pops from the BinaryHeap.      | Equals `nodes_evaluated` when no duplicate removal occurs.                       |
| `neighbors_checked` | `int`             | Successful + rejected neighbor checks.   | Used to justify optimizations; resets per run.                                   |

**Relationships**: `SearchTelemetry` is embedded in `PathResult` and also logged separately for viztracer annotation.

## PathResult
| Field       | Type                           | Description                                                          | Validation                                              |
| ----------- | ------------------------------ | -------------------------------------------------------------------- | ------------------------------------------------------- |
| `path`      | `list[tuple[int,int]] \| None` | Ordered coordinates from `start` to `goal` or `None` if unreachable. | Ensures final coordinate equals `goal` when not `None`. |
| `telemetry` | `SearchTelemetry`              | Metrics bundle for the same run.                                     | Non-null even when `path` is `None`.                    |

**Relationships**: `PathResult` is the value returned from both Python and Rust `find_path()` implementations and is transformed into the `(path, duration, nodes_evaluated)` tuple the CLI expects.

## State Transitions
1. **Initialization**: `GridConfig` + RNG produce `ObstacleStore`, ensuring `start`/`goal` clearance.
2. **Search start**: Rust `find_path()` clones lightweight pointers to `ObstacleStore` and seeds the BinaryHeap with `(f=0, start)`.
3. **Iteration**: For each pop, telemetry counters advance and neighbors reference `ObstacleStore` membership; nodes push into the heap with updated scores.
4. **Termination**: On reaching `goal`, `PathResult.path` is reconstructed via `came_from`; otherwise the function exits with `path=None` once the heap empties.
5. **Exposure**: `PathResult` is converted into the backwards-compatible tuple for Python consumers, and telemetry is available for viztracer logging.
