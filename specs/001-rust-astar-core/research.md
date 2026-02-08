# Phase 0 Research — Rust A* Core Rewrite

## Task: Design PyO3 contract for `AStarPathfinder`
- **Decision**: Implement a `#[pyclass] RustPathfinder` that mirrors the Python constructor (`size`, `obstacle_ratio`, `seed`) and exposes a `find_path()` `#[pymethod]` returning `(path, duration, telemetry)` where telemetry is a lightweight `PyClass` convertible to dicts/tuples.
- **Rationale**: A stateful PyClass lets us generate the obstacle store once, hold onto `HashSet<(i32, i32)>`, and reuse allocations between runs, satisfying FR-005 while staying pythonic for CLI callers.
- **Alternatives considered**: (1) Pure `#[pyfunction]` with plain arguments—simpler but would rebuild the grid on every call; (2) Exposing low-level functions that expect `numpy` buffers—adds dependencies and diverges from the current API surface.

## Task: Select native priority queue + scoring strategy
- **Decision**: Use `BinaryHeap<Reverse<NodeCost>>` with a custom struct that stores `(f_score, tie_breaker, coord)` so we can reproduce heap behavior deterministically and avoid allocating Python tuples.
- **Rationale**: `BinaryHeap` exists in std, keeps the implementation dependency-free, and `Reverse` ensures min-heap semantics similar to Python's `heapq`. Tracking a monotonic `tie_breaker` counter keeps deterministic ordering when `f` scores match, meeting ±1% parity constraints.
- **Alternatives considered**: (1) `binary_heap_plus` crate—feature-rich but adds an unnecessary dependency for simple ordering; (2) FFI calls back into Python `heapq`—would forfeit the performance gain we are targeting.

## Task: Telemetry exposure strategy
- **Decision**: Record `nodes_evaluated`, `heap_pushes`, `heap_pops`, and `neighbors_checked` inside the Rust struct and expose them via a `#[pyclass] SearchTelemetry` plus helper to transform into Python `dict`/tuple before returning.
- **Rationale**: Keeping counters within Rust avoids cross-language mutability and gives us a clean hook for viztracer instrumentation. Surfacing telemetry as a PyClass maintains binary compatibility with the tuple contract by flattening before returning to Python.
- **Alternatives considered**: (1) Returning a Python dict alone—breaks existing tuple contract; (2) Writing into Python-side mutable references—complicates lifetime management and risks borrowing errors.

## Task: Viztracer profiling of mixed Python/Rust stack
- **Decision**: Document a profiling command that uses `uv run python -m viztracer --tracer_entries 2000000 --min_duration 1000 --ignore_frozen` to avoid buffer exhaustion and include Rust span names via `pyo3::ffi::PyTraceMalloc_Track` compatible markers.
- **Rationale**: `--tracer_entries 2000000` matches User Story 3 requirements, while `--min_duration 1000` keeps JSON manageable. Adding explicit span names around PyO3 entry points ensures the report captures the native loop.
- **Alternatives considered**: (1) Lower tracer entries—risk missing spans; (2) Using perf/callgrind—adds toolchain complexity for Windows users and diverges from viztracer-focused success criteria.

## Task: Best practices for PyO3 compute-heavy sections
- **Decision**: Wrap the core search loop inside `py.allow_threads(|| { ... })` so the GIL is released, allocate buffers with `Vec::with_capacity`, and convert Python inputs via `PyAny::extract` into owned Rust structs before search.
- **Rationale**: Releasing the GIL allows concurrent Python tasks (viztracer, logging) to continue and maximizes performance. Preallocations reduce allocator churn when scanning millions of nodes.
- **Alternatives considered**: (1) Holding the GIL throughout—simpler but risks starving the interpreter; (2) Copy-on-write Python views—complicates borrow checking with negligible benefit.

## Task: Best practices for maturin/uv builds on Windows
- **Decision**: Use `uv run maturin develop --release` inside `build.ps1` so wheels match the repo's uv workflow, and document that `.venv` must be activated before building; CI should call `maturin develop --features pyo3/extension-module` per `pyproject` defaults.
- **Rationale**: Aligns with existing toolchain (uv + maturin) and ensures the PyO3 extension is compiled with the correct feature flags tested locally.
- **Alternatives considered**: (1) Calling `cargo build` directly—would not produce the Python package metadata; (2) Using setuptools-rust—conflicts with current `pyproject` and adds migration work.

## Task: Integration pattern for Python fallback toggle
- **Decision**: Introduce an environment-driven flag (e.g., `A_STAR_FORCE_PYTHON=1`) plus a runtime capability probe that attempts to import `a_star._native` and falls back gracefully with a log message when unavailable.
- **Rationale**: Keeps CLI unchanged while giving ops a deterministic override, satisfying FR-008 without new CLI switches. Environment variables are easy to document in quickstart.
- **Alternatives considered**: (1) Command-line-only switch—harder to use in automated runs; (2) Automatic fallback without logging—would obscure whether the Rust port is active.
