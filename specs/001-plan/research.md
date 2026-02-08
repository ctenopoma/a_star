# Research

## Decision: Use viztracer for execution-time profiling
- Rationale: Matches the requested tooling and produces a detailed trace with minimal setup in a Python-only workflow.
- Notes: Use `uv run python -m viztracer main.py` for the minimal invocation; default output is result.json and can be customized with `-o`.
- Notes: For large runs, prefer a smaller representative workload or use `--min_duration` and `--tracer_entries` to control trace size.
- Alternatives considered: cProfile (built-in but less visual), py-spy (external sampling), scalene (broader profiling scope).

## Decision: Run profiling via uv-managed dev dependency
- Rationale: Keeps tooling consistent with the project build workflow and avoids global installs.
- Alternatives considered: System pip install or OS-level tooling.

## Decision: Default profiling target is main.py
- Rationale: eval_single_process.py is not present in the repository; main.py exercises the A* run and is a suitable stand-in.
- Alternatives considered: Add eval_single_process.py or move the workload into a new script before profiling.
