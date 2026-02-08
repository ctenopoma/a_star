"""a_star

Rust-backed Python package scaffold that re-exports functions from the native extension module.

Build the extension before importing in documentation or runtime contexts:
`uv run maturin develop`.
"""

from dataclasses import dataclass
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Optional

from a_star.pure_python import AStarPathfinder as PurePythonAStarPathfinder

__all__ = [
    "AStarPathfinder",
    "SearchTelemetry",
    "validate_name",
    "native_available",
    "__version__",
]

_NATIVE_MODULE = "a_star._native"


def _load_native() -> Any:
    try:
        return import_module(_NATIVE_MODULE)
    except ImportError:
        return None


def _require_native() -> Any:
    native = _load_native()
    if native is None:
        raise RuntimeError(
            "Native extension module is not built. Run `uv run maturin develop` and retry."
        )
    return native


try:
    __version__ = version("a_star")
except PackageNotFoundError:  # pragma: no cover - fallback for editable installs
    __version__ = "0.1.0"


def native_available() -> bool:
    return _load_native() is not None



def validate_name(name: str) -> str:
    """Return the stripped name or raise ``ValueError`` when blank."""

    native = _require_native()
    return str(native.validate_name(str(name)))


@dataclass
class SearchTelemetry:
    duration: float
    nodes_evaluated: int
    heap_pushes: int = 0
    heap_pops: int = 0
    neighbors_checked: int = 0


class AStarPathfinder:
    def __init__(self, size: int, obstacle_ratio: float, seed: int, force_python: bool = False):
        self._force_python = force_python
        self._python_finder = PurePythonAStarPathfinder(size, obstacle_ratio, seed)
        self._native = None if force_python else _load_native()
        self._last_telemetry: Optional[SearchTelemetry] = None

    def find_path(self):
        if self._native is None:
            path, duration, nodes = self._python_finder.find_path()
            self._last_telemetry = SearchTelemetry(duration=duration, nodes_evaluated=nodes)
            return path, duration, nodes

        native_find_path = getattr(self._native, "native_find_path", None)
        if native_find_path is None:
            path, duration, nodes = self._python_finder.find_path()
            self._last_telemetry = SearchTelemetry(duration=duration, nodes_evaluated=nodes)
            return path, duration, nodes

        print("[*] 経路探索開始...")
        result = native_find_path(*self._python_finder.to_native_args())
        if isinstance(result, tuple) and len(result) == 4:
            path, duration, nodes, telemetry = result
            self._last_telemetry = telemetry
            return path, duration, nodes

        return result

    @property
    def telemetry(self) -> Optional[SearchTelemetry]:
        """Return telemetry from the most recent `find_path()` run."""

        return self._last_telemetry
