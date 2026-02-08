a_star
=====

Rust-backed A* pathfinding package with a Python fallback.

Quickstart
----------

.. code-block:: powershell

   uv sync --group dev
   uv run maturin develop --release
   uv run sphinx-build -b html docs build/docs

Rust Pathfinding
---------------

- The default pathfinder uses the Rust core when ``a_star._native`` is available.
- Set ``A_STAR_FORCE_PYTHON=1`` to force the Python implementation.

Telemetry
---------

- ``AStarPathfinder.telemetry`` exposes metrics from the latest run.
- Fields: ``duration``, ``nodes_evaluated``, ``heap_pushes``, ``heap_pops``, ``neighbors_checked``.

API Reference
-------------

.. automodule:: a_star
   :members:
   :undoc-members:
   :show-inheritance:

Native Boundary
---------------

- PyO3 extension module: ``a_star._native``
- Functions: ``native_find_path`` and ``validate_name``
- Classes: ``RustPathfinder`` and ``SearchTelemetry``
- Built with maturin via ``uv build``

Developer Notes
---------------

- Run `uv run ruff check` and `uv run pytest` before committing
- Use `cargo fmt -- --check` and `cargo clippy -- -D warnings` for Rust hygiene
- See `BUILDING.md` for detailed build and verification steps
