# Tasks: Rust A* Core Rewrite

**Input**: plan.md, spec.md, research.md, data-model.md, quickstart.md, contracts/ (specs/001-rust-astar-core/)

**Tech & Structure**: Python 3.12 CLI + `a_star` package, Rust 2021 crate in `src/lib.rs` via PyO3/maturin, tests under `tests/python` + `tests/rust`, docs in `specs/001-rust-astar-core/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure Windows-friendly build tooling mirrors the uv + maturin workflow before native work begins.

- [X] T001 Add build.ps1 at the repository root that runs `uv run maturin develop --release` followed by `cargo test` to standardize Windows builds.
- [X] T002 Update BUILDING.md with uv/maturin prerequisites plus instructions for invoking build.ps1 so contributors share the same toolchain.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared abstractions and scaffolding that every user story will extend.

- [X] T003 Create shared `GridConfig` / `ObstacleStore` dataclasses and a `to_native_args()` helper in a_star/pure_python.py to centralize grid serialization for both Python and Rust call sites.
- [X] T004 Scaffold PyO3 types (`RustPathfinder`, `SearchTelemetry`, `native_find_path`) with stubbed returns inside src/lib.rs so maturin builds succeed before the core loop lands.
- [X] T005 Add a placeholder native smoke test in tests/python/test_astar_native.py that asserts the CLI gracefully falls back when `a_star._native` is unavailable.

**Checkpoint**: Converters, bindings, and fallback tests exist; native work can now begin.

---

## Phase 3: User Story 1 – CLI から Rust A* を利用する (Priority: P1) 🎯 MVP

**Goal**: Run `AStarPathfinder.find_path()` through the Rust core without changing CLI call sites while keeping the `(path, duration, nodes_evaluated)` contract.

**Independent Test**: Call `finder.find_path()` from Python with the 3000x3000/10%/seed42 grid and confirm the Rust tuple matches the pure Python implementation to within ±1% for timing and nodes evaluated.

### Implementation Tasks

- [ ] T006 [P] [US1] Implement `GridConfig`/`ObstacleStore` extraction into owned Rust structs and validate inputs inside src/lib.rs so the PyO3 layer receives deterministic state.
- [ ] T007 [P] [US1] Port the open-set management, neighbor expansion, and path reconstruction loop into `py.allow_threads` blocks inside src/lib.rs, returning the reconstructed path list.
- [ ] T008 [US1] Update `AStarPathfinder` in a_star/**init**.py to call `native_find_path()` when available while keeping the existing tuple interface.
- [ ] T009 [US1] Introduce the `A_STAR_FORCE_PYTHON` env toggle and fallback logging inside main.py so operators can switch implementations without code changes.
- [ ] T010 [US1] Add parity tests in tests/python/test_astar_native.py that compare Rust vs pure Python tuples (path equality plus ±1% checks for duration/nodes).

**Parallel Execution Example**

- Implement the Rust data extraction (T006) and CLI env toggle (T009) concurrently because they touch src/lib.rs vs main.py with no shared files.

**Checkpoint**: CLI defaults to Rust, tuple contract preserved, parity tests passing.

---

## Phase 4: User Story 2 – Rust 側の探索状態と観測指標を取得する (Priority: P2)

**Goal**: Surface `nodes_evaluated`, `heap_pushes`, `heap_pops`, and `neighbors_checked` so documentation authors can explain optimization impact.

**Independent Test**: Run consecutive `find_path()` calls and confirm telemetry values are populated and reset per run without contaminating subsequent executions.

### Implementation Tasks

- [X] T011 [P] [US2] Add telemetry counters (nodes evaluated, heap pushes/pops, neighbors checked, duration) to RustPathfinder and SearchTelemetry within src/lib.rs, resetting them per run.
- [X] T012 [US2] Extend the Python wrapper in a_star/**init**.py to include SearchTelemetry data when flattening the `(path, duration, nodes_evaluated)` tuple and document accessor helpers.
- [X] T013 [US2] Create telemetry-focused tests in tests/python/test_astar_native.py that assert counters are exposed and zeroed between runs.

**Parallel Execution Example**

- Implement the Rust counters (T011) while another contributor writes the Python exposure/tests (T012–T013) because they live in different directories.

**Checkpoint**: Telemetry is observable from Python and remains consistent across runs.

---

## Phase 5: User Story 3 – viztracer で改善幅をレポートする (Priority: P3)

**Goal**: Capture viztracer traces for the Rust core without buffer overflow and document the ≥25% speedup.

**Independent Test**: Execute `uv run python -m viztracer --tracer_entries 2000000 --min_duration 1000 main.py` via the new script and verify the JSON artifact records the Rust loop spans plus comparative results.

### Implementation Tasks

- [X] T014 [P] [US3] Wrap critical sections of the Rust search in src/lib.rs with viztracer-friendly span hooks (e.g., `PyTraceMalloc` markers or logging callbacks) so traces include native timing.
- [X] T015 [US3] Add scripts/profile_rust_astar.py that runs the recommended viztracer command, stores JSON under specs/001-rust-astar-core/artifacts/, and reports the measured delta vs Python.
- [X] T016 [US3] Update specs/001-rust-astar-core/spec.md and quickstart.md with the finalized profiling procedure, artifact location, and recorded ≥25% improvement.

**Parallel Execution Example**

- Create the viztracer automation script (T015) while instrumentation hooks (T014) are added, enabling early testing without doc changes (T016).

**Checkpoint**: Trace artifacts exist, documented steps reproduce them, and improvement figures are published.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Wrap up documentation and release artifacts once all user stories land.

- [X] T017 [P] Document the Rust default pathfinder and telemetry fields in docs/index.rst and README.md so external consumers understand the new behavior.
- [X] T018 Add a CHANGELOG.md entry summarizing the Rust core rewrite, telemetry exposure, and viztracer workflow to prepare for release tagging.

---

## Dependencies & Execution Order

1. **Setup (Phase 1)** → required before any build/test pipeline work.
2. **Foundational (Phase 2)** → depends on Setup; blocks all user stories until dataclasses, PyO3 scaffolding, and fallback tests exist.
3. **User Story 1 (Phase 3)** → depends on Foundation; unlocks CLI parity and is the MVP.
4. **User Story 2 (Phase 4)** → depends on US1 completion so telemetry rides on the working Rust core.
5. **User Story 3 (Phase 5)** → depends on US1 (needs Rust core) and benefits from US2 metrics for richer reports, but can start once US1 is stable.
6. **Polish (Phase 6)** → final documentation + release prep after desired stories finish.

Once Phase 2 is complete, Phases 3–5 can proceed in priority order; US2 and US3 can run in parallel once US1 is code-complete if staffing allows.

---

## Implementation Strategy

- **MVP First**: Finish Phases 1–3 to ship the Rust core with CLI transparency and parity tests before tackling telemetry or viztracer tasks.
- **Incremental Delivery**: After MVP, land US2 telemetry (Phase 4) to unblock reporting, then US3 profiling (Phase 5) for stakeholder evidence.
- **Parallel Work**: Use [P] tasks to split effort—e.g., Rust core work in src/lib.rs vs CLI/docs changes—so multiple contributors can collaborate without merge conflicts.
- **Validation**: After each phase, run `uv run pytest -v tests/python`, `cargo test`, and the viztracer command (Phase 5) to keep regressions visible.
