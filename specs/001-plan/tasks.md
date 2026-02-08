---

description: "Task list for execution time profiling report"
---

# Tasks: Execution Time Profiling Report

**Input**: Design documents from `/specs/001-plan/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md, contracts/

**Tests**: Tests are not required because this feature is profiling/report-only with no behavior or API changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create profiling artifacts folder and ignore trace outputs in specs/001-plan/artifacts/.gitignore
- [x] T002 Ensure viztracer dev dependency is recorded in pyproject.toml
- [x] T003 [P] Update profiling command/output location in specs/001-plan/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core artifacts that MUST be complete before ANY user story can be implemented

**Checkpoint**: Foundation ready - user story implementation can now begin

- [x] T004 Create report template with required sections in specs/001-plan/runtime-profiling-report.md

---

## Phase 3: User Story 1 - 実行時間の可視化とボトルネック抽出 (Priority: P1) MVP

**Goal**: Profile main.py, identify Python hotspots, and document Rust candidates in a saved report.

**Independent Test**: Run profiling on a representative input and confirm the report contains top hotspots with time ratios and Rust candidates with rationale.

### Implementation for User Story 1

- [x] T005 [US1] Run viztracer and save trace to specs/001-plan/artifacts/viztracer-main.json
- [x] T006 [P] [US1] Record profiling run metadata (inputs, environment, commands) in specs/001-plan/runtime-profiling-report.md
- [x] T007 [US1] Document top hotspots with time and percentage in specs/001-plan/runtime-profiling-report.md
- [x] T008 [US1] Add Rustification candidates with rationale and expected impact in specs/001-plan/runtime-profiling-report.md
- [x] T009 [US1] Document edge cases and rerun guidance in specs/001-plan/runtime-profiling-report.md

**Checkpoint**: User Story 1 should be fully documented and independently reviewable

---

## Phase 4: User Story 2 - レポートのレビューによる意思決定 (Priority: P2)

**Goal**: Provide decision-ready guidance for stakeholders reviewing the report.

**Independent Test**: A reviewer can read the report alone and decide priorities and next actions.

### Implementation for User Story 2

- [x] T010 [US2] Add executive summary and prioritized actions in specs/001-plan/runtime-profiling-report.md
- [x] T011 [US2] Add decision guidance mapping hotspots to Rust candidates in specs/001-plan/runtime-profiling-report.md

**Checkpoint**: User Story 2 should be fully documented and independently reviewable

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final quality pass across stories

- [x] T012 [P] Add success-criteria checklist and coverage summary in specs/001-plan/runtime-profiling-report.md
- [x] T013 [P] Note report location and trace handling guidance in specs/001-plan/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - no dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - depends on US1 report content but remains independently reviewable

### Parallel Opportunities

- T002 and T003 can run in parallel
- T006 can run in parallel with T005 after the report template exists
- T012 and T013 can run in parallel after US1 and US2 are complete

---

## Parallel Example: User Story 1

```bash
Task: "Record profiling run metadata in specs/001-plan/runtime-profiling-report.md"
Task: "Document top hotspots with time and percentage in specs/001-plan/runtime-profiling-report.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate User Story 1 independently

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 and validate
3. Add User Story 2 and validate
4. Finish Polish tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and reviewable
- Avoid implementation changes; this feature is analysis and reporting only
