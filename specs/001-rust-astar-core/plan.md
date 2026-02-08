# Implementation Plan: Rust A* Core Rewrite

**Branch**: `[001-rust-astar-core]` | **Date**: 2026-02-08 | **Spec**: [Feature Spec](spec.md)
**Input**: Feature specification from `/specs/001-rust-astar-core/spec.md`

**Note**: Plan assembled via `speckit.plans` workflow.

## Summary

Rebuild the `AStarPathfinder.find_path()` core loop in Rust (PyO3) so CLI clients keep receiving the same `(path, duration, nodes_evaluated)` tuple while gaining ≥25% runtime savings on the profiled 3000x3000 map. The port must encapsulate open-set management and neighbor expansion entirely in Rust, surface telemetry counters (`nodes_evaluated`, heap ops, neighbor checks), and remain swappable with the current Python implementation when the native module is unavailable. Viztracer profiling will be repeated post-port to document the improvement.

## Technical Context

**Language/Version**: Python 3.12 (per `pyproject.toml`) + Rust stable toolchain (2021 edition crate) via PyO3 0.27  
**Primary Dependencies**: PyO3 0.27, maturin build backend, uv toolchain, pytest, viztracer, ruff, pyrefly (linting), BinaryHeap from Rust stdlib for priority queue  
**Storage**: In-memory grid + obstacle sets only; no external persistence (N/A)  
**Testing**: Python `pytest -v tests/python`, Rust `cargo test` (unit + FFI shim), viztracer regression capture  
**Target Platform**: Windows CLI execution of `main.py`, with expectation to run under uv/venv and maturin-built wheels  
**Project Type**: Hybrid Python package + Rust native extension consumed by CLI + tests  
**Performance Goals**: ≥25% faster than Python baseline on 3000x3000 grid; telemetry parity (path equality, ±1% nodes evaluated)  
**Constraints**: Preserve tuple contract, provide auto-fallback to Python path on ImportError/build failure, avoid viztracer buffer overflow via documented flags, maintain deterministic behavior for identical seeds  
**Scale/Scope**: Grids from 1000x1000 to 5000x5000, up to 40% obstacle density, repeated CLI runs with reusable obstacle stores

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Status**: NEEDS CLARIFICATION — `.specify/memory/constitution.md` still contains the stock placeholder with unnamed principles, so no enforceable governance criteria are defined. Proceeding under default engineering best practices until product/ops supply the ratified constitution.
- **Post-Phase-1 Review**: Still blocked waiting for an adopted constitution; no new violations introduced by the research/data-model/contracts deliverables.

## Project Structure

### Documentation (this feature)

```text
specs/001-rust-astar-core/
├── plan.md
├── spec.md
├── research.md          # Phase 0 (to be generated)
├── data-model.md        # Phase 1 (to be generated)
├── quickstart.md        # Phase 1 (to be generated)
├── contracts/           # Phase 1 (to be generated)
└── tasks.md             # Phase 2 (future /speckit.tasks output)
```

### Source Code (repository root)

```text
a_star/
├── __init__.py
└── pure_python.py

src/
└── lib.rs              # Rust A* core + PyO3 bindings

docs/
├── conf.py
└── index.rst

tests/
├── python/
│   └── test_example.py
└── rust/
    └── lib_tests.rs

main.py                 # CLI entry point invoking AStarPathfinder
```

**Structure Decision**: Maintain single Python package (`a_star`) with Rust cdylib in `src/` built via maturin. Tests stay under `tests/python` and `tests/rust`, while feature documentation lives in `specs/001-rust-astar-core/`.

## Complexity Tracking

> No constitution-defined violations at this time; section intentionally left blank pending governance guidance.
