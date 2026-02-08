# Implementation Plan: Execution Time Profiling (viztracer)

**Branch**: `001-plan` | **Date**: 2026-02-08 | **Spec**: [specs/001-plan/spec.md](specs/001-plan/spec.md)
**Input**: Feature specification from `/specs/001-plan/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Profile the A* execution time using viztracer with uv-managed dev tooling, capture trace output, and review results with vizviewer to identify hotspots.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12, Rust 2021 (stable toolchain)  
**Primary Dependencies**: uv, maturin, pyo3, viztracer (dev)  
**Storage**: N/A  
**Testing**: pytest, ruff, pyrefly, cargo test/clippy/fmt  
**Target Platform**: Windows with MSVC (primary), cross-platform compatible
**Project Type**: single project (Python package + Rust crate)  
**Performance Goals**: Capture a profiling trace for a representative A* run; no explicit perf target yet.  
**Constraints**: Keep Rust core unchanged; profiling runs in Python using uv-managed dev deps.  
**Scale/Scope**: One profiling workflow for a single script (main.py as default target).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Rust core owns algorithmic logic; Python layer is a thin wrapper.
- Build steps are reproducible and aligned with BUILDING.md.
- Quality gates (ruff, pytest, cargo fmt/clippy/test) are planned to pass.
- User-facing changes include SemVer impact and a changelog update plan.
- Documentation updates are planned for public API or workflow changes.

**Post-Design Check**: PASS (profiling-only workflow, no API/build changes, documentation covered in quickstart).

## Project Structure

### Documentation (this feature)

```text
specs/001-plan/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
a_star/
├── __init__.py
└── pure_python.py

src/
└── lib.rs

tests/
├── python/
└── rust/

docs/
main.py
BUILDING.md
pyproject.toml
Cargo.toml
```

**Structure Decision**: Single project layout with a Python package and Rust crate, using the existing repository structure listed above.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
| -------------------------- | ------------------ | ------------------------------------ |
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |
