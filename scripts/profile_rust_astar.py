from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT / "specs" / "001-rust-astar-core" / "artifacts"
TRACE_PATH = ARTIFACTS_DIR / "viztracer-rust.json"
TRACE_HTML_PATH = ARTIFACTS_DIR / "viztracer-rust.html"


def run_command(command: list[str]) -> float:
    start = time.perf_counter()
    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
    )
    return time.perf_counter() - start

def run_main(force_python: bool) -> float:
    command = ["uv", "run", "python", "-m", "viztracer", "main.py"]
    if force_python:
        command.append("--force-python")
    return run_command(command)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile A* runtimes")
    parser.add_argument(
        "--force-python",
        action="store_true",
        help="Run only the pure Python implementation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print("[profile] running viztracer")

    if args.force_python:
        print("[profile] measuring python runtime")
        python_time = run_main(force_python=True)
        print(f"[profile] python runtime: {python_time:.2f}s")
        return

    print("[profile] measuring native runtime")
    native_time = run_main(force_python=False)

    print("[profile] measuring python runtime")
    python_time = run_main(force_python=True)

    delta = 0.0
    if python_time > 0:
        delta = (python_time - native_time) / python_time * 100.0

    print(f"[profile] native runtime: {native_time:.2f}s")
    print(f"[profile] python runtime: {python_time:.2f}s")
    print(f"[profile] delta vs python: {delta:.2f}%")
    print(f"[profile] trace saved to: {TRACE_PATH}")

if __name__ == "__main__":
    main()
