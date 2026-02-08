# Quickstart — Rust A* Core Rewrite

## 1. Environment
1. Install [uv](https://github.com/astral-sh/uv) and a Rust toolchain (`rustup toolchain install stable`).
2. From repo root, create the virtual env:
   ```powershell
   uv venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Sync Python deps (dev extras include pytest, viztracer, maturin, ruff):
   ```powershell
   uv pip install -e ".[dev]"
   ```

## 2. Build the Rust extension
```powershell
uv run maturin develop --release
```
This compiles `a_star._native` with PyO3 0.27 and installs it into the active venv. Use `build.ps1` for CI/packaged artifacts.

## 3. Run the CLI with Rust core
```powershell
uv run python main.py
```
Expected output includes:
- Grid generation summary
- `[*] 経路探索開始...`
- Final `(path, duration, nodes_evaluated)` printed via Python fallback logger

Set `A_STAR_FORCE_PYTHON=1` to compare the legacy implementation.

## 4. Viztracer profiling
```powershell
uv run python scripts/profile_rust_astar.py
```
The script runs viztracer with the required flags, writes the JSON trace to
`specs/001-rust-astar-core/artifacts/viztracer-rust.json`, and prints the delta
versus the Python fallback run.

## 5. Tests
- Python parity tests: `uv run pytest -v tests/python`
- Rust unit tests: `cargo test`
- Optional smoke test for the PyO3 binding (once implemented): `uv run python - <<'PY'
from a_star import native_find_path
print(native_find_path(100, 0.1, 42))
PY`

## 6. Lint & formatting
```powershell
uv run ruff check .
uv run ruff format .
cargo fmt
cargo clippy --all-targets --all-features
```
