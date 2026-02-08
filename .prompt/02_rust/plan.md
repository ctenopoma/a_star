# 技術スタック

- Python
  - ruff
  - pyrefly
  - pytest
  - viztracer

- Rust
  - cargo
  - cargo fmt
  - cargo clippy
  - cargo test
if you build, you should use build.ps1 or read BUILDING.md

# ディレクトリ

初期構成ディレクトリは以下の通り。
必要に応じてスクリプトを適切な箇所に追加する。

// python
a_star/
├── __init__.py
└── pure_python.py

// rust
src/
└── lib.rs

// tests
tests/
├── python/
└── rust/

// entry point
main.py
